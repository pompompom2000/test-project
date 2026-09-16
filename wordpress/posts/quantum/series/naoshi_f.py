# -*- coding: utf-8 -*-
u"""③ 見通しの図に、ムーンショットの2030年の中間目標を反映する。
   本文の一覧には足したのに図に無く、両者が食い違っていた。
   2030年は2029年の目盛りのすぐ隣になるため、目盛りは増やさず
   ムーンショットの注記に添える。"""
import os
import naoshi_a as base

base.NAOSHI = [
 (4, u'F-1 図版にムーンショットの2030年',
  u'<text x="530" y="182" text-anchor="middle" font-size="11.5" fill="currentColor" opacity="0.7">'
  u'誤りに強い汎用の機械の実現</text>',
  u'<text x="530" y="182" text-anchor="middle" font-size="11.5" fill="currentColor" opacity="0.7">'
  u'誤りに強い汎用の機械。2030年に中間目標</text>', 1),
 (4, u'F-2 図版の説明文にも2030年',
  u'国の研究目標ムーンショットが2050年、そして',
  u'国の研究目標ムーンショットが2050年で2030年に中間目標、そして', 1),
]

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    base.main()
