#!/bin/bash
# スマホと同じ HTTP/2 で、トップページを繰り返し取り、札（Content-Type）と中身の頭を記録する
UA='Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Mobile Safari/537.36'
OUT=/tmp/claude-0/kansi.tsv
: > $OUT
for i in $(seq 1 150); do
  for proto in --http2 --http1.1; do
    R=$(curl -s $proto --compressed -A "$UA" -H 'Accept: text/html,application/xhtml+xml,*/*;q=0.8' \
         -H 'Accept-Language: ja' -o /tmp/claude-0/kansi_body.html \
         -w '%{http_version}\t%{http_code}\t%{content_type}\t%{size_download}' \
         https://www.ishinazaka.co.jp/)
    HEAD=$(head -c 15 /tmp/claude-0/kansi_body.html | tr -d '\n')
    END=$(tail -c 8 /tmp/claude-0/kansi_body.html | tr -d '\n')
    echo -e "$(date +%H:%M:%S)\t$i\t$R\t$HEAD\t$END" >> $OUT
  done
  sleep 1
done
echo 終わり
