// 照会記録票 ― 運輸局・労基署等への照会の回答を、その場で書き留めるための1枚。
// 口頭回答は記録しないと残らない。応対者の氏名と日付を必ず取ること。
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageOrientation,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign,
  TableLayoutType,
} = require("docx");

const MIN = { ascii: "ＭＳ 明朝", eastAsia: "ＭＳ 明朝", hAnsi: "ＭＳ 明朝" };
const GO  = { ascii: "ＭＳ ゴシック", eastAsia: "ＭＳ ゴシック", hAnsi: "ＭＳ ゴシック" };
const S = 20;
const NAVY = "16395C", HEAD = "E8ECF0", WARN = "FDF4E2";
const W = 9072;

const p = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { line: o.line ?? 290, lineRule: "auto", before: o.before ?? 0, after: o.after ?? 0 },
  children: [new TextRun({ text, bold: o.bold, size: o.size ?? S, font: o.go ? GO : MIN })],
});
const blank = (n = 1) => Array.from({ length: n }, () => p(""));

const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  columnSpan: o.span,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined,
  verticalAlign: o.top ? VerticalAlign.TOP : VerticalAlign.CENTER,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: (Array.isArray(text) ? text : [text]).map((t) => new Paragraph({
    alignment: o.align,
    spacing: { line: 260, lineRule: "auto" },
    children: [new TextRun({ text: t, bold: o.bold, size: o.size ?? 19,
      font: o.go ? GO : MIN, color: o.color })],
  })),
});

const mk = (cols, rows) => new Table({
  columnWidths: cols,
  width: { size: cols.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  layout: TableLayoutType.FIXED,
  rows,
});

const C = [1900, 7172];
const row = (l, v, o = {}) => new TableRow({
  children: [cell(l, C[0], { shade: HEAD, bold: true, go: true }),
             cell(v, C[1], { top: o.top })],
});
const full = (text, o = {}) => new TableRow({
  children: [cell(text, W, { span: 2, top: true, ...o })],
});
const lines = (n) => Array.from({ length: n }, () => "");

const children = [
  p("照 会 記 録 票", { align: AlignmentType.CENTER, go: true, bold: true, size: 32, after: 80 }),
  p("運輸局・運輸支局・労働基準監督署・県への照会と、その回答の記録",
    { align: AlignmentType.CENTER, size: 18, after: 240 }),

  mk(C, [
    row("整理番号", "（例：A-1、B-3　※21_運輸局への照会事例集の番号）"),
    row("照会日時", "　　　　年　　月　　日（　）　　　時　　分　〜　　　時　　分"),
    row("方法", "□ 電話　　□ 窓口で対面　　□ 書面（FAX・メール）　　□ その他（　　　　　　　）"),
    row("照会先", ["□ 東北運輸局 自動車交通部 貨物課（022-791-7531）",
                   "□ 岩手運輸支局 輸送・監査部門（019-638-2154 音声案内【3】）",
                   "□ 岩手運輸支局 登録部門　　□ 盛岡労働基準監督署　　□ ハローワーク盛岡",
                   "□ 岩手県 資源循環推進課（019-629-5388）　　□ 年金事務所",
                   "□ その他（　　　　　　　　　　　　　　　　　　　　　　　　　　　　）"], { top: true }),
    row("応対者", "部署：　　　　　　　　　役職：　　　　　　　　　氏名："),
    row("当社担当", "氏名："),
  ]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell("１　聞いたこと", W,
    { shade: NAVY, bold: true, go: true, size: 21, color: "FFFFFF" })] })]),
  mk([W], [new TableRow({ children: [cell(lines(6), W, { top: true })] })]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell("２　回答（できるだけ言われたとおりに書く）", W,
    { shade: NAVY, bold: true, go: true, size: 21, color: "FFFFFF" })] })]),
  mk([W], [new TableRow({ children: [cell(lines(12), W, { top: true })] })]),

  ...blank(1),
  mk(C, [
    row("結論", "□ 当社の理解どおり　　□ 一部異なる　　□ 異なる　　□ 明確な回答は得られず"),
    row("言質の強さ", ["□ 断定的（「そのとおりです」）",
                       "□ 留保つき（「一般論としては」「個別には実態で」）",
                       "□ 回答不可（「個別具体の判断はできない」「他の窓口へ」）"], { top: true }),
    row("書面回答", "□ 依頼した（回答予定：　　月　　日頃）　　□ 依頼したが断られた　　□ 依頼せず"),
  ]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell("３　前提のどれが変わると結論が変わるか", W,
    { shade: NAVY, bold: true, go: true, size: 21, color: "FFFFFF" })] })]),
  mk([W], [new TableRow({ children: [cell([
    "※ここが一番大事です。必ず聞いて、聞けなかったときは「聞けなかった」と書いてください。",
    ...lines(5),
  ], W, { top: true })] })]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell("４　次にやること", W,
    { shade: NAVY, bold: true, go: true, size: 21, color: "FFFFFF" })] })]),
  mk([1500, 5072, 2500], [
    new TableRow({ children: [
      cell("", 1500, { shade: HEAD }),
      cell("内容", 5072, { shade: HEAD, bold: true, go: true }),
      cell("期限・担当", 2500, { shade: HEAD, bold: true, go: true }),
    ] }),
    new TableRow({ children: [
      cell("□", 1500, { align: AlignmentType.CENTER }),
      cell("本編PDFの該当章を直す（章番号：　　　　　）", 5072), cell("", 2500)] }),
    new TableRow({ children: [
      cell("□", 1500, { align: AlignmentType.CENTER }),
      cell("早見表（PDF・Word）を直す（▲番号：　　　　　）", 5072), cell("", 2500)] }),
    new TableRow({ children: [
      cell("□", 1500, { align: AlignmentType.CENTER }),
      cell("照会事例集から消し込む", 5072), cell("", 2500)] }),
    new TableRow({ children: [
      cell("□", 1500, { align: AlignmentType.CENTER }),
      cell("現場・配車室へ周知する", 5072), cell("", 2500)] }),
    new TableRow({ children: [
      cell("□", 1500, { align: AlignmentType.CENTER }),
      cell("別の窓口へ聞き直す（　　　　　　　　　　　）", 5072), cell("", 2500)] }),
    new TableRow({ children: [
      cell("□", 1500, { align: AlignmentType.CENTER }), cell("", 5072), cell("", 2500)] }),
  ]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell([
    "書き方の注意",
    "・応対者の氏名と日付は必ず取ること。後から「誰に聞いたか」が分からない記録は使えません。",
    "・回答は要約せず、言われた言葉のまま書くこと。とくに「一般論としては」「実態によります」",
    "　といった留保は、落とさずに書いてください。留保の有無で使える強さが変わります。",
    "・「個別具体の判断はできない」と言われた場合も、そう言われたこと自体が記録になります。",
    "・重要なものは「書面でいただけますか」と頼むこと。断られても、頼んだ事実を残します。",
    "・この票は事案ごとに1枚。まとめて書かないでください。",
  ], W, { top: true, size: 17, shade: WARN })] })]),

  ...blank(1),
  p("※ 記入後は社内リポジトリ docs/legal-research/verify_shokai/ に保存してください。",
    { size: 17 }),
];

const doc = new Document({
  styles: { default: { document: { run: { size: S, font: MIN } } } },
  sections: [{
    properties: { page: {
      size: { orientation: PageOrientation.PORTRAIT, width: 11906, height: 16838 },
      margin: { top: 1134, bottom: 1134, left: 1417, right: 1417 },
    } },
    children,
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync("照会記録票.docx", b);
  console.log("wrote 照会記録票.docx");
});
