#!/usr/bin/env node
/**
 * コマンドラインからレースを判定する。
 *   node tools/predict.js data/races/<race>.json
 * JSON の形式は data/races/ 内のサンプルを参照。
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.join(__dirname, '..');
const context = vm.createContext({ console, Math, Object, Number, Array, String, JSON });
['assets/js/sire-data.js', 'assets/js/course-data.js', 'assets/js/engine.js'].forEach((f) => {
  vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), context, { filename: f });
});

const file = process.argv[2];
if (!file) {
  console.error('usage: node tools/predict.js <race.json>');
  process.exit(1);
}
const input = JSON.parse(fs.readFileSync(file, 'utf8'));

const race = {
  surfaceKey: input.surface,
  stateKey: input.state,
  trend: input.trend ? context.parseTrend(input.trend) : null,
  course: context.getCourse(input.courseKey),
  popularity: input.trend ? context.parsePopularity(input.trend.popularity || '') : [],
};

const horses = input.horses.map((h) => ({
  no: h.no,
  name: h.name,
  sex: h.sex,
  sire: h.sire,
  jockey: h.jockey,
  trainer: h.trainer,
  post: h.post,
  style: h.style,
  weight: h.weight,
  odds: h.odds || 0,
  firmStarts: h.firmStarts || 0,
  firmPlaces: h.firmPlaces || 0,
  mudStarts: h.mudStarts || 0,
  mudPlaces: h.mudPlaces || 0,
}));

const result = context.evaluateRace(horses, race);
const stance = context.raceStance(race, result.shakeUp);

console.log(`\n■ ${input.title || ''}`);
console.log(`  ${input.surfaceLabel || race.surfaceKey} / 馬場:${result.state.label} / 波乱度 ${result.shakeUp}`);
console.log(`  ${stance.title}`);
console.log(`  ${context.surfaceInsight(race)}`);
if (result.popBias) console.log(`  ${result.popBias.note}`);
console.log('');

result.horses.forEach((h) => {
  const shift = h.rankShift > 0 ? `▲${h.rankShift}` : h.rankShift < 0 ? `▼${-h.rankShift}` : '→';
  const market = h.marketRank ? `市場${h.marketRank}番人気(${h.odds.toFixed(1)})` : '';
  const value =
    h.valueGap > 2 ? ` 妙味◎(+${h.valueGap})` : h.valueGap < -2 ? ` 人気先行(${h.valueGap})` : '';
  console.log(
    `${String(h.rank).padStart(2)}位 ${h.mark.mark} ${String(Math.round(h.score)).padStart(2)}点  ` +
      `${h.no}番 ${h.name}（父${h.sire} / ${h.jockey}）  ${market}${value}  良馬場評価${h.firmRank}位 ${shift}`
  );
  console.log(`      血統 ${fmt(h.sireInfo.value)} : ${h.sireInfo.tags.map((t) => t.label).join('、') || '該当なし'}`);
  console.log(`      馬体重 ${fmt(h.weightInfo.value * result.state.mud)} : ${h.weightInfo.note}`);
  console.log(`      道悪実績 ${fmt(h.recordInfo.value * result.state.mud)} : ${h.recordInfo.note}`);
  if (h.courseInfo && h.courseInfo.value) console.log(`      コース傾向 ${fmt(h.courseInfo.value)} : ${h.courseInfo.note}`);
  if (h.trendInfo && h.trendInfo.value) console.log(`      当日傾向 ${fmt(h.trendInfo.value)} : ${h.trendInfo.note}`);
  if (h.sireInfo.note) console.log(`      ※ ${h.sire}：${h.sireInfo.note}`);
  console.log('');
});

function fmt(v) {
  const r = Math.round(v * 10) / 10;
  return r > 0 ? `+${r}` : `${r}`;
}
