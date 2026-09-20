/**
 * 外厩（がいきゅう）施設別成績。
 *
 * 外厩は休み明けの馬の仕上がりを判断するための情報で、
 * どの施設で調整されたかによって明確な成績差が出る。
 *
 * 出典: かよちんの外厩情報-競馬wiki「外厩ランキング2025 TOP50」
 *       https://keiba-wiki.com/260920nakayama/
 *
 * winRate / placeRate はパーセント表記の数値（複勝率＝3着内率）。
 */
const GAIKYU_DATA = [
  { name: 'ノーザンＦしがらき', starts: 2661, winRate: 11.3, placeRate: 29.6 },
  { name: 'チャンピオンヒルズ', starts: 2410, winRate: 10.5, placeRate: 28.3 },
  { name: 'ノーザンＦ天栄', starts: 2171, winRate: 13.8, placeRate: 33.2 },
  { name: '山元トレセン', starts: 1587, winRate: 9.5, placeRate: 25.0 },
  { name: '阿見トレセン', starts: 1436, winRate: 5.2, placeRate: 16.9 },
  { name: '宇治田原優駿Ｓ', starts: 1397, winRate: 7.4, placeRate: 21.3 },
  { name: 'キャニオンＦ土山', starts: 1362, winRate: 7.2, placeRate: 21.0 },
  { name: 'ＫＳトレセン', starts: 1342, winRate: 3.9, placeRate: 14.0 },
  { name: '吉澤ステーブルWEST', starts: 980, winRate: 6.4, placeRate: 17.6 },
  { name: 'エスティＦ小見川', starts: 932, winRate: 5.3, placeRate: 18.6 },
  { name: 'グリーンウッド', starts: 848, winRate: 6.1, placeRate: 18.9 },
  { name: '松風馬事センター', starts: 699, winRate: 5.4, placeRate: 18.0 },
  { name: '大山ヒルズ', starts: 685, winRate: 7.6, placeRate: 24.7 },
  { name: '社台ファーム鈴鹿', starts: 528, winRate: 9.3, placeRate: 26.5 },
  { name: '吉澤ステーブルEAST', starts: 433, winRate: 3.9, placeRate: 13.6 },
  { name: '高橋トレセン', starts: 399, winRate: 3.0, placeRate: 10.5 },
  { name: '小野瀬ファーム', starts: 390, winRate: 3.1, placeRate: 12.3 },
  { name: 'ブルーステーブル', starts: 369, winRate: 6.0, placeRate: 18.2 },
  { name: '西山牧場阿見分場', starts: 309, winRate: 3.6, placeRate: 10.0 },
  { name: 'ビッグレッドＦ鉾田', starts: 308, winRate: 5.5, placeRate: 12.7 },
  { name: 'ミッドウェイＦ', starts: 269, winRate: 9.3, placeRate: 27.9 },
  { name: '山岡トレセン', starts: 269, winRate: 8.2, placeRate: 18.2 },
  { name: 'Tomorrow Farm', starts: 269, winRate: 6.7, placeRate: 19.3 },
  { name: 'ドラゴンファーム', starts: 261, winRate: 4.6, placeRate: 16.9 },
  { name: 'ミルファーム千葉', starts: 243, winRate: 2.1, placeRate: 8.2 },
  { name: '三重ホーストレセン', starts: 219, winRate: 4.1, placeRate: 20.1 },
  { name: 'フォレストヒル', starts: 212, winRate: 8.5, placeRate: 20.3 },
  { name: 'グリーンファーム', starts: 211, winRate: 8.1, placeRate: 20.9 },
  { name: 'JOJI STABLE', starts: 205, winRate: 5.4, placeRate: 21.0 },
  { name: '大瀧ステーブル', starts: 203, winRate: 5.4, placeRate: 13.8 },
  { name: 'オークヒルファーム', starts: 202, winRate: 2.0, placeRate: 9.9 },
  { name: 'ヒイラギawaji', starts: 183, winRate: 3.3, placeRate: 15.8 },
  { name: 'ノーザンＦ空港', starts: 179, winRate: 7.8, placeRate: 27.9 },
  { name: 'テンコートレセン', starts: 171, winRate: 3.5, placeRate: 9.9 },
  { name: 'アカデミー牧場', starts: 170, winRate: 1.8, placeRate: 12.9 },
  { name: '信楽牧場（滋賀県）', starts: 163, winRate: 4.3, placeRate: 14.1 },
  { name: '井ノ岡トレセン', starts: 148, winRate: 4.1, placeRate: 7.4 },
  { name: '千代田牧場(千葉県)', starts: 145, winRate: 5.5, placeRate: 18.6 },
  { name: '小松トレセン', starts: 141, winRate: 1.4, placeRate: 10.6 },
  { name: 'ノルマンディ小野町', starts: 137, winRate: 0.7, placeRate: 8.8 },
  { name: '名張ホースランドＰ', starts: 131, winRate: 7.6, placeRate: 22.1 },
  { name: 'EISHIN STABLE', starts: 131, winRate: 7.6, placeRate: 18.3 },
  { name: 'ワコーファーム', starts: 130, winRate: 2.3, placeRate: 9.2 },
  { name: 'ノーザンＦ早来', starts: 129, winRate: 6.2, placeRate: 28.7 },
  { name: '和田牧場（千葉県）', starts: 104, winRate: 2.9, placeRate: 4.8 },
  { name: 'ムラセファーム', starts: 94, winRate: 2.1, placeRate: 11.7 },
  { name: '下河辺トレセン', starts: 93, winRate: 2.2, placeRate: 12.9 },
  { name: '優楽ステーブル', starts: 89, winRate: 4.5, placeRate: 15.7 },
  { name: '北総牧場（千葉県）', starts: 88, winRate: 2.3, placeRate: 6.8 },
];

/** 全体の複勝率の目安。これを上回る施設ほど加点する。 */
const GAIKYU_BASELINE_PLACE = 18;

/** 全角英字・記号や空白の差を吸収して施設名を突き合わせる。 */
function normalizeGaikyuName(name) {
  return (name || '')
    .replace(/[\s\u3000・.．\-–—]/g, '')
    .replace(/[Ａ-Ｚａ-ｚ０-９]/g, (c) => String.fromCharCode(c.charCodeAt(0) - 0xfee0))
    .toUpperCase();
}

/** 施設名から成績を引く。該当なしは null。 */
function getGaikyu(name) {
  const key = normalizeGaikyuName(name);
  if (!key || key === '–' || key === '-') return null;
  return (
    GAIKYU_DATA.find((g) => normalizeGaikyuName(g.name) === key) ||
    GAIKYU_DATA.find((g) => {
      const n = normalizeGaikyuName(g.name);
      return n.includes(key) || key.includes(n);
    }) ||
    null
  );
}

/** 入力補完用の施設名一覧。 */
function allGaikyuNames() {
  return GAIKYU_DATA.map((g) => g.name);
}
