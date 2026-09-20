/**
 * 道悪（稍重・重・不良）予想エンジン。
 *
 * 出典:
 *  [1][2] 重馬場・不良馬場2024-2025種牡馬別成績（芝／ダート）
 *         https://omokeiba.blog.jp/archives/96500810.html
 *         https://omokeiba.blog.jp/archives/96495353.html
 *  [3]    JRA-VAN「重馬場・不良馬場とは？雨の日の競馬の勝ち方！」
 *         https://jra-van.jp/fun/baken/index23.html
 *
 * [3] から取り込んだ考え方:
 *   - 馬場状態は良・稍重・重・不良の4段階。2022年のJRA平地3331レースの内訳は
 *     良70% / 稍重20% / 重8% / 不良2% で、重・不良はめったにない特殊条件。
 *   - 道悪は良馬場の成績がアテにならず、単勝・馬連の平均配当が上昇する＝荒れやすい。
 *   - 芝は道悪でパワー重視・時計が掛かり、ダートは砂が締まってスピード重視・時計が速くなる。
 *   - ダートの重・不良は500kg以上が好成績。芝は440kg以上なら馬体重差はほぼ出ない。
 *   - 不確定要素が大きいため、自信がなければ金額を抑えるか「見」（ケン）も選択肢。
 *
 * [1][2] から取り込んだ考え方:
 *   - 種牡馬ごとに「重・不良で狙える／狙い難い」がはっきり分かれる。
 *   - さらに稍重・重・不良それぞれで「要注意」「いまいち」な種牡馬がある。
 *   - 牡馬／牝馬限定の傾向を持つ種牡馬がある。
 */

const TRACK_STATES = [
  { key: 'firm', label: '良', mud: 0, share: '約70%' },
  { key: 'good', label: '稍重', mud: 0.35, share: '約20%' },
  { key: 'yielding', label: '重', mud: 0.85, share: '約8%' },
  { key: 'soft', label: '不良', mud: 1.0, share: '約2%' },
];

const SURFACES = [
  { key: 'turf', label: '芝' },
  { key: 'dirt', label: 'ダート' },
];

const SEXES = ['牡', '牝', 'セン'];

const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

/**
 * 補正の合計を 5〜95 点に収める。
 * 単純に切り詰めると上位が同点に張り付いて差が出ないので、
 * 双曲線正接でなだらかに圧縮する（0 のとき 50 点）。
 */
function toScore(total) {
  return 50 + 45 * Math.tanh(total / 45);
}
const stateByKey = (key) => TRACK_STATES.find((s) => s.key === key) || TRACK_STATES[0];

/**
 * 種牡馬データによる評価。馬場状態ごとのリストも参照する。
 * 「狙える／狙い難い」は重・不良基準の分類なので、稍重では効きを弱める。
 */
function sireEvaluation(surfaceKey, stateKey, sireName, sex) {
  const db = SIRE_DB[surfaceKey];
  const state = stateByKey(stateKey);
  const name = (sireName || '').trim();
  const tags = [];

  if (!name) {
    return { value: 0, tags, note: '', summary: '種牡馬未入力のため血統補正なし' };
  }
  if (state.mud === 0) {
    return {
      value: 0,
      tags,
      note: db.notes[name] || '',
      summary: '良馬場のため道悪の血統補正は加味しない',
    };
  }

  // favorable / unfavorable は「重・不良」での集計なので稍重では割り引く
  const factor = stateKey === 'good' ? 0.35 : 1;
  let value = 0;

  if (listHit(db.favorable, name, sex)) {
    value += SIRE_WEIGHTS.favorable * factor;
    tags.push({ tone: 'plus', label: '重・不良で狙える' });
  }
  if (listHit(db.unfavorable, name, sex)) {
    value += SIRE_WEIGHTS.unfavorable * factor;
    tags.push({ tone: 'minus', label: '重・不良で狙い難い' });
  }
  if (listHit(db.watch[stateKey] || [], name, sex)) {
    value += SIRE_WEIGHTS.watch;
    tags.push({ tone: 'plus', label: `${state.label}で要注意` });
  }
  if (listHit(db.poor[stateKey] || [], name, sex)) {
    value += SIRE_WEIGHTS.poor;
    tags.push({ tone: 'minus', label: `${state.label}でいまいち` });
  }
  if (listHit(db.picks2026, name, sex)) {
    value += SIRE_WEIGHTS.pick2026 * factor;
    tags.push({ tone: 'plus', label: '2026年の推し' });
  }

  // JRA-VAN 記事（2020〜2022年・芝）の補助シグナル
  const legacy = legacyTurfHit(surfaceKey, name);
  if (legacy) {
    value += legacy.value * factor;
    tags.push({
      tone: legacy.tier === 'weak' ? 'minus' : 'plus',
      label: legacy.tier === 'weak' ? '旧データでも道悪不振' : '旧データでも道悪巧者',
    });
  }

  const summary = tags.length
    ? `${db.label}の道悪データに該当あり`
    : `${db.label}の道悪データに該当なし（標準評価）`;

  return { value, tags, note: db.notes[name] || '', summary };
}

/**
 * 馬体重による補正（出典[3]）。ダートの道悪でのみ大きく効く。
 * 返す値は道悪度1.0のときの補正。
 */
function weightAdjust(surfaceKey, weight) {
  if (!weight) return { value: 0, note: '馬体重未入力のため補正なし' };

  if (surfaceKey === 'dirt') {
    if (weight >= 520 && weight <= 538) {
      return {
        value: 16,
        note: '520〜538kg。ダートの重・不良で勝率11.1%／連対率18.5%／複勝率26.2%と頭一つ抜けた馬体重帯',
      };
    }
    if (weight >= 500) return { value: 11, note: '500kg以上。ダートの重・不良で積極的に狙いたい馬格' };
    if (weight >= 480) return { value: 4, note: '480kg台。ダートの道悪では及第点の馬格' };
    if (weight >= 460) return { value: 0, note: '460kg台。ダートの道悪では平均的な馬格' };
    return { value: -8, note: '460kg未満。ダートの重・不良では数字を落としやすい馬格' };
  }

  if (weight >= 440) return { value: 0, note: '芝は440kg以上なら馬体重による差はほぼ出ない' };
  return { value: -5, note: '芝でも440kg未満はやや割引' };
}

/**
 * 過去実績による補正。良馬場と道悪の複勝率の差を見る。
 * 道悪の出走数が少ないうちは補正を弱める（「走ってみないと分からない」）。
 */
function recordAdjust(horse) {
  const hasFirm = horse.firmStarts > 0;
  const hasMud = horse.mudStarts > 0;
  const firmRate = hasFirm ? horse.firmPlaces / horse.firmStarts : null;
  const mudRate = hasMud ? horse.mudPlaces / horse.mudStarts : null;

  if (!hasFirm || !hasMud) {
    return {
      value: 0,
      firmRate,
      mudRate,
      note: hasMud ? '良馬場の実績が未入力のため実績補正なし' : '道悪の出走実績なし。適性は未知数',
    };
  }

  const confidence = Math.min(1, horse.mudStarts / 5);
  const value = clamp((mudRate - firmRate) * 70, -22, 28) * confidence;
  const pct = (r) => `${Math.round(r * 100)}%`;

  let note;
  if (mudRate - firmRate >= 0.1) note = `道悪複勝率${pct(mudRate)}＞良馬場${pct(firmRate)}。道悪替わりで上昇`;
  else if (firmRate - mudRate >= 0.1) note = `道悪複勝率${pct(mudRate)}＜良馬場${pct(firmRate)}。道悪で割引`;
  else note = `道悪複勝率${pct(mudRate)}。良馬場と大きな差はなし`;

  if (confidence < 1) note += `（道悪${horse.mudStarts}戦のみ。サンプル不足のため補正を抑制）`;
  return { value, firmRate, mudRate, note };
}

/** 良馬場での基礎能力。複勝率30%を基準にする。 */
function baseAbility(horse) {
  if (!horse.firmStarts) return 0;
  return clamp((horse.firmPlaces / horse.firmStarts - 0.3) * 50, -15, 35);
}

const MARKS = [
  { min: 72, mark: '◎', label: '本命級' },
  { min: 62, mark: '○', label: '対抗' },
  { min: 55, mark: '▲', label: '単穴' },
  { min: 46, mark: '△', label: '押さえ' },
  { min: -Infinity, mark: '×', label: '評価を下げたい' },
];

const markFor = (score) => MARKS.find((m) => score >= m.min);

/** 1頭ぶんの評価。 */
function evaluateHorse(horse, race) {
  const state = stateByKey(race.stateKey);
  const sire = sireEvaluation(race.surfaceKey, race.stateKey, horse.sire, horse.sex);
  const weight = weightAdjust(race.surfaceKey, horse.weight);
  const record = recordAdjust(horse);

  const trend = trendAdjust(horse, race.trend);
  const course = courseAdjust(horse, race);
  const gaikyu = gaikyuAdjust(horse);
  const comment = commentAdjust(horse, race);
  const training = trainingAdjust(horse);

  const ability = baseAbility(horse);
  const mudBonus = sire.value + state.mud * (weight.value + record.value);

  return {
    ...horse,
    sireInfo: sire,
    weightInfo: weight,
    recordInfo: record,
    trendInfo: trend,
    courseInfo: course,
    gaikyuInfo: gaikyu,
    commentInfo: comment,
    trainingInfo: training,
    ability,
    mudBonus,
    firmScore: toScore(ability),
    score: toScore(
      ability + mudBonus + trend.value + course.value + gaikyu.value + comment.value + training.value
    ),
    get mark() {
      return markFor(this.score);
    },
  };
}

/** レース全体の評価。良馬場評価からの順位変動で「波乱度」も算出する。 */
function evaluateRace(horses, race) {
  const state = stateByKey(race.stateKey);
  const evaluated = horses.map((h) => evaluateHorse(h, race));

  [...evaluated].sort((a, b) => b.firmScore - a.firmScore).forEach((h, i) => {
    h.firmRank = i + 1;
  });
  const ranked = [...evaluated].sort((a, b) => b.score - a.score);
  ranked.forEach((h, i) => {
    h.rank = i + 1;
    h.rankShift = h.firmRank - h.rank; // 正なら道悪で評価を上げた馬
  });

  const avgShift = evaluated.length
    ? evaluated.reduce((sum, h) => sum + Math.abs(h.rankShift), 0) / evaluated.length
    : 0;
  // 単勝オッズが入っていれば、市場の評価順と比べて妙味を出す
  const withOdds = evaluated.filter((h) => h.odds > 0);
  if (withOdds.length) {
    [...withOdds].sort((a, b) => a.odds - b.odds).forEach((h, i) => {
      h.marketRank = i + 1;
    });
    evaluated.forEach((h) => {
      h.valueGap = h.marketRank ? h.marketRank - h.rank : null;
    });
  }

  const popBias = popularityBias(race.popularity);
  const shakeUp = Math.round(
    clamp(state.mud * 55 + avgShift * 6 + (popBias ? popBias.adjust : 0), 0, 100)
  );

  return { horses: ranked, shakeUp, avgShift, state, popBias };
}

/** 芝・ダートの道悪一般傾向（出典[3]）。 */
function surfaceInsight(race) {
  const state = stateByKey(race.stateKey);
  if (state.mud === 0) {
    return race.surfaceKey === 'turf'
      ? '芝の良馬場はスピード・瞬発力に優れた馬が力を発揮しやすい、日本競馬のスタンダードな条件です。'
      : 'ダートの良馬場はパワーに秀でた馬が力を発揮しやすい条件です。';
  }
  return race.surfaceKey === 'turf'
    ? '芝は水分で路盤が柔らかくなりクッション性が落ち、濡れて滑るため地面を蹴るパワーが要求されます。走破タイムは良馬場より遅くなる傾向（＝パワー重視）。'
    : 'ダートは砂が水分を含んで引き締まり、脚元が沈みにくく走りやすい馬場になります。走破タイムは良馬場より速くなる傾向（＝スピード重視）。';
}

/** 買い方のスタンス（出典[3]）。 */
function raceStance(race, shakeUp) {
  const state = stateByKey(race.stateKey);

  if (state.key === 'firm') {
    return {
      level: 'calm',
      title: '良馬場：通常どおりの組み立てで',
      body: '2022年のJRA平地3331レースのうち約70%が良馬場。日本競馬のスタンダードな条件なので、芝ならスピードと瞬発力、ダートならパワーに優れた馬を素直に評価して問題ありません。',
    };
  }
  if (state.key === 'good') {
    return {
      level: 'watch',
      title: '稍重：良馬場の延長線。ただし血統チェックは必須',
      body: '稍重は全レースの約20%。良馬場に近い扱いで構いませんが、水分を含み始めているため、稍重で「要注意」「いまいち」な種牡馬だけは事前に確認しておきましょう。',
    };
  }

  const heavy = state.label;
  return {
    level: shakeUp >= 60 ? 'alert' : 'watch',
    title: `${heavy}馬場：荒れやすい特殊条件（年間${state.share}）`,
    body:
      `${heavy}馬場は良馬場と比べて単勝・馬連ともに平均配当が大きく上昇する、荒れやすい条件です。` +
      '高配当のチャンスである一方、道悪の経験自体が少ない馬が多く「走ってみないと分からない」不確定要素も大きい条件。' +
      'よほどの自信・確信がある時以外は、いつもより購入金額を抑えるか、「見」（ケン＝買わずに見送り）も有力な選択肢です。',
  };
}

/* ===================================================================
 * 本日の傾向（当日の開催バイアス）
 *
 * 競馬ラボ「本日の傾向」のように、当日の各レースで3着内に来た
 * 枠番・脚質・騎手・調教師・血統、そして人気を拾って、
 * 同日の後のレースの評価に上乗せする。
 * 当日数レースの小サンプルなので、補正はいずれも控えめに掛ける。
 * =================================================================== */

const RUN_STYLES = ['逃げ', '先行', '差し', '追込'];

/**
 * 「名前」または「名前 2」「名前 x2」形式のリストをパースする。
 * @returns {Object<string, number>} 名前 → 出現回数
 */
function parseCountList(text) {
  const counts = {};
  (text || '')
    .split(/[\n,、]/)
    .map((line) => line.trim())
    .filter(Boolean)
    .forEach((line) => {
      const m = line.match(/^(.+?)[\s　]*(?:[x×*][\s　]*)?(\d+)?$/);
      if (!m) return;
      const name = m[1].trim();
      if (!name) return;
      counts[name] = (counts[name] || 0) + (m[2] ? Number(m[2]) : 1);
    });
  return counts;
}

/** 血統（種牡馬）の当日好走リスト。 */
const parseSireTrend = parseCountList;

/** 調教師の当日好走リスト。 */
const parseTrainerTrend = parseCountList;

/**
 * 騎手の当日成績。
 * "三浦皇成 2.0.0.3" / "C.ルメール【3.0.0.3】" は着度数として、
 * 着度数のない "津村明秀" は出現回数として扱う。
 * @returns {Object<string, {first?:number, second?:number, third?:number, out?:number, count?:number}>}
 */
function parseJockeyTrend(text) {
  const table = {};
  (text || '')
    .split(/[\n,、]/)
    .map((line) => line.trim())
    .filter(Boolean)
    .forEach((line) => {
      const withRecord = line.match(/^(.+?)[\s　]*[【\[(]?[\s　]*(\d+)[.．\-](\d+)[.．\-](\d+)[.．\-](\d+)/);
      if (withRecord) {
        const key = normalizeName(withRecord[1]);
        table[key] = {
          first: Number(withRecord[2]),
          second: Number(withRecord[3]),
          third: Number(withRecord[4]),
          out: Number(withRecord[5]),
        };
        return;
      }
      const key = normalizeName(line);
      if (!key) return;
      const prev = table[key];
      if (prev && prev.first !== undefined) return; // 着度数の情報を優先
      table[key] = { count: (prev && prev.count ? prev.count : 0) + 1 };
    });
  return table;
}

/** 1〜8 の枠番など、数字だけのリストをパースする。 */
function parseNumberList(text, min, max) {
  const counts = {};
  (text || '')
    .split(/[^0-9]+/)
    .map((v) => Number(v))
    .filter((n) => Number.isFinite(n) && n >= min && n <= max)
    .forEach((n) => {
      counts[n] = (counts[n] || 0) + 1;
    });
  return counts;
}

/** 当日3着内に来た馬の人気。"1,5,8" でも改行区切りでも可。 */
function parsePopularity(text) {
  return (text || '')
    .split(/[^0-9]+/)
    .map((v) => Number(v))
    .filter((n) => Number.isFinite(n) && n > 0);
}

/** 騎手名・調教師名は空白や中黒の有無を無視して突き合わせる。 */
function normalizeName(name) {
  return (name || '').replace(/[\s　・.．]/g, '');
}

function lookupByName(table, name) {
  const key = normalizeName(name);
  if (!key) return null;
  if (table[key]) return table[key];
  const hit = Object.keys(table).find((k) => {
    const nk = normalizeName(k);
    return nk === key || nk.includes(key) || key.includes(nk);
  });
  return hit ? table[hit] : null;
}

/** 出現回数ベースの共通ボーナス。 */
function countBonus(count, perHit, cap) {
  if (!count) return 0;
  return Math.min(count * perHit, cap);
}

/**
 * 当日トレンドによる補正。枠番・脚質・騎手・調教師・血統の5軸を見る。
 * @param {object} horse
 * @param {object} trend parseTrend() の戻り値
 */
function trendAdjust(horse, trend) {
  const empty = { value: 0, tags: [], notes: [], note: '当日トレンドの入力なし' };
  if (!trend) return empty;

  const tags = [];
  const notes = [];
  let value = 0;

  // 血統（種牡馬）
  const sireHits = horse.sire ? trend.sires[horse.sire] || 0 : 0;
  if (sireHits > 0) {
    value += countBonus(sireHits, 4, 12);
    notes.push(`本日${sireHits}回3着内の血統`);
    tags.push({ tone: 'plus', label: `本日の好走血統 ${sireHits}回` });
  }

  // 騎手
  const jockey = lookupByName(trend.jockeys, horse.jockey);
  if (jockey) {
    if (jockey.first !== undefined) {
      const starts = jockey.first + jockey.second + jockey.third + jockey.out;
      if (starts > 0) {
        const placeRate = (jockey.first + jockey.second + jockey.third) / starts;
        const bonus = clamp((placeRate - 0.35) * 28, -6, 10);
        value += bonus;
        notes.push(
          `騎手は本日【${jockey.first}.${jockey.second}.${jockey.third}.${jockey.out}】（複勝率${Math.round(placeRate * 100)}%）`
        );
        if (bonus > 0.5) tags.push({ tone: 'plus', label: '本日好調の騎手' });
        else if (bonus < -0.5) tags.push({ tone: 'minus', label: '本日不振の騎手' });
      }
    } else {
      value += countBonus(jockey.count, 3, 9);
      notes.push(`騎手は本日${jockey.count}回3着内`);
      tags.push({ tone: 'plus', label: '本日好調の騎手' });
    }
  }

  // 調教師
  const trainerHits = horse.trainer ? (lookupByName(trend.trainers, horse.trainer) || 0) : 0;
  if (trainerHits) {
    value += countBonus(trainerHits, 3, 9);
    notes.push(`調教師は本日${trainerHits}回3着内`);
    tags.push({ tone: 'plus', label: '本日好調の厩舎' });
  }

  // 枠番
  const postHits = horse.post ? trend.posts[horse.post] || 0 : 0;
  const postTotal = Object.values(trend.posts).reduce((a, b) => a + b, 0);
  if (horse.post && postTotal >= 6) {
    if (postHits >= 3) {
      value += 6;
      notes.push(`${horse.post}枠は本日${postHits}回3着内と好調`);
      tags.push({ tone: 'plus', label: `${horse.post}枠が好走中` });
    } else if (postHits === 2) {
      value += 3;
      notes.push(`${horse.post}枠は本日2回3着内`);
    } else if (postHits === 0) {
      value -= 2;
      notes.push(`${horse.post}枠は本日まだ3着内なし`);
    }
  }

  // 脚質
  const styleHits = horse.style ? trend.styles[horse.style] || 0 : 0;
  const styleTotal = Object.values(trend.styles).reduce((a, b) => a + b, 0);
  if (horse.style && styleTotal >= 4) {
    if (styleHits >= 3) {
      value += 6;
      notes.push(`本日は${horse.style}が${styleHits}回3着内と有利`);
      tags.push({ tone: 'plus', label: `${horse.style}有利の傾向` });
    } else if (styleHits === 2) {
      value += 3;
      notes.push(`本日の${horse.style}は2回3着内`);
    } else if (styleHits === 0) {
      value -= 3;
      notes.push(`本日の${horse.style}はまだ3着内なし`);
      tags.push({ tone: 'minus', label: `${horse.style}は苦戦中` });
    }
  }

  return {
    value,
    tags,
    notes,
    note: notes.length ? notes.join(' / ') : '当日トレンドに該当なし',
  };
}

/** フォーム入力から trend オブジェクトを組み立てる。 */
function parseTrend(input) {
  return {
    sires: parseSireTrend(input.sires),
    jockeys: parseJockeyTrend(input.jockeys),
    trainers: parseTrainerTrend(input.trainers),
    posts: parseNumberList(input.posts, 1, 8),
    styles: parseCountList(input.styles),
    popularity: parsePopularity(input.popularity),
  };
}

/**
 * 当日3着内馬の平均人気から、その日の堅い／荒れるの傾向を判定する。
 * 例: 3着内に7〜9番人気が並ぶ日は、人気サイドを信頼しすぎないほうがよい。
 */
function popularityBias(list) {
  if (!list || !list.length) return null;
  const avg = list.reduce((a, b) => a + b, 0) / list.length;
  const longshots = list.filter((p) => p >= 7).length;
  const favorites = list.filter((p) => p <= 3).length;

  let level;
  let note;
  if (avg >= 5.5) {
    level = 'rough';
    note = `3着内馬の平均人気は${avg.toFixed(1)}番人気。7番人気以下が${longshots}頭と、人気薄がよく来ている荒れ気味の開催です。`;
  } else if (avg <= 3.5) {
    level = 'solid';
    note = `3着内馬の平均人気は${avg.toFixed(1)}番人気。1〜3番人気が${favorites}頭と、人気サイドが堅調な開催です。`;
  } else {
    level = 'neutral';
    note = `3着内馬の平均人気は${avg.toFixed(1)}番人気。極端に堅くも荒れてもいない標準的な傾向です。`;
  }
  return { avg, longshots, favorites, level, note, adjust: clamp((avg - 4) * 6, -12, 18) };
}

/** 当日トレンドの総評。 */
function trendSummary(trend) {
  if (!trend) return null;
  const lines = [];

  const sires = Object.entries(trend.sires).sort((a, b) => b[1] - a[1]);
  const repeatSires = sires.filter(([, c]) => c >= 2);
  if (repeatSires.length) {
    lines.push(`複数回3着内の血統：${repeatSires.map(([n, c]) => `${n}（${c}回）`).join('、')}`);
  }

  const posts = Object.entries(trend.posts).sort((a, b) => b[1] - a[1]);
  const postTotal = posts.reduce((sum, [, c]) => sum + c, 0);
  if (postTotal >= 6) {
    const inner = posts.filter(([p]) => Number(p) <= 4).reduce((s, [, c]) => s + c, 0);
    const outer = postTotal - inner;
    if (inner >= outer * 2) lines.push(`枠順は内枠（1〜4枠）が${inner}／${postTotal}と優勢`);
    else if (outer >= inner * 2) lines.push(`枠順は外枠（5〜8枠）が${outer}／${postTotal}と優勢`);
    else lines.push(`枠順による偏りは今のところ小さめ（内${inner}／外${outer}）`);
  }

  const styles = Object.entries(trend.styles).sort((a, b) => b[1] - a[1]);
  if (styles.length && styles[0][1] >= 3) {
    lines.push(`脚質は${styles[0][0]}が${styles[0][1]}回と目立つ`);
  }

  const jockeys = Object.keys(trend.jockeys);
  if (jockeys.length) lines.push(`好調騎手として${jockeys.length}名を登録中`);

  return lines.length ? lines : null;
}

/* ===================================================================
 * コース傾向
 *
 * 「そのコースで枠順・脚質がどう出るか」を馬場状態込みで持たせる。
 * データは data/courses/*.json 相当の形式で race.course に渡す。
 * =================================================================== */

/**
 * コース傾向による補正。枠順と脚質の2つを見る。
 * course = {
 *   name, note,
 *   innerPosts: [1,2,3,4,5,6],              // 有利とされる枠
 *   styleRank:    ['先行','差し','逃げ','追込'],  // 良〜稍重での脚質優位順
 *   wetStyleRank: ['差し','追込','先行','逃げ'],  // 重・不良での脚質優位順
 * }
 */
function courseAdjust(horse, race) {
  const course = race.course;
  if (!course) return { value: 0, notes: [], tags: [], note: 'コース傾向の指定なし' };

  const state = stateByKey(race.stateKey);
  const notes = [];
  const tags = [];
  let value = 0;

  if (horse.post && Array.isArray(course.innerPosts) && course.innerPosts.length) {
    const inner = course.innerPosts.includes(Number(horse.post));
    // 道悪が深いほど枠順よりも脚質が効くため、内枠の利を少し弱める
    const postWeight = 1 - state.mud * 0.4;
    if (inner) {
      value += 5 * postWeight;
      notes.push(`${horse.post}枠は当コースで有利とされる枠`);
    } else {
      value -= 4 * postWeight;
      notes.push(`${horse.post}枠は当コースでコーナーの距離ロスを抱えやすい枠`);
    }
  }

  const rank = state.mud >= 0.8 ? course.wetStyleRank : course.styleRank;
  if (horse.style && Array.isArray(rank) && rank.length) {
    const idx = rank.indexOf(horse.style);
    if (idx >= 0) {
      const bonus = [7, 3, -1, -5][idx] !== undefined ? [7, 3, -1, -5][idx] : 0;
      value += bonus;
      const label = state.mud >= 0.8 ? `${state.label}馬場` : 'この馬場';
      notes.push(`${label}の当コースでは${horse.style}が${idx + 1}番手の脚質評価`);
      if (bonus >= 5) tags.push({ tone: 'plus', label: `コース適性：${horse.style}` });
      else if (bonus <= -5) tags.push({ tone: 'minus', label: `コース不利：${horse.style}` });
    }
  }

  return { value, notes, tags, note: notes.length ? notes.join(' / ') : 'コース傾向に該当なし' };
}

/* ===================================================================
 * 外厩と厩舎コメント
 * =================================================================== */

/**
 * 外厩による補正。施設ごとの複勝率を基準値と比べる。
 * 休み明け（horse.layoff）の場合は仕上がりへの寄与が大きいので効きを強める。
 */
function gaikyuAdjust(horse) {
  const facility = getGaikyu(horse.gaikyu);
  if (!facility) {
    return {
      value: 0,
      tags: [],
      note: horse.gaikyu ? '外厩データに該当なし' : '外厩の入力なし',
    };
  }

  const base = clamp((facility.placeRate - GAIKYU_BASELINE_PLACE) * 0.5, -6, 8);
  const value = base * (horse.layoff ? 1.5 : 1);
  const tags = [];
  if (value >= 4) tags.push({ tone: 'plus', label: `外厩上位：${facility.name}` });
  else if (value <= -4) tags.push({ tone: 'minus', label: `外厩下位：${facility.name}` });

  return {
    value,
    tags,
    facility,
    note:
      `${facility.name}（勝率${facility.winRate}% / 複勝率${facility.placeRate}%）` +
      (horse.layoff ? '。休み明けのため外厩の比重を大きく見る' : ''),
  };
}

/**
 * 厩舎コメントによる補正。
 * horse.comment = {
 *   wet: 'welcome' | 'avoid' | null,   // 道悪を歓迎しているか、避けたがっているか
 *   condition: 'sharp' | 'doubt' | null, // 仕上がりの評価
 *   text: '...'                        // 表示用の原文
 * }
 * 道悪への言及は馬場が渋るほど効き、仕上がりの評価は馬場状態によらず効く。
 */
function commentAdjust(horse, race) {
  const c = horse.comment;
  if (!c) return { value: 0, tags: [], notes: [], note: '厩舎コメントの入力なし' };

  const state = stateByKey(race.stateKey);
  const notes = [];
  const tags = [];
  let value = 0;

  if (c.wet === 'welcome') {
    value += 9 * state.mud;
    notes.push('陣営が道悪を歓迎');
    if (state.mud > 0) tags.push({ tone: 'plus', label: '陣営が道悪歓迎' });
  } else if (c.wet === 'avoid') {
    value -= 11 * state.mud;
    notes.push('陣営は良馬場で走らせたい意向');
    if (state.mud > 0) tags.push({ tone: 'minus', label: '陣営は良馬場希望' });
  }

  if (c.condition === 'sharp') {
    value += 5;
    notes.push('仕上がり良好');
    tags.push({ tone: 'plus', label: '仕上がり良好' });
  } else if (c.condition === 'doubt') {
    value -= 5;
    notes.push('仕上がりに不安');
    tags.push({ tone: 'minus', label: '仕上がりに不安' });
  }

  return { value, tags, notes, note: notes.length ? notes.join(' / ') : '道悪・仕上がりへの言及なし' };
}

/* ===================================================================
 * 調教（追い切り）
 *
 * netkeiba の調教評価は S / A / B / C / D のランクと、
 * 「仕上上々」「目立たず」といった短評で構成される。
 * B が最も多い標準的な評価なので、B を基準（0）として増減させる。
 * =================================================================== */

const TRAINING_RANK_ADJUST = { S: 11, A: 7, B: 0, C: -6, D: -10 };

/** 調教短評のキーワード。ランクだけでは拾えないニュアンスを補う。 */
const TRAINING_CRITIC_WORDS = [
  { value: 5, words: ['迫力', '抜群', '絶好', '上々', '態勢整う', '文句なし'] },
  { value: 2, words: ['元気', '好調', 'キビキビ', '安定', '良化', '仕上がる', '上向'] },
  { value: -5, words: ['目立たず', '平凡', '物足', '案外', '一息', '余裕残り'] },
];

/**
 * 調教による補正。
 * horse.training = { rank: 'B', critic: '仕上上々' }
 */
function trainingAdjust(horse) {
  const t = horse.training;
  if (!t || (!t.rank && !t.critic)) {
    return { value: 0, tags: [], note: '調教データの入力なし' };
  }

  const notes = [];
  const tags = [];
  let value = 0;

  const rank = (t.rank || '').toUpperCase();
  if (TRAINING_RANK_ADJUST[rank] !== undefined) {
    value += TRAINING_RANK_ADJUST[rank];
    notes.push(`調教ランク${rank}`);
    if (rank === 'S' || rank === 'A') tags.push({ tone: 'plus', label: `調教${rank}評価` });
    else if (rank === 'C' || rank === 'D') tags.push({ tone: 'minus', label: `調教${rank}評価` });
  }

  if (t.critic) {
    const hit = TRAINING_CRITIC_WORDS.find((g) => g.words.some((w) => t.critic.includes(w)));
    if (hit) {
      value += hit.value;
      notes.push(`短評「${t.critic}」`);
    } else {
      notes.push(`短評「${t.critic}」（加減点なし）`);
    }
  }

  return { value, tags, note: notes.join(' / ') };
}
