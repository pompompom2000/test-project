const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  PageBreak, VerticalAlign,
} = require("docx");

const MIN = { ascii: "ＭＳ 明朝", eastAsia: "ＭＳ 明朝", hAnsi: "ＭＳ 明朝" };
const GO  = { ascii: "ＭＳ ゴシック", eastAsia: "ＭＳ ゴシック", hAnsi: "ＭＳ ゴシック" };

// 本文 10.5pt = 21 half-points
const S = 21;

const p = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { line: o.line ?? 320, lineRule: "auto", before: o.before ?? 0, after: o.after ?? 0 },
  indent: o.indent,
  border: o.border,
  children: [new TextRun({ text, bold: o.bold, size: o.size ?? S, font: o.go ? GO : MIN })],
});

const blank = (n = 1) => Array.from({ length: n }, () => p(""));

// ---- 表のセル -------------------------------------------------------------
const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined,
  verticalAlign: VerticalAlign.CENTER,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: (Array.isArray(text) ? text : [text]).map((t) => new Paragraph({
    alignment: o.align,
    spacing: { line: 260, lineRule: "auto" },
    children: [new TextRun({ text: t, bold: o.bold, size: o.size ?? 19, font: o.go ? GO : MIN })],
  })),
});

const COLS = [620, 4180, 900, 3372];          // 合計 9072 DXA（A4・左右25mm）
const HEAD = "E8ECF0";

const docRow = (no, name, bu, note) => new TableRow({
  children: [
    cell(no,   COLS[0], { align: AlignmentType.CENTER }),
    cell(name, COLS[1]),
    cell(bu,   COLS[2], { align: AlignmentType.CENTER }),
    cell(note, COLS[3], { size: 18 }),
  ],
});

const DOCS = [
  ["１", "一般貨物自動車運送事業許可書の写し", "１部", "許可番号及び許可年月日が読み取れるもの"],
  ["２", "事業用自動車の自動車検査証の写し", "全車分", "弊社の運送に使用される車両のすべて。「自家用」ではなく「事業用」である旨をご確認ください"],
  ["３", "自動車損害賠償責任保険証明書の写し", "全車分", ""],
  ["４", "任意保険（対人・対物賠償責任保険）証券の写し", "１部", "補償限度額が確認できるもの"],
  ["５", "運送業者貨物賠償責任保険証券の写し", "１部", "被保険車両が限定されている場合は、対象車両の一覧もご添付ください"],
  ["６", "運行管理者選任届出書の写し", "１部", ""],
  ["７", "表示番号の指定通知書の写し", "該当車両分", "ダンプ車をご使用の場合のみ。土砂等を運搬する大型自動車による交通事故の防止等に関する特別措置法第３条第２項"],
];

const docTable = new Table({
  columnWidths: COLS,
  width: { size: COLS.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell("No",     COLS[0], { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER }),
        cell("書 類 名", COLS[1], { shade: HEAD, bold: true, go: true }),
        cell("部数",   COLS[2], { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER }),
        cell("備 考",  COLS[3], { shade: HEAD, bold: true, go: true }),
      ],
    }),
    ...DOCS.map((d) => docRow(...d)),
  ],
});

// ---- 別紙：チェックシート --------------------------------------------------
const C2 = [620, 5452, 1500, 1500];
const chkRow = (no, name) => new TableRow({
  children: [
    cell(no,   C2[0], { align: AlignmentType.CENTER }),
    cell(name, C2[1]),
    cell("□",  C2[2], { align: AlignmentType.CENTER, size: 22 }),
    cell("□",  C2[3], { align: AlignmentType.CENTER, size: 22 }),
  ],
});

const chkTable = new Table({
  columnWidths: C2,
  width: { size: C2.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell("No",       C2[0], { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER }),
        cell("書 類 名", C2[1], { shade: HEAD, bold: true, go: true }),
        cell("提出済",   C2[2], { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER }),
        cell("該当なし", C2[3], { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER }),
      ],
    }),
    ...DOCS.map((d) => chkRow(d[0], d[1])),
  ],
});

const R3 = [2200, 6872];
const respRow = (label, value) => new TableRow({
  children: [
    cell(label, R3[0], { shade: HEAD, bold: true, go: true }),
    cell(value, R3[1]),
  ],
});

const respTable = new Table({
  columnWidths: R3,
  width: { size: R3.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  rows: [
    respRow("貴 社 名", ""),
    respRow("ご 担 当 者 名", ""),
    respRow("電 話 番 号", ""),
    respRow("ご 提 出 日", "令和　　年　　月　　日"),
    respRow("許 可 番 号", ""),
    respRow("車 両 台 数", "　　　　台（うち今回ご提出分　　　　台）"),
  ],
});

// ---- 文書 ------------------------------------------------------------------
const doc = new Document({
  styles: { default: { document: { run: { size: S, font: MIN } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },          // A4 縦
        margin: { top: 1701, bottom: 1701, left: 1417, right: 1417 }, // 上下30mm・左右25mm
      },
    },
    children: [
      p("石商発第　　　号", { align: AlignmentType.RIGHT }),
      p("令和　　年　　月　　日", { align: AlignmentType.RIGHT }),
      ...blank(1),
      p("お 取 引 先 各 位", { go: true, size: 22 }),
      ...blank(1),
      p("岩手県盛岡市〇〇〇〇", { align: AlignmentType.RIGHT }),
      p("有限会社石名坂商事", { align: AlignmentType.RIGHT, go: true, size: 22 }),
      p("代表取締役　〇〇　〇〇　　㊞", { align: AlignmentType.RIGHT }),
      p("（担当）運行管理担当　〇〇　〇〇", { align: AlignmentType.RIGHT, size: 19 }),
      p("ＴＥＬ ０１９－〇〇〇－〇〇〇〇／ＦＡＸ ０１９－〇〇〇－〇〇〇〇", { align: AlignmentType.RIGHT, size: 19 }),
      ...blank(2),

      p("一般貨物自動車運送事業許可書の写し等ご提出のお願い",
        { align: AlignmentType.CENTER, go: true, bold: true, size: 28 }),
      ...blank(2),

      p("拝啓　時下ますますご清栄のこととお慶び申し上げます。平素は格別のお引き立てを賜り、厚く御礼申し上げます。",
        { indent: { firstLine: 210 } }),
      ...blank(1),
      p("さて、令和８年４月１日に施行された改正貨物自動車運送事業法第６５条の２により、許可又は届出を受けていない事業者へ貨物の運送を委託することが禁止され、これに違反した委託者には１００万円以下の罰金が科されることとなりました。同条は「何人も」を名宛人としており、委託する側が委託先の資格を確認すべき仕組みとなっております。",
        { indent: { firstLine: 210 } }),
      ...blank(1),
      p("つきましては、弊社の法令遵守体制の整備のため、誠に恐れ入りますが、下記の書類を期限までにご提出くださいますようお願い申し上げます。既にご提出いただいている書類につきましては、重ねてのご提出は不要でございます。",
        { indent: { firstLine: 210 } }),
      ...blank(1),
      p("なお、ご提出が確認できない場合には、誠に不本意ながら弊社からの運送委託を見合わせざるを得ませんので、何卒ご理解とご協力を賜りますようお願い申し上げます。",
        { indent: { firstLine: 210 } }),
      ...blank(1),
      p("敬具", { align: AlignmentType.RIGHT }),
      ...blank(1),
      p("記", { align: AlignmentType.CENTER, go: true }),
      ...blank(1),

      p("１　ご提出をお願いする書類", { go: true, bold: true, after: 120 }),
      docTable,
      ...blank(1),

      p("２　提 出 期 限", { go: true, bold: true, after: 60 }),
      p("令和　　年　　月　　日（　　）", { indent: { left: 420 } }),
      ...blank(1),

      p("３　提 出 方 法", { go: true, bold: true, after: 60 }),
      p("郵送・ＦＡＸ又は電子メール（ＰＤＦ）のいずれかにより、別紙チェックシートを添えてご返送ください。",
        { indent: { left: 420 } }),
      p("〒〇〇〇－〇〇〇〇　岩手県盛岡市〇〇〇〇　有限会社石名坂商事　〇〇　宛",
        { indent: { left: 420 } }),
      p("ＦＡＸ ０１９－〇〇〇－〇〇〇〇　／　電子メール 〇〇〇＠〇〇〇.co.jp",
        { indent: { left: 420 } }),
      ...blank(1),

      p("４　今後のお取扱い", { go: true, bold: true, after: 60 }),
      p("ご提出いただいた書類は、本件の確認以外の目的には使用いたしません。許可の有効期間の満了、取消し若しくは停止、又は事業の休止・廃止があった場合には、速やかに弊社担当までご連絡くださいますようお願いいたします。また、年に一度、記載内容に変更がないかのご確認をお願いする場合がございます。",
        { indent: { left: 420 } }),
      ...blank(1),
      p("以上", { align: AlignmentType.RIGHT }),

      new Paragraph({ children: [new PageBreak()] }),

      // ---------------- 別紙 ----------------
      p("（別紙）", { size: 19 }),
      ...blank(1),
      p("提 出 書 類 チ ェ ッ ク シ ー ト",
        { align: AlignmentType.CENTER, go: true, bold: true, size: 26 }),
      ...blank(1),
      p("本シートに必要事項をご記入のうえ、書類を添えてご返送ください。",
        { indent: { firstLine: 210 } }),
      ...blank(1),
      respTable,
      ...blank(1),
      chkTable,
      ...blank(1),
      p("※　「該当なし」にチェックされた場合は、その理由を下欄にご記入ください。", { size: 19 }),
      ...blank(1),
      p("（理由欄）", { size: 19 }),
      p("", { border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "888888" } }, after: 200 }),
      p("", { border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "888888" } }, after: 200 }),
      p("", { border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "888888" } }, after: 200 }),
      ...blank(2),
      p("【弊社使用欄】", { go: true, size: 19 }),
      p("受領日：令和　　年　　月　　日　　／　　確認者：　　　　　　　　／　　台帳記載：済・未", { size: 19 }),
      p("次回確認予定日：令和　　年　　月　　日", { size: 19 }),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("許可証提出依頼書.docx", buf);
  console.log("wrote 許可証提出依頼書.docx", buf.length, "bytes");
});
