# -*- coding: utf-8 -*-
"""
市道羽場線外２路線道路改良工事　完成イメージ（Blender ベースモデル）

  3つの施工箇所を1本のスクリプトで作る
    --site=haba    市道羽場線（NO.0〜NO.4+13.00、L=93m、幅員6.5m・両側皿型側溝）
    --site=yuden   市道油田線（NO.21+15.45〜NO.25+2.50、歩道2.2m新設・L型擁壁・転落防止柵）
    --site=doumae  堂の前踏切（JR山田線 単線、交差角67°、歩道2.0m・遮断機・±7.5%の坂）

使い方
  Blender 4.x → Scripting タブ → このファイルを開き、下の SITE を変えて ▶ Run Script
  コマンドライン:
    blender -b -P habasen_kansei.py -- --site=doumae --render [--fast] [--save]

値は図面（08-01〜08-03）と工事数量総括表から読み取ったもの。
周辺の建物・樹木・地形は図面の記号を参考にした「それらしい形」で、測量データではない。
"""
import bpy
import math
import os
import random
import sys
import json
from mathutils import Vector, noise

SITE = "doumae"          # Blender の画面から実行するときはここを変える

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()


# =================================================================
# 1. 線形エンジン（直線・円曲線をつなぐ平面線形、縦断は計画高の折れ線）
# =================================================================
class Alignment:
    def __init__(self, s0, elems, heading_deg=0.0):
        """elems = [("line", L), ("arc", L, R, +1=左/-1=右), ...]"""
        self.segs = []
        x, y, h, s = 0.0, 0.0, math.radians(heading_deg), s0
        for e in elems:
            if e[0] == "line":
                self.segs.append((s, e[1], 0.0, x, y, h))
                x += e[1] * math.cos(h)
                y += e[1] * math.sin(h)
            else:
                k = e[3] / e[2]
                self.segs.append((s, e[1], k, x, y, h))
                h2 = h + k * e[1]
                x += (math.sin(h2) - math.sin(h)) / k
                y -= (math.cos(h2) - math.cos(h)) / k
                h = h2
            s += e[1]
        self.s0, self.s1 = s0, s
        self.end = (x, y, h)

    def plan(self, s):
        if s < self.s0:
            _, _, _, x, y, h = self.segs[0]
            u = s - self.s0
            return x + u * math.cos(h), y + u * math.sin(h), h
        for (ss, L, k, x, y, h) in self.segs:
            if s <= ss + L:
                u = s - ss
                if k == 0:
                    return x + u * math.cos(h), y + u * math.sin(h), h
                h2 = h + k * u
                return x + (math.sin(h2) - math.sin(h)) / k, y - (math.cos(h2) - math.cos(h)) / k, h2
        x, y, h = self.end
        u = s - self.s1
        return x + u * math.cos(h), y + u * math.sin(h), h


def interp(table, s):
    """[(s, v), ...] の折れ線補間（両端は端の勾配で延長）"""
    if s <= table[0][0]:
        (a, va), (b, vb) = table[0], table[1]
    elif s >= table[-1][0]:
        (a, va), (b, vb) = table[-2], table[-1]
    else:
        for i in range(len(table) - 1):
            if table[i][0] <= s <= table[i + 1][0]:
                (a, va), (b, vb) = table[i], table[i + 1]
                break
    return va + (vb - va) * (s - a) / (b - a)


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def sta(no, plus=0.0):
    return no * 20.0 + plus


def sta_name(s):
    n = int(math.floor(s / 20.0 + 1e-9))
    p = s - n * 20.0
    return f"NO.{n}" + (f"+{p:.1f}" if p >= 0.05 else "")


# =================================================================
# 2. 施工箇所の設定
# =================================================================
class Site:
    name = ""
    base_el = 0.0
    s_range = (0, 100)          # 地形を作る範囲
    work = (0, 100)             # 施工範囲（新しい舗装）
    d_half = 60.0

    def zc(self, s):
        return interp(self.fh, s) - self.base_el

    def point(self, s, d, h=0.0):
        x, y, a = self.al.plan(s)
        return Vector((x - math.sin(a) * d, y + math.cos(a) * d, self.zc(s) + h))

    def ground(self, s, d):
        return -0.3


# ---------------------------------------------------------------- 羽場線
class Haba(Site):
    name = "市道羽場線"
    title = "市道羽場線　道路改良工事"
    base_el = 135.6
    s_range = (-45, 150)
    work = (0.0, 93.0)
    d_half = 70.0
    # 図面では R=650 の大きな曲線（ほぼ直線）。BC1 NO.-1-18.4 → EC1 NO.1+14.046
    al = Alignment(-38.4, [("arc", 72.446, 650.0, -1), ("line", 400.0)], heading_deg=0)
    fh = [(-38.4, 135.55), (0.0, 135.630), (20.0, 135.690), (40.0, 135.750), (60.0, 135.826),
          (64.0, 135.850), (80.0, 135.971), (100.0, 136.156), (120.0, 136.342), (160.0, 136.86)]
    gh = [(-38.4, 134.59), (-20, 134.89), (0, 135.53), (20, 135.43), (40, 135.60),
          (60, 135.75), (80, 135.90), (100, 136.10), (160, 136.80)]
    half = 2.75                  # 車道 5.5m
    ditch = 0.5

    def ground(self, s, d):
        a = abs(d)
        g = interp(self.gh, s) - self.base_el - self.zc(s)       # 現況地盤（道路からの高さ）
        g = min(g, -0.12)
        if a < self.half + self.ditch:
            return -0.6
        # 側溝の外 1:1.0 で現況へすり付け
        return max(g, -0.06 - (a - self.half - self.ditch) * 1.0) if a < 6 else g + noise.noise(Vector((s * .05, d * .05, 1))) * 0.15

    def stations(self):
        out = [(sta(n), f"NO.{n}", False) for n in range(0, 5)]
        out[0] = (0.0, "NO.0 起点", True)
        out += [(93.0, "NO.4+13 終点", True), (34.046, "EC1", True)]
        return out


# ---------------------------------------------------------------- 油田線
class Yuden(Site):
    name = "市道油田線"
    title = "市道油田線　歩道設置"
    base_el = 176.0
    s_range = (400, 545)
    work = (sta(21, 15.45), sta(25, 2.5))
    d_half = 60.0
    al = Alignment(380, [("line", 300)], heading_deg=20)
    # 側溝天端（歩道側の車道端）計画高。中心はこれ +0.07
    edge = [(sta(21, 15.45), 175.960), (sta(22), 176.147), (sta(22, 10), 176.557), (sta(23), 176.967),
            (sta(23, 10), 177.377), (sta(24), 177.801), (sta(24, 10), 178.272), (sta(25), 178.793),
            (sta(25, 2.5), 178.930), (sta(25, 22.5), 180.10)]
    fh = [(s, v + 0.07) for s, v in edge]
    paddy = 176.80
    half = 3.5

    def walk_in(self):
        return self.half + 0.18          # 歩道内側（縁石外面）

    def walk_out(self):
        return self.half + 0.18 + 2.0 + 0.3

    def wall_zone(self, s):
        return smooth(sta(23, 15.0), sta(23, 18.0), s) * (1 - smooth(sta(25, 0.5), sta(25, 3.5), s))

    def ground(self, s, d):
        if d > 0:   # 北：歩道 → 盛土法 or 擁壁 → 田
            wo = self.walk_out()
            if self.wall_zone(s) > 0.5 and d > self.walk_in():
                return self.paddy - self.base_el - self.zc(s) - 0.02     # 擁壁の裏は田面（崖は擁壁で隠れる）
            if d < wo:
                return -0.6
            top = 0.10
            paddy = self.paddy - self.base_el - self.zc(s)
            drop = top - paddy
            run = max(drop, 0.0) * 1.5
            slope = top - (d - wo) / max(run, 0.01) * drop if d < wo + run else paddy
            wall = paddy if d > wo + 0.05 else top
            h = slope + (wall - slope) * self.wall_zone(s)
            return max(h, paddy) if d > wo + 0.05 else h
        # 南：既設U型側溝 → 切土斜面で台地へ
        a = -d
        if a < self.half + 0.3:
            return -0.6
        rise = min((a - self.half - 0.3) * 0.8, 2.6) + max(0, a - 7.5) * 0.04
        for c in (sta(22, 0), sta(25, 0)):      # 南へ上る脇道
            w = 1 - smooth(2.5, 5.0, abs(s - c))
            rise = rise * (1 - w) + (0.12 * (a - 3.8)) * w
        return -0.07 + rise + noise.noise(Vector((s * .04, a * .06, 2))) * 0.3 * smooth(9, 20, a)

    def stations(self):
        out = [(sta(n), f"NO.{n}", False) for n in range(22, 26)]
        out += [(self.work[0], "NO.21+15.45 起点", True), (self.work[1], "NO.25+2.5 終点", True)]
        return out


# ---------------------------------------------------------------- 堂の前踏切
class Doumae(Site):
    name = "堂の前踏切"
    title = "堂の前踏切　歩道設置・線形改良"
    base_el = 128.0
    s_range = (-25, 120)
    work = (12.2, 76.05)
    d_half = 55.0
    # BP→直線8.0→R20左→直線→R25右→直線（踏切）→R110右→直線
    al = Alignment(0.0, [("line", 8.0), ("arc", 12.025, 20.0, +1), ("line", 1.486),
                         ("arc", 19.220, 25.0, -1), ("line", 13.611), ("arc", 37.822, 110.0, -1),
                         ("line", 60.0)], heading_deg=0)
    fh = [(0.0, 128.15), (7.0, 128.176), (8.0, 128.180), (13.873, 128.246), (20.0, 128.443), (20.841, 128.481),
          (25.432, 128.730), (31.121, 129.134), (31.439, 129.157), (35.0, 129.424), (37.478, 129.610),
          (40.0, 129.799), (40.782, 129.858), (44.645, 130.139), (46.853, 130.059), (54.202, 129.509),
          (56.803, 129.314), (60.0, 129.083), (67.047, 128.644), (73.355, 128.336), (77.156, 128.187),
          (95.0, 127.75), (120.0, 127.6)]
    gh = [(-25, 128.1), (0, 128.14), (30, 128.7), (45.7, 129.3), (60, 128.9), (80, 128.0), (95, 127.59), (120, 127.5)]
    cross_s = 45.726           # 踏切中心（山田線交差）
    cross_ang = 67.0           # 交差角
    half = 2.5                 # 車道 5.0m

    def strip(self, s):
        """歩道と車道の間の幅（踏切部は施設帯 1.2m）"""
        return 0.2 + 1.0 * (1 - smooth(5.0, 12.0, abs(s - self.cross_s)))

    def walk(self, s):
        wi = self.half + self.strip(s)
        on = smooth(8.0, 13.0, s) * (1 - smooth(78.0, 84.0, s))   # 歩道は施工区間＋すり付け
        return wi, wi + 2.0 * on

    def rail_dir(self):
        x, y, a = self.al.plan(self.cross_s)
        r = a + math.radians(self.cross_ang)
        return Vector((math.cos(r), math.sin(r), 0))

    def rail_dist(self, P):
        c = self.point(self.cross_s, 0, 0)
        v = Vector((P.x - c.x, P.y - c.y, 0))
        t = self.rail_dir()
        return abs(v.x * t.y - v.y * t.x), v.x * t.x + v.y * t.y

    def ground(self, s, d):
        wi, wo = self.walk(s)
        g = interp(self.gh, s) - self.base_el - self.zc(s)
        if d > wi and 49.0 < s < 73.5 and g < -0.4:
            return g                    # L型擁壁の外は現況地盤（崖は擁壁で隠れる）
        if -self.half - 0.6 < d < wo + 0.1:
            return -0.6
        a = (d - wo) if d > 0 else (-d - self.half - 0.6)
        # 擁壁（北側 NO.2+9.07〜NO.3+13.355）は垂直に落とし、それ以外は 1:1.5
        wall = smooth(48.0, 50.0, s) * (1 - smooth(72.5, 74.5, s)) if d > 0 else 0.0
        top = -0.05
        if g < top:
            h = max(g, top - a / 1.5)
            h = h * (1 - wall) + (g if a > 0.05 else top) * wall
        else:
            h = min(g, top + a * 0.6)
        # 線路の盛土（施工基面）
        P = self.point(s, d, 0)
        dist, _ = self.rail_dist(P)
        rail_top = self.zc(self.cross_s) + 0.02
        bed = rail_top - 0.57 - (self.zc(s) - 0)
        w = 1 - smooth(2.8, 5.5, dist)
        h = h * (1 - w) + bed * w
        return h

    def stations(self):
        out = [(sta(n), f"NO.{n}", False) for n in range(1, 5)]
        out += [(self.cross_s, "踏切 NO.2+5.7", True), (12.2, "施工起点", True), (76.05, "施工終点", True)]
        return out


SITES = {"haba": Haba(), "yuden": Yuden(), "doumae": Doumae()}


# =================================================================
# 3. Blender ユーティリティ
# =================================================================
def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
        for b in list(blocks):
            if b.users == 0:
                blocks.remove(b)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


def link(ob, c):
    for x in ob.users_collection:
        x.objects.unlink(ob)
    c.objects.link(ob)
    return ob


def mesh(name, verts, faces, mat, c, smooth_shade=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    if smooth_shade:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    c.objects.link(ob)
    return ob


def sweep(S, name, s0, s1, prof, mat, c, step=0.5, closed=False):
    """prof = [(d, h), ...] または s を受け取って [(d, h)...] を返す関数"""
    n = max(2, int(math.ceil((s1 - s0) / step)) + 1)
    verts, faces = [], []
    m = None
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1)
        pr = prof(s) if callable(prof) else prof
        m = len(pr)
        for d, h in pr:
            verts.append(S.point(s, d, h))
    segs = m if closed else m - 1
    for i in range(n - 1):
        for j in range(segs):
            j2 = (j + 1) % m
            a, b = i * m + j, i * m + j2
            faces.append((a, b, b + m, a + m))
    if closed:
        faces.append(tuple(range(m - 1, -1, -1)))
        faces.append(tuple((n - 1) * m + j for j in range(m)))
    return mesh(name, verts, faces, mat, c)


def box(name, center, size, yaw, mat, c, pitch=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.rotation_euler = (0.0, -pitch, yaw)
    ob.location = center
    ob.data.materials.append(mat)
    return link(ob, c)


def cyl(name, p, r, h, mat, c, verts=12, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=p, vertices=verts, rotation=rot)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return link(ob, c)


def material(name, color, rough=0.6, nscale=0.0, color2=None, metallic=0.0, alpha=1.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        b.inputs["Transmission Weight"].default_value = 0.6
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    if nscale and color2:
        t = nt.nodes.new("ShaderNodeTexNoise")
        t.inputs["Scale"].default_value = nscale
        t.inputs["Detail"].default_value = 8
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].color = (*color, 1)
        r.color_ramp.elements[1].color = (*color2, 1)
        nt.links.new(t.outputs["Fac"], r.inputs["Fac"])
        nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    return m


def mat_terrain(flat, slope):
    m = bpy.data.materials.new("地形")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = 0.95
    g = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(g.outputs["Normal"], sp.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position = 0.75
    r.color_ramp.elements[0].color = (*slope, 1)
    r.color_ramp.elements[1].position = 0.92
    r.color_ramp.elements[1].color = (*flat, 1)
    nt.links.new(sp.outputs["Z"], r.inputs["Fac"])
    t = nt.nodes.new("ShaderNodeTexNoise")
    t.inputs["Scale"].default_value = 2.0
    t.inputs["Detail"].default_value = 10
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = "RGBA"
    mx.blend_type = "MULTIPLY"
    mx.inputs["Factor"].default_value = 0.3
    nt.links.new(r.outputs["Color"], mx.inputs[6])
    nt.links.new(t.outputs["Color"], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m


def mats():
    return {
        "asp_new": material("舗装（新設）", (0.04, 0.04, 0.045), 0.75, 60, (0.08, 0.08, 0.08)),
        "asp_old": material("舗装（既設）", (0.16, 0.16, 0.15), 0.85, 40, (0.23, 0.22, 0.21)),
        "asp_walk": material("歩道舗装", (0.13, 0.12, 0.12), 0.85, 50, (0.18, 0.17, 0.16)),
        "line": material("区画線（白）", (0.85, 0.85, 0.82), 0.5),
        "yellow": material("黄色", (0.85, 0.65, 0.05), 0.5),
        "conc": material("コンクリート", (0.55, 0.55, 0.52), 0.8, 25, (0.65, 0.64, 0.60)),
        "dark": material("開口部", (0.02, 0.02, 0.02), 1.0),
        "steel": material("鋼材", (0.75, 0.75, 0.74), 0.35, metallic=0.6),
        "white": material("白塗装", (0.88, 0.88, 0.86), 0.4),
        "brown": material("茶塗装", (0.25, 0.17, 0.10), 0.5),
        "red": material("赤", (0.65, 0.03, 0.02), 0.4),
        "black": material("黒", (0.03, 0.03, 0.03), 0.5),
        "amber": material("反射体", (1.0, 0.45, 0.0), 0.2),
        "gravel": material("砂利", (0.40, 0.37, 0.33), 0.95, 80, (0.55, 0.52, 0.47)),
        "ballast": material("バラスト", (0.30, 0.29, 0.28), 0.95, 120, (0.48, 0.46, 0.44)),
        "sleeper": material("PCまくらぎ", (0.50, 0.49, 0.46), 0.8),
        "rail": material("レール", (0.35, 0.30, 0.27), 0.3, metallic=0.8),
        "panel": material("踏切舗装版", (0.25, 0.25, 0.26), 0.8, 30, (0.32, 0.32, 0.33)),
        "water": material("水", (0.10, 0.16, 0.15), 0.05),
        "paddy": material("田（稲刈り後）", (0.22, 0.19, 0.10), 0.95, 6, (0.32, 0.28, 0.14)),
        "wall": material("外壁", (0.82, 0.80, 0.74), 0.8),
        "wall2": material("外壁2", (0.70, 0.72, 0.74), 0.8),
        "roof": material("屋根", (0.22, 0.25, 0.30), 0.6),
        "roof2": material("屋根2", (0.45, 0.18, 0.12), 0.6),
        "glass": material("ガラス", (0.15, 0.2, 0.25), 0.1),
        "vinyl": material("ビニールハウス", (0.85, 0.88, 0.88), 0.2, alpha=0.5),
        "leaf": material("葉", (0.10, 0.25, 0.06), 0.9, 4, (0.20, 0.33, 0.08)),
        "apple": material("りんごの木", (0.14, 0.30, 0.07), 0.9, 5, (0.25, 0.38, 0.10)),
        "trunk": material("幹", (0.15, 0.09, 0.05), 0.9),
        "lamp": material("照明", (1.0, 0.95, 0.85), 0.3, emit=3.0),
        "redlamp": material("警報灯", (0.9, 0.05, 0.03), 0.3),
        "pole": material("電柱", (0.38, 0.38, 0.37), 0.8),
    }


def house(name, c, M, p, yaw, w=8.0, dpt=7.0, h=5.5, roof="roof", wallm="wall"):
    box(name + "_壁", p + Vector((0, 0, h / 2)), (w, dpt, h), yaw, M[wallm], c)
    # 切妻屋根
    ca, sa = math.cos(yaw), math.sin(yaw)
    hw, hd, rh = w / 2 + 0.4, dpt / 2 + 0.4, 1.8
    loc = lambda x, y, z: p + Vector((ca * x - sa * y, sa * x + ca * y, z))
    vs = [loc(-hw, -hd, h), loc(hw, -hd, h), loc(hw, 0, h + rh), loc(-hw, 0, h + rh),
          loc(-hw, hd, h), loc(hw, hd, h)]
    mesh(name + "_屋根", vs, [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)], M[roof], c)


def apartment(name, c, M, p, yaw, w=24.0, dpt=10.0, floors=3, wallm="wall2"):
    h = floors * 3.0
    box(name, p + Vector((0, 0, h / 2)), (w, dpt, h), yaw, M[wallm], c)
    ca, sa = math.cos(yaw), math.sin(yaw)
    for f in range(floors):
        for k in range(int(w / 3)):
            x = -w / 2 + 1.5 + k * 3
            q = p + Vector((ca * x - sa * (-dpt / 2 - 0.02), sa * x + ca * (-dpt / 2 - 0.02), 1.6 + f * 3))
            box(name + "_窓", q, (1.6, 0.04, 1.2), yaw, M["glass"], c)


def tree(c, M, p, s=1.0, kind="leaf"):
    cyl("幹", p + Vector((0, 0, 1.0 * s)), 0.12 * s, 2.0 * s, M["trunk"], c, 6)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.6 * s, location=p + Vector((0, 0, 2.6 * s)))
    ob = bpy.context.active_object
    ob.scale = (1, 1, 0.8)
    ob.data.materials.append(M[kind])
    link(ob, c)


def snow_pole(c, M, p):
    for k in range(6):
        cyl("スノーポール", p + Vector((0, 0, 0.15 + k * 0.3)), 0.03, 0.3, M["red"] if k % 2 == 0 else M["white"], c, 8)
    cyl("反射体", p + Vector((0, 0, 1.0)), 0.05, 0.02, M["amber"], c, 12, rot=(math.pi / 2, 0, 0))


def light_pole(c, M, p, toward, h=8.0):
    cyl("照明柱", p + Vector((0, 0, h / 2)), 0.08, h, M["steel"], c, 12)
    t = (toward - p)
    t.z = 0
    t.normalize()
    head = p + t * 1.2 + Vector((0, 0, h))
    box("照明アーム", (p + head) / 2 + Vector((0, 0, 0)), (1.3, 0.08, 0.08), math.atan2(t.y, t.x), M["steel"], c)
    box("LED灯具", head + Vector((0, 0, -0.05)), (0.7, 0.3, 0.1), math.atan2(t.y, t.x), M["lamp"], c)


def board_label(S, c, M, font, s, d, label, key):
    g = S.point(s, d, S.ground(s, d) if abs(d) > 3.5 else 0)
    a = S.al.plan(s)[2]
    t = Vector((math.cos(a), math.sin(a), 0))
    box(f"測点杭_{label}", g + Vector((0, 0, 0.75)), (0.07, 0.07, 1.5), a, M["brown"], c)
    bc = g + Vector((0, 0, 1.45)) - t * 0.05
    box(f"測点板_{label}", bc, (0.03, 1.4, 0.42), a, M["yellow"] if key else M["white"], c)
    cu = bpy.data.curves.new(f"測点文字_{label}", "FONT")
    cu.body = label
    if font:
        cu.font = font
    cu.size = 0.24 if len(label) <= 6 else 0.17
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = 0.004
    tx = bpy.data.objects.new(f"測点文字_{label}", cu)
    tx.location = bc - t * 0.03
    tx.rotation_euler = (math.pi / 2, 0, a - math.pi / 2)
    tx.data.materials.append(M["black"])
    c.objects.link(tx)


def load_font():
    for fp in ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", "C:/Windows/Fonts/meiryo.ttc",
               "C:/Windows/Fonts/msgothic.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"):
        try:
            return bpy.data.fonts.load(fp, check_existing=True)
        except Exception:
            pass
    return None


# =================================================================
# 4. 共通：地形
# =================================================================
def build_terrain(S, M, c, flat, slope, step=0.5):
    """平面上の格子で地形を作る（急な曲線でも地形が折り返さない）。
    各格子点から一番近い道路中心を探し、(s, d) に直して S.ground で高さを決める"""
    from mathutils import kdtree
    s0, s1 = S.s_range
    samples = []
    s = s0
    while s <= s1:
        x, y, a = S.al.plan(s)
        samples.append((s, x, y, a))
        s += 0.2
    kd = kdtree.KDTree(len(samples))
    for i, (s, x, y, a) in enumerate(samples):
        kd.insert((x, y, 0), i)
    kd.balance()
    xs = [p[1] for p in samples]
    ys = [p[2] for p in samples]
    D = S.d_half
    x0, x1 = min(xs) - D, max(xs) + D
    y0, y1 = min(ys) - D, max(ys) + D
    nx, ny = int((x1 - x0) / step) + 1, int((y1 - y0) / step) + 1
    verts, keep = [], []
    for j in range(ny):
        for i in range(nx):
            X, Y = x0 + i * step, y0 + j * step
            _, idx, dist = kd.find((X, Y, 0))
            s, x, y, a = samples[idx]
            d = -(X - x) * math.sin(a) + (Y - y) * math.cos(a)
            # 範囲外（道路の端より先・遠すぎる所）は作らない
            along = (X - x) * math.cos(a) + (Y - y) * math.sin(a)
            ok = dist <= D and abs(along) < 1.0
            keep.append(ok)
            verts.append(Vector((X, Y, S.zc(s) + S.ground(s, d))))
    faces = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            a = j * nx + i
            q = (a, a + 1, a + 1 + nx, a + nx)
            if all(keep[k] for k in q):
                faces.append(q)
    tm = mat_terrain(flat, slope)
    zmin = min(v.z for v in verts)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mesh("遠景の地面", [Vector((cx - 1500, cy - 1500, zmin - 0.4)), Vector((cx + 1500, cy - 1500, zmin - 0.4)),
                     Vector((cx + 1500, cy + 1500, zmin - 0.4)), Vector((cx - 1500, cy + 1500, zmin - 0.4))],
         [(0, 1, 2, 3)], tm, c)
    return mesh("地形", verts, faces, tm, c, smooth_shade=True)


# =================================================================
# 5. 各施工箇所のモデル
# =================================================================
def build_haba(S, M, C):
    w0, w1 = S.work
    H = S.half
    road = [(-H, -0.5), (-H, -0.02 * H), (0, 0), (H, -0.02 * H), (H, -0.5)]
    sweep(S, "舗装_新設", w0, w1, road, M["asp_new"], C["道路"])
    old = [(-2.4, -0.5), (-2.4, -0.05), (0, 0), (2.4, -0.05), (2.4, -0.5)]
    sweep(S, "舗装_既設_起点側", S.s_range[0], w0 - 4.0, old, M["asp_old"], C["道路"])
    sweep(S, "舗装_既設_終点側", w1, S.s_range[1], lambda s: [(-2.4 - 0.35 * (1 - smooth(w1, w1 + 8, s)), -0.5),
          (-2.4 - 0.35 * (1 - smooth(w1, w1 + 8, s)), -0.05), (0, 0), (2.4 + 0.35 * (1 - smooth(w1, w1 + 8, s)), -0.05),
          (2.4 + 0.35 * (1 - smooth(w1, w1 + 8, s)), -0.5)], M["asp_old"], C["道路"])
    sweep(S, "舗装_交差点すり付け", w0 - 4.0, w0, road, M["asp_new"], C["道路"])
    # 外側線（白実線 15cm）
    for sd in (1, -1):
        d = (H - 0.15) * sd
        sweep(S, "外側線", w0, w1, [(d - 0.075, -0.02 * abs(d) + 0.006), (d + 0.075, -0.02 * abs(d) + 0.006)], M["line"], C["道路"])
    # 皿型側溝（土留め付き）：天端は路面端、中央が 3cm 下がる皿形＋コンクリート蓋
    for sd, s0 in ((1, sta(0, 5.5)), (-1, sta(0, 13.4))):
        prof = [(H, -0.6), (H, -0.055), (H + 0.25, -0.085), (H + 0.5, -0.055), (H + 0.5, -0.6)]
        prof = [(d * sd, h) for d, h in prof]
        if sd < 0:
            prof.reverse()
        sweep(S, "皿型側溝_" + ("左" if sd > 0 else "右"), s0, w1, prof, M["conc"], C["排水"])
        # 約20mごとにグレーチング
        s = s0 + 10
        while s < w1:
            a = S.al.plan(s)[2]
            box("グレーチング", S.point(s, (H + 0.25) * sd, -0.07), (1.0, 0.35, 0.02), a, M["steel"], C["排水"])
            s += 20
    # 集水桝の蓋
    for s, d, w in ((sta(0, 5.1), H + 0.3, 0.6), (sta(2, 12.66), H + 0.25, 0.4), (sta(0, 12.91), -H - 0.35, 0.7)):
        box("集水桝蓋", S.point(s, d, -0.06), (w, w, 0.03), S.al.plan(s)[2], M["steel"], C["排水"])
    # マンホール（右側車道内）
    for s in (sta(0, 7.33), sta(2, 8.39), sta(4, 9.28)):
        cyl("マンホール", S.point(s, -1.4, -0.026), 0.33, 0.02, M["steel"], C["道路"], 24)
    # 進入路
    for nm, s, sd, w, L, mat in (("L1", sta(0, 16.09), 1, 6.0, 3.0, "asp_new"), ("L2", sta(2, 14.72), 1, 3.5, 2.5, "gravel"),
                                 ("R1", sta(0, 5.72), -1, 11.5, 3.0, "asp_new"), ("R2", sta(2, 4.63), -1, 5.0, 3.0, "gravel"),
                                 ("R3", sta(4, 8.8), -1, 6.0, 1.5, "gravel")):
        vs = []
        for a in (H + 0.5, H + 0.5 + L):
            for off in (-w / 2, w / 2):
                vs.append(S.point(s + off, a * sd, -0.06 - (a - H - 0.5) * 0.07 + 0.01))
        mesh("進入路_" + nm, vs, [(0, 1, 3, 2)] if sd > 0 else [(0, 2, 3, 1)], M[mat], C["道路"])
    # 起点の交差道路（南北の既設道路）と鹿妻幹線水路
    x, y, a = S.al.plan(-6.0)
    p0 = S.point(-6.0, 0, -0.03)
    perp = a + math.pi / 2
    box("交差道路（既設）", p0, (6.0, 140.0, 0.1), a, M["asp_old"], C["道路"])
    for k in (-1, 1):
        sweep_pts = None
    ch = S.point(-11.0, 0, -0.9)
    box("鹿妻幹線水路_底", ch, (1.6, 140.0, 0.1), a, M["water"], C["排水"])
    for k in (-1, 1):
        box("鹿妻幹線水路_壁", S.point(-11.0 + k * 0.9, 0, -0.5), (0.2, 140.0, 0.9), a, M["conc"], C["排水"])
    # 交差道路の中央の矢印標示の代わりに中央線
    box("交差道路_中央線", S.point(-6.0, 0, 0.03), (0.12, 140.0, 0.01), a, M["line"], C["道路"])
    # 照明灯 NO.0+13.24 右
    light_pole(C["施設"], M, S.point(sta(0, 13.24), -(H + 1.0), -0.06), S.point(sta(0, 13.24), 0, 0))
    # スノーポール（L 6本、R 5本）
    for k in range(6):
        s = 8 + k * 16.5
        snow_pole(C["施設"], M, S.point(s, H + 0.75, -0.08))
    for k in range(5):
        s = 18 + k * 17.5
        snow_pole(C["施設"], M, S.point(s, -(H + 0.75), -0.08))
    # 周辺：りんご園・住宅・ビニールハウス
    random.seed(11)
    for side in (1, -1):
        for si in range(-40, 150, 5):
            for di in range(10, 64, 4):
                s, d = si + random.uniform(-0.5, 0.5), di * side
                if side > 0 and -2 < s < 45 and di < 30:      # L側 NO.0〜NO.2 は住宅
                    continue
                if -16 < s < 0:
                    continue
                if random.random() < 0.08:
                    continue
                tree(C["周辺"], M, S.point(s, d, S.ground(s, d)), random.uniform(0.75, 0.95), "apple")
    yaw = S.al.plan(15)[2]
    house("住宅1", C["周辺"], M, S.point(8, 14, S.ground(8, 14)), yaw, 10, 8, 5.8, "roof")
    house("住宅2", C["周辺"], M, S.point(26, 19, S.ground(26, 19)), yaw, 8, 7, 5.0, "roof2", "wall")
    house("小屋", C["周辺"], M, S.point(38, 12, S.ground(38, 12)), yaw, 5, 4, 3.2, "roof")
    for k in range(2):
        p = S.point(14 + k * 7, 25, S.ground(14, 25))
        bpy.ops.mesh.primitive_cylinder_add(radius=2.8, depth=20, vertices=24, location=p,
                                            rotation=(0, math.pi / 2, yaw + math.pi / 2))
        ob = bpy.context.active_object
        ob.name = "ビニールハウス"
        ob.scale = (1, 1, 1)
        ob.data.materials.append(M["vinyl"])
        link(ob, C["周辺"])
    house("住宅3", C["周辺"], M, S.point(-24, 12, S.ground(-24, 12)), yaw, 9, 8, 5.5, "roof2")


def build_yuden(S, M, C):
    s0, s1 = S.s_range
    w0, w1 = S.work
    H = S.half
    road = [(-H, -0.5), (-H, -0.07), (0, 0), (H, -0.07), (H, -0.5)]
    sweep(S, "車道（既設）", s0, s1, road, M["asp_old"], C["道路"])
    sweep(S, "車道_打換え", w0 - 3, w1 + 0.5, [(H - 1.0, -0.07 + 0.02 * 1.0 + 0.003), (H, -0.067)], M["asp_new"], C["道路"])
    for sd in (1, -1):
        d = (H - 0.75) * sd
        z = -0.02 * abs(d) + 0.006
        sweep(S, "外側線", s0 if sd < 0 else w0 - 3, s1 if sd < 0 else w1 + 3, [(d - 0.075, z), (d + 0.075, z)], M["line"], C["道路"])
    # 縁石（歩車道境界ブロック B種）＋歩道
    wi, wo = S.walk_in(), S.walk_out()
    cut = [(sta(21, 18.7), sta(22, 4.1)), (sta(23, 12.45), sta(23, 17.85))]    # 切下げ・車両乗入

    def curb_h(s):
        h = 0.15
        for a, b in cut:
            h -= 0.12 * (smooth(a - 0.6, a, s) * (1 - smooth(b, b + 0.6, s)))
        return h

    sweep(S, "歩車道境界ブロック", sta(21, 12.1), sta(25, 0.9),
          lambda s: [(H, -0.4), (H, -0.07 + curb_h(s)), (wi, -0.07 + curb_h(s)), (wi, -0.4)], M["conc"], C["歩道"], step=0.3)
    sweep(S, "歩道舗装", w0 - 0.5, w1 + 0.3,
          lambda s: [(wi, -0.07 + curb_h(s) - 0.005), (wo - 0.3, -0.07 + curb_h(s) + 0.035), (wo, -0.07 + curb_h(s) + 0.035),
                     (wo, -0.6)], M["asp_walk"], C["歩道"], step=0.3)
    # 擁壁区間（可変勾配側溝B500＋L型擁壁）と転落防止柵
    a0, a1 = sta(23, 16.5), sta(25, 1.0)
    paddy = lambda s: S.paddy - S.base_el - S.zc(s)
    sweep(S, "可変勾配側溝・L型擁壁", a0, a1,
          lambda s: [(wo - 0.02, 0.12), (wo + 0.18, 0.12), (wo + 0.18, paddy(s) - 0.05), (wo - 0.02, paddy(s) - 0.05)],
          M["conc"], C["歩道"], closed=True)
    f0, f1 = sta(23, 17.4), sta(24, 19.4)
    n = int((f1 - f0) / 2.0)
    for k in range(n + 1):
        s = f0 + k * (f1 - f0) / n
        cyl("転落防止柵_支柱", S.point(s, wo + 0.08, 0.12 + 0.55), 0.03, 1.1, M["brown"], C["歩道"], 10)
    for zz in (0.55, 1.15):
        sweep(S, "転落防止柵_横桟", f0, f1,
              [(wo + 0.06, 0.12 + zz), (wo + 0.10, 0.12 + zz), (wo + 0.10, 0.12 + zz + 0.04), (wo + 0.06, 0.12 + zz + 0.04)],
              M["brown"], C["歩道"], closed=True)
    # 進入路（アスファルト 3.3m ＋ 敷砂利）
    for s, L in ((sta(22, 1.4), 4.0), (sta(23, 15.15), 4.5)):
        vs, a = [], wo
        for dd in (wo, wo + 3.3, wo + L + 2.0):
            for off in (-2.0, 2.0):
                hh = 0.07 if dd == wo else (S.ground(s + off, dd) + 0.03)
                vs.append(S.point(s + off, dd, hh))
        mesh("進入路_As", vs[:4], [(0, 1, 3, 2)], M["asp_walk"], C["歩道"])
        mesh("進入路_砂利", vs[2:], [(0, 1, 3, 2)], M["gravel"], C["歩道"])
    # 南側の既設U型側溝
    sweep(S, "既設U型側溝", s0, s1, [(-H - 0.4, -0.5), (-H - 0.4, -0.07), (-H - 0.35, -0.07), (-H - 0.35, -0.35),
                                     (-H - 0.05, -0.35), (-H - 0.05, -0.07), (-H, -0.07), (-H, -0.5)], M["conc"], C["道路"])
    # 視線誘導標（4本）・ポストコーン（5本）
    for s in (sta(21, 18.4), sta(22, 4.4), sta(23, 12.15), sta(23, 18.15)):
        snow_pole(C["施設"], M, S.point(s, H + 0.09, 0.08))
    for k, s in enumerate((sta(21, 12.6), sta(21, 14.6), sta(25, 0.6), sta(25, 2.0), sta(25, 3.4))):
        cyl("ポストコーン", S.point(s, H - 0.25, 0.33), 0.04, 0.8, M["amber"], C["施設"], 10)
    # 田（北）
    pd = S.paddy - S.base_el
    p = S.point(470, 30, 0)
    box("田んぼ", Vector((p.x, p.y, pd - 0.04)), (150, 46, 0.1), S.al.plan(470)[2], M["paddy"], C["周辺"])
    for k in range(-3, 4):          # 畦
        q = S.point(470 + k * 22, 30, 0)
        box("畦", Vector((q.x, q.y, pd + 0.05)), (0.4, 46, 0.15), S.al.plan(470)[2], M["gravel"], C["周辺"])
    # 終点の先の民家（北）・南の台地の電柱
    yaw = S.al.plan(510)[2]
    house("母屋", C["周辺"], M, S.point(518, 16, S.ground(518, 16)), yaw, 12, 9, 6.2, "roof")
    house("車庫", C["周辺"], M, S.point(530, 12, S.ground(530, 12)), yaw, 6, 6, 3.2, "roof2", "wall2")
    for s in range(405, 545, 32):
        cyl("電柱", S.point(s, -5.0, S.ground(s, -5.0) + 5.5), 0.15, 11.0, M["pole"], C["周辺"], 10)
    random.seed(5)
    for _ in range(140):
        s, d = random.uniform(400, 545), -random.uniform(12, 60)
        tree(C["周辺"], M, S.point(s, d, S.ground(s, d)), random.uniform(0.8, 1.4))


def build_doumae(S, M, C):
    s0, s1 = S.s_range
    H = S.half
    cs = S.cross_s

    def cross_slope(s):
        return 0.015 * (1 - smooth(30, 40, s) * (1 - smooth(52, 60, s))) + 0.007 * smooth(30, 40, s) * (1 - smooth(52, 60, s))

    road = lambda s: [(-H - 0.5, -0.5), (-H - 0.5, -cross_slope(s) * H - 0.01), (-H, -cross_slope(s) * H), (0, 0),
                      (H, -cross_slope(s) * H), (H, -0.5)]
    sweep(S, "車道", s0, s1, road, M["asp_new"], C["道路"], step=0.4)
    # 踏切舗装版（線路の両側 約2.2m）：線路と平行な帯
    c = S.point(cs, 0, 0)
    t = S.rail_dir()
    yaw_r = math.atan2(t.y, t.x)
    nrm = Vector((-t.y, t.x, 0))
    wtot = 13.0
    box("踏切舗装版", c + Vector((0, 0, 0.005)), (wtot, 2.8, 0.03), yaw_r, M["panel"], C["鉄道"])
    # 歩道・施設帯・縁石
    def walk_prof(s):
        wi, wo = S.walk(s)
        z = -0.0 + 0.12
        return [(H, -0.5), (H, z), (wi, z), (wi, -0.5)]

    sweep(S, "縁石・施設帯", 8, 84, walk_prof, M["conc"], C["歩道"], step=0.4)

    def walk2(s):
        wi, wo = S.walk(s)
        return [(wi, 0.10), (wo, 0.12), (wo, -0.6)]

    sweep(S, "歩道舗装", 9, 83, walk2, M["asp_walk"], C["歩道"], step=0.4)
    # 線形をまたぐ線路
    rail_top = S.zc(cs) + 0.02
    L = 90.0
    gauge = 1.067
    for k in (-1, 1):
        q = c + nrm * (k * gauge / 2)
        box("レール", Vector((q.x, q.y, rail_top - 0.08)), (L, 0.07, 0.15), yaw_r, M["rail"], C["鉄道"])
    # バラスト（台形断面）
    vs = []
    for u in (-L / 2, L / 2):
        for v, z in ((-2.5, -0.57), (-1.4, -0.16), (1.4, -0.16), (2.5, -0.57)):
            q = c + t * u + nrm * v
            vs.append(Vector((q.x, q.y, rail_top + z)))
    mesh("バラスト", vs, [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6)], M["ballast"], C["鉄道"])
    k = -L / 2
    while k < L / 2:
        if abs(k) > 6.8:
            q = c + t * k
            box("PCまくらぎ", Vector((q.x, q.y, rail_top - 0.2)), (0.2, 2.0, 0.14), yaw_r, M["sleeper"], C["鉄道"])
        k += 0.6
    # 遮断機・警報機（線路の両側、歩道外側／施設帯／車道外側の3基）
    a_r = S.al.plan(cs)[2]
    for side in (-1, 1):
        sm = cs + side * 5.0
        for nm, d in (("歩道外側", S.walk(sm)[1] + 0.35), ("施設帯", H + 0.6), ("車道外側", -H - 0.7)):
            p = S.point(sm, d, 0.12 if d > 0 else -0.05)
            cyl("遮断機_柱", p + Vector((0, 0, 1.4)), 0.09, 2.8, M["black"], C["鉄道"], 12)
            for z in range(7):
                cyl("遮断機_柱黄", p + Vector((0, 0, 0.2 + z * 0.4)), 0.092, 0.2, M["yellow"], C["鉄道"], 12)
            box("遮断機_機箱", p + Vector((0, 0, 1.0)), (0.45, 0.35, 0.8), a_r, M["yellow"], C["鉄道"])
            # 遮断かん（上がった状態）
            for z in range(10):
                cyl("遮断かん", p + Vector((0.15, 0, 1.6 + z * 0.35)), 0.03, 0.35,
                    M["yellow"] if z % 2 else M["black"], C["鉄道"], 8)
            if nm != "歩道外側":
                # 警報灯と踏切警標（×印）
                top = p + Vector((0, 0, 3.0))
                box("踏切警報機_腕", top, (0.12, 0.9, 0.1), a_r, M["black"], C["鉄道"])
                for kk in (-1, 1):
                    q = top + Vector((-math.sin(a_r), math.cos(a_r), 0)) * (kk * 0.35)
                    cyl("警報灯", q + Vector((0, 0, -0.05)), 0.12, 0.08, M["redlamp"], C["鉄道"], 16,
                        rot=(math.pi / 2, 0, a_r + math.pi / 2))
                for ang in (0.6, -0.6):
                    bpy.ops.mesh.primitive_cube_add(size=1, location=top + Vector((0, 0, 0.6)))
                    ob = bpy.context.active_object
                    ob.name = "踏切警標"
                    ob.scale = (0.03, 1.1, 0.18)
                    ob.rotation_euler = (ang, 0, a_r)
                    ob.data.materials.append(M["yellow"])
                    link(ob, C["鉄道"])
    # 停止線・横断歩道・誘導ブロック
    for s, d0, d1 in ((40.5, 0.0, H - 0.5), (51.0, -H + 0.5, 0.0)):
        sweep(S, "停止線", s - 0.225, s + 0.225, [(d0, 0.006), (d1, 0.006 - 0.007 * abs(d1 - d0))], M["line"], C["道路"])
    for k in range(-4, 5):
        if k % 2 == 0:
            continue
    for k in range(9):
        d = -H + 0.25 + k * 0.6
        if d > H - 0.2:
            break
        sweep(S, "横断歩道", 88.0, 92.0, [(d, -0.02 * abs(d) + 0.006), (d + 0.45, -0.02 * abs(d + 0.45) + 0.006)], M["line"], C["道路"])
    for s in (39.5, 52.0):
        wi, wo = S.walk(s)
        sweep(S, "視覚障害者誘導ブロック", s - 0.3, s + 0.3, [(wi + 0.1, 0.125), (wo - 0.1, 0.125)], M["yellow"], C["歩道"])
    for sd in (1, -1):
        d = (H - 0.5) * sd
        sweep(S, "外側線", 10, 84, [(d - 0.075, -0.015 * abs(d) + 0.006), (d + 0.075, -0.015 * abs(d) + 0.006)], M["line"], C["道路"])
    # L型擁壁＋転落防止柵（北側 NO.2+9.07〜NO.3+13.355）
    a0, a1 = sta(2, 9.07), sta(3, 13.355)

    def wall_prof(s):
        wi, wo = S.walk(s)
        g = S.ground(s, wo + 1.0)
        return [(wo, 0.12), (wo + 0.2, 0.12), (wo + 0.2, g - 0.1), (wo, g - 0.1)]

    sweep(S, "L型擁壁", a0, a1, wall_prof, M["conc"], C["歩道"], closed=True)
    n = int((a1 - a0) / 2.0)
    for k in range(n + 1):
        s = a0 + k * (a1 - a0) / n
        cyl("転落防止柵_支柱", S.point(s, S.walk(s)[1] + 0.1, 0.12 + 0.55), 0.03, 1.1, M["brown"], C["歩道"], 10)
    for zz in (0.5, 1.1):
        sweep(S, "転落防止柵_横桟", a0, a1, lambda s, zz=zz: [(S.walk(s)[1] + 0.08, 0.12 + zz), (S.walk(s)[1] + 0.12, 0.12 + zz),
                                                          (S.walk(s)[1] + 0.12, 0.16 + zz), (S.walk(s)[1] + 0.08, 0.16 + zz)],
              M["brown"], C["歩道"], closed=True)
    # 照明柱 2基
    light_pole(C["施設"], M, S.point(36.0, -H - 1.4, -0.2), S.point(36.0, 0, 0))
    light_pole(C["施設"], M, S.point(80.0, S.walk(80)[1] + 0.6, 0.0), S.point(80.0, 0, 0))
    # 周辺：住宅（北）・集合住宅（南）
    random.seed(3)
    yaw = S.al.plan(45)[2]
    for s, d in ((5, 14), (22, 15), (64, 14), (95, 14), (110, 16)):
        P = S.point(s, d, S.ground(s, d))
        dist, _ = S.rail_dist(P)
        if dist > 9:
            house("住宅", C["周辺"], M, P, S.al.plan(s)[2], random.uniform(8, 10), 7.5, 5.8,
                  random.choice(["roof", "roof2"]))
    for s, d, fl in ((10, -20, 3), (70, -22, 4), (100, -20, 3)):
        P = S.point(s, d, S.ground(s, d))
        dist, _ = S.rail_dist(P)
        if dist > 12:
            apartment("集合住宅", C["周辺"], M, P, S.al.plan(s)[2], 22, 9, fl)
    for k in (-4, -3, -2, 2, 3, 4):
        q = c + t * (k * 16.0) + nrm * 5.5
        z = S.zc(cs) - 0.6
        cyl("線路沿い電柱", Vector((q.x, q.y, z + 4.5)), 0.13, 9.0, M["pole"], C["周辺"], 10)
    for _ in range(50):
        s, d = random.uniform(-20, 120), random.choice((1, -1)) * random.uniform(26, 50)
        P = S.point(s, d, S.ground(s, d))
        if S.rail_dist(P)[0] > 7:
            tree(C["周辺"], M, P, random.uniform(0.8, 1.3))


# =================================================================
# 6. シーン全体
# =================================================================
CAMS = {
    "haba": {
        "01_鳥瞰": ((-30, -38, 26), (55, 3, -1), 26),
        "02_ドライバー視点": ((-8, 1.1, 1.3), (60, 0.8, 0.8), 30),
        "03_照明と交差点": ((30, -16, 3.5), (-2, 0, 0), 26),
    },
    "yuden": {
        "01_鳥瞰": ((415, 35, 24), (475, 2, -1), 26),
        "02_歩行者視点": ((436, 4.8, 1.6), (500, 5.2, 2.0), 28),
        "03_田んぼ側から": ((492, 22, 0.0), (482, 4, 0.5), 24),
    },
    "doumae": {
        "01_鳥瞰": ((5, -40, 30), (48, 3, -1), 26),
        "02_ドライバー視点": ((14, 1.1, 1.3), (55, 0.2, 1.3), 30),
        "03_歩道から踏切": ((30, 4.6, 1.6), (55, 5.0, 0.8), 28),
    },
}


def build(site_key):
    S = SITES[site_key]
    clear_scene()
    sc = bpy.context.scene
    M = mats()
    C = {k: coll(k) for k in ("道路", "歩道", "排水", "施設", "鉄道", "地形", "周辺", "測点")}
    if site_key == "yuden":
        build_terrain(S, M, C["地形"], (0.12, 0.20, 0.06), (0.20, 0.30, 0.08))
        build_yuden(S, M, C)
    elif site_key == "haba":
        build_terrain(S, M, C["地形"], (0.10, 0.18, 0.05), (0.20, 0.30, 0.08))
        build_haba(S, M, C)
    else:
        build_terrain(S, M, C["地形"], (0.12, 0.20, 0.06), (0.20, 0.30, 0.08))
        build_doumae(S, M, C)
    font = load_font()
    for s, label, key in S.stations():
        d = -(S.half + 2.2) if site_key != "yuden" else -(S.half + 1.2)
        if site_key == "doumae" and "踏切" in label:
            continue
        board_label(S, C["測点"], M, font, s, d, label, key)
    # 空と太陽
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(40)
    sky.sun_rotation = math.radians(160)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.35
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    sd = bpy.data.lights.new("太陽", "SUN")
    sd.energy = 3.0
    sd.angle = math.radians(1.5)
    sun = bpy.data.objects.new("太陽", sd)
    sun.rotation_euler = (math.radians(50), 0, math.radians(70))
    sc.collection.objects.link(sun)
    # カメラ
    cams = {}
    for key, ((es, ed, eh), (ts, td, th), lens) in CAMS[site_key].items():
        cd = bpy.data.cameras.new(key)
        cd.lens = lens
        cd.clip_end = 2000
        co = bpy.data.objects.new("CAM_" + key, cd)
        eye = S.point(es, ed, max(S.ground(es, ed), -0.1) + eh)
        co.location = eye
        co.rotation_euler = (S.point(ts, td, th) - eye).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(co)
        cams[key] = co
    sc.camera = next(iter(cams.values()))
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = -1.0
    return S, cams


def station_overlay(sc, S, cam):
    from bpy_extras.object_utils import world_to_camera_view
    rx = sc.render.resolution_x * sc.render.resolution_percentage / 100
    ry = sc.render.resolution_y * sc.render.resolution_percentage / 100
    terrain = bpy.data.objects.get("地形")
    eye = cam.matrix_world.translation.copy()
    pts = []
    for s, label, key in S.stations():
        P = S.point(s, 0, 0.3)
        co = world_to_camera_view(sc, cam, P)
        v = P - eye
        if terrain and terrain.ray_cast(eye, v.normalized(), distance=v.length - 0.5)[0]:
            continue
        if co.z > 0 and 0.02 < co.x < 0.98 and 0.02 < co.y < 0.98:
            pts.append({"label": label, "key": key, "s": s, "x": co.x * rx, "y": (1 - co.y) * ry, "dist": co.z})
    return {"points": pts, "drive_s": None}


# 動画の経路：(ドローン開始s, 終了s, 横d, 高さ) と (走行開始s, 終了s, 左車線のd)
VIDEO = {
    "haba": {"drone": (-35, 40, -30, 30), "drive": (-15, 110, 1.4)},
    "yuden": {"drone": (410, 470, 32, 26), "drive": (422, 515, 1.9)},
    "doumae": {"drone": (-10, 45, 40, 30), "drive": (0, 95, 1.0)},
}


def setup_video(S, site, fps=24):
    """①ドローンで全景（4秒）→ ②左車線を走るドライバー視点（10秒）"""
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("CAM_動画")
    cd.clip_end = 2000
    cam = bpy.data.objects.new("CAM_動画", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.fps = fps
    V = VIDEO[site]

    def key(eye, target, lens, f):
        cam.location = eye
        cam.rotation_euler = (target - eye).to_track_quat("-Z", "Y").to_euler()
        cd.lens = lens
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cd.keyframe_insert("lens", frame=f)

    frame = 1
    a0, a1, ad, ah = V["drone"]
    n = 4 * fps
    for i in range(n):
        u = smooth(0, 1, i / (n - 1))
        s = a0 + (a1 - a0) * u
        key(S.point(s, ad * (1 - 0.35 * u), ah * (1 - 0.3 * u)), S.point(s + 55, 0, -1), 26, frame)
        frame += 1
    b0, b1, bd = V["drive"]
    n = 10 * fps
    drive = {}
    for i in range(n):
        s = b0 + (b1 - b0) * i / (n - 1)
        key(S.point(s, bd, 1.25), S.point(s + 25, bd * 0.8, 0.6), 28, frame)
        drive[frame] = s
        frame += 1
    sc.frame_start, sc.frame_end = 1, frame - 1
    return cam, drive


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    site = next((a.split("=", 1)[1] for a in argv if a.startswith("--site=")), SITE)
    S, cams = build(site)
    sc = bpy.context.scene
    outdir = os.path.join(HERE, "renders", site)
    if "--render" in argv:
        os.makedirs(outdir, exist_ok=True)
        if "--fast" in argv:
            sc.cycles.samples = 16
            sc.render.resolution_percentage = 50
        only = [a.split("=", 1)[1] for a in argv if a.startswith("--cam=")]
        for key, cam in cams.items():
            if only and not any(o in key for o in only):
                continue
            sc.camera = cam
            sc.render.filepath = os.path.join(outdir, f"{key}.png")
            bpy.ops.render.render(write_still=True)
            with open(os.path.join(outdir, f"{key}_stations.json"), "w", encoding="utf-8") as fp:
                json.dump(station_overlay(sc, S, cam), fp, ensure_ascii=False)
    if "--video" in argv:
        vdir = os.path.join(outdir, "video")
        os.makedirs(vdir, exist_ok=True)
        vcam, drive = setup_video(S, site)
        sc.cycles.samples = 10
        sc.render.resolution_percentage = 50
        sc.render.use_persistent_data = True
        sc.render.filepath = os.path.join(vdir, "f_####")
        for a in argv:
            if a.startswith("--frames="):
                f0, f1 = a.split("=", 1)[1].split("-")
                sc.frame_start, sc.frame_end = int(f0), int(f1)
        data = {}
        for f in range(sc.frame_start, sc.frame_end + 1):
            sc.frame_set(f)
            d = station_overlay(sc, S, vcam)
            if f in drive:
                d["drive_s"] = drive[f]
                d["drive_name"] = sta_name(drive[f])
            data[f] = d
        meta = {"title": S.title, "s0": S.work[0], "s1": S.work[1]}
        with open(os.path.join(vdir, "stations.json"), "w", encoding="utf-8") as fp:
            json.dump({"meta": meta, "frames": data}, fp, ensure_ascii=False)
        if "--overlay-only" not in argv:
            bpy.ops.render.render(animation=True)
    if "--save" in argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, f"habasen_{site}.blend"))
