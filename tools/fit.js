#!/usr/bin/env node
/**
 * 検証用レースから係数を学習する（条件付きロジット／Plackett-Luce）。
 *
 *   node tools/fit.js data/validation/*.json
 *   node tools/fit.js --with-market data/validation/*.json
 *
 * 各馬の効用を u_i = w·x_i とし、レース内のソフトマックスで着順の
 * 尤度を最大化する。1着だけでなく3着までの並びを使う Plackett-Luce に
 * することで、少ないレース数から取れる情報を増やしている。
 *
 *   L = -Σ_race [ log p(1着) + log p(2着|1着を除く) + log p(3着|上位2頭を除く) ]
 *       + λ‖w‖²
 *
 * 59レース程度では係数を素直に当てると過学習するため、正則化の強さ λ は
 * 交差検証で選び、性能も必ず交差検証で報告する（学習に使ったレースでの
 * 当てはまりの良さは意味がない）。
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

const args = process.argv.slice(2);
const withMarket = args.includes('--with-market');
// --g1: 秋G1向けの特徴量セットを使う（良馬場中心なので道悪以外の材料が要る）
const useG1 = args.includes('--g1');
// --predict=<file>: 学習したモデルで未来のレースの確率を出す
const predictArg = args.find((a) => a.startsWith('--predict='));
// --offset: 市場の対数確率を係数1固定のオフセットとして使う。
// w=0 のときモデルは市場と完全に一致するので、「市場に情報を
// 上乗せできるか」を公平に測れる。
const useOffset = args.includes('--offset');
const files = args.filter((a) => !a.startsWith('--'));
const predictFile = predictArg ? predictArg.split('=')[1] : null;

/* ---------- 特徴量 ---------- */

const PRIOR_RATE = 0.3; // 複勝率の事前値。出走数が少ない馬をここへ縮める
const PRIOR_N = 2;

const shrunk = (places, starts) => (places + PRIOR_N * PRIOR_RATE) / (starts + PRIOR_N) - PRIOR_RATE;

/* ---------- 秋G1向けの特徴量 ---------- */

const G1_FEATURES = [
  '芝の複勝率', '芝の勝率', '芝の経験',
  'G1の3着内率', 'G1の経験', '重賞の3着内率', '重賞の経験',
  '同距離帯の複勝率', '同距離帯の経験', '同競馬場の複勝率', '同競馬場の経験',
  '前走着順', '前走人気', '前走からの間隔', '長期休養明け',
  '斤量', '年齢', '馬体重', '枠順(内→外)',
  '脚質:逃げ', '脚質:先行', '脚質:差し',
  '血統:道悪で狙える', '血統:道悪で狙い難い',
];

/** 前走着順を0〜1に直す。1着=1、最下位=0。 */
function finishScore(place, field) {
  if (!place || !field || field < 2) return 0.5;
  return 1 - (place - 1) / (field - 1);
}

function featurizeG1(h, input) {
  const sire = context.sireEvaluation(input.surface, input.state, h.sire, h.sex);
  const has = (label) => sire.tags.some((t) => t.label.includes(label));
  const days = h.daysSinceLast;

  return [
    shrunk(h.places, h.starts),
    shrunk(h.wins, h.starts),
    Math.log(1 + h.starts) / 3,
    shrunk(h.g1Places, h.g1Starts),
    Math.log(1 + h.g1Starts) / 2,
    shrunk(h.gradePlaces, h.gradeStarts),
    Math.log(1 + h.gradeStarts) / 2.5,
    shrunk(h.distPlaces, h.distStarts),
    Math.log(1 + h.distStarts) / 2.5,
    shrunk(h.coursePlaces, h.courseStarts),
    Math.log(1 + h.courseStarts) / 2,
    finishScore(h.lastFinish, h.lastField),
    h.lastPopularity ? 1 / h.lastPopularity : 0.25,
    days ? Math.min(Math.log(1 + days) / 5, 1.5) : 0.7,
    days && days > 120 ? 1 : 0,
    h.handicap ? (h.handicap - 56) / 2 : 0,
    h.age ? (h.age - 4) / 2 : 0,
    h.weight ? (h.weight - 470) / 30 : 0,
    h.post ? (h.post - 4.5) / 3.5 : 0,
    h.style === '逃げ' ? 1 : 0,
    h.style === '先行' ? 1 : 0,
    h.style === '差し' ? 1 : 0,
    has('狙える') ? 1 : 0,
    has('狙い難い') ? 1 : 0,
  ];
}

const FEATURES = [
  '良馬場複勝率', '良馬場の経験', '良馬場データなし',
  '道悪複勝率', '道悪の経験', '道悪データなし', '道悪−良馬場の差',
  '血統:狙える', '血統:狙い難い', '血統:馬場別要注意', '血統:馬場別いまいち', '血統:2026推し',
  '血統:旧データ巧者', '血統:旧データ不振',
  '馬体重', '馬体重データなし', '枠順(内→外)',
  '脚質:逃げ', '脚質:先行', '脚質:差し',
];

function featurize(h, input) {
  const db = context.SIRE_DB ? null : null; // SIRE_DB は const のため lookup 関数経由で使う
  const sire = context.sireEvaluation(input.surface, input.state, h.sire, h.sex);
  const has = (label) => sire.tags.some((t) => t.label.includes(label));

  const legacy = context.legacyTurfHit(input.surface, (h.sire || '').trim());

  const x = [
    shrunk(h.firmPlaces, h.firmStarts),
    Math.log(1 + h.firmStarts) / 3,
    h.firmStarts === 0 ? 1 : 0,
    shrunk(h.mudPlaces, h.mudStarts),
    Math.log(1 + h.mudStarts) / 3,
    h.mudStarts === 0 ? 1 : 0,
    h.firmStarts > 0 && h.mudStarts > 0 ? shrunk(h.mudPlaces, h.mudStarts) - shrunk(h.firmPlaces, h.firmStarts) : 0,
    has('狙える') ? 1 : 0,
    has('狙い難い') ? 1 : 0,
    has('要注意') ? 1 : 0,
    has('いまいち') ? 1 : 0,
    has('推し') ? 1 : 0,
    legacy && legacy.tier !== 'weak' ? 1 : 0,
    legacy && legacy.tier === 'weak' ? 1 : 0,
    h.weight ? (h.weight - 470) / 30 : 0,
    h.weight ? 0 : 1,
    h.post ? (h.post - 4.5) / 3.5 : 0,
    h.style === '逃げ' ? 1 : 0,
    h.style === '先行' ? 1 : 0,
    h.style === '差し' ? 1 : 0,
  ];
  return x;
}

/* ---------- データ読み込み ---------- */

const races = files
  .map((f) => {
    const input = JSON.parse(fs.readFileSync(f, 'utf8'));
    const byNo = new Map(input.horses.map((h) => [h.no, h]));
    const order = input.finish.map((no) => byNo.get(no)).filter(Boolean);
    if (order.length < 3) return null;
    const horses = input.horses;
    const odds = horses.map((h) => h.odds || 0);
    if (!odds.every((o) => o > 0)) return null;

    const market = context.marketProbs(odds);
    const index = new Map(horses.map((h, i) => [h.no, i]));
    return {
      title: input.title,
      X: horses.map((h) => {
        const base = useG1 ? featurizeG1(h, input) : featurize(h, input);
        return withMarket ? [...base, Math.log(Math.max(market[horses.indexOf(h)], 1e-6))] : base;
      }),
      offset: horses.map((h, i) => Math.log(Math.max(market[i], 1e-6))),
      market,
      finishIdx: input.finish.map((no) => index.get(no)).filter((i) => i !== undefined),
      n: horses.length,
    };
  })
  .filter(Boolean);

const featureNames = useG1 ? G1_FEATURES : FEATURES;
const names = withMarket ? [...featureNames, '市場の対数確率'] : featureNames;

/** 予測対象のレースを読む（着順が未確定でもよい）。 */
function loadTarget(file) {
  const input = JSON.parse(fs.readFileSync(file, 'utf8'));
  return {
    title: input.title,
    horses: input.horses,
    X: input.horses.map((h) => (useG1 ? featurizeG1(h, input) : featurize(h, input))),
  };
}
const target = predictFile ? loadTarget(predictFile) : null;
const D = names.length;

// 特徴量を標準化する（係数の大きさを比べられるようにするため）
const mean = new Array(D).fill(0);
const sd = new Array(D).fill(0);
let count = 0;
races.forEach((r) => r.X.forEach((x) => { x.forEach((v, j) => { mean[j] += v; }); count += 1; }));
mean.forEach((_, j) => { mean[j] /= count; });
races.forEach((r) => r.X.forEach((x) => x.forEach((v, j) => { sd[j] += (v - mean[j]) ** 2; })));
sd.forEach((_, j) => { sd[j] = Math.sqrt(sd[j] / count) || 1; });
races.forEach((r) => { r.Z = r.X.map((x) => x.map((v, j) => (v - mean[j]) / sd[j])); });
if (target) target.Z = target.X.map((x) => x.map((v, j) => (v - mean[j]) / sd[j]));

/* ---------- 学習 ---------- */

function softmaxOver(z, w, active, offset) {
  const u = active.map((i) => z[i].reduce((s, v, j) => s + v * w[j], 0) + (offset ? offset[i] : 0));
  const m = Math.max(...u);
  const e = u.map((v) => Math.exp(v - m));
  const sum = e.reduce((a, b) => a + b, 0);
  return e.map((v) => v / sum);
}

/** Plackett-Luce の負の対数尤度と勾配。 */
function lossAndGrad(trainRaces, w, lambda) {
  let loss = 0;
  const grad = new Array(w.length).fill(0);

  trainRaces.forEach((r) => {
    let active = r.Z.map((_, i) => i);
    r.finishIdx.slice(0, 3).forEach((winner) => {
      const pos = active.indexOf(winner);
      if (pos < 0) return;
      const p = softmaxOver(r.Z, w, active, useOffset ? r.offset : null);
      loss += -Math.log(Math.max(p[pos], 1e-12));
      // 勾配: -(x_winner - Σ p_i x_i)
      // 馬ごとに一度だけ回して期待値を足し込む（特徴量ごとに回すより速い）
      const expected = new Array(w.length).fill(0);
      for (let k = 0; k < active.length; k += 1) {
        const z = r.Z[active[k]];
        const pk = p[k];
        for (let j = 0; j < w.length; j += 1) expected[j] += pk * z[j];
      }
      const zw = r.Z[winner];
      for (let j = 0; j < w.length; j += 1) grad[j] -= zw[j] - expected[j];
      active = active.filter((i) => i !== winner);
    });
  });

  for (let j = 0; j < w.length; j += 1) {
    loss += lambda * w[j] * w[j];
    grad[j] += 2 * lambda * w[j];
  }
  return { loss, grad };
}

/** Adam による最適化。 */
function fit(trainRaces, lambda, iterations = 1500) {
  let w = new Array(D).fill(0);
  const m = new Array(D).fill(0);
  const v = new Array(D).fill(0);
  const lr = 0.05;
  for (let t = 1; t <= iterations; t += 1) {
    const { grad } = lossAndGrad(trainRaces, w, lambda);
    for (let j = 0; j < D; j += 1) {
      m[j] = 0.9 * m[j] + 0.1 * grad[j];
      v[j] = 0.999 * v[j] + 0.001 * grad[j] * grad[j];
      const mh = m[j] / (1 - 0.9 ** t);
      const vh = v[j] / (1 - 0.999 ** t);
      w[j] -= (lr * mh) / (Math.sqrt(vh) + 1e-8);
    }
  }
  return w;
}

/** 単勝の対数損失（評価用）。 */
function winLoss(testRaces, w) {
  let total = 0;
  testRaces.forEach((r) => {
    const active = r.Z.map((_, i) => i);
    const p = softmaxOver(r.Z, w, active, useOffset ? r.offset : null);
    total += -Math.log(Math.max(p[r.finishIdx[0]], 1e-12));
  });
  return total / testRaces.length;
}

function marketLoss(testRaces) {
  let total = 0;
  testRaces.forEach((r) => { total += -Math.log(Math.max(r.market[r.finishIdx[0]], 1e-12)); });
  return total / testRaces.length;
}

/* ---------- 交差検証 ---------- */

const K = 5;
const folds = Array.from({ length: K }, () => []);
races.forEach((r, i) => folds[i % K].push(r));

/** 交差検証。レースごとの損失も返して、市場との対応のある比較に使う。 */
function crossValidate(lambda) {
  const perRace = [];
  folds.forEach((testSet, k) => {
    if (!testSet.length) return;
    const trainSet = folds.filter((_, i) => i !== k).flat();
    const w = fit(trainSet, lambda, 400);
    testSet.forEach((r) => {
      perRace.push({
        model: winLoss([r], w),
        market: marketLoss([r]),
      });
    });
  });
  return {
    loss: perRace.reduce((s, x) => s + x.model, 0) / perRace.length,
    perRace,
  };
}

/** 対応のある差の平均と標準誤差。 */
function pairedDiff(pairs) {
  const diffs = pairs.map((x) => x.market - x.model);
  const n = diffs.length;
  const mean = diffs.reduce((s, d) => s + d, 0) / n;
  const variance = diffs.reduce((s, d) => s + (d - mean) ** 2, 0) / (n - 1);
  return { mean, se: Math.sqrt(variance / n), n };
}

console.log(
  `\n■ 係数の学習（${races.length}レース, 特徴量${D}個` +
    `${useOffset ? ', 市場をオフセットに固定' : withMarket ? ', 市場の確率を特徴量に含む' : ''}）\n`
);

const lambdas = [1, 3, 10, 30, 100, 300];
console.log('正則化λ   交差検証の単勝対数損失');
const cv = lambdas.map((l) => {
  const v = crossValidate(l);
  console.log(`${String(l).padStart(7)}   ${v.loss.toFixed(4)}`);
  return { lambda: l, ...v };
});
const best = cv.reduce((a, b) => (b.loss < a.loss ? b : a));
const base = marketLoss(races);

console.log(`\n最良のλ = ${best.lambda}（交差検証の損失 ${best.loss.toFixed(4)}）`);
console.log(`市場のみの損失         ${base.toFixed(4)}`);
console.log(
  best.loss < base
    ? `→ 学習したモデルは市場より ${(base - best.loss).toFixed(4)} 良い`
    : `→ 学習したモデルは市場より ${(best.loss - base).toFixed(4)} 悪い`
);

const d = pairedDiff(best.perRace);
const t = d.se > 0 ? d.mean / d.se : 0;
console.log(`\n  市場 − モデル の損失差: ${d.mean.toFixed(4)} ± ${d.se.toFixed(4)}（標準誤差, n=${d.n}）`);
console.log(`  t値 ${t.toFixed(2)}`);
if (Math.abs(t) < 2) {
  console.log('  → 差は誤差の範囲。この標本数では市場を上回っているとは言えない。');
} else if (t > 0) {
  console.log('  → 統計的に意味のある改善。');
} else {
  console.log('  → 統計的に意味のある悪化。');
}
console.log('  ※ λ を同じ交差検証で選んでいるため、この差はやや楽観的に出ている。');

const wFinal = fit(races, best.lambda, 2000);
console.log('\n学習した係数（標準化後。絶対値が大きいほど効いている）');
names
  .map((name, j) => ({ name, w: wFinal[j] }))
  .sort((a, b) => Math.abs(b.w) - Math.abs(a.w))
  .forEach((f) => {
    const bar = '■'.repeat(Math.min(30, Math.round(Math.abs(f.w) * 20)));
    console.log(`${f.name.padEnd(18)} ${f.w >= 0 ? '+' : '-'}${Math.abs(f.w).toFixed(3)} ${bar}`);
  });


/* ---------- 未来のレースを予測する ---------- */

if (target) {
  const active = target.Z.map((_, i) => i);
  const p = softmaxOver(target.Z, wFinal, active, null);
  const place = target.Z.map((_, i) => {
    // 3着以内の確率は Harville モデルで近似する
    const probs = p;
    let total = probs[i];
    for (let j = 0; j < probs.length; j += 1) {
      if (j === i) continue;
      total += probs[j] * (probs[i] / (1 - probs[j]));
      for (let k = 0; k < probs.length; k += 1) {
        if (k === i || k === j) continue;
        total += probs[j] * (probs[k] / (1 - probs[j])) * (probs[i] / (1 - probs[j] - probs[k]));
      }
    }
    return Math.min(total, 1);
  });

  const order = active.slice().sort((a, b) => p[b] - p[a]);
  console.log(`\n\n■ 予測: ${target.title}`);
  console.log('  ※ この特徴量だけのモデルは、過去検証で市場（単勝オッズ）に0.31及ばない。\n');
  console.log('順位 馬番 馬名             勝率    複勝率   損益分岐の単勝オッズ');
  order.forEach((i, rank) => {
    const h = target.horses[i];
    console.log(
      `${String(rank + 1).padStart(3)}  ${String(h.no).padStart(3)}  ${h.name.padEnd(16)}` +
        `${(p[i] * 100).toFixed(1).padStart(5)}%  ${(place[i] * 100).toFixed(1).padStart(5)}%  ` +
        `${(1 / p[i]).toFixed(1).padStart(8)}倍`
    );
  });

  // 単勝オッズがあれば市場と合成する。検証では市場に勝てていないため、
  // モデルは市場からの「ずらし幅」として控えめに使う。
  const odds = target.horses.map((h) => h.odds || 0);
  if (odds.every((o) => o > 0)) {
    const market = context.marketProbs(odds);
    const weight = 0.15;
    const blend = context.blendProbs(p, market, weight);
    const placeBlend = blend.map((_, i) => context.probPlace(blend, i));
    const ranked = active.slice().sort((a, b) => blend[b] - blend[a]);

    console.log(`\n■ 市場と合成した確率（モデルの重み ${weight}）`);
    console.log('順位 馬番 馬名             合成勝率  市場勝率  複勝率   単勝オッズ  期待値');
    ranked.forEach((i, rank) => {
      const h = target.horses[i];
      console.log(
        `${String(rank + 1).padStart(3)}  ${String(h.no).padStart(3)}  ${h.name.padEnd(16)}` +
          `${(blend[i] * 100).toFixed(1).padStart(6)}%  ${(market[i] * 100).toFixed(1).padStart(6)}%  ` +
          `${(placeBlend[i] * 100).toFixed(1).padStart(5)}%  ${odds[i].toFixed(1).padStart(8)}  ` +
          `${(blend[i] * odds[i]).toFixed(2).padStart(6)}`
      );
    });
  }
}
