# -*- coding: utf-8 -*-
u"""Googleの見通しを戻す。英語原文で "by the end of this decade" を確認できたため。
   naoshi_a.py と同じ約束で動く。"""
import os
import naoshi_a as base

NAOSHI_E = [
 (4, u'E-1 Googleの見通しを戻す（本文）',
  u'<li>IBMは、大規模で誤りに強い機械の実現目標として<strong>2029年</strong>を掲げています'
  u'（目標であって、確定した予定ではありません）</li>',
  u'<li>IBMは、大規模で誤りに強い機械の実現目標として<strong>2029年</strong>を掲げています。'
  u'Googleも、超電導方式で「商用に意味のある」機械が<strong>2020年代の終わり</strong>までに'
  u'使えるようになるとしています（どちらも目標であって、確定した予定ではありません）</li>', 1),
 (4, u'E-1 Googleの見通しを戻す（図版）',
  u'>IBMの目標</text>', u'>IBM・Googleの目標</text>', 1),
 (4, u'E-1 Googleの見通しを戻す（図版の説明文）',
  u'実用化の見通しは、IBMの目標が2029年、',
  u'実用化の見通しは、IBMの目標が2029年でGoogleも2020年代の終わり、', 1),
 (4, u'E-2 Googleの記事名を実際の見出しに',
  u'<li>Google「Google Quantum AI to include neutral atom computing」（中性原子方式への拡大）<br>',
  u'<li>Google「Building superconducting and neutral atom quantum computers」2026年3月24日'
  u'（中性原子方式への拡大。超電導方式は「2020年代の終わりまでに商用に意味のあるものになる」との見通し）<br>', 1),
]

base.NAOSHI = NAOSHI_E

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    base.main()
