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
  pageBreakBefore: o.br,
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
  p("社 内 限 り", { align: AlignmentType.RIGHT, go: true, bold: true, size: 18, after: 40 }),
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
                   "□ 岩手県 資源循環推進課 廃棄物対策担当（019-629-5366）　　□ 年金事務所",
                   "□ その他（　　　　　　　　　　　　　　　　　　　　　　　　　　　　）",
                   "※運輸支局の電話受付は平日 8:30〜11:45／13:00〜17:00。昼休みは出ません"], { top: true }),
    row("応対者", "部署：　　　　　　　　　役職：　　　　　　　　　氏名："),
    row("当社担当", "氏名："),
    row("この照会の当事者", ["□ 甲社〔緑〕　　□ 乙社〔白〕　　□ 丙社〔白〕　　□ 丁社　　□ 戊〔白〕",
                             "□ その他（　　　　　　　　　　　　　　　　　　　　　　　　　　　）"], { top: true }),
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

  p("", { br: true }),
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
  mk([W], [new TableRow({ children: [cell("仮称の対照（照会書と同じ記号で書いてください）", W,
    { shade: NAVY, bold: true, go: true, size: 20, color: "FFFFFF" })] })]),
  mk([1100, 3500, 1900, 2572], [
    new TableRow({ children: [
      cell("仮称", 1100, { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("どのような会社か", 3500, { shade: HEAD, bold: true, go: true, size: 18 }),
      cell("運送事業の許可", 1900, { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("ナンバー", 2572, { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
    ] }),
    new TableRow({ children: [
      cell("甲社", 1100, { bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("運送事業者（大型ダンプ5両）", 3500, { size: 18 }),
      cell("有（一般貨物）", 1900, { align: AlignmentType.CENTER, bold: true, size: 18 }),
      cell("〔緑〕事業用", 2572, { align: AlignmentType.CENTER, bold: true, size: 18 }),
    ] }),
    new TableRow({ children: [
      cell("乙社", 1100, { bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("砕石の製造販売業者。甲社の親会社", 3500, { size: 18 }),
      cell("無", 1900, { align: AlignmentType.CENTER, size: 18 }),
      cell("〔白〕自家用", 2572, { align: AlignmentType.CENTER, size: 18 }),
    ] }),
    new TableRow({ children: [
      cell("丙社", 1100, { bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("砂利・砕石の販売業者", 3500, { size: 18 }),
      cell("無", 1900, { align: AlignmentType.CENTER, size: 18 }),
      cell("〔白〕自家用", 2572, { align: AlignmentType.CENTER, size: 18 }),
    ] }),
    new TableRow({ children: [
      cell("丁社", 1100, { bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("建設業者（元請）", 3500, { size: 18 }),
      cell("無", 1900, { align: AlignmentType.CENTER, size: 18 }),
      cell("―", 2572, { align: AlignmentType.CENTER, size: 18 }),
    ] }),
    new TableRow({ children: [
      cell("戊", 1100, { bold: true, go: true, align: AlignmentType.CENTER, size: 18 }),
      cell("個人。自ら運転する（持込み運転者）", 3500, { size: 18 }),
      cell("無", 1900, { align: AlignmentType.CENTER, size: 18 }),
      cell("〔白〕自家用", 2572, { align: AlignmentType.CENTER, size: 18 }),
    ] }),
  ]),
  mk([W], [new TableRow({ children: [cell([
    "・〔緑〕＝一般貨物の許可あり・事業用自動車　　〔白〕＝許可なし・自家用自動車",
    "・照会書（forms/運輸局照会書.docx）と同じ仮称で聞き、同じ仮称で記録してください。",
    "　実名で記録すると、実際に話した内容と記録が食い違い、あとで読み返せなくなります。",
    "・仮称と実名の対応表は 21_運輸局への照会事例集.md にあります。この票には書きません。",
    "　どの取引先の話だったかを残したいときは、下の「実名の控え」に書いてください。",
  ], W, { top: true, size: 17, shade: WARN })] })]),
  mk([2400, 6672], [new TableRow({ children: [
    cell(["実名の控え", "（社内限り・任意）"], 2400, { shade: HEAD, bold: true, go: true, size: 18 }),
    cell(["仮称　　　　＝", "仮称　　　　＝"], 6672, { top: true, size: 18 }),
  ] })]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell([
    "書き方の注意",
    "・会社名は仮称（甲社〔緑〕・乙社〔白〕など）で書くこと。聞くときも仮称で聞きます。",
    "・応対者の氏名と日付は必ず取ること。後から「誰に聞いたか」が分からない記録は使えません。",
    "・回答は要約せず、言われた言葉のまま書くこと。とくに「一般論としては」「実態によります」",
    "　といった留保は、落とさずに書いてください。留保の有無で使える強さが変わります。",
    "・「個別具体の判断はできない」と言われた場合も、そう言われたこと自体が記録になります。",
    "・重要なものは「書面でいただけますか」と頼むこと。断られても、頼んだ事実を残します。",
    "・この票は事案ごとに1枚。まとめて書かないでください。",
    "・この票は社内限りです。運輸局等に渡さないでください（実名の控えが入るため）。",
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
