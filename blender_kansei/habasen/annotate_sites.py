# -*- coding: utf-8 -*-
"""renders/<site>/*.png に測点注記を描き、renders/<site>/annotated/ に保存する"""
import glob
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from annotate import draw_labels  # noqa: E402

for js in sorted(glob.glob(os.path.join(HERE, "renders", "*", "*_stations.json"))):
    png = js.replace("_stations.json", ".png")
    if not os.path.exists(png):
        continue
    out = os.path.join(os.path.dirname(png), "annotated")
    os.makedirs(out, exist_ok=True)
    img = Image.open(png).convert("RGB")
    draw_labels(img, json.load(open(js, encoding="utf-8"))["points"])
    img.save(os.path.join(out, os.path.basename(png)))
    print("saved", os.path.relpath(os.path.join(out, os.path.basename(png)), HERE))
