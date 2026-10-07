# -*- coding: utf-8 -*-
"""
測点注記を描き込む
  python annotate_sites.py              … renders/<site>/*.png → renders/<site>/annotated/
  python annotate_sites.py video <site> … renders/<site>/video/f_####.png → renders/<site>/video_annotated/
"""
import glob
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from annotate import draw_labels, draw_hud  # noqa: E402


def stills():
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


def video(site):
    src = os.path.join(HERE, "renders", site, "video")
    out = os.path.join(HERE, "renders", site, "video_annotated")
    os.makedirs(out, exist_ok=True)
    js = json.load(open(os.path.join(src, "stations.json"), encoding="utf-8"))
    meta = js["meta"]
    n = 0
    for f, fd in js["frames"].items():
        png = os.path.join(src, f"f_{int(f):04d}.png")
        if not os.path.exists(png):
            continue
        img = Image.open(png).convert("RGB")
        driving = fd.get("drive_s") is not None
        draw_labels(img, fd["points"], max_dist=60.0 if driving else 400.0)
        draw_hud(img, fd, meta["title"], s0=meta["s0"], s1=meta["s1"], start_name="施工起点")
        img.save(os.path.join(out, os.path.basename(png)))
        n += 1
    print("annotated", n, "frames")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "video":
        video(sys.argv[2])
    else:
        stills()
