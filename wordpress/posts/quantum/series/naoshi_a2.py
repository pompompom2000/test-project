# -*- coding: utf-8 -*-
u"""出典確認Aの残り2件（第3回のIBM 133量子ビット、第4回の2029年）を直す。

  naoshi_a.py と同じ約束で動く。
  ・鍵は環境変数 IZK_AUTH からしか読まない。標準出力にも出さない。
  ・--apply と --yes の両方がなければ、何も書き込まない。
  ・置き換えは出現数を数え、合わなければ中止する。
  ・書き込んだあと、必ず読み返して確かめる。
"""
import os, sys, io
import naoshi_a as base

# 第3回の出典リストの最後（QuEraの項目）。ここの直前に足す
ANCHOR3 = (u'<li>QuEra「Quantum Interference」「Grover\'s Algorithm」「Dilution Refrigerator」'
           u'（干渉、探索、冷凍機）<br><a href="https://www.quera.com/glossary/quantum-interference">'
           u'https://www.quera.com/glossary/quantum-interference</a></li>\n'
           u'<!-- /wp:list-item -->\n</ul>')

SOE3 = (u'<li>QuEra「Quantum Interference」「Grover\'s Algorithm」「Dilution Refrigerator」'
        u'（干渉、探索、冷凍機）<br><a href="https://www.quera.com/glossary/quantum-interference">'
        u'https://www.quera.com/glossary/quantum-interference</a></li>\n'
        u'<!-- /wp:list-item -->\n'
        u'<!-- wp:list-item -->\n'
        u'<li>Willsch ほか「The State of Factoring on Quantum Computers」'
        u'（IBMが1,121量子ビットのQPUを製造した旨の記載。原典は D. Castelvecchi, Nature 624, 238 (2023)）'
        u'<br><a href="https://arxiv.org/html/2410.14397v1">https://arxiv.org/html/2410.14397v1</a></li>\n'
        u'<!-- /wp:list-item -->\n'
        u'<!-- wp:list-item -->\n'
        u'<li>IBM Quantum「Hardware」（現行機はHeron 133・156量子ビット、Nighthawk 120量子ビット）'
        u'<br><a href="https://www.ibm.com/quantum/hardware">https://www.ibm.com/quantum/hardware</a></li>\n'
        u'<!-- /wp:list-item -->\n</ul>')

ANCHOR4 = (u'<li>IEEE Spectrum「The Case Against Quantum Computing」（実現への反対論）<br>'
           u'<a href="https://spectrum.ieee.org/the-case-against-quantum-computing">'
           u'https://spectrum.ieee.org/the-case-against-quantum-computing</a></li>\n'
           u'<!-- /wp:list-item -->\n</ul>')

SOE4 = (u'<li>IEEE Spectrum「The Case Against Quantum Computing」（実現への反対論）<br>'
        u'<a href="https://spectrum.ieee.org/the-case-against-quantum-computing">'
        u'https://spectrum.ieee.org/the-case-against-quantum-computing</a></li>\n'
        u'<!-- /wp:list-item -->\n'
        u'<!-- wp:list-item -->\n'
        u'<li>IBM Quantum「Hardware」（耐障害性の機械 Starling を2029年の稼働目標として開発中）<br>'
        u'<a href="https://www.ibm.com/quantum/hardware">https://www.ibm.com/quantum/hardware</a></li>\n'
        u'<!-- /wp:list-item -->\n</ul>')

NAOSHI2 = [
 # ---- 第3回：主力は133個ではなく、いまは120〜156個 ----
 (3, u'A-3 IBMの主力機（本文）',
  u'それを示す出来事があります。IBMは2023年に1,121量子ビットの機械を発表しましたが、その後、'
  u'<strong>133量子ビットの機械を主力に切り替えました。</strong>'
  u'数を減らしたのに、性能は上がっています。数ではなく質に舵を切ったのです。',
  u'それを示す出来事があります。IBMは2023年に1,121量子ビットの機械を発表しました。ところが、'
  u'いま同社が主力に据えているのは<strong>120個から156個の機械です。</strong>'
  u'数を減らしたのに、性能は上がっています。数ではなく質に舵を切ったのです。', 1),
 (3, u'A-3 IBMの主力機（図版）',
  u'IBMは1,121個の機械から、133個の機械に主力を移しました',
  u'IBMは1,121個の機械から、120〜156個の機械に主力を移しました', 1),
 (3, u'A-3 出典を2本追加', ANCHOR3, SOE3, 1),

 # ---- 第4回：2029年はIBMの目標。Googleの2029年は裏づけが取れていない ----
 (4, u'A-7 2029年はIBMの目標（本文）',
  u'<li>IBMとGoogleは、<strong>2029年</strong>を自社の目標に掲げています'
  u'（目標であって、確定した予定ではありません）</li>',
  u'<li>IBMは、大規模で誤りに強い機械の実現目標として<strong>2029年</strong>を掲げています'
  u'（目標であって、確定した予定ではありません）</li>', 1),
 (4, u'A-7 2029年はIBMの目標（図版）',
  u'>IBM・Googleの目標</text>', u'>IBMの目標</text>', 1),
 (4, u'A-7 2029年はIBMの目標（図版の説明文）',
  u'実用化の見通しは、IBMとGoogleの目標が2029年',
  u'実用化の見通しは、IBMの目標が2029年', 1),
 (4, u'A-7 出典を1本追加', ANCHOR4, SOE4, 1),
]

base.NAOSHI = NAOSHI2

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    base.main()
