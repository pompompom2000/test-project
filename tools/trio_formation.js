#!/usr/bin/env node
/**
 * 3連複のフォーメーションを総当たりで作り、的中確率の高い順に並べる。
 *   node tools/trio_formation.js probs.json --odds=odds.json [件数] [--max-tickets=N]
 *
 * 3連複は着順を問わないので、フォーメーションは
 * 「1頭目の候補群 × 2頭目の候補群 × 3頭目の候補群」から
 * 重複を除いた組み合わせの集合になる。
 *
 * 的中確率だけで並べると点数の多い買い目が上に来るので、
 * 点数・損益分岐オッズ・期待値を必ず並記する。
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

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith('--') && a.endsWith('.json'));
const limit = Number(args.find((a) => /^\d+$/.test(a)) || 15);
const oddsArg = args.find((a) => a.startsWith('--odds='));
const maxArg = args.find((a) => a.startsWith('--max-tickets='));
const maxTickets = maxArg ? Number(maxArg.split('=')[1]) : 60;

const data = JSON.parse(fs.readFileSync(file, 'utf8'));
const odds = oddsArg ? JSON.parse(fs.readFileSync(oddsArg.split('=')[1], 'utf8')).trio : null;

const horses = data.horses;
const p = horses.map((h) => h.p);
const order = horses.map((_, i) => i).sort((a, b) => p[b] - p[a]);
const no = (i) => horses[i].no;
const key = (nos) => nos.slice().sort((a, b) => a - b).map((n) => String(n).padStart(2, '0')).join('');

/** 3グループから、重複を除いた3頭の組み合わせを作る。 */
function formation(A, B, C) {
  const seen = new Set();
  const out = [];
  A.forEach((a) => B.forEach((b) => C.forEach((c) => {
    if (a === b || b === c || a === c) return;
    const t = [a, b, c].sort((x, y) => x - y);
    const k = t.join('-');
    if (seen.has(k)) return;
    seen.add(k);
    out.push(t);
  })));
  return out;
}

const bets = [];
const label = (g) => g.map(no).join('・');

function add(name, A, B, C) {
  const tickets = formation(A, B, C);
  if (!tickets.length || tickets.length > maxTickets) return;
  const hit = tickets.reduce((s, t) => s + context.probExactTop(p, t), 0);
  let ev = null;
  if (odds) {
    const payouts = tickets.map((t) => {
      const v = odds[key(t.map(no))];
      // 1000倍以上は "1,312.5" のようにカンマ区切りで来るので取り除く
      const x = v ? Number(String(v[0]).replace(/,/g, '')) : NaN;
      return Number.isFinite(x) && x > 0 ? x : null;
    });
    if (payouts.every((o) => o !== null)) {
      ev = tickets.reduce((s, t, i) => s + context.probExactTop(p, t) * payouts[i], 0) / tickets.length;
    }
  }
  const sig = tickets.map((t) => t.join('-')).sort().join(',');
  bets.push({ name, tickets: tickets.length, hit, ev, sig });
}

const top = (n) => order.slice(0, n);
const range = (a, b) => order.slice(a, b);

// 1頭軸流し: 軸1頭 × 相手n頭から2頭
for (let n = 3; n <= 9; n += 1) {
  add(`軸${no(order[0])} → 相手${label(range(1, 1 + n))}`, [order[0]], range(1, 1 + n), range(1, 1 + n));
}
// 2頭軸流し: 軸2頭 + 相手n頭から1頭
for (let n = 2; n <= 9; n += 1) {
  add(`軸${no(order[0])}・${no(order[1])} → 相手${label(range(2, 2 + n))}`,
    [order[0]], [order[1]], range(2, 2 + n));
}
// フォーメーション: 1列目は軸、2列目は上位、3列目を広げる
for (let b = 2; b <= 5; b += 1) {
  for (let c = b + 1; c <= 10; c += 1) {
    add(`${no(order[0])} × ${label(range(1, 1 + b))} × ${label(range(1, 1 + c))}`,
      [order[0]], range(1, 1 + b), range(1, 1 + c));
  }
}
// 軸なしフォーメーション: 上位群 × 中位群 × 広め
for (let a = 2; a <= 4; a += 1) {
  for (let b = a + 1; b <= 6; b += 1) {
    for (let c = b + 1; c <= 10; c += 1) {
      add(`${label(top(a))} × ${label(top(b))} × ${label(top(c))}`, top(a), top(b), top(c));
    }
  }
}
// ボックス
for (let n = 4; n <= 8; n += 1) add(`${label(top(n))} ボックス`, top(n), top(n), top(n));

// 同じ買い目になったものは点数が少ないほうだけ残す
const uniq = new Map();
bets.forEach((b) => {
  const prev = uniq.get(b.sig);
  if (!prev || b.name.length < prev.name.length) uniq.set(b.sig, b);
});
const list = [...uniq.values()].sort((a, b) => b.hit - a.hit);

console.log(`\n■ ${data.title}  3連複フォーメーション`);
console.log(`  的中確率の高い順（${maxTickets}点以下）。損益分岐＝点数÷的中確率\n`);
console.log('順  買い方                                          点数  的中確率  損益分岐   期待値');
list.slice(0, limit).forEach((b, i) => {
  console.log(
    `${String(i + 1).padStart(2)}  ${b.name.padEnd(46)}${String(b.tickets).padStart(4)}  ` +
      `${(b.hit * 100).toFixed(1).padStart(6)}%  ${(b.tickets / b.hit).toFixed(1).padStart(7)}倍  ` +
      `${(b.ev === null ? '-' : b.ev.toFixed(3)).padStart(6)}`
  );
});

if (odds) {
  const byEv = list.filter((b) => b.ev !== null).sort((a, b) => b.ev - a.ev).slice(0, 5);
  console.log('\n■ 期待値が高い順（上位5）');
  byEv.forEach((b) => {
    console.log(
      `   ${b.name.padEnd(46)}${String(b.tickets).padStart(4)}点  ` +
        `的中${(b.hit * 100).toFixed(1)}%  期待値 ${b.ev.toFixed(3)}`
    );
  });
}
