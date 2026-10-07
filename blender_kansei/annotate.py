# -*- coding: utf-8 -*-
"""
レンダリング画像に測点の注記を描き込む（Pillow を使用）

  python annotate.py stills   … renders/*.png に測点ラベルを描いて renders/annotated/ に保存
  python annotate.py video    … renders/video/f_####.png に測点と「現在の測点」を描いて
                                 renders/video_annotated/ に保存

座標は futagosawa_kansei.py が書き出す *_stations.json / stations.json を使う。
"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]
S_END = 190.07

DARK = (31, 42, 46)
LIGHT = (244, 242, 236)
ORANGE = (224, 122, 31)


def font(size):
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def draw_labels(img, points, max_dist=400.0):
    w = img.width
    k = w / 960.0
    d = ImageDraw.Draw(img, "RGBA")
    f = font(int(15 * k))
    placed = []
    # 近いものから順に置き、重なるラベルは省く
    for p in sorted(points, key=lambda q: q["dist"]):
        if p["dist"] > max_dist:
            continue
        x, y = p["x"], p["y"]
        lead = 34 * k
        tw = d.textlength(p["label"], font=f)
        pad = 5 * k
        box = (x - tw / 2 - pad, y - lead - 15 * k - 2 * pad, x + tw / 2 + pad, y - lead)
        if box[1] < 0 or box[0] < 0 or box[2] > w:
            continue
        if any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in placed):
            continue
        placed.append(box)
        bg = ORANGE + (235,) if p["key"] else LIGHT + (235,)
        d.line((x, y, x, y - lead), fill=DARK + (220,), width=max(1, int(2 * k)))
        r = 3.5 * k
        d.ellipse((x - r, y - r, x + r, y + r), fill=(200, 30, 20, 255), outline=LIGHT + (255,))
        d.rounded_rectangle(box, radius=4 * k, fill=bg, outline=DARK + (200,), width=max(1, int(k)))
        d.text((box[0] + pad, box[1] + pad - 1 * k), p["label"], font=f, fill=DARK)


def draw_hud(img, data, title, reverse=False, s0=0.0, s1=None, start_name="起点"):
    k = img.width / 960.0
    d = ImageDraw.Draw(img, "RGBA")
    big, small = font(int(26 * k)), font(int(13 * k))
    x0, y0 = 20 * k, 18 * k
    s = data.get("drive_s")
    S_END = (s1 - s0) if s1 is not None else globals()["S_END"]
    if s is not None:
        s = s - s0
    if s is None:
        tf = font(int(22 * k))
        tw = max(300 * k, d.textlength(title, font=tf) + 28 * k)
        d.rounded_rectangle((x0, y0, x0 + tw, y0 + 46 * k), radius=6 * k, fill=DARK + (200,))
        d.text((x0 + 14 * k, y0 + 8 * k), title, font=tf, fill=LIGHT)
        return
    if reverse:      # BC-10（終点）→ NO.50（起点）
        if s < 0:
            name, sub = "起点通過", f"施工延長 {S_END:.2f}m"
        elif s >= S_END - 0.05:
            name, sub = "BC-10（終点）", "ここから NO.50 へ"
        else:
            name, sub = data["drive_name"], f"BC-10から {S_END - s:.0f}m ／ {S_END:.0f}m"
    elif s < 0:
        name, sub = "起点手前", f"起点まで {-s:.0f}m"
    elif s > S_END:
        name, sub = "終点通過", f"施工延長 {S_END:.2f}m"
    else:
        name, sub = data["drive_name"], f"{start_name}から {s:.0f}m ／ {S_END:.0f}m"
    wbox = 300 * k
    d.rounded_rectangle((x0, y0, x0 + wbox, y0 + 94 * k), radius=6 * k, fill=DARK + (205,))
    d.text((x0 + 14 * k, y0 + 8 * k), "現在の測点", font=small, fill=(242, 166, 90))
    d.text((x0 + 14 * k, y0 + 24 * k), name, font=big, fill=LIGHT)
    d.text((x0 + 14 * k, y0 + 58 * k), sub, font=small, fill=(217, 222, 216))
    # 進み具合のバー
    bx0, bx1, by = x0 + 14 * k, x0 + wbox - 14 * k, y0 + 80 * k
    d.rounded_rectangle((bx0, by, bx1, by + 6 * k), radius=3 * k, fill=(90, 100, 104, 255))
    u = max(0.0, min(1.0, (S_END - s if reverse else s) / S_END))
    d.rounded_rectangle((bx0, by, bx0 + (bx1 - bx0) * u, by + 6 * k), radius=3 * k, fill=ORANGE + (255,))


def stills():
    outdir = os.path.join(HERE, "renders", "annotated")
    os.makedirs(outdir, exist_ok=True)
    for js in glob.glob(os.path.join(HERE, "renders", "*_stations.json")):
        png = js.replace("_stations.json", ".png")
        if not os.path.exists(png):
            continue
        data = json.load(open(js, encoding="utf-8"))
        img = Image.open(png).convert("RGB")
        draw_labels(img, data["points"])
        img.save(os.path.join(outdir, os.path.basename(png)))
        print("saved", os.path.basename(png))


def video(reverse=False, tag=""):
    name = ("video_rev" if reverse else "video") + tag
    src = os.path.join(HERE, "renders", name)
    outdir = os.path.join(HERE, "renders", name + "_annotated")
    os.makedirs(outdir, exist_ok=True)
    data = json.load(open(os.path.join(src, "stations.json"), encoding="utf-8"))
    for f, fd in data.items():
        png = os.path.join(src, f"f_{int(f):04d}.png")
        if not os.path.exists(png):
            continue
        img = Image.open(png).convert("RGB")
        driving = fd.get("drive_s") is not None
        # 走行中は近くの測点だけ（遠い注記は画面がうるさくなる）
        draw_labels(img, fd["points"], max_dist=70.0 if (driving and not tag) else 400.0)
        draw_hud(img, fd, "市道二子沢線　完成イメージ", reverse)
        img.save(os.path.join(outdir, os.path.basename(png)))
    print("annotated", len(data), "frames")


if __name__ == "__main__":
    {"stills": stills, "video": video, "video_rev": lambda: video(reverse=True),
     "video_rev_drone": lambda: video(reverse=True, tag="_drone")}[
        sys.argv[1] if len(sys.argv) > 1 else "stills"]()
