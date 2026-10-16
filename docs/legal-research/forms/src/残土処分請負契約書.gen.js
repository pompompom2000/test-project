// 残土処分請負契約書（Word）
// 中身は src/keiyaku.json にあり、PDF版（残土処分請負契約書.gen.py）も同じものを読む。
// 文面を直すときは keiyaku.json だけを直すこと。
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, PageOrientation,
  Table, TableRow, TableCell, WidthType, ShadingType, VerticalAlign,
  TableLayoutType, BorderStyle,
} = require("docx");

const D = JSON.parse(fs.readFileSync(path.join(__dirname, "keiyaku.json"), "utf8"));

const MIN = { ascii: "ＭＳ 明朝", eastAsia: "ＭＳ 明朝", hAnsi: "ＭＳ 明朝" };
const GO  = { ascii: "ＭＳ ゴシック", eastAsia: "ＭＳ ゴシック", hAnsi: "ＭＳ ゴシック" };
const S = 21;                       // 本文 10.5pt
const NAVY = "16395C", HEAD = "E8ECF0", WARN = "FDF4E2";
const W = 9072;                     // A4縦・左右25mm余白のときの本文幅
const KANSUJI = ["", "", "２", "３", "４", "５", "６", "７", "８", "９", "10"];

const p = (text, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { line: o.line ?? 300, lineRule: "auto", before: o.before ?? 0, after: o.after ?? 0 },
  indent: o.indent,
  pageBreakBefore: o.br,
  keepNext: o.keep,
  children: [new TextRun({ text, bold: o.bold, size: o.size ?? S, font: o.go ? GO : MIN })],
});
const blank = (n = 1) => Array.from({ length: n }, () => p(""));

const cell = (text, w, o = {}) => new TableCell({
  width: { size: w, type: WidthType.DXA },
  columnSpan: o.span,
  shading: o.shade ? { type: ShadingType.CLEAR, fill: o.shade, color: "auto" } : undefined,
  verticalAlign: o.top ? VerticalAlign.TOP : VerticalAlign.CENTER,
  margins: { top: 70, bottom: 70, left: 100, right: 100 },
  borders: o.noborder ? {
    top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
    left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
  } : undefined,
  children: (Array.isArray(text) ? text : String(text).split("\n")).map((t) => new Paragraph({
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

// ------------------------------------------------------------ 契約書本体
const out = [
  p(D.title, { align: AlignmentType.CENTER, go: true, bold: true, size: 32, after: 100 }),
  p(D.subtitle, { align: AlignmentType.CENTER, go: true, size: 19, after: 340 }),
  ...D.preamble.map((t) => p(t, { indent: { firstLine: 210 }, after: 240 })),
];

D.articles.forEach((a) => {
  out.push(p(`${a.no}（${a.title}）`, { go: true, bold: true, size: 22, before: 220, after: 80, keep: true }));
  let n = 0;
  a.paras.forEach((x) => {
    if (Array.isArray(x)) {                       // 号の列挙
      x.forEach((t) => out.push(p(t, { indent: { left: 420, hanging: 210 }, size: 20 })));
      return;
    }
    n += 1;
    const label = n === 1 ? "" : `${KANSUJI[n]}　`;
    out.push(p(label + x, { indent: { left: 210, hanging: n === 1 ? 0 : 210 } }));
  });
});

out.push(...blank(1));
D.closing.forEach((t) => out.push(p(t, { indent: { firstLine: 210 }, after: 240 })));
out.push(p(D.sign_date, { after: 240 }));

const SC = [700, 1500, 6872];
D.sign_rows.forEach(([mark, ...labels]) => {
  labels.forEach((lab, i) => {
    out.push(mk(SC, [new TableRow({ children: [
      cell(i === 0 ? mark : "", SC[0], { noborder: true, go: true, bold: true, align: AlignmentType.CENTER, size: 21 }),
      cell(lab, SC[1], { noborder: true, size: 20 }),
      cell(lab === "代表者" ? "　　　　　　　　　　　　　　　　　　　　印" : "", SC[2], { noborder: true, size: 20 }),
    ] })]));
  });
  out.push(p("", { after: 120 }));
});

// ------------------------------------------------------------ 別紙１
out.push(p(D.att1_title, { go: true, bold: true, size: 24, after: 200, br: true }));
const A1 = D.att1_cols;
out.push(mk(A1, [
  new TableRow({ children: D.att1_head.map((h, i) => cell(h, A1[i],
    { shade: HEAD, bold: true, go: true, align: AlignmentType.CENTER })) }),
  ...D.att1_rows.map((r) => new TableRow({ children: r.map((v, i) => cell(v, A1[i], {
    top: true, align: i >= 2 ? AlignmentType.CENTER : undefined,
  })) })),
  new TableRow({ children: D.att1_total.map((v, i) => cell(v, A1[i],
    { shade: HEAD, bold: i === 0, go: i === 0, align: AlignmentType.CENTER })) }),
]));
out.push(mk([W], [new TableRow({ children: [cell(D.att1_note, W, { top: true, size: 18, shade: WARN })] })]));

// ------------------------------------------------------------ 別紙２
out.push(p(D.att2_title, { go: true, bold: true, size: 24, after: 200, br: true }));
const A2 = D.att2_cols;
out.push(mk(A2, D.att2_rows.map(([k, v]) => new TableRow({ children: [
  cell(k, A2[0], { shade: HEAD, bold: true, go: true, size: 18, top: true }),
  cell(v || "", A2[1], { top: true, size: 18 }),
] }))));

// ------------------------------------------------------------ 社内用メモ
out.push(p(D.memo_title, { go: true, bold: true, size: 24, after: 160, br: true }));
out.push(mk([W], [new TableRow({ children: [
  cell(D.memo_lead, W, { top: true, size: 19, shade: WARN, bold: true })] })]));
out.push(...blank(1));
D.memo_sections.forEach((s) => {
  out.push(band(s.h));
  s.ps.forEach((t) => out.push(p(t, { size: 19, line: 280, indent: { left: 180 } })));
  out.push(p("", { after: 140 }));
});

const doc = new Document({
  styles: { default: { document: { run: { size: S, font: MIN } } } },
  sections: [{
    properties: { page: {
      size: { orientation: PageOrientation.PORTRAIT, width: 11906, height: 16838 },
      margin: { top: 1134, bottom: 1134, left: 1417, right: 1417 },
    } },
    children: out,
  }],
});

Packer.toBuffer(doc).then((b) => {
  fs.writeFileSync(path.join(__dirname, "..", "残土処分請負契約書.docx"), b);
  console.log("wrote 残土処分請負契約書.docx");
});
