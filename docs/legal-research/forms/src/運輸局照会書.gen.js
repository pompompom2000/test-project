// 運輸局照会書（Word）― 1件の照会につき1ページ。
// 中身は src/shokai.json にあり、PDF版（運輸局照会書.gen.py）も同じものを読む。
// 文面を直すときは shokai.json だけを直すこと。
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageOrientation,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign,
  TableLayoutType,
} = require("docx");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "shokai.json"), "utf8"));

const MIN = { ascii: "ＭＳ 明朝", eastAsia: "ＭＳ 明朝", hAnsi: "ＭＳ 明朝" };
const GO  = { ascii: "ＭＳ ゴシック", eastAsia: "ＭＳ ゴシック", hAnsi: "ＭＳ ゴシック" };
const S = 20;
const NAVY = "16395C", HEAD = "E8ECF0", WARN = "FDF4E2";
const W = 9072;

const p = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { line: o.line ?? 290, lineRule: "auto", before: o.before ?? 0, after: o.after ?? 0 },
  indent: o.indent,
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
    spacing: { line: 250, lineRule: "auto" },
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

const band = (text) => mk([W], [new TableRow({
  children: [cell(text, W, { shade: NAVY, bold: true, go: true, size: 21, color: "FFFFFF" })],
})]);

// ---------------------------------------------------------------- 表紙
const C2 = [2400, 6672];
const cover = [
  p(D.title, { align: AlignmentType.CENTER, go: true, bold: true, size: 34, after: 100 }),
  p(D.subtitle, { align: AlignmentType.CENTER, go: true, size: 21, after: 320 }),
  p("年　　月　　日", { align: AlignmentType.RIGHT, after: 240 }),
  p(D.to, { size: 22, after: 60 }),
  p(D.to_note, { size: 17, after: 300 }),
  mk(C2, D.sender.map(([l, v]) => new TableRow({
    children: [cell(l, C2[0], { shade: HEAD, bold: true, go: true }), cell(v, C2[1])],
  }))),

  ...blank(1),
  band(D.cast_title),
  mk([1100, 2900, 2400, 2672], [
    new TableRow({ children: D.cast_head.map((h, i) => cell(h, [1100, 2900, 2400, 2672][i],
      { shade: HEAD, bold: true, go: true, align: i === 1 ? undefined : AlignmentType.CENTER })) }),
    ...D.cast.map(([no, what, kyoka, car]) => new TableRow({ children: [
      cell(no, 1100, { bold: true, go: true, align: AlignmentType.CENTER }),
      cell(what, 2900),
      cell(kyoka, 2400, { align: AlignmentType.CENTER, bold: true }),
      cell(car, 2672, { align: AlignmentType.CENTER, bold: no === "甲社" }),
    ] })),
  ]),
  mk([W], [new TableRow({ children: [cell(D.cast_note, W, { top: true, size: 17, shade: WARN })] })]),

  ...blank(1),
  mk([W], [new TableRow({ children: [cell(D.greeting, W, { top: true, size: 19 })] })]),
  ...blank(1),
  mk([W], [new TableRow({ children: [cell(D.scope_note, W, { top: true, size: 17, shade: WARN })] })]),
];

// ---------------------------------------------------------------- 照会本体
const body = [];
D.inquiries.forEach((q, i) => {
  body.push(p(`【${q.no}】　${q.title}`,
    { go: true, bold: true, size: 24, before: i === 0 ? 0 : 400, after: 140, br: i !== 0 }));
  if (q.note.length) {
    q.note.forEach((t) => body.push(p(t, { size: 17, line: 250 })));
    body.push(p("", { after: 60 }));
  }
  [["fact", 0], ["mine", 1], ["base", 2], ["ask", 3]].forEach(([k, bi]) => {
    body.push(band(D.bands[bi]));
    q[k].forEach((t) => body.push(p(t, { line: 290, indent: { left: 180 }, size: k === "base" ? 19 : undefined })));
    body.push(p("", { after: bi === 3 ? 120 : 80 }));
  });
  body.push(mk([W], [new TableRow({ children: [
    cell([D.answer_box, "", "", "", "", ""], W, { top: true, size: 18 })] })]));
});

const doc = new Document({
  styles: { default: { document: { run: { size: S, font: MIN } } } },
  sections: [{
    properties: { page: {
      size: { orientation: PageOrientation.PORTRAIT, width: 11906, height: 16838 },
      margin: { top: 1134, bottom: 1134, left: 1417, right: 1417 },
    } },
    children: [...cover, ...body],
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(path.join(__dirname, "..", "運輸局照会書.docx"), b);
  console.log("wrote 運輸局照会書.docx");
});
