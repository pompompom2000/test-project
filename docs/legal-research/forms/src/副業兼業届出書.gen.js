const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign,
} = require("docx");

const MIN = { ascii: "ＭＳ 明朝", eastAsia: "ＭＳ 明朝", hAnsi: "ＭＳ 明朝" };
const GO  = { ascii: "ＭＳ ゴシック", eastAsia: "ＭＳ ゴシック", hAnsi: "ＭＳ ゴシック" };
const S = 21;

const p = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { line: o.line ?? 300, lineRule: "auto", before: o.before ?? 0, after: o.after ?? 0 },
  indent: o.indent,
  children: [new TextRun({ text, bold: o.bold, size: o.size ?? S, font: o.go ? GO : MIN })],
});
const blank = (n = 1) => Array.from({ length: n }, () => p(""));

const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  columnSpan: o.span,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined,
  verticalAlign: VerticalAlign.CENTER,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: (Array.isArray(text) ? text : [text]).map((t) => new Paragraph({
    alignment: o.align,
    spacing: { line: 250, lineRule: "auto" },
    children: [new TextRun({ text: t, bold: o.bold, size: o.size ?? 19, font: o.go ? GO : MIN })],
  })),
});

const HEAD = "E8ECF0";
const W = 9072;
const C = [2600, 6472];

const row = (label, value, o = {}) => new TableRow({
  children: [
    cell(label, C[0], { shade: HEAD, bold: true, go: true }),
    cell(value, C[1], { size: o.size }),
  ],
});

// ---- 他の使用者の事業場（1社分のブロック）--------------------------------
const block = (title) => [
  new TableRow({
    children: [cell(title, W, { span: 2, shade: "16395C", bold: true, go: true, size: 20, align: AlignmentType.LEFT })],
  }),
  row("事業場の名称", ""),
  row("所 在 地", ""),
  row("労働契約を締結した日　★", ["令和　　年　　月　　日",
    "※ 所定労働時間は労働契約の締結の先後の順に通算されるため、必ずご記入ください"]),
  row("労働契約の期間", "令和　　年　　月　　日　〜　令和　　年　　月　　日　／　□ 期間の定めなし　□ 日雇い"),
  row("従事する業務の内容", ""),
  row("所 定 労 働 日", "□月　□火　□水　□木　□金　□土　□日　／　その他（　　　　　　　　　　）"),
  row("所定労働時間", "始業　　時　　分　　終業　　時　　分　　休憩　　　分　　／　１日　　　時間　　分"),
  row("１週間の所定労働時間", "　　　時間　　　分"),
  row("所定外労働", "□ 無　／　□ 有（１か月の見込み　　　　時間程度）"),
  row("運転業務の有無　★", ["□ 無　／　□ 有（□ 土砂等の運搬を含む）",
    "※ 有の場合、改善基準告示の拘束時間・運転時間も通算して管理します"]),
];

const tbl = (rows) => new Table({
  columnWidths: C,
  width: { size: W, type: WidthType.DXA },
  rows,
});

// ---- 確認欄 ---------------------------------------------------------------
const CK = [620, 8452];
const ck = (text) => new TableRow({
  children: [
    cell("□", CK[0], { align: AlignmentType.CENTER, size: 22 }),
    cell(text, CK[1]),
  ],
});

const ckTable = new Table({
  columnWidths: CK,
  width: { size: W, type: WidthType.DXA },
  rows: [
    ck("上記の内容に相違ありません。"),
    ck("記載内容に変更が生じたときは、速やかに届け出ます。"),
    ck("会社が労働基準法第３８条第１項により労働時間を通算して管理すること、及びその結果として時間外労働の割増賃金の計算に用いることを了解しました。"),
  ],
});

const SIGN = [2600, 6472];
const signTable = new Table({
  columnWidths: SIGN,
  width: { size: W, type: WidthType.DXA },
  rows: [
    new TableRow({ children: [
      cell("届 出 日", SIGN[0], { shade: HEAD, bold: true, go: true }),
      cell("令和　　年　　月　　日", SIGN[1]),
    ]}),
    new TableRow({ children: [
      cell("氏 名", SIGN[0], { shade: HEAD, bold: true, go: true }),
      cell("　　　　　　　　　　　　　　　　　　　　　　　　㊞", SIGN[1]),
    ]}),
    new TableRow({ children: [
      cell("連 絡 先", SIGN[0], { shade: HEAD, bold: true, go: true }),
      cell("ＴＥＬ　　　　　－　　　　　－", SIGN[1]),
    ]}),
  ],
});

const doc = new Document({
  styles: { default: { document: { run: { size: S, font: MIN } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1418, bottom: 1418, left: 1417, right: 1417 },
      },
    },
    children: [
      p("副 業 ・ 兼 業 に 関 す る 届 出 書",
        { align: AlignmentType.CENTER, go: true, bold: true, size: 30 }),
      ...blank(1),
      p("〇〇〇〇〇〇〇〇　代表取締役　殿", { size: 20 }),
      p("※ 有限会社石名坂商事 又は 株式会社石名坂 のうち、届出先の社名をご記入ください", { size: 16 }),
      ...blank(1),
      p("　下記のとおり、他の使用者の事業場における就業について届け出ます。",
        { indent: { firstLine: 0 } }),
      ...blank(1),

      p("１　他の使用者の事業場", { go: true, bold: true, after: 100 }),
      tbl(block("【１社目】")),
      ...blank(1),
      tbl(block("【２社目】　※ 該当がない場合は空欄のままで結構です")),
      ...blank(1),

      p("２　確 認 事 項", { go: true, bold: true, after: 100 }),
      ckTable,
      ...blank(1),

      p("３　届 出 者", { go: true, bold: true, after: 100 }),
      signTable,
      ...blank(1),

      p("〔 会 社 記 入 欄 〕", { go: true, size: 19 }),
      new Table({
        columnWidths: [2600, 6472],
        width: { size: W, type: WidthType.DXA },
        rows: [
          new TableRow({ children: [
            cell("受 理 日", 2600, { shade: HEAD, bold: true, go: true }),
            cell("令和　　年　　月　　日　　　受理者　　　　　　　　　　　㊞", 6472),
          ]}),
          new TableRow({ children: [
            cell("当社の位置づけ", 2600, { shade: HEAD, bold: true, go: true }),
            cell("□ 使用者Ａ（先に労働契約を締結）　　□ 使用者Ｂ（後から労働契約を締結）", 6472),
          ]}),
          new TableRow({ children: [
            cell("通算後の取扱い", 2600, { shade: HEAD, bold: true, go: true }),
            cell(["□ 通算しても法定労働時間の範囲内",
                  "□ 法定労働時間を超えるため、当社で時間外労働として取り扱う（　　　時間／日）",
                  "□ 管理モデルにより上限を設定する（別紙「労働時間の上限設定書」）"], 6472),
          ]}),
        ],
      }),
      ...blank(1),

      p("〔 根 拠 〕", { go: true, size: 18 }),
      p("労働基準法第３８条第１項「労働時間は、事業場を異にする場合においても、労働時間に関する規定の適用については通算する。」", { size: 17, line: 240 }),
      p("「事業場を異にする場合」とは事業主を異にする場合をも含む（昭和２３年５月１４日付け基発第７６９号）。", { size: 17, line: 240 }),
      p("労働時間の通算は、自らの事業場における労働時間と、労働者からの申告等により把握した他の使用者の事業場における労働時間とを通算することによって行う（令和２年９月１日付け基発０９０１第３号 第３の１(2)）。正確にご記入ください。", { size: 17, line: 240 }),
      p("通算されるのは法定労働時間（法第３２条・第４０条）等です。休憩（第３４条）・休日（第３５条）・年次有給休暇（第３９条）は通算されません（同通達 第１の３）。", { size: 17, line: 240 }),
    ],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(__dirname + "/../副業兼業届出書.docx", b);
  console.log("wrote 副業兼業届出書.docx");
});
