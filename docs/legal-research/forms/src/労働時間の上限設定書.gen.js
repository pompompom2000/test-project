const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign, PageBreak,
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
const NAVY = "16395C";
const W = 9072;
const C = [2800, 6272];
const row = (label, value) => new TableRow({
  children: [
    cell(label, C[0], { shade: HEAD, bold: true, go: true }),
    cell(value, C[1]),
  ],
});
const band = (title) => new TableRow({
  children: [cell(title, W, { span: 2, shade: NAVY, bold: true, go: true, size: 20 })],
});
const tbl = (rows) => new Table({ columnWidths: C, width: { size: W, type: WidthType.DXA }, rows });

// ---- 当事者 ---------------------------------------------------------------
const party = tbl([
  band("使用者Ａ　―　時間的に先に労働契約を締結していた使用者"),
  row("名 称", ""),
  row("所 在 地", ""),
  row("労働契約を締結した日", "令和　　年　　月　　日"),
  row("担当者・連絡先", "　　　　　　　　　　　　　ＴＥＬ　　　　－　　　　－"),
  band("使用者Ｂ　―　時間的に後から労働契約を締結した使用者"),
  row("名 称", ""),
  row("所 在 地", ""),
  row("労働契約を締結した日", "令和　　年　　月　　日"),
  row("担当者・連絡先", "　　　　　　　　　　　　　ＴＥＬ　　　　－　　　　－"),
]);

// ---- 上限の設定 -----------------------------------------------------------
const U = [3400, 2836, 2836];
const urow = (label, a, b, o = {}) => new TableRow({
  children: [
    cell(label, U[0], { shade: o.shade ?? HEAD, bold: true, go: true, size: o.size }),
    cell(a, U[1], { align: AlignmentType.CENTER, size: o.size, bold: o.bold }),
    cell(b, U[2], { align: AlignmentType.CENTER, size: o.size, bold: o.bold }),
  ],
});

const upper = new Table({
  columnWidths: U,
  width: { size: W, type: WidthType.DXA },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell("項 目", U[0], { shade: NAVY, bold: true, go: true, size: 20 }),
        cell("使用者Ａ", U[1], { shade: NAVY, bold: true, go: true, size: 20, align: AlignmentType.CENTER }),
        cell("使用者Ｂ", U[2], { shade: NAVY, bold: true, go: true, size: 20, align: AlignmentType.CENTER }),
      ],
    }),
    urow("月の労働時間の起算日", "毎月　　　日", "毎月　　　日"),
    urow("１か月の上限として設定する時間",
      ["法定外労働時間", "　　　　時間"],
      ["労働時間（所定＋所定外）", "　　　　時間"]),
    urow("うち深夜業の見込み", "　　　　時間", "　　　　時間"),
    new TableRow({
      children: [
        cell("１か月の合計（Ａ＋Ｂ）", U[0], { shade: HEAD, bold: true, go: true }),
        cell("　　　　　　時間", U[1] + U[2], { span: 2, align: AlignmentType.CENTER }),
      ],
    }),
    urow("　　→　単月１００時間未満であること", "□ 確認", "□ 確認", { shade: "FDF4E2" }),
    urow("　　→　複数月平均８０時間以内であること", "□ 確認", "□ 確認", { shade: "FDF4E2" }),
    urow("３６協定の延長時間の範囲内であること", "□ 確認", "□ 確認"),
  ],
});

// ---- 割増賃金 -------------------------------------------------------------
const wage = tbl([
  band("時間外労働の割増賃金の取扱い"),
  row("使用者Ａが支払う範囲", ["自らの事業場における【法定外労働時間】の労働について支払う。",
    "※ 所定外労働時間についても割増賃金を支払うこととしている場合は、所定外労働時間の労働について支払う"]),
  row("使用者Ｂが支払う範囲", "自らの事業場における【労働時間】の労働について支払う（所定労働時間を含む）"),
  row("割 増 率", ["それぞれ自らの事業場の就業規則等で定めた率（２割５分以上）。",
    "ただし、使用者Ａの法定外労働時間の上限に使用者Ｂの労働時間を通算して、自らの事業場の労働時間制度における法定労働時間を超える部分が１か月について６０時間を超えた場合には、その超えた時間の労働のうち自らの事業場において労働させた時間については５割以上の率"]),
]);

// ---- 運用 -----------------------------------------------------------------
const ope = tbl([
  band("運用上の取決め"),
  row("実労働時間の把握", "各々の使用者は、あらかじめ設定した上記の上限の範囲内で労働させる限り、【相手方の事業場における実労働時間を把握することを要しない】。"),
  row("上限を変更する場合", "あらかじめ【労働者を通じて】相手方に通知し、必要に応じて相手方において設定した上限を変更する。"),
  row("３以上の事業場の場合", "労働者が事業主を異にする３以上の事業場で労働する場合も、同様に取り扱う。"),
  row("改善基準告示", "土砂等の運搬その他の運転業務に従事する場合は、通算した拘束時間・運転時間が「自動車運転者の労働時間等の改善のための基準」に適合するよう管理する。"),
  row("有効期間", ["令和　　年　　月　　日　から　令和　　年　　月　　日　まで",
    "□ 期間満了後も、いずれかから申出がない限り同一条件で継続する"]),
]);

// ---- 署名 -----------------------------------------------------------------
const G = [2200, 6872];
const sign = (label, lines) => new TableRow({
  children: [
    cell(label, G[0], { shade: HEAD, bold: true, go: true }),
    cell(lines, G[1]),
  ],
});
const signTable = new Table({
  columnWidths: G,
  width: { size: W, type: WidthType.DXA },
  rows: [
    sign("設 定 日", ["令和　　年　　月　　日"]),
    sign("対象となる労働者", ["氏名　　　　　　　　　　　　　　　　　　　㊞", "生年月日　　　　年　　月　　日"]),
    sign("使 用 者 Ａ", ["名称　　　　　　　　　　　　　　　　　　　", "代表者又は責任者　　　　　　　　　　　　　㊞"]),
    sign("使 用 者 Ｂ", ["名称　　　　　　　　　　　　　　　　　　　", "代表者又は責任者　　　　　　　　　　　　　㊞"]),
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
      p("労 働 時 間 の 上 限 設 定 書 （ 管 理 モ デ ル ）",
        { align: AlignmentType.CENTER, go: true, bold: true, size: 28 }),
      p("令和２年９月１日付け基発０９０１第３号「副業・兼業の場合における労働時間管理に係る労働基準法第３８条第１項の解釈等について」第５に基づく",
        { align: AlignmentType.CENTER, size: 17 }),
      ...blank(1),

      p("　下記の労働者について、副業・兼業の開始前に、各々の使用者の事業場における労働時間の上限を次のとおり設定する。",
        { indent: { firstLine: 0 } }),
      p("　各々の使用者は、それぞれ設定した範囲内で労働させることとし、これにより、相手方の事業場における実労働時間を把握することなく労働基準法を遵守するものとする。",
        { indent: { firstLine: 0 } }),
      ...blank(1),

      p("１　当 事 者", { go: true, bold: true, after: 100 }),
      party,
      ...blank(1),

      p("２　１か月の労働時間の上限", { go: true, bold: true, after: 100 }),
      upper,
      p("※ 月の労働時間の起算日が使用者Ａと使用者Ｂとで異なる場合は、各々の事業場の労働時間制度における起算日を基に、そこから起算した１か月における上限をそれぞれ設定して差し支えない（同通達 第５の３(2)）。",
        { size: 17, line: 240, before: 80 }),
      p("※ 合計を８０時間を超えるものとした場合、翌月以降に複数月平均８０時間未満となるよう調整が必要になり得るため、そのような調整が生じないように上限を設定することが望ましい（同 第５の４(1)）。",
        { size: 17, line: 240 }),

      new Paragraph({ children: [new PageBreak()] }),

      p("３　時間外労働の割増賃金", { go: true, bold: true, after: 100 }),
      wage,
      ...blank(1),

      p("４　運 用", { go: true, bold: true, after: 100 }),
      ope,
      ...blank(1),

      p("５　署 名", { go: true, bold: true, after: 100 }),
      signTable,
      ...blank(1),

      p("〔 使 い 方 〕", { go: true, size: 19 }),
      p("１　労働者から「副業・兼業に関する届出書」を受け取り、労働契約の締結日の先後から使用者Ａ・使用者Ｂを確定します。",
        { size: 18, line: 250 }),
      p("２　管理モデルは、一般に、使用者Ａが労働者に対して管理モデルにより副業・兼業を行うことを求め、労働者及び労働者を通じて使用者Ｂがこれに応じることによって導入されます（同通達 第５の３(1)）。",
        { size: 18, line: 250 }),
      p("３　本書は労働者を通じて相手方に交付し、三者が各１通を保有します。",
        { size: 18, line: 250 }),
      p("４　上限を変更するときは、あらかじめ労働者を通じて相手方に通知します。変更があり得る旨をあらかじめ留保しておくことが望ましいとされています（同 第５の４(2)）。",
        { size: 18, line: 250 }),
      ...blank(1),
      p("〔 注 意 〕", { go: true, size: 19 }),
      p("通算されるのは法定労働時間（労基法第３２条・第４０条）及び時間外労働と休日労働の合計で単月１００時間未満・複数月平均８０時間以内の要件（第３６条第６項第２号・第３号）です。休憩（第３４条）・休日（第３５条）・年次有給休暇（第３９条）は通算されません。３６協定の限度時間（第３６条第４項）及び特別条項の年の上限（同第５項）は、それぞれの事業場ごとに定めます（同通達 第１の３）。",
        { size: 17, line: 240 }),
    ],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(__dirname + "/../労働時間の上限設定書（管理モデル）.docx", b);
  console.log("wrote 労働時間の上限設定書（管理モデル）.docx");
});
