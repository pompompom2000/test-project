# -*- coding: utf-8 -*-
u"""出典確認Bの直し（出典欄の精度）。naoshi_a.py と同じ約束で動く。"""
import os
import naoshi_a as base

FEY_MAE = (u'<li>R.P.Feynman「Simulating Physics with Computers」（1981年の講演。量子コンピュータの着想）'
           u'<br><a href="https://www.wisdom.weizmann.ac.il/~naor/COURSE/feynman-simulating.pdf">'
           u'https://www.wisdom.weizmann.ac.il/~naor/COURSE/feynman-simulating.pdf</a></li>')

FEY_ATO = (u'<li>R. P. Feynman「Simulating Physics with Computers」'
           u'International Journal of Theoretical Physics 21, 467-488 (1982)'
           u'（1981年にMITで開かれた第1回 Physics and Computation 会議での講演にもとづく論文。'
           u'量子コンピュータの着想）<br>'
           u'※下記はワイツマン科学研究所の講義資料で、論文そのものではなく内容を紹介したものです<br>'
           u'<a href="https://www.wisdom.weizmann.ac.il/~naor/COURSE/feynman-simulating.pdf">'
           u'https://www.wisdom.weizmann.ac.il/~naor/COURSE/feynman-simulating.pdf</a></li>')

BOJ_MAE = (u'<li>日本銀行（同ステートメント）<br>'
           u'<a href="https://www.boj.or.jp/intl_finance/meeting/group/gro240926a.htm">'
           u'https://www.boj.or.jp/intl_finance/meeting/group/gro240926a.htm</a></li>')

BOJ_ATO = (u'<li>日本銀行（同ステートメント。2024年9月25日付の文書を、9月26日に公表）<br>'
           u'<a href="https://www.boj.or.jp/intl_finance/meeting/group/gro240926a.htm">'
           u'https://www.boj.or.jp/intl_finance/meeting/group/gro240926a.htm</a></li>\n'
           u'<!-- /wp:list-item -->\n'
           u'<!-- wp:list-item -->\n'
           u'<li>同ステートメントの日本語仮訳（PDF。「いま盗んで、あとで読む」の記述はこの本文にあります）<br>'
           u'<a href="https://www.boj.or.jp/intl_finance/meeting/group/data/gro240926a.pdf">'
           u'https://www.boj.or.jp/intl_finance/meeting/group/data/gro240926a.pdf</a></li>')

NAOSHI_B = [
 # B-12 ファインマンの出典を原典の書誌に。リンク先が講義資料であることも明記する
 (5, u'B-12 ファインマンの出典', FEY_MAE, FEY_ATO, 1),

 # B-13 中間とりまとめの表紙は「令和7年11月」。日は書かれていない
 (6, u'B-13 内閣官房の日付（本文）',
  u'そして2025年11月20日、内閣官房の国家サイバー統括室が、',
  u'そして2025年11月、内閣官房の国家サイバー統括室が、', 1),
 (6, u'B-13 内閣官房の日付（出典）',
  u'（中間とりまとめ）」2025年11月20日<br>',
  u'（中間とりまとめ）」2025年11月<br>', 1),

 # B-14 G7ステートメントの仮訳PDFを出典に足す
 (6, u'B-14 G7の仮訳PDFを追加', BOJ_MAE, BOJ_ATO, 1),
]

base.NAOSHI = NAOSHI_B

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    base.main()
