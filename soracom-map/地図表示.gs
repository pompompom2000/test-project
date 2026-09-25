/**
 * 車両の現在地をWebページ（地図）で表示する機能
 *
 * 既存の「コード.gs」と同じGASプロジェクトに、別ファイルとして追加する。
 * 「現在地」シートを読み、map.html の地図に全車両を表示する。
 *
 * 表示URL： ウェブアプリのURL（…/exec）の末尾に ?key=閲覧用合言葉 を付ける
 */

// ▼ 設定（ここだけ書き換える）
const MAP_VIEW_KEY = 'ここに閲覧用の合言葉'; // Beam用の合言葉とは別のものにする
const MAP_SHEET_NAME = '現在地';
const MAP_STALE_MINUTES = 30; // これより古い受信は「通信途絶」扱い（灰色表示）

// シートの見出し名の候補（既存シートの見出しに合わせて自動で列を探す）
const MAP_HEADERS = {
  car: ['車両', '車両名', 'car'],
  time: ['受信日時', '日時', '時刻', '更新日時', 'timestamp'],
  lat: ['緯度', 'lat'],
  lon: ['経度', 'lon', 'lng'],
  latlon: ['緯度経度'],
  temp: ['温度', 'temp', 'temperature'],
  humi: ['湿度', 'humi', 'humidity'],
};

/** ブラウザでURLを開いたときに呼ばれる */
function doGet(e) {
  const key = (e && e.parameter && e.parameter.key) || '';
  if (!mapIsValidKey_(key)) {
    return HtmlService.createHtmlOutput('<p>このページを表示する権限がありません。</p>')
      .setTitle('アクセスできません');
  }
  const t = HtmlService.createTemplateFromFile('map');
  t.viewKey = key;
  t.staleMinutes = MAP_STALE_MINUTES;
  return t.evaluate()
    .setTitle('車両 現在地マップ')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    // 会社ホームページに iframe で埋め込めるようにする
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/** 地図ページから1分ごとに呼ばれ、全車両の最新位置を返す */
function getCurrentLocations(key) {
  if (!mapIsValidKey_(key)) throw new Error('権限がありません');

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(MAP_SHEET_NAME);
  if (!sheet) throw new Error('「' + MAP_SHEET_NAME + '」シートが見つかりません');

  const now = new Date();
  const values = sheet.getDataRange().getValues();
  if (values.length < 2) return { updated: mapFormat_(now), cars: [] };

  const header = values[0].map(function (h) { return String(h).trim(); });
  const col = {};
  Object.keys(MAP_HEADERS).forEach(function (k) {
    col[k] = mapFindColumn_(header, MAP_HEADERS[k]);
  });

  const cars = [];
  values.slice(1).forEach(function (row, i) {
    const name = col.car >= 0 ? String(row[col.car]).trim() : '車両' + (i + 1);
    if (!name) return;

    let lat = col.lat >= 0 ? mapToNumber_(row[col.lat]) : null;
    let lon = col.lon >= 0 ? mapToNumber_(row[col.lon]) : null;
    if ((lat === null || lon === null) && col.latlon >= 0) {
      const parts = String(row[col.latlon]).split(',');
      if (parts.length === 2) {
        lat = mapToNumber_(parts[0]);
        lon = mapToNumber_(parts[1]);
      }
    }

    const time = col.time >= 0 ? mapToDate_(row[col.time]) : null;
    cars.push({
      name: name,
      lat: lat,
      lon: lon,
      time: time ? mapFormat_(time) : '',
      ageMinutes: time ? Math.floor((now.getTime() - time.getTime()) / 60000) : null,
      temp: col.temp >= 0 ? mapToNumber_(row[col.temp]) : null,
      humi: col.humi >= 0 ? mapToNumber_(row[col.humi]) : null,
    });
  });

  return { updated: mapFormat_(now), cars: cars };
}

/** 地図ページが開けるか確認するためのテスト関数（エディタから実行） */
function testGetCurrentLocations() {
  Logger.log(JSON.stringify(getCurrentLocations(MAP_VIEW_KEY), null, 2));
}

function mapIsValidKey_(key) {
  return MAP_VIEW_KEY !== 'ここに閲覧用の合言葉' && key === MAP_VIEW_KEY;
}

function mapFindColumn_(header, candidates) {
  for (let i = 0; i < candidates.length; i++) {
    const idx = header.indexOf(candidates[i]);
    if (idx >= 0) return idx;
  }
  return -1;
}

function mapToNumber_(v) {
  if (v === '' || v === null || v === undefined || v === 'null') return null;
  const n = Number(v);
  return isNaN(n) ? null : n;
}

function mapToDate_(v) {
  if (v instanceof Date) return v;
  if (!v) return null;
  const d = new Date(String(v));
  return isNaN(d.getTime()) ? null : d;
}

function mapFormat_(d) {
  return Utilities.formatDate(d, 'Asia/Tokyo', 'M/d HH:mm');
}
