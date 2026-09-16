# -*- coding: utf-8 -*-
u"""Aの積み残し。第5回の分野ごとの表にも「15と21」が残っていた。"""
import os
import naoshi_a as base
base.NAOSHI = [
 (5, u'A-11 35以下（第5回の表）',
  u'ただし<strong>実機で分解できた最大の数は15と21</strong>',
  u'ただし<strong>実機で分解できたのは35以下のごく小さな数</strong>', 1),
]
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    base.main()
