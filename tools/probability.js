#!/usr/bin/env node
/**
 * レースの的中確率を計算する。
 *   node tools/probability.js data/races/<race>.json [買い目...]
 *
 * 買い目は "券種:馬番,馬番,..." の形で複数指定できる。
 *   例: node tools/probability.js race.json 3連複:12,2,3,6,5 ワイド:12,2,3
 * 省略した場合は、上位5頭の代表的な買い方を自動で評価する。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.join(__dirname, '..');
const context = vm.createContext({ console, Math, Object, Number, Array, String, JSON, Set, Infinity });
[
  'assets/js/sire-data.js',
  'assets/js/course-data.js',
  'assets/js/gaikyu-data.js',
  'assets/js/engine.js',
  'assets/js/probability.js',
].forEach((f) => vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), context, { filename: f }));

const file = process.argv[2];
if (!file) {
  console.error('usage: node tools/probability.js <race.json> [券種:馬番,馬番,...]');
  process.exit(1);
}
const input = JSON.parse(fs.readFileSync(file, 'utf8'));

const race = {
  surfaceKey: input.surface,
  stateKey: input.state,
  course: context.getCourse(input.courseKey),
  trend: input.trend ? context.parseTrend(input.trend) : null,
  popularity: input.trend ? context.parsePopularity(input.trend.popularity || '') : [],
};

const horses = input.horses.map((h) => ({ ...h, comment: h.comment || null, training: h.training || null }));
const result = context.evaluateRace(horses, race);

// evaluateRace は評価順に並ぶので、馬番順に並べ直してから確率を出す
const byNo = [...result.horses].sort((a, b) => a.no - b.no);
const scores = byNo.map((h) => h.score);
const odds = byNo.map((h) => h.odds || 0);
const idxOf = new Map(byNo.map((h, i) => [h.no, i]));

const hasOdds = odds.every((o) => o > 0);
const market = context.marketProbs(odds);
const temperature = hasOdds
  ? context.calibrateTemperature(scores, context.entropy(market))
  : 12;
const p = context.softmaxProbs(scores, temperature);

const pct = (v) => `${(v * 100).toFixed(1)}%`;

console.log(`\n■ ${input.title || ''}`);
console.log(`  馬場:${result.state.label} / 波乱度 ${result.shakeUp}`);
console.log(`  温度パラメータ ${temperature.toFixed(1)}（市場のエントロピー ${context.entropy(market).toFixed(3)} に合わせて決定）\n`);

console.log('馬番 馬名             モデル勝率  市場勝率   複勝率   単勝オッズ  単勝期待値');
byNo.forEach((h, i) => {
  const ev = odds[i] > 0 ? p[i] * odds[i] : null;
  console.log(
    `${String(h.no).padStart(3)}  ${h.name.padEnd(14)} ${pct(p[i]).padStart(8)} ${pct(market[i]).padStart(8)} ` +
      `${pct(context.probPlace(p, i)).padStart(8)} ${(odds[i] || '-').toString().padStart(9)} ` +
      `${(ev === null ? '-' : ev.toFixed(2)).padStart(9)}`
  );
});

const args = process.argv.slice(3);
const blendArg = args.find((a) => a.startsWith('--blend='));
const checkArg = args.find((a) => a.startsWith('--check='));
const weight = blendArg ? Number(blendArg.split('=')[1]) : 0.35;
const pBlend = hasOdds ? context.blendProbs(p, market, weight) : p;

if (hasOdds) {
  console.log(`\n市場と合成した確率（モデルの重み ${weight}）`);
  console.log('馬番 馬名             合成勝率   合成複勝率  単勝オッズ  単勝期待値');
  byNo.forEach((h, i) => {
    const ev = pBlend[i] * odds[i];
    console.log(
      `${String(h.no).padStart(3)}  ${h.name.padEnd(14)} ${pct(pBlend[i]).padStart(8)} ` +
        `${pct(context.probPlace(pBlend, i)).padStart(9)} ${odds[i].toString().padStart(9)} ` +
        `${ev.toFixed(2).padStart(9)}`
    );
  });
}

const pUse = hasOdds ? pBlend : p;
const bets = args.filter((a) => !a.startsWith('--'));
const specs = bets.length
  ? bets.map((b) => {
      const [type, list] = b.split(':');
      return { type, nos: list.split(',').map(Number) };
    })
  : defaultBets(result.horses);

console.log('\n買い目の的中確率');
console.log('券種      買い目                      点数  的中確率   損益分岐オッズ');
specs.forEach((spec) => {
  const idx = spec.nos.map((n) => idxOf.get(n));
  if (idx.some((i) => i === undefined)) {
    console.log(`  ${spec.type}: 馬番が見つかりません（${spec.nos.join(',')}）`);
    return;
  }
  const r = context.evaluateBet(pUse, { type: spec.type, horses: idx });
  const be = context.breakEvenOdds(r.probability, r.tickets);
  console.log(
    `${spec.type.padEnd(8)} ${spec.nos.join('-').padEnd(26)} ${String(r.tickets).padStart(4)}  ` +
      `${pct(r.probability).padStart(7)}   ${be === Infinity ? '-' : `${be.toFixed(1)}倍`}`
  );
});

if (checkArg) {
  const nos = checkArg.split('=')[1].split(/[-,]/).map(Number);
  const idx = nos.map((n) => idxOf.get(n));
  console.log(`\n実際の着順 ${nos.join('→')} にモデルが与えていた確率`);
  const raw = context.scoreActualResult(p, idx);
  const bl = context.scoreActualResult(pUse, idx);
  const mk = context.scoreActualResult(market, idx);
  console.log('券種      モデル単独    市場との合成   市場');
  Object.keys(raw).forEach((k) => {
    const f = (v) => (v === null ? '-' : `${(v * 100).toFixed(2)}%`);
    console.log(`${k.padEnd(8)} ${f(raw[k]).padStart(10)} ${f(bl[k]).padStart(13)} ${f(mk[k]).padStart(10)}`);
  });
}

/** 買い目の指定がないときの既定の評価対象。 */
function defaultBets(ranked) {
  const top = ranked.slice(0, 5).map((h) => h.no);
  return [
    { type: '単勝', nos: [top[0]] },
    { type: '複勝', nos: [top[0]] },
    { type: 'ワイド', nos: top.slice(0, 3) },
    { type: '馬連', nos: top.slice(0, 3) },
    { type: '3連複', nos: top },
    { type: '3連単', nos: top.slice(0, 3) },
  ];
}
