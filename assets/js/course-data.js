/**
 * コース傾向データ。
 *
 * 出典: 中山芝2200mのコース傾向
 *       https://keiba-wiki.com/nakayama-turf-2200-trend/
 *
 * innerPosts    … そのコースで有利とされる枠
 * styleRank     … 良〜稍重での脚質の優位順
 * wetStyleRank  … 重・不良での脚質の優位順
 */
const COURSE_DB = {
  'nakayama-turf-2200': {
    key: 'nakayama-turf-2200',
    label: '中山 芝2200m（右・外）',
    surface: 'turf',
    note:
      'スタンド前の坂下発走。最初のコーナーまで約430mあり序盤は落ち着く。向正面から3コーナーが下りでペースが上がり、' +
      '直線約310m＋高低差2.2mの坂で持久力勝負になるロングスパート型コース。良馬場は内前有利、稍重でパワー型が浮上し、' +
      '重・不良では差し・追込が台頭する。',
    innerPosts: [1, 2, 3, 4, 5, 6],
    styleRank: ['先行', '差し', '逃げ', '追込'],
    wetStyleRank: ['差し', '追込', '先行', '逃げ'],
    sireLines: ['ハーツクライ系', 'ステイゴールド系', 'ルーラーシップ系'],
    source: 'https://keiba-wiki.com/nakayama-turf-2200-trend/',
  },
};

/** 選択肢用のリスト。 */
function courseOptions() {
  return Object.values(COURSE_DB).map((c) => ({ key: c.key, label: c.label }));
}

/** キーからコース傾向を引く。 */
function getCourse(key) {
  return (key && COURSE_DB[key]) || null;
}
