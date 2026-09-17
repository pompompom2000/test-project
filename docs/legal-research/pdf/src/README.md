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
