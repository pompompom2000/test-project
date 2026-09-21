#!/usr/bin/env node
/**
 * 各馬の勝率から、買い方ごとの的中確率を計算して並べる。
 *   node tools/bet_rank.js probs.json [表示件数]
 *
 * 的中確率だけで並べると、点数の多い買い目と堅い買い目が必ず上に来る。
 * 判断には点数と損益分岐オッズが要るので必ず並記する。
 *
 * 損益分岐オッズ = 点数 ÷ 的中確率
 *   （1点100円で買ったとき、これを上回る配当でなければ長期的には負ける）
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const context = vm.createContext({ console, Math, Object, Number, Array, String, JSON, Set, Infinity });
vm.runInContext(
  fs.readFileSync(path.join(__dirname, '..', 'assets/js/probability.js'), 'utf8'),
  context,
  { filename: 'probability.js' }
);

const file = process.argv[2];
const limit = Number(process.argv[3] || 15);
// 実オッズがあれば期待値も出す（単勝・複勝・ワイド・馬連・3連複）
const oddsArg = process.argv.find((a) => a.startsWith('--odds='));
const realOdds = oddsArg ? JSON.parse(fs.readFileSync(oddsArg.split('=')[1], 'utf8')) : null;
if (!file) {
  console.error('usage: node tools/bet_rank.js <probs.json> [件数]');
  process.exit(1);
}
const data = JSON.parse(fs.readFileSync(file, 'utf8'));
const horses = data.horses;
const p = horses.map((h) => h.p);
const order = horses.map((_, i) => i).sort((a, b) => p[b] - p[a]);
const no = (i) => horses[i].no;

/** 券種ごとに、1点ぶんの的中確率を返す。 */
const ticketProb = {
  単勝: (t) => p[t[0]],
  複勝: (t) => context.probPlace(p, t[0]),
  ワイド: (t) => context.probWide(p, t[0], t[1]),
  馬連: (t) => context.probExactTop(p, t),
  馬単: (t) => context.harvilleOrder(p, t),
  '3連複': (t) => context.probExactTop(p, t),
  '3連単': (t) => context.harvilleOrder(p, t),
};

/** 馬番をオッズ表のキー（2桁ゼロ詰め、組み合わせは昇順）に直す。 */
const key = (nos) => nos.slice().sort((a, b) => a - b).map((n) => String(n).padStart(2, '0')).join('');

/** 券種とオッズ表の対応。複勝とワイドは下限・上限があるので下限で見る。 */
const ODDS_TABLE = {
  単勝: 'win', 複勝: 'place', ワイド: 'wide', 馬連: 'quinella',
  '3連複': 'trio', 馬単: 'exacta', '3連単': 'trifecta',
};

/** 着順が意味を持つ券種は、組み合わせを並べ替えずにキーを作る。 */
const ORDERED = new Set(['馬単', '3連単']);

/** 1点ぶんの実オッズ。取れなければ null。 */
function realOddsFor(type, ticket) {
  if (!realOdds) return null;
  const table = realOdds[ODDS_TABLE[type]];
  if (!table) return null;
  const nos = ticket.map((i) => no(i));
  const k = ORDERED.has(type)
    ? nos.map((n) => String(n).padStart(2, '0')).join('')
    : key(nos);
  const v = table[k];
  if (!v) return null;
  const low = Number(v[0]);
  return Number.isFinite(low) && low > 0 ? low : null;
}

const bets = [];
const add = (type, label, tickets) => {
  // 複勝とワイドは「どれか1点でも当たれば的中」なので重複を除いて足す。
  // 他の券種は同着を除けば排反なのでそのまま足せる。
  const probs = tickets.map((t) => ticketProb[type](t));
  const hit =
    type === '複勝' || type === 'ワイド'
      ? 1 - probs.reduce((acc, q) => acc * (1 - q), 1)
      : probs.reduce((a, b) => a + b, 0);
  // 期待値 = Σ(1点の的中確率 × その配当) ÷ 点数
  let ev = null;
  const payouts = tickets.map((t) => realOddsFor(type, t));
  if (payouts.every((o) => o !== null)) {
    ev = tickets.reduce((sum, t, i) => sum + probs[i] * payouts[i], 0) / tickets.length;
  }
  bets.push({ type, label, tickets: tickets.length, hit, ev });
};

const combos = (list, k) => {
  if (k === 0) return [[]];
  if (list.length < k) return [];
  const [h, ...rest] = list;
  return [...combos(rest, k - 1).map((c) => [h, ...c]), ...combos(rest, k)];
};

const top = (n) => order.slice(0, n);
const axis = order[0];
const partners = (n) => order.slice(1, 1 + n);

// 単勝・複勝
add('単勝', `${no(axis)}`, [[axis]]);
[1, 2, 3].forEach((n) => add('複勝', top(n).map(no).join('・'), top(n).map((i) => [i])));

// ワイド
[2, 3, 4, 5].forEach((n) =>
  add('ワイド', `${no(axis)} 軸流し → ${partners(n).map(no).join('・')}`, partners(n).map((j) => [axis, j]))
);
[3, 4].forEach((n) => add('ワイド', `${top(n).map(no).join('・')} ボックス`, combos(top(n), 2)));

// 馬連
[1, 2, 3, 4, 5].forEach((n) =>
  add('馬連', `${no(axis)} 軸流し → ${partners(n).map(no).join('・')}`, partners(n).map((j) => [axis, j]))
);
[3, 4].forEach((n) => add('馬連', `${top(n).map(no).join('・')} ボックス`, combos(top(n), 2)));

// 馬単（1着固定）
[2, 3, 4].forEach((n) =>
  add('馬単', `${no(axis)} 1着固定 → ${partners(n).map(no).join('・')}`, partners(n).map((j) => [axis, j]))
);

// 3連複
[3, 4, 5, 6].forEach((n) =>
  add('3連複', `${no(axis)} 軸1頭流し → ${partners(n).map(no).join('・')}`,
    combos(partners(n), 2).map((c) => [axis, ...c]))
);
[4, 5, 6].forEach((n) => add('3連複', `${top(n).map(no).join('・')} ボックス`, combos(top(n), 3)));

// 3連単（1着固定）
[3, 4].forEach((n) => {
  const list = partners(n);
  const tickets = [];
  combos(list, 2).forEach(([a, b]) => { tickets.push([axis, a, b]); tickets.push([axis, b, a]); });
  add('3連単', `${no(axis)} 1着固定 → ${list.map(no).join('・')}`, tickets);
});

bets.sort((a, b) => b.hit - a.hit);

console.log(`\n■ ${data.title}`);
console.log('  的中確率の高い順。損益分岐オッズ＝点数÷的中確率（1点100円で買った場合）\n');
console.log('順  券種     買い方                                  点数  的中確率  損益分岐   期待値');
bets.slice(0, limit).forEach((b, i) => {
  console.log(
    `${String(i + 1).padStart(2)}  ${b.type.padEnd(7)} ${b.label.padEnd(38)}` +
      `${String(b.tickets).padStart(4)}  ${(b.hit * 100).toFixed(1).padStart(6)}%  ` +
      `${(b.tickets / b.hit).toFixed(1).padStart(7)}倍  ` +
      `${(b.ev === null ? '-' : b.ev.toFixed(3)).padStart(6)}`
  );
});

if (realOdds) {
  const positive = bets.filter((b) => b.ev !== null && b.ev >= 1).sort((a, b) => b.ev - a.ev);
  console.log(
    positive.length
      ? `\n■ 期待値が1.00以上の買い方（${positive.length}件）`
      : '\n■ 期待値が1.00以上の買い方はありません'
  );
  positive.slice(0, 10).forEach((b) => {
    console.log(
      `   ${b.type.padEnd(7)} ${b.label.padEnd(38)}${String(b.tickets).padStart(3)}点  ` +
        `的中${(b.hit * 100).toFixed(1)}%  期待値 ${b.ev.toFixed(3)}`
    );
  });
}
