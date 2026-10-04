# -*- coding: utf-8 -*-
"""
市道二子沢線道路改良工事　完成イメージ（Blender ベースモデル）

使い方
  Blender（4.x）→ Scripting タブ → このファイルを開いて「▶ Run Script」
  コマンドラインで画像まで出す場合:
    blender -b -P futagosawa_kansei.py -- --render

図面から拾った値（単位 m）
  施工延長 190.07m（NO.50 〜 NO.59+10.07）、測点間隔 20m
  車道幅員 5.0m（路肩0.5＋2.0＋2.0＋路肩0.5）、横断勾配 2%、サイドライン
  平面線形：直線 → BC-9(NO.52+14.56)〜EC-9(NO.55+3.73) 右カーブ → 直線
  縦断：計画高 FH（横断図より）
  側溝：U-300×300（左 NO.50〜NO.53+13.80）、落蓋式300×300（左 24m、右 72.93m）
  第3号横断函渠：ボックスカルバート B1200×H1000、L=23.15m、斜角約60°（NO.55+8.00）
  第4・5号面壁：幅6.0m×高2.5m
  水路舗装工：かごマット・ふとんかご（第1号 L=14m、第2号 L=66m）
  ガードレール Gr-C-4E（右 25m、左 77m）、視線誘導標
  進入路：第16号（B=3.0m L=10m）、第17号（B=4.0m L=3.0m）

※ 地形（山の形・水路の位置）は横断図を参考にした「それらしい形」です。
  インターン生がここから図面と照らし合わせて精度を上げていく前提のたたき台です。
"""
import bpy
import math
import random
import sys
from mathutils import Vector, Matrix, noise

random.seed(2026)

# ---------------------------------------------------------------
# 1. 設計値
# ---------------------------------------------------------------
BASE_EL = 337.0                 # 標高の基準（NO.50 付近）。Blender の Z=0 にあたる
S_END = 190.07                  # 施工延長
STA = 20.0                      # 測点間隔

# 計画高 FH（NO.50 〜 NO.60）
FH = [337.27, 338.04, 338.80, 339.56, 340.32, 341.08,
      342.04, 343.40, 344.96, 346.52, 348.08]

BC9 = 2 * STA + 14.56           # NO.52+14.56
EC9 = 5 * STA + 3.73            # NO.55+3.73
CURVE_R = 110.0                 # 曲線半径（平面図からの読み取り値）

HALF_W = 2.5                    # 舗装の片側幅
LINE_D = 2.0                    # サイドライン位置
CROSS = 0.02                    # 横断勾配

CULVERT_S = 5 * STA + 8.0       # NO.55+8.00
CH_D = 10.0                     # 水路中心までの距離
CH_DEPTH = 3.4                  # 路面から水路底までの深さ
CH_BED = 2.4                    # 水路底の幅


def sta(no, plus=0.0):
    """測点 NO.xx+yy を NO.50 からの追加距離に変換"""
    return (no - 50) * STA + plus


# ---------------------------------------------------------------
# 2. 線形（平面・縦断）
# ---------------------------------------------------------------
def plan(s):
    """追加距離 s → (x, y, 方位角)。左カーブなら+、右カーブなら−"""
    if s <= BC9:
        return s, 0.0, 0.0
    lc = EC9 - BC9
    if s <= EC9:
        u = s - BC9
        t = u / CURVE_R
        return BC9 + CURVE_R * math.sin(t), -CURVE_R * (1 - math.cos(t)), -t
    t = lc / CURVE_R
    x0 = BC9 + CURVE_R * math.sin(t)
    y0 = -CURVE_R * (1 - math.cos(t))
    u = s - EC9
    return x0 + u * math.cos(-t), y0 + u * math.sin(-t), -t


def zc(s):
    """路面中心の高さ（BASE_EL を 0 とする）"""
    i = s / STA
    if i <= 0:
        g = (FH[1] - FH[0]) / STA
        return FH[0] - BASE_EL + g * s
    if i >= len(FH) - 1:
        g = (FH[-1] - FH[-2]) / STA
        return FH[-1] - BASE_EL + g * (s - STA * (len(FH) - 1))
    k = int(i)
    f = i - k
    return FH[k] + (FH[k + 1] - FH[k]) * f - BASE_EL


def point(s, d, h):
    """測点 s、中心から左へ d（右は負）、路面中心からの高さ h の位置"""
    x, y, a = plan(s)
    nx, ny = -math.sin(a), math.cos(a)
    return Vector((x + nx * d, y + ny * d, zc(s) + h))


def smooth(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------
# 3. 地形（横断図を参考にしたモデル）
# ---------------------------------------------------------------
# カメラ位置：(測点s, 横d, 地面からの高さ, 注視点s, 注視点d, 注視点高さ, レンズmm)
CAMS = {
    "01_鳥瞰": (35, -40, 45, 118, 4, -2, 30),
    "02_ドライバー視点": (62, -1.1, 1.2, 150, 0.5, 3.5, 28),
    "03_水路側から": (178, 14.5, 2.5, 128, 5, -1.5, 24),
    "04_函渠付近": (92, -13, 1.6, 113, 4, -1.5, 22),
}


def side_profile(a, w_channel, s):
    """片側の地盤高。a=中心からの距離、w_channel=水路側(盛土)の度合い 0〜1"""
    if a < HALF_W:
        return -0.45
    if a < 3.0:
        return -0.07
    # 切土側：1:1.0 の法面 → 山
    cut = -0.07 + min(a - 3.0, 2.5) + max(0.0, a - 5.5) * 0.35
    # 盛土＋水路側：1:1.7 の法面 → 水路底 → 対岸
    toe = CH_D - CH_BED / 2
    far = CH_D + CH_BED / 2
    if a < toe:
        fill = -0.07 - (a - 3.0) / (toe - 3.0) * (CH_DEPTH - 0.07)
    elif a < far:
        fill = -CH_DEPTH
    else:
        fill = -CH_DEPTH + min(a - far, CH_DEPTH + 0.5) + max(0.0, a - far - CH_DEPTH - 0.5) * 0.3
    h = cut + (fill - cut) * w_channel
    # 遠くの山並みに起伏を付ける
    if a > 14:
        x, y, _ = plan(s)
        n = noise.noise(Vector((s * 0.025, a * 0.03, 7.3)))
        h += n * 6.0 * smooth(14, 45, a)
    return h


def w_left(s):
    return smooth(110.0, 114.5, s)          # 函渠より先は左に水路


def w_right(s):
    return 1.0 - smooth(101.5, 106.0, s)    # 函渠より手前は右に水路


def ground(s, d):
    if d >= 0:
        h = side_profile(d, w_left(s), s)
    else:
        h = side_profile(-d, w_right(s), s)
    # 進入路（第16号：左 B=3.0 L=10 / 第17号：右 B=4.0 L=3）
    for es, side, b, ln in ((sta(54, 4.5), 1, 3.0, 10.0), (sta(55, 12.4), -1, 4.0, 3.0)):
        a = d * side
        if a > 2.5:
            w = 1.0 - smooth(b / 2, b / 2 + 3.0, abs(s - es))
            w *= 1.0 - smooth(3.0 + ln, 3.0 + ln + 4.0, a)
            h = h + ((-0.07 + 0.06 * (a - 3.0)) - h) * w
    return h


# ---------------------------------------------------------------
# 4. ユーティリティ
# ---------------------------------------------------------------
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for blocks in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                   bpy.data.lights, bpy.data.collections):
        for b in list(blocks):
            if b.users == 0:
                blocks.remove(b)


def collection(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(c)
    return c


def mesh_object(name, verts, faces, mat, coll, smooth_shade=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    if smooth_shade:
        for p in me.polygons:
            p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    coll.objects.link(ob)
    return ob


def sweep(name, s0, s1, profile, mat, coll, step=1.0, closed=False, z_func=None):
    """断面形状 profile=[(d, h), ...] を線形に沿って押し出す"""
    n = max(2, int(math.ceil((s1 - s0) / step)) + 1)
    verts, faces = [], []
    m = len(profile)
    for i in range(n):
        s = s0 + (s1 - s0) * i / (n - 1)
        for d, h in profile:
            p = point(s, d, h)
            if z_func:
                p.z = z_func(s, d, h)
            verts.append(p)
    segs = m if closed else m - 1
    for i in range(n - 1):
        for j in range(segs):
            j2 = (j + 1) % m
            a, b = i * m + j, i * m + j2
            faces.append((a, b, b + m, a + m))
    if closed:
        faces.append(tuple(range(m - 1, -1, -1)))
        last = (n - 1) * m
        faces.append(tuple(last + j for j in range(m)))
    return mesh_object(name, verts, faces, mat, coll)


def box(name, center, size, yaw, pitch, mat, coll):
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = size
    ob.rotation_euler = (0.0, -pitch, yaw)
    ob.location = center
    ob.data.materials.append(mat)
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob


# ---------------------------------------------------------------
# 5. マテリアル
# ---------------------------------------------------------------
def material(name, color, rough=0.6, noise_scale=0.0, color2=None, metallic=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if noise_scale and color2:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = noise_scale
        tex.inputs["Detail"].default_value = 8.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*color, 1)
        ramp.color_ramp.elements[1].color = (*color2, 1)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def mat_terrain():
    """法面（傾斜が急）は種子散布の明るい緑、平らな所は濃い緑"""
    m = bpy.data.materials.new("地形")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.95
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sep.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.72
    ramp.color_ramp.elements[0].color = (0.20, 0.36, 0.05, 1)   # 法面（種子散布）
    ramp.color_ramp.elements[1].position = 0.88
    ramp.color_ramp.elements[1].color = (0.04, 0.10, 0.02, 1)   # 林床
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 3.0
    tex.inputs["Detail"].default_value = 10.0
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(ramp.outputs["Color"], mix.inputs[6])
    nt.links.new(tex.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return m


def mat_stone():
    """かごマットの詰石"""
    m = bpy.data.materials.new("詰石")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.85
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 4.5
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.12, 0.11, 0.10, 1)
    ramp.color_ramp.elements[1].color = (0.55, 0.52, 0.47, 1)
    nt.links.new(vor.outputs["Color"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    nt.links.new(vor.outputs["Distance"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


# ---------------------------------------------------------------
# 6. モデル作成
# ---------------------------------------------------------------
def build():
    clear_scene()
    sc = bpy.context.scene

    M = {
        "asphalt": material("舗装（新設）", (0.045, 0.045, 0.048), 0.75, 60, (0.09, 0.09, 0.09)),
        "asphalt_old": material("舗装（既設）", (0.13, 0.13, 0.12), 0.85, 40, (0.20, 0.19, 0.18)),
        "line": material("区画線", (0.85, 0.85, 0.82), 0.5),
        "concrete": material("コンクリート", (0.55, 0.55, 0.52), 0.8, 25, (0.65, 0.64, 0.60)),
        "dark": material("開口部", (0.01, 0.01, 0.01), 1.0),
        "rail": material("ガードレール", (0.88, 0.88, 0.86), 0.35, metallic=0.2),
        "post": material("支柱", (0.80, 0.80, 0.78), 0.4, metallic=0.3),
        "red": material("赤", (0.6, 0.03, 0.02), 0.4),
        "amber": material("反射体", (1.0, 0.45, 0.0), 0.2),
        "water": material("水", (0.10, 0.16, 0.14), 0.05),
        "terrain": mat_terrain(),
        "stone": mat_stone(),
        "sugi": material("杉", (0.03, 0.09, 0.03), 0.9, 4, (0.05, 0.13, 0.05)),
        "broad": material("広葉樹", (0.10, 0.22, 0.05), 0.9, 4, (0.20, 0.30, 0.06)),
        "trunk": material("幹", (0.12, 0.07, 0.04), 0.9),
    }

    C_ROAD = collection("01_道路")
    C_DRAIN = collection("02_排水構造物")
    C_SAFE = collection("03_安全施設")
    C_WATER = collection("04_水路")
    C_TERRAIN = collection("05_地形")
    C_TREE = collection("06_樹木")

    # --- 地形 ----------------------------------------------------
    s_list = [s * 1.0 for s in range(-70, 271)]
    d_list = sorted(set([x * 0.25 for x in range(-24, 25)] +
                        [x * 0.5 for x in range(-30, 31)] +
                        [float(x) for x in range(-70, 71, 2)]))
    verts, faces = [], []
    nd = len(d_list)
    for s in s_list:
        for d in d_list:
            verts.append(point(s, d, ground(s, d)))
    for i in range(len(s_list) - 1):
        for j in range(nd - 1):
            a = i * nd + j
            faces.append((a, a + 1, a + 1 + nd, a + nd))
    mesh_object("地形", verts, faces, M["terrain"], C_TERRAIN, smooth_shade=True)

    # --- 舗装 ----------------------------------------------------
    road = [(-HALF_W, -0.40), (-HALF_W, -CROSS * HALF_W), (0, 0),
            (HALF_W, -CROSS * HALF_W), (HALF_W, -0.40)]
    sweep("舗装_新設", 0.0, S_END, road, M["asphalt"], C_ROAD, step=0.5)
    sweep("舗装_既設_起点側", -70.0, 0.0, road, M["asphalt_old"], C_ROAD)
    sweep("舗装_既設_終点側", S_END, 270.0, road, M["asphalt_old"], C_ROAD)
    for side in (1, -1):
        d = LINE_D * side
        sweep("サイドライン_" + ("左" if side > 0 else "右"), 0.0, S_END,
              [(d - 0.075, -CROSS * abs(d) + 0.006), (d + 0.075, -CROSS * abs(d) + 0.006)],
              M["line"], C_ROAD, step=0.5)

    # 進入路
    for name, es, side, b, ln in (("第16号進入路", sta(54, 4.5), 1, 3.0, 10.0),
                                  ("第17号進入路", sta(55, 12.4), -1, 4.0, 3.0)):
        vs = []
        for a in (2.5, 3.0 + ln):
            for off in (-b / 2, b / 2):
                p = point(es + off, a * side, ground(es + off, a * side) + 0.03)
                if a == 2.5:
                    p.z = zc(es + off) - CROSS * 2.5 + 0.002
                vs.append(p)
        f = [(0, 1, 3, 2)] if side > 0 else [(0, 2, 3, 1)]
        mesh_object(name, vs, f, M["asphalt"], C_ROAD)

    # --- 側溝 ----------------------------------------------------
    def u_ditch(name, s0, s1, side, lid):
        a0, a1 = HALF_W, HALF_W + 0.5
        top = -CROSS * HALF_W
        if lid:
            prof = [(a0, -0.45), (a0, top), (a1, top), (a1, -0.45)]
        else:
            prof = [(a0, -0.45), (a0, top), (a0 + 0.1, top), (a0 + 0.1, top - 0.3),
                    (a1 - 0.1, top - 0.3), (a1 - 0.1, top), (a1, top), (a1, -0.45)]
        prof = [(d * side, h) for d, h in prof]
        if side < 0:
            prof.reverse()
        sweep(name, s0, s1, prof, M["concrete"], C_DRAIN, step=0.5)
        if not lid:
            inner = [(a0 + 0.1, top - 0.29), (a1 - 0.1, top - 0.29)]
            inner = [(d * side, h) for d, h in inner]
            if side < 0:
                inner.reverse()
            sweep(name + "_底", s0, s1, inner, M["dark"], C_DRAIN, step=0.5)
        else:
            # 落蓋の目地（0.5m ごと）
            n = int((s1 - s0) / 0.5)
            for k in range(n):
                s = s0 + k * 0.5
                p = point(s, (a0 + 0.25) * side, top + 0.002)
                box(f"{name}_目地", p, (0.012, 0.5, 0.004), plan(s)[2], 0, M["dark"], C_DRAIN)

    u_ditch("U型側溝_左", 0.0, sta(53, 13.80), 1, lid=False)
    u_ditch("落蓋式側溝_左", sta(53, 13.80), sta(54, 17.0), 1, lid=True)
    u_ditch("落蓋式側溝_右", sta(55, 7.15), sta(59), -1, lid=True)

    # --- 第3号横断函渠（ボックスカルバート）＋第4・5号面壁 --------
    s_in, s_out = CULVERT_S + 6.5, CULVERT_S - 6.5           # 斜角約60°
    p_in = point(s_in, CH_D, -CH_DEPTH)
    p_out = point(s_out, -CH_D, -CH_DEPTH - 0.3)
    axis = p_out - p_in
    yaw = math.atan2(axis.y, axis.x)
    pitch = math.atan2(axis.z, axis.xy.length)
    ln = axis.length
    mid = (p_in + p_out) / 2
    box("ボックスカルバート_B1200xH1000", mid + Vector((0, 0, 0.63)),
        (ln, 1.46, 1.26), yaw, pitch, M["concrete"], C_DRAIN)
    dirv = axis.normalized()
    for name, p, sgn in (("第4号面壁", p_in, -1), ("第5号面壁", p_out, 1)):
        c = p + Vector((0, 0, 1.25 - 0.2))
        box(name, c, (0.4, 6.0, 2.5), yaw, 0, M["concrete"], C_DRAIN)
        hole = p + dirv * (0.21 * sgn) + Vector((0, 0, 0.6))
        box(name + "_開口", hole, (0.01, 1.2, 1.0), yaw, 0, M["dark"], C_DRAIN)

    # --- 水路（かごマット・ふとんかご・水面） ---------------------
    def channel(name, s0, s1, side):
        bed = -CH_DEPTH
        c = CH_D
        parts = [("かごマット", [(c - 1.7, bed - 0.5), (c - 1.7, bed), (c + 1.7, bed), (c + 1.7, bed - 0.5)])]
        for k in range(3):
            a_in = c - CH_BED / 2 - 0.5 * k
            parts.append((f"ふとんかご_路側{k + 1}段",
                          [(a_in - 1.0, bed + 0.5 * k), (a_in - 1.0, bed + 0.5 * (k + 1)),
                           (a_in, bed + 0.5 * (k + 1)), (a_in, bed + 0.5 * k)]))
            a_out = c + CH_BED / 2 + 0.5 * k
            parts.append((f"ふとんかご_対岸{k + 1}段",
                          [(a_out, bed + 0.5 * k), (a_out, bed + 0.5 * (k + 1)),
                           (a_out + 1.0, bed + 0.5 * (k + 1)), (a_out + 1.0, bed + 0.5 * k)]))
        for pname, prof in parts:
            prof = [(d * side, h) for d, h in prof]
            if side < 0:
                prof.reverse()
            sweep(f"{name}_{pname}", s0, s1, prof, M["stone"], C_WATER, step=1.0, closed=True)
        w = [(c - 0.55, bed + 0.12), (c + 0.55, bed + 0.12)]
        w = [(d * side, h) for d, h in w]
        if side < 0:
            w.reverse()
        sweep(f"{name}_水面", s0 - 30 if side < 0 else s0, s1 + 60 if side > 0 else s1,
              w, M["water"], C_WATER, step=1.0)

    channel("第2号水路舗装工", sta(55, 16.15), sta(59, 2.0), 1)    # L=66m 左
    channel("第1号水路舗装工", sta(54, 3.95) - 4.0, s_out, -1)      # L=14m 右

    # --- ガードレール Gr-C-4E ------------------------------------
    def guardrail(name, s0, s1, side):
        a = HALF_W + 0.25
        n = int((s1 - s0) / 4.0)
        for k in range(n + 1):
            s = s0 + k * (s1 - s0) / n
            p = point(s, a * side, -0.07 + 0.5)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=1.0, location=p, vertices=12)
            ob = bpy.context.active_object
            ob.name = f"{name}_支柱"
            ob.data.materials.append(M["post"])
            for cc in ob.users_collection:
                cc.objects.unlink(ob)
            C_SAFE.objects.link(ob)
        beam = [(a - 0.08, 0.45), (a - 0.14, 0.53), (a - 0.08, 0.62), (a - 0.14, 0.71),
                (a - 0.08, 0.80), (a - 0.06, 0.80), (a - 0.06, 0.45)]
        beam = [(d * side, h - 0.07) for d, h in beam]
        if side < 0:
            beam.reverse()
        sweep(name + "_ビーム", s0 - 0.3, s1 + 0.3, beam, M["rail"], C_SAFE, step=0.5, closed=True)

    guardrail("ガードレール_右_L25", sta(54, 3.95), sta(55, 3.0), -1)
    guardrail("ガードレール_左_L77", sta(55, 10.0), sta(59, 7.0), 1)

    # --- 視線誘導標（スノーポール併用） ----------------------------
    for k in range(13):
        s = 4.0 + k * 7.5
        p = point(s, HALF_W + 0.75, -0.07)
        h = 1.8
        for seg in range(6):
            mat = M["red"] if seg % 2 == 0 else M["post"]
            bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=h / 6,
                                                location=p + Vector((0, 0, h / 12 + seg * h / 6)),
                                                vertices=10)
            ob = bpy.context.active_object
            ob.name = f"視線誘導標_{k + 1:02d}"
            ob.data.materials.append(mat)
            for cc in ob.users_collection:
                cc.objects.unlink(ob)
            C_SAFE.objects.link(ob)
        x, y, a = plan(s)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.01, vertices=16,
                                            location=p + Vector((0, 0, 0.9)) - Vector((-math.sin(a), math.cos(a), 0)) * 0.04,
                                            rotation=(math.pi / 2, 0, a + math.pi / 2))
        ob = bpy.context.active_object
        ob.name = f"視線誘導標_{k + 1:02d}_反射体"
        ob.data.materials.append(M["amber"])
        for cc in ob.users_collection:
            cc.objects.unlink(ob)
        C_SAFE.objects.link(ob)

    # --- 樹木 ----------------------------------------------------
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=1.6, depth=9.0, location=(0, 0, -100))
    sugi = bpy.context.active_object
    sugi.name = "杉_原型"
    sugi.data.materials.append(M["sugi"])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=2.6, location=(0, 0, -100))
    broad = bpy.context.active_object
    broad.name = "広葉樹_原型"
    broad.data.materials.append(M["broad"])
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=4.0, location=(0, 0, -100))
    trunk = bpy.context.active_object
    trunk.name = "幹_原型"
    trunk.data.materials.append(M["trunk"])
    global CAM_EYES
    CAM_EYES = [point(v[0], v[1], 0) for v in CAMS.values()]
    for o in (sugi, broad, trunk):
        for cc in o.users_collection:
            cc.objects.unlink(o)
        C_TREE.objects.link(o)
        o.hide_render = True
        o.hide_viewport = True

    count = 0
    tries = 0
    while count < 900 and tries < 6000:
        tries += 1
        s = random.uniform(-70, 270)
        d = random.choice((-1, 1)) * random.uniform(14.0, 70)
        a = abs(d)
        g0 = point(s, d, 0)
        if any((g0.xy - k.xy).length < 9.0 for k in CAM_EYES):
            continue
        if CH_D - 3 < a < CH_D + 4 and ((d > 0 and w_left(s) > 0.1) or (d < 0 and w_right(s) > 0.1)):
            continue
        g = point(s, d, ground(s, d))
        sc_ = random.uniform(0.75, 1.35)
        is_sugi = random.random() < 0.6
        tr = trunk.copy()
        tr.location = g + Vector((0, 0, 2.0 * sc_))
        tr.scale = (sc_, sc_, sc_)
        tr.hide_render = tr.hide_viewport = False
        C_TREE.objects.link(tr)
        top = (sugi if is_sugi else broad).copy()
        if is_sugi:
            top.location = g + Vector((0, 0, (2.5 + 4.5) * sc_ * 1.2))
            top.scale = (sc_, sc_, sc_ * 1.2)
        else:
            top.location = g + Vector((0, 0, 4.8 * sc_))
            top.scale = (sc_, sc_, sc_ * 0.85)
        top.rotation_euler = (0, 0, random.uniform(0, 6.28))
        top.hide_render = top.hide_viewport = False
        C_TREE.objects.link(top)
        count += 1

    # --- 空・太陽 ------------------------------------------------
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_elevation = math.radians(38)
    sky.sun_rotation = math.radians(150)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.35
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    sun_data = bpy.data.lights.new("太陽", "SUN")
    sun_data.energy = 3.0
    sun_data.angle = math.radians(1.5)
    sun = bpy.data.objects.new("太陽", sun_data)
    sun.rotation_euler = (math.radians(52), 0, math.radians(150 - 90))
    sc.collection.objects.link(sun)

    # --- カメラ --------------------------------------------------
    def camera(name, eye, target, lens):
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.clip_end = 2000
        co = bpy.data.objects.new(name, cd)
        co.location = eye
        direction = target - eye
        co.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(co)
        return co

    cams = {}
    for key, (es, ed, eh, ts, td, th, lens) in CAMS.items():
        cams[key] = camera("CAM_" + key, point(es, ed, ground(es, ed) + eh), point(ts, td, th), lens)
    sc.camera = cams["01_鳥瞰"]
    return cams


def setup_render(sc, samples=64):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.view_settings.exposure = -0.6


if __name__ == "__main__":
    cams = build()
    sc = bpy.context.scene
    setup_render(sc)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--render" in argv:
        import os
        outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
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
    if "--save" in argv:
        import os
        bpy.ops.wm.save_as_mainfile(
            filepath=os.path.join(os.path.dirname(os.path.abspath(__file__)), "futagosawa_kansei.blend"))
