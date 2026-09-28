# PDF の再生成手順

`docs/legal-research/pdf/` に置いてある2本のPDFのソースです。

| 出力 | スクリプト | 中身 |
|---|---|---|
| `傭車の考え方と利用運送の登録判断.pdf` | `gen.py` | 本編（全編） |
| `白ダンプの早見表.pdf` | `gen_hayami.py` | 本編の65〜69章（付録：白ダンプ早見表）だけを抜き出した現場用の抜き刷り |

## 構成
- `body.html` — 本文（HTML）。**早見表もここが原本です**
- `style.css` — A4向けのスタイル。2本のPDFで共用
- `gen.py` — Chromium で印刷して本編PDFを書き出すスクリプト
- `gen_hayami.py` — `body.html` から `<!-- ============ 付録：白ダンプ早見表 ============ -->` 以降を切り出し、
  専用の表紙を付けて `hayami.html` を組み、同じ流れで早見表PDFを書き出すスクリプト

## 生成
```bash
apt-get install -y fonts-noto-cjk      # 日本語フォント（太字を含む）
pip install playwright
python3 gen.py            # 本編
python3 gen_hayami.py     # 早見表
```

生成物は `src/` に出ます（`.gitignore` 済み）。リポジトリに載せるときは
親ディレクトリ `docs/legal-research/pdf/` にコピーしてください。

**早見表を直すときは `body.html` を直してください。** `gen_hayami.py` は切り出すだけなので、
本編を直せば早見表も自動で追随します。逆に `hayami.html` を直しても次の生成で消えます。

`gen.py` は Playwright 経由で Chromium を起動します。Claude Code の実行環境では
`/opt/pw-browsers/chromium-1194/chrome-linux/chrome` を直接指定しています。
別環境では `executable_path` を書き換えるか、`playwright install chromium` を実行してください。

ページ番号とフッターは `gen.py` の `footer_template` で付与しています
（Chromium は `@page` のマージンボックスに対応していないため CSS では出せません）。

## 注意 ― 末尾のページが欠けたPDFが出ることがあります

`pg.pdf()` をレイアウト確定前に呼ぶと、**末尾の数ページが黙って落ちたPDF**が生成されます
（ページ途中で本文が切れた状態になります）。`gen.py` では `document.fonts.ready` の待機と
3秒のウェイトを入れてありますが、生成後は必ず**総ページ数と最終ページの末尾**を確認してください。

```python
import pypdfium2 as p
for f in ['傭車の考え方と利用運送の登録判断.pdf', '白ダンプの早見表.pdf']:
    d = p.PdfDocument(f)
    print(f, len(d), d[len(d)-1].get_textpage().get_text_range()[-80:])
```

2026年9月28日時点で、本編は117ページ、早見表は15ページです。
