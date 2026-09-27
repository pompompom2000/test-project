# PDF の再生成手順

`docs/legal-research/pdf/傭車の考え方と利用運送の登録判断.pdf` のソースです。

## 構成
- `body.html` — 本文（HTML）
- `style.css` — A4向けのスタイル
- `gen.py` — Chromium で印刷して PDF を書き出すスクリプト

## 生成
```bash
apt-get install -y fonts-noto-cjk      # 日本語フォント（太字を含む）
pip install playwright
python3 gen.py
```

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
d = p.PdfDocument('傭車の考え方と利用運送の登録判断.pdf')
print(len(d), d[len(d)-1].get_textpage().get_text_range()[-80:])
```
