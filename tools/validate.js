#!/usr/bin/env node
/**
 * 過去レースでモデルの重みを検証する。
 *   node tools/validate.js data/validation/*.json
 *
 * 各レースについて、モデルの評価スコアから求めた勝率と、
 * 市場（単勝オッズ）から求めた勝率を合成し、実際の勝ち馬に
 * どれだけ高い確率を与えられていたかを対数損失で測る。
 *
 * 対数損失（小さいほど良い）:
 *   L = -1/N × Σ log P(実際の勝ち馬)
 *
 * 合成の重み w を 0（市場のみ）から 1（モデルのみ）まで動かし、
 * 損失が最小になる w を探す。w が 0 に近ければモデルは市場に
 * 情報を足せていない、という結論になる。
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

const files = process.argv.slice(2);
if (!files.length) {
  console.error('usage: node tools/validate.js <race.json ...>');
  process.exit(1);
}

/** 1レースぶんの確率を求める。 */
function prepare(input) {
  const race = {
    surfaceKey: input.surface,
    stateKey: input.state,
    course: context.getCourse(input.courseKey),
    trend: input.trend ? context.parseTrend(input.trend) : null,
    popularity: input.trend ? context.parsePopularity(input.trend.popularity || '') : [],
  };
  const evaluated = context.evaluateRace(input.horses, race);
  const byNo = [...evaluated.horses].sort((a, b) => a.no - b.no);

  const scores = byNo.map((h) => h.score);
  const odds = byNo.map((h) => h.odds || 0);
  if (!odds.every((o) => o > 0)) return null;

  const market = context.marketProbs(odds);
  const temperature = context.calibrateTemperature(scores, context.entropy(market));
  const model = context.softmaxProbs(scores, temperature);

  const index = new Map(byNo.map((h, i) => [h.no, i]));
  const finish = input.finish.map((no) => index.get(no)).filter((i) => i !== undefined);
  if (finish.length < 3) return null;

  return { model, market, finish, n: byNo.length, title: input.title };
}

const races = files
  .map((f) => {
    try {
      return prepare(JSON.parse(fs.readFileSync(f, 'utf8')));
    } catch (e) {
      console.error(`skip ${path.basename(f)}: ${e.message}`);
      return null;
    }
  })
  .filter(Boolean);

if (!races.length) {
  console.error('検証できるレースがありません（単勝オッズと着順が必要です）');
  process.exit(1);
}

/** 重み w でのレースごとの単勝対数損失を返す（有意性の検定用）。 */
function perRaceWinLoss(weight) {
  return races.map((r) => {
    const p = weight === 0 ? r.market : weight === 1 ? r.model : context.blendProbs(r.model, r.market, weight);
    return -Math.log(Math.max(p[r.finish[0]], 1e-12));
  });
}

/**
 * 対応のある差の平均と標準誤差。
 * 同じレースを両方の重みで評価しているので、レース間のばらつきを
 * 打ち消せる対応のある比較を使う。
 */
function pairedDiff(a, b) {
  const diffs = a.map((x, i) => x - b[i]);
  const n = diffs.length;
  const mean = diffs.reduce((s, d) => s + d, 0) / n;
  const variance = diffs.reduce((s, d) => s + (d - mean) ** 2, 0) / (n - 1);
  return { mean, se: Math.sqrt(variance / n), n };
}

/** 重み w での対数損失と的中指標。 */
function score(weight) {
  let winLoss = 0;
  let placeLoss = 0;
  let topPickWins = 0;
  let topPickPlaces = 0;

  races.forEach((r) => {
    const p = weight === 0 ? r.market : weight === 1 ? r.model : context.blendProbs(r.model, r.market, weight);
    const winner = r.finish[0];
    winLoss += -Math.log(Math.max(p[winner], 1e-12));

    const top3 = new Set(r.finish.slice(0, 3));
    p.forEach((prob, i) => {
      const placeProb = Math.min(Math.max(context.probPlace(p, i), 1e-9), 1 - 1e-9);
      const actual = top3.has(i) ? 1 : 0;
      placeLoss += -(actual * Math.log(placeProb) + (1 - actual) * Math.log(1 - placeProb));
    });

    let best = 0;
    p.forEach((prob, i) => {
      if (prob > p[best]) best = i;
    });
    if (best === winner) topPickWins += 1;
    if (top3.has(best)) topPickPlaces += 1;
  });

  const horseCount = races.reduce((s, r) => s + r.n, 0);
  return {
    weight,
    winLoss: winLoss / races.length,
    placeLoss: placeLoss / horseCount,
    winRate: topPickWins / races.length,
    placeRate: topPickPlaces / races.length,
  };
}

const grid = [];
for (let w = 0; w <= 1.0001; w += 0.05) grid.push(score(Math.round(w * 100) / 100));

console.log(`\n■ 検証対象 ${races.length}レース\n`);
console.log('重み w   単勝の対数損失   複勝の対数損失   本命の勝率   本命の複勝率');
grid.forEach((g) => {
  console.log(
    `${g.weight.toFixed(2).padStart(5)}   ${g.winLoss.toFixed(4).padStart(12)}   ` +
      `${g.placeLoss.toFixed(4).padStart(12)}   ${(g.winRate * 100).toFixed(1).padStart(8)}%   ` +
      `${(g.placeRate * 100).toFixed(1).padStart(9)}%`
  );
});

const bestWin = grid.reduce((a, b) => (b.winLoss < a.winLoss ? b : a));
const bestPlace = grid.reduce((a, b) => (b.placeLoss < a.placeLoss ? b : a));
const marketOnly = grid[0];
const modelOnly = grid[grid.length - 1];

console.log('\n結論');
console.log(`  単勝の対数損失が最小になる重み: w=${bestWin.weight.toFixed(2)}（損失 ${bestWin.winLoss.toFixed(4)}）`);
console.log(`  複勝の対数損失が最小になる重み: w=${bestPlace.weight.toFixed(2)}（損失 ${bestPlace.placeLoss.toFixed(4)}）`);
console.log(`  市場のみ（w=0）: ${marketOnly.winLoss.toFixed(4)} / モデルのみ（w=1）: ${modelOnly.winLoss.toFixed(4)}`);
// 最良の重みと市場のみを、対応のある差で比較する
const diff = pairedDiff(perRaceWinLoss(0), perRaceWinLoss(bestWin.weight));
const t = diff.se > 0 ? diff.mean / diff.se : 0;
console.log(
  `\n  市場のみ − w=${bestWin.weight.toFixed(2)} の損失差: ${diff.mean.toFixed(4)} ± ${diff.se.toFixed(4)}（標準誤差, n=${diff.n}）`
);
console.log(`  t値 ${t.toFixed(2)}`);

if (Math.abs(t) < 2) {
  console.log('  → 差は誤差の範囲。この標本数では、モデルが市場に情報を足しているとは言えない。');
} else if (t > 0) {
  console.log('  → 統計的に意味のある改善。モデルは市場に情報を足している。');
} else {
  console.log('  → モデルを混ぜると有意に悪化している。');
}
console.log(`  モデル単独（w=1）は市場より ${(modelOnly.winLoss - marketOnly.winLoss).toFixed(4)} 悪い。`);

// レース数が少ないときの目安を添える
if (races.length < 30) {
  console.log(`\n  ※ ${races.length}レースは標本として少なく、最適な w は偶然で±0.1程度動きます。`);
}
