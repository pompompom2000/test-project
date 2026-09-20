/**
 * 評価スコアから的中確率を計算する。
 *
 * 手順:
 *  1. スコアをソフトマックスで勝率に変換する。
 *  2. 温度パラメータは、市場（単勝オッズ）の確率分布とエントロピーが
 *     揃うように決める。「モデルは市場と同じくらいの自信の強さで
 *     予想している」という前提を置く形で、恣意的な決め打ちを避ける。
 *  3. 2着・3着は Harville モデル（復元なしの逐次抽選）で求める。
 *     P(i→j→k) = p_i × p_j/(1-p_i) × p_k/(1-p_i-p_j)
 *
 * 注意: Harville モデルは人気馬の連対率をやや高く、穴馬をやや低く
 * 見積もる既知の偏りがある。あくまで目安として扱うこと。
 */

/** スコアの配列をソフトマックスで勝率に変換する。 */
function softmaxProbs(scores, temperature) {
  const max = Math.max(...scores);
  const exps = scores.map((s) => Math.exp((s - max) / temperature));
  const sum = exps.reduce((a, b) => a + b, 0);
  return exps.map((e) => e / sum);
}

/** 単勝オッズから市場の推定勝率を出す。控除率を取り除いて合計1に正規化する。 */
function marketProbs(oddsList) {
  const raw = oddsList.map((o) => (o > 0 ? 1 / o : 0));
  const sum = raw.reduce((a, b) => a + b, 0);
  return sum > 0 ? raw.map((r) => r / sum) : oddsList.map(() => 1 / oddsList.length);
}

/** 確率分布のエントロピー（自信の強さの逆指標）。 */
function entropy(probs) {
  return -probs.reduce((sum, p) => sum + (p > 0 ? p * Math.log(p) : 0), 0);
}

/**
 * 市場と同じエントロピーになる温度を二分探索で求める。
 * 温度が低いほど上位に確率が集中し、高いほど平坦になる。
 */
function calibrateTemperature(scores, targetEntropy) {
  let lo = 0.5;
  let hi = 200;
  for (let i = 0; i < 60; i += 1) {
    const mid = (lo + hi) / 2;
    if (entropy(softmaxProbs(scores, mid)) < targetEntropy) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2;
}

/** Harville モデルによる着順（i→j→k）の確率。 */
function harvilleOrder(p, idx) {
  let remaining = 1;
  let prob = 1;
  for (const i of idx) {
    if (remaining <= 1e-12) return 0;
    prob *= p[i] / remaining;
    remaining -= p[i];
  }
  return prob;
}

/** 順列を列挙する。 */
function permutations(list) {
  if (list.length <= 1) return [list];
  const out = [];
  list.forEach((item, i) => {
    const rest = [...list.slice(0, i), ...list.slice(i + 1)];
    permutations(rest).forEach((perm) => out.push([item, ...perm]));
  });
  return out;
}

/** 指定した組み合わせが「順不同で上位 n 着を占める」確率。 */
function probExactTop(p, idx) {
  return permutations(idx).reduce((sum, perm) => sum + harvilleOrder(p, perm), 0);
}

/** i が3着以内に入る確率（複勝）。 */
function probPlace(p, i) {
  const n = p.length;
  let total = p[i];
  for (let j = 0; j < n; j += 1) {
    if (j === i) continue;
    total += harvilleOrder(p, [j, i]);
    for (let k = 0; k < n; k += 1) {
      if (k === i || k === j) continue;
      total += harvilleOrder(p, [j, k, i]);
    }
  }
  return total;
}

/** i と j がともに3着以内に入る確率（ワイド）。 */
function probWide(p, i, j) {
  const n = p.length;
  let total = probExactTop(p, [i, j]); // 2頭で1・2着
  for (let k = 0; k < n; k += 1) {
    if (k === i || k === j) continue;
    // 3着が i か j のパターン（1・2着のどちらかに k が入る）
    total += harvilleOrder(p, [i, k, j]);
    total += harvilleOrder(p, [k, i, j]);
    total += harvilleOrder(p, [j, k, i]);
    total += harvilleOrder(p, [k, j, i]);
  }
  return total;
}

/** 組み合わせを列挙する。 */
function combinations(list, k) {
  if (k === 0) return [[]];
  if (list.length < k) return [];
  const [head, ...rest] = list;
  return [...combinations(rest, k - 1).map((c) => [head, ...c]), ...combinations(rest, k)];
}

/**
 * 買い目の的中確率と点数を返す。
 * @param {number[]} p 各馬の勝率
 * @param {object} bet { type, horses }（horses は添字の配列）
 */
function evaluateBet(p, bet) {
  const { type, horses } = bet;
  let combos = [];

  switch (type) {
    case '単勝':
      combos = horses.map((i) => [i]);
      break;
    case '複勝':
      combos = horses.map((i) => [i]);
      return {
        tickets: combos.length,
        probability: 1 - combos.reduce((acc, [i]) => acc * (1 - probPlace(p, i)), 1),
        perTicket: combos.map(([i]) => ({ combo: [i], probability: probPlace(p, i) })),
      };
    case '馬連':
      combos = combinations(horses, 2);
      break;
    case 'ワイド':
      combos = combinations(horses, 2);
      return {
        tickets: combos.length,
        probability: combos.reduce((sum, c) => sum + probWide(p, c[0], c[1]), 0),
        perTicket: combos.map((c) => ({ combo: c, probability: probWide(p, c[0], c[1]) })),
      };
    case '3連複':
      combos = combinations(horses, 3);
      break;
    case '馬単':
      combos = permutations(horses).map((x) => x.slice(0, 2));
      break;
    case '3連単':
      combos = permutations(horses).map((x) => x.slice(0, 3));
      break;
    default:
      throw new Error(`未対応の券種: ${type}`);
  }

  // 重複を除く（馬単・3連単の順列生成で同じ並びが複数出るため）
  const seen = new Set();
  const unique = combos.filter((c) => {
    const key = c.join('-');
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });

  const ordered = type === '馬単' || type === '3連単';
  const perTicket = unique.map((c) => ({
    combo: c,
    probability: ordered ? harvilleOrder(p, c) : probExactTop(p, c),
  }));

  return {
    tickets: unique.length,
    probability: perTicket.reduce((sum, t) => sum + t.probability, 0),
    perTicket,
  };
}

/** 損益分岐となる必要オッズ（1点あたり100円で買った場合）。 */
function breakEvenOdds(probability, tickets) {
  if (probability <= 0) return Infinity;
  return tickets / probability;
}

/**
 * モデルと市場の確率を対数線形で合成する。
 *   p ∝ p_model^w × p_market^(1-w)
 *
 * モデル単独の確率をそのまま信じると、市場と評価順が食い違う馬で
 * 期待値が数倍という非現実的な値になる。市場はもっとも多くの情報を
 * 織り込んだ推定値なので、そこからの「ずらし幅」としてモデルを使う。
 *
 * 2025〜2026年の芝・重／不良59レースで検証したところ、
 * 単勝の対数損失は w=0.05、複勝は w=0.20 で最小だった。ただし
 * 市場のみ（w=0）との差は誤差の範囲で、モデルが市場に情報を
 * 足せているとは言えない。既定値は控えめに 0.15 としている。
 */
function blendProbs(modelProbs, market, weight) {
  const raw = modelProbs.map((pm, i) => {
    const a = Math.max(pm, 1e-9);
    const b = Math.max(market[i], 1e-9);
    return Math.exp(weight * Math.log(a) + (1 - weight) * Math.log(b));
  });
  const sum = raw.reduce((x, y) => x + y, 0);
  return raw.map((r) => r / sum);
}

/** 実際の着順に対してモデルが与えていた確率（答え合わせ用）。 */
function scoreActualResult(p, orderIdx) {
  return {
    単勝: p[orderIdx[0]],
    複勝: probPlace(p, orderIdx[0]),
    馬連: orderIdx.length >= 2 ? probExactTop(p, orderIdx.slice(0, 2)) : null,
    馬単: orderIdx.length >= 2 ? harvilleOrder(p, orderIdx.slice(0, 2)) : null,
    '3連複': orderIdx.length >= 3 ? probExactTop(p, orderIdx.slice(0, 3)) : null,
    '3連単': orderIdx.length >= 3 ? harvilleOrder(p, orderIdx.slice(0, 3)) : null,
  };
}
