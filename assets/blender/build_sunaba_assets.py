# りったい すなば（3D 試作）の 部品を Blender で 一から作り、assets/models/sunaba.glb に書き出す。
#
#   blender -b --factory-startup --python assets/blender/build_sunaba_assets.py
#
# Blender 4.2 LTS で確認。座標は Blender（Z が上、正面は -Y）で組み立て、
# glTF 書き出し時に Y が上・正面 +Z に変換される。
# ノード名・アニメ名は runtime（js/spots/sunaba3d.js）が名前で使うので変えないこと。

import bpy
import bmesh
import math
import os
import random
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'assets', 'models', 'sunaba.glb')
FPS = 30
SAND = '#e8c98a'

random.seed(7)


# ---------------------------------------------------------------- 準備

def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.actions, bpy.data.curves,
                 bpy.data.cameras, bpy.data.lights):
        for d in list(coll):
            coll.remove(d)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start = 0
    sc.frame_end = 60


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_rgb(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def mix_hex(a, b, t):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return '#' + ''.join('%02x' % round((ra[i] * (1 - t) + rb[i] * t) * 255) for i in range(3))


MATS = {}


def mat(h, rough=0.9):
    """色だけの マテリアル（Principled BSDF・ラフネス高め・テクスチャなし）。同じ色は共有。"""
    key = h.lower()
    if key in MATS:
        return MATS[key]
    lin = [srgb_to_lin(c) for c in hex_rgb(key)]
    m = bpy.data.materials.new('C_' + key.lstrip('#'))
    m.use_nodes = True
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*lin, 1.0)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = 0.0
    bsdf.inputs['Specular IOR Level'].default_value = 0.15
    m.diffuse_color = (*lin, 1.0)
    m.roughness = rough
    m.use_backface_culling = True  # glTF では片面（doubleSided=false）
    MATS[key] = m
    return m


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def place(o, color, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0)):
    o.location = loc
    o.scale = scale
    o.rotation_euler = [math.radians(a) for a in rot]
    o.data.materials.append(mat(color))
    return o


# ---------------------------------------------------------------- 形の部品（1つずつ オブジェクト）

def sphere(color, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), seg=20, rings=12, ico=0):
    if ico:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=ico, radius=1)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1)
    return place(bpy.context.active_object, color, loc, scale, rot)


def cylinder(color, r, depth, loc=(0, 0, 0), rot=(0, 0, 0), verts=16, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth)
    return place(bpy.context.active_object, color, loc, scale, rot)


def cone(color, r1, r2, depth, loc=(0, 0, 0), rot=(0, 0, 0), verts=16, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth)
    return place(bpy.context.active_object, color, loc, scale, rot)


def box(color, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, segs=2):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = place(bpy.context.active_object, color, loc, size, rot)
    if bevel:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        m = o.modifiers.new('Bevel', 'BEVEL')
        m.width = bevel
        m.segments = segs
        m.limit_method = 'ANGLE'
    return o


def torus(color, R, r, loc=(0, 0, 0), rot=(0, 0, 0), keep=None, major_seg=20, minor_seg=8, scale=(1, 1, 1)):
    """keep(v) が False の頂点を消す（半分の輪＝口や取っ手）。"""
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r,
                                     major_segments=major_seg, minor_segments=minor_seg)
    o = bpy.context.active_object
    if keep:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not keep(v.co)], context='VERTS')
        bm.to_mesh(o.data)
        bm.free()
    return place(o, color, loc, scale, rot)


def capsule(color, p0, p1, r, seg=14, rings=10, scale_xy=(1, 1)):
    """p0→p1 の まるい棒（腕・脚・しっぽ）。"""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    L = d.length
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r)
    o = bpy.context.active_object
    for v in o.data.vertices:
        v.co.x *= scale_xy[0]
        v.co.y *= scale_xy[1]
        v.co.z += L / 2 if v.co.z > 1e-6 else -L / 2
    o.location = (p0 + p1) / 2
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = d.to_track_quat('Z', 'Y')
    o.data.materials.append(mat(color))
    return o


def mesh_obj(name, bm, color):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(bpy.data.objects.new(name, me))
    o.data.materials.append(mat(color))
    return o


def lathe(color, prof, segs=16, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0)):
    """(半径, 高さ) の列を Z 軸まわりに回して作る形。"""
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1),
                   angle=2 * math.pi, steps=segs, use_duplicate=False)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj('lathe', bm, color)
    o.data.materials.clear()
    return place(o, color, loc, scale, rot)


def prism(color, pts2d, z0, z1, loc=(0, 0, 0), rot=(0, 0, 0)):
    """XY 平面の多角形を Z 方向に押し出した板。"""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z0)) for x, y in pts2d]
    f = bm.faces.new(vs)
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    top = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, z1 - z0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj('prism', bm, color)
    o.data.materials.clear()
    return place(o, color, loc, (1, 1, 1), rot)


def add_mod(o, kind, **kw):
    m = o.modifiers.new(kind.title(), kind)
    for k, v in kw.items():
        setattr(m, k, v)
    return o


# ---------------------------------------------------------------- まとめる

def shade(o, angle=50):
    """面はなめらか、角度の大きい辺だけ シャープ（書き出し時に法線が分かれる）。"""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    lim = math.radians(angle)
    for f in bm.faces:
        f.smooth = True
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0) < lim
    bm.to_mesh(o.data)
    bm.free()


def finalize(pieces, name, pivot=(0, 0, 0), parent=None, angle=50, floor=False):
    """部品を モディファイア適用 → 1つのメッシュに結合し、原点を pivot に置く。"""
    vl = bpy.context.view_layer
    for o in vl.objects:
        o.select_set(False)
    for o in pieces:
        o.select_set(True)
    vl.objects.active = pieces[0]
    bpy.ops.object.convert(target='MESH')  # モディファイアを適用
    if len(pieces) > 1:
        bpy.ops.object.join()
    o = vl.objects.active
    o.rotation_mode = 'XYZ'
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if floor:  # 底を ぴったり z=0 に（原点 = 底の中心）
        pivot = (pivot[0], pivot[1], min(v.co.z for v in o.data.vertices))
    o.data.transform(Matrix.Translation(-Vector(pivot)))
    if floor:
        pivot = (pivot[0], pivot[1], 0)
    o.location = pivot
    o.name = name
    o.data.name = name
    shade(o, angle)
    if parent:
        o.parent = parent
    return o


def empty(name):
    o = link(bpy.data.objects.new(name, None))
    o.empty_display_type = 'PLAIN_AXES'
    o.empty_display_size = 0.2
    return o


# ---------------------------------------------------------------- キャラクター

# 2D 版 js/characters.js の色
CHARS = {
    'Inu': dict(kind='inu', skin='#d9a066', dark='#a86b3c', smock='#c98b4f',
                hand='#d9a066', leg='#d9a066', foot='#a86b3c'),
    'Pen': dict(kind='pen', skin='#2f4a6d', dark='#1e3350', smock='#3a6ea5',
                hand='#2f4a6d', leg='#2f4a6d', foot='#ff9f1c'),
    'KidGirl': dict(kind='human', style='pigtails', skin='#ffdcbf', hair='#5b3a29', smock='#ff8fb1',
                    hand='#ffdcbf', leg='#ffffff', foot='#e9edf5'),
    'KidBoy': dict(kind='human', style='short', skin='#ffd6b3', hair='#3b2a20', smock='#6aa8ff',
                   hand='#ffd6b3', leg='#ffffff', foot='#e9edf5'),
    'Kid': dict(kind='human', style='bob', skin='#f6cfa8', hair='#4a2f22', smock='#6cc77a',
                hand='#f6cfa8', leg='#ffffff', foot='#e9edf5'),
}

# 関節（Blender 座標・キャラの足もとが原点）
HIP = Vector((0, 0, 0.20))
NECK = Vector((0, 0, 0.44))
SHOULDER = {'L': Vector((0.155, 0, 0.42)), 'R': Vector((-0.155, 0, 0.42))}
HIPJ = {'L': Vector((0.072, 0, 0.20)), 'R': Vector((-0.072, 0, 0.20))}
TAILJ = Vector((0, 0.13, 0.25))
HC = Vector((0, 0, 0.70))           # 頭の中心
HR = Vector((0.27, 0.245, 0.25))    # 頭の半径（大きい頭 = ちびキャラ）


def ell_front(x, z, c, r):
    t = 1 - (x / r.x) ** 2 - ((z - c.z) / r.z) ** 2
    return c.y - r.y * math.sqrt(t) if t > 0 else c.y


def build_hair(cfg):
    style = cfg['style']
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=13, radius=1)
    o = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(o.data)

    def keep(n):
        if style == 'bob':  # おかっぱ：横と後ろは あごまで、前髪は まっすぐ
            if n.z < -0.5:
                return False
            if n.y < -0.3 and n.z < 0.36:
                return False
            return True
        if style == 'short':  # みじかい：耳の上まで、前髪は ギザギザ
            lim = -0.25 if n.y > 0.2 else 0.08
            if n.z < lim:
                return False
            ang = math.atan2(n.x, -n.y)
            bang = 0.46 + 0.07 * math.cos(ang * 14)
            if n.y < -0.5 and n.z < bang:
                return False
            return True
        # ふたつむすび：前髪は 少し ななめ
        lim = -0.35 if n.y > 0.2 else 0.0
        if n.z < lim:
            return False
        if n.y < -0.5 and n.z < 0.40 + 0.12 * n.x:
            return False
        return True

    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not keep(f.calc_center_median().normalized())],
                     context='FACES')
    for v in bm.verts:
        if style == 'bob':
            w = 1 + 0.10 * max(0.0, -v.co.z)  # すそを少し ふくらませる
            v.co.x *= w
            v.co.y *= w
    bm.to_mesh(o.data)
    bm.free()
    place(o, cfg['hair'], HC + Vector((0, 0.008, 0.008)), (HR.x * 1.07, HR.y * 1.08, HR.z * 1.08))
    parts = [o]
    if style == 'pigtails':
        for s in (1, -1):
            parts.append(sphere(cfg['hair'], (s * 0.30, 0.04, 0.64), (0.085, 0.08, 0.10), seg=14, rings=10))
            parts.append(sphere('#ff5c8a', (s * 0.245, 0.02, 0.71), (0.035, 0.035, 0.035), seg=12, rings=8))
    if style == 'short':
        # ぴょこんと はねた毛
        parts.append(cone(cfg['hair'], 0.03, 0.0, 0.11, (0.02, 0.02, 0.98), rot=(-25, 15, 0), verts=10))
    return parts


def build_head(name, cfg, root):
    p = []
    skin = cfg['skin']
    kind = cfg['kind']
    p.append(sphere(skin, HC, tuple(HR), seg=24, rings=12))
    faces = [(HC, HR)]
    if kind == 'pen':  # 白い顔
        pc, pr = Vector((0, -0.055, 0.68)), Vector((0.215, 0.2, 0.205))
        p.append(sphere('#ffffff', pc, tuple(pr), seg=22, rings=12))
        faces.append((pc, pr))

    def front(x, z):
        return min(ell_front(x, z, c, r) for c, r in faces)

    eye_z = 0.705 if kind == 'inu' else 0.69
    for s in (1, -1):
        x = s * 0.095
        y = front(x, eye_z)
        p.append(sphere('#2b2b2b', (x, y + 0.006, eye_z), (0.032, 0.02, 0.043), seg=12, rings=8))
        p.append(sphere('#ffffff', (x + 0.012, y - 0.012, eye_z + 0.016), (0.012, 0.008, 0.012), seg=8, rings=6))
        cx = s * 0.17
        p.append(sphere(mix_hex(skin if kind != 'pen' else '#ffffff', '#ff8fa3', 0.6),
                        (cx, front(cx, 0.625) + 0.008, 0.625), (0.042, 0.012, 0.026), seg=10, rings=6,
                        rot=(-8, 0, s * -25)))

    smile = lambda v: v.y < 0.002  # noqa: E731
    if kind == 'inu':
        mc = Vector((0, front(0, 0.615) + 0.045, 0.615))
        p.append(sphere('#fff4e6', mc, (0.105, 0.075, 0.072), seg=16, rings=10))
        p.append(sphere('#2b2b2b', (0, mc.y - 0.07, 0.655), (0.038, 0.026, 0.026), seg=14, rings=8))
        p.append(torus('#7a3b2e', 0.026, 0.0065, (0, mc.y - 0.068, 0.605), rot=(90, 0, 0), keep=smile))
        dark = cfg['dark']
        for s in (1, -1):  # たれ耳
            p.append(sphere(dark, (s * 0.258, 0.01, 0.66), (0.065, 0.04, 0.135), seg=12, rings=8,
                            rot=(0, s * -18, 0)))
        # 目の上の もよう
        p.append(sphere(mix_hex(skin, dark, 0.55), (0.125, front(0.125, 0.79) + 0.005, 0.79),
                        (0.055, 0.012, 0.045), seg=14, rings=8, rot=(-30, 0, -25)))
    elif kind == 'pen':
        p.append(cone('#ff9f1c', 0.04, 0.0, 0.07, (0, front(0, 0.635) - 0.025, 0.635), rot=(90, 0, 0),
                      verts=12, scale=(1.3, 0.8, 1)))
    else:
        p.append(torus('#7a3b2e', 0.026, 0.0065, (0, front(0, 0.61) - 0.002, 0.61), rot=(90, 0, 0), keep=smile))
        for s in (1, -1):
            p.append(sphere(skin, (s * 0.268, 0.0, 0.665), (0.035, 0.045, 0.055), seg=10, rings=6))
        p += build_hair(cfg)
    return finalize(p, 'Head', NECK, root)


def build_body(name, cfg, root):
    smock = cfg['smock']
    prof = [(0, 0.15), (0.15, 0.15), (0.175, 0.162), (0.18, 0.19), (0.168, 0.27), (0.145, 0.36),
            (0.115, 0.43), (0.075, 0.465), (0, 0.475)]
    body = lathe(smock, prof, segs=10)
    add_mod(body, 'SUBSURF', levels=1, render_levels=1)
    p = [body]
    # 白い えり
    p.append(torus('#ffffff', 0.072, 0.02, (0, -0.005, 0.452), rot=(-8, 0, 0), major_seg=14, minor_seg=5,
                   scale=(1, 1, 0.6)))
    # 名札（黄色）と ポケット
    p.append(cylinder('#ffe066', 0.03, 0.012, (-0.062, -0.142, 0.345), rot=(73, 0, 23), verts=14))
    p.append(box(mix_hex(smock, '#000000', 0.12), (0.08, 0.02, 0.06), (0.065, -0.163, 0.215),
                 rot=(-4, 0, -22), bevel=0.012, segs=2))
    return finalize(p, 'Body', HIP, root)


def build_arm(side, cfg, root):
    s = 1 if side == 'L' else -1
    sh = SHOULDER[side]
    p = [capsule(cfg['smock'], sh, sh + Vector((s * 0.035, 0, -0.15)), 0.046, seg=10, rings=8)]
    hand_c = sh + Vector((s * 0.045, 0, -0.195))
    if cfg['kind'] == 'pen':  # ひれ
        p.append(sphere(cfg['hand'], hand_c + Vector((0, 0, -0.01)), (0.028, 0.05, 0.075), seg=10, rings=8))
    else:
        p.append(sphere(cfg['hand'], hand_c, (0.048, 0.048, 0.048), seg=10, rings=8))
    # そで口
    p.append(torus(mix_hex(cfg['smock'], '#ffffff', 0.35), 0.04, 0.012, sh + Vector((s * 0.033, 0, -0.16)),
                   major_seg=10, minor_seg=4))
    return finalize(p, 'Arm' + side, sh, root)


def build_leg(side, cfg, root):
    s = 1 if side == 'L' else -1
    hj = HIPJ[side]
    p = [capsule(cfg['leg'], hj, Vector((hj.x, 0, 0.07)), 0.047, seg=10, rings=8)]
    if cfg['kind'] == 'pen':
        p.append(sphere(cfg['foot'], (hj.x + s * 0.005, -0.03, 0.025), (0.06, 0.085, 0.025), seg=12, rings=6))
    else:
        p.append(sphere(cfg['foot'], (hj.x, -0.022, 0.038), (0.056, 0.075, 0.04), seg=12, rings=6))
        if cfg['kind'] == 'human':  # くつの ストラップ
            p.append(box(cfg['smock'], (0.1, 0.03, 0.012), (hj.x, -0.04, 0.072), rot=(20, 0, 0)))
    return finalize(p, 'Leg' + side, hj, root)


def build_tail(cfg, root):
    d = cfg['dark']
    p = [capsule(d, TAILJ, (0, 0.23, 0.31), 0.028, seg=8, rings=6),
         capsule(d, (0, 0.23, 0.31), (0, 0.255, 0.4), 0.026, seg=8, rings=6)]
    return finalize(p, 'Tail', TAILJ, root)


def build_character(name, cfg):
    root = empty(name)
    parts = {}
    parts['Body'] = build_body(name, cfg, root)
    parts['Head'] = build_head(name, cfg, root)
    for s in 'LR':
        parts['Arm' + s] = build_arm(s, cfg, root)
        parts['Leg' + s] = build_leg(s, cfg, root)
    if cfg['kind'] == 'inu':
        parts['Tail'] = build_tail(cfg, root)
    # Blender では 名前が重ねられないので「Inu.Head」とし、書き出し後に「Head」へ もどす（fix_node_names）
    for n, o in parts.items():
        o.name = '%s.%s' % (name, n)
        o.data.name = '%s_%s' % (name, n)
    return root, parts


# ---------------------------------------------------------------- アニメーション
#
# ポーズ = {'lift': (dx,dy,dz), 'Body': (rx,ry,rz), 'Head': ..., ...}（角度は度）。
# Body の回転は 頭・腕・しっぽにも 伝える（見かけ上の 親子関係）。脚は腰で つながる。

UPPER = ('Head', 'ArmL', 'ArmR', 'Tail')


def R(*a):
    return a


MOTIONS = {
    # ゆらゆら（2秒）
    'idle': (60, [
        (0, {}),
        (15, {'Body': R(0, 3, 0), 'Head': R(0, -5, 0), 'ArmL': R(0, -3, 0), 'ArmR': R(0, -3, 0),
              'Tail': R(0, 0, 25), 'lift': (0, 0, 0.006)}),
        (30, {}),
        (45, {'Body': R(0, -3, 0), 'Head': R(0, 5, 0), 'ArmL': R(0, 3, 0), 'ArmR': R(0, 3, 0),
              'Tail': R(0, 0, -25), 'lift': (0, 0, 0.006)}),
        (60, {}),
    ]),
    # あるく（1秒で2歩）
    'walk': (30, [
        (0, {'LegL': R(-32, 0, 0), 'LegR': R(32, 0, 0), 'ArmL': R(30, 0, 0), 'ArmR': R(-30, 0, 0),
             'Body': R(3, 0, 3), 'Tail': R(0, 0, 30)}),
        (8, {'lift': (0, 0, 0.03), 'Body': R(3, 0, 0), 'Head': R(-3, 0, 0)}),
        (15, {'LegL': R(32, 0, 0), 'LegR': R(-32, 0, 0), 'ArmL': R(-30, 0, 0), 'ArmR': R(30, 0, 0),
              'Body': R(3, 0, -3), 'Tail': R(0, 0, -30)}),
        (23, {'lift': (0, 0, 0.03), 'Body': R(3, 0, 0), 'Head': R(-3, 0, 0)}),
        (30, 0),  # 0 = 最初と同じ
    ]),
    # スコップで ほる（両手を前に → ぐっと さす → すくい上げる）
    'dig': (30, [
        (0, {'Body': R(20, 0, 0), 'Head': R(-8, 0, 0), 'ArmL': R(-75, 0, -8), 'ArmR': R(-75, 0, 8),
             'LegL': R(-10, 0, 0), 'LegR': R(-10, 0, 0), 'lift': (0, 0, -0.01), 'Tail': R(0, 0, 20)}),
        (10, {'Body': R(32, 0, 0), 'Head': R(-14, 0, 0), 'ArmL': R(-55, 0, -8), 'ArmR': R(-55, 0, 8),
              'LegL': R(-14, 0, 0), 'LegR': R(-14, 0, 0), 'lift': (0, 0, -0.02), 'Tail': R(0, 0, -20)}),
        (20, {'Body': R(12, 0, 0), 'Head': R(-12, 0, 0), 'ArmL': R(-115, 0, -8), 'ArmR': R(-115, 0, 8),
              'LegL': R(-6, 0, 0), 'LegR': R(-6, 0, 0), 'lift': (0, 0, -0.005), 'Tail': R(0, 0, 20)}),
        (30, 0),
    ]),
    # すわる（1秒 同じポーズ。おしりが 原点の高さ y=0 に来る）
    'sit': (30, [
        (0, {'lift': (0, 0, -0.17), 'Body': R(-6, 0, 0), 'Head': R(4, 0, 0),
             'LegL': R(-82, 0, -6), 'LegR': R(-82, 0, 6), 'ArmL': R(-28, 0, -10), 'ArmR': R(-28, 0, 10),
             'Tail': R(-30, 0, 0)}),
        (15, {'lift': (0, 0, -0.165), 'Body': R(-6, 0, 0), 'Head': R(6, 3, 0),
              'LegL': R(-82, 0, -6), 'LegR': R(-82, 0, 6), 'ArmL': R(-28, 0, -10), 'ArmR': R(-28, 0, 10),
              'Tail': R(-30, 0, 15)}),
        (30, 0),
    ]),
    # ばんざい ぴょんぴょん
    'cheer': (30, [
        (0, {'ArmL': R(-15, -122, 0), 'ArmR': R(-15, 122, 0), 'Head': R(-6, 0, 0), 'Tail': R(0, 0, 30)}),
        (7, {'lift': (0, 0, 0.12), 'ArmL': R(-15, -138, 0), 'ArmR': R(-15, 138, 0), 'Head': R(-12, 0, 0),
             'LegL': R(-12, 0, 0), 'LegR': R(10, 0, 0), 'Tail': R(0, 0, -30)}),
        (14, {'ArmL': R(-15, -118, 0), 'ArmR': R(-15, 118, 0), 'Head': R(-4, 0, 0), 'lift': (0, 0, -0.01),
              'Tail': R(0, 0, 30)}),
        (22, {'lift': (0, 0, 0.12), 'ArmL': R(-15, -138, 0), 'ArmR': R(-15, 138, 0), 'Head': R(-12, 0, 0),
              'LegL': R(10, 0, 0), 'LegR': R(-12, 0, 0), 'Tail': R(0, 0, -30)}),
        (30, 0),
    ]),
    # りょうてを まえに（物を もつ・わたす）
    'hold': (60, [
        (0, {'ArmL': R(-80, 0, -14), 'ArmR': R(-80, 0, 14), 'Head': R(6, 0, 0)}),
        (30, {'ArmL': R(-74, 0, -14), 'ArmR': R(-74, 0, 14), 'Head': R(6, 4, 0), 'Body': R(0, 2, 0),
              'lift': (0, 0, 0.008), 'Tail': R(0, 0, 20)}),
        (60, 0),
    ]),
    # 手を ふる（右手）
    'wave': (60, [
        (0, {'ArmR': R(-15, 118, 0), 'Head': R(0, 6, 0), 'Body': R(0, 2, 0)}),
        (10, {'ArmR': R(-15, 138, 15), 'Head': R(0, 8, 0), 'Body': R(0, 3, 0), 'Tail': R(0, 0, 30)}),
        (20, {'ArmR': R(-15, 98, -15), 'Head': R(0, 5, 0), 'Body': R(0, 1, 0), 'Tail': R(0, 0, -30)}),
        (30, {'ArmR': R(-15, 138, 15), 'Head': R(0, 8, 0), 'Body': R(0, 3, 0), 'Tail': R(0, 0, 30)}),
        (40, {'ArmR': R(-15, 98, -15), 'Head': R(0, 5, 0), 'Body': R(0, 1, 0), 'Tail': R(0, 0, -30)}),
        (50, {'ArmR': R(-15, 128, 8), 'Head': R(0, 7, 0), 'Body': R(0, 2, 0)}),
        (60, 0),
    ]),
}


def solve_pose(pose, parts):
    """各パーツの (location, euler) を求める。"""
    lift = Vector(pose.get('lift', (0, 0, 0)))
    rb = Euler([math.radians(a) for a in pose.get('Body', (0, 0, 0))]).to_matrix()
    out = {}
    for n, o in parts.items():
        rest = o['rest']
        rot = Euler([math.radians(a) for a in pose.get(n, (0, 0, 0))]).to_matrix()
        if n in UPPER:
            loc = HIP + lift + rb @ (Vector(rest) - HIP)
            rot = rb @ rot
        elif n == 'Body':
            loc = Vector(rest) + lift
            rot = rb
        else:
            loc = Vector(rest) + lift
        out[n] = (loc, rot)
    return out


def animate(cname, parts):
    for o in parts.values():
        o['rest'] = list(o.location)
        o.animation_data_create()
    for motion, (length, keys) in MOTIONS.items():
        first = keys[0][1]
        acts = {}
        for n, o in parts.items():
            a = bpy.data.actions.new('%s_%s_%s' % (cname, n, motion))
            o.animation_data.action = a
            acts[n] = a
        for frame, pose in keys:
            if pose == 0:
                pose = first
            sol = solve_pose(pose, parts)
            for n, o in parts.items():
                loc, rot = sol[n]
                o.location = loc
                prev = o.rotation_euler.copy()
                o.rotation_euler = rot.to_euler('XYZ', prev)
                o.keyframe_insert('location', frame=frame)
                o.keyframe_insert('rotation_euler', frame=frame)
        track_name = '%s_%s' % (cname, motion)
        for n, o in parts.items():
            a = acts[n]
            for fc in a.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'BEZIER'
                    kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
            o.animation_data.action = None
            tr = o.animation_data.nla_tracks.new()
            tr.name = track_name
            tr.mute = True  # Blender 上では 重ならないように（書き出しには影響なし）
            st = tr.strips.new(track_name, 0, a)
            st.extrapolation = 'NOTHING'
    # 休みのポーズに もどす
    for o in parts.values():
        o.location = o['rest']
        o.rotation_euler = (0, 0, 0)
        del o['rest']


# ---------------------------------------------------------------- 道具・型・かざり

def build_shovel():
    p = [cylinder('#e63b2e', 0.017, 0.30, (0, 0, 0.32)),
         cylinder('#e63b2e', 0.022, 0.11, (0, 0, 0.478), rot=(0, 90, 0), verts=12),  # にぎり
         sphere('#e63b2e', (0.055, 0, 0.478), (0.024, 0.024, 0.024), seg=10, rings=6),
         sphere('#e63b2e', (-0.055, 0, 0.478), (0.024, 0.024, 0.024), seg=10, rings=6),
         cylinder('#3d7be0', 0.024, 0.05, (0, 0, 0.18))]
    # すくう所：まるい さじ形を すこし まげる
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=1)
    blade = bpy.context.active_object
    for v in blade.data.vertices:
        v.co.y = v.co.y * 0.22 + 0.35 * v.co.x * v.co.x
    place(blade, '#3d7be0', (0, 0, 0.095), (0.075, 0.1, 0.095))
    p.append(blade)
    return finalize(p, 'Shovel', (0, 0, 0), floor=True)


def build_bucket():
    body = lathe('#3d7be0', [(0, 0.0), (0.1, 0.0), (0.105, 0.005), (0.13, 0.285), (0.138, 0.3)], segs=18)
    add_mod(body, 'SOLIDIFY', thickness=0.012, offset=-1.0)
    p = [body,
         torus('#2a5bb0', 0.136, 0.012, (0, 0, 0.297), major_seg=18, minor_seg=4),
         torus('#ffd23f', 0.13, 0.007, (0, 0, 0.285), rot=(90, 0, 0), keep=lambda v: v.y > -0.01,
               major_seg=24, minor_seg=6)]
    return finalize(p, 'Bucket', (0, 0, 0), floor=True)


def build_watering_can():
    g, lg = '#43a857', '#8bd17c'
    p = [lathe(g, [(0, 0), (0.11, 0), (0.115, 0.01), (0.115, 0.15), (0.1, 0.19), (0.06, 0.215),
                   (0.04, 0.22), (0, 0.22)], segs=20),
         capsule(g, (0, -0.07, 0.07), (0, -0.25, 0.25), 0.02, seg=10, rings=6),
         cone(lg, 0.022, 0.045, 0.04, (0, -0.265, 0.265), rot=(-45, 0, 0), verts=14),
         torus(g, 0.085, 0.014, (0, 0.06, 0.21), rot=(90, 0, 90), keep=lambda v: v.y > -0.03,
               major_seg=18, minor_seg=6),
         sphere(lg, (0, 0, 0.225), (0.035, 0.035, 0.015), seg=12, rings=6)]
    return finalize(p, 'WateringCan', (0, 0, 0), floor=True)


def build_castle():
    p = [box(SAND, (0.9, 0.9, 0.24), (0, 0, 0.12), bevel=0.03, segs=1)]
    p.append(box(SAND, (0.46, 0.46, 0.3), (0, 0.04, 0.39), bevel=0.02, segs=1))
    # まんなかの 塔
    p.append(cylinder(SAND, 0.13, 0.2, (0, 0.04, 0.64), verts=20))
    for i in range(6):
        a = i / 6 * 2 * math.pi
        p.append(box(SAND, (0.06, 0.05, 0.06), (0.11 * math.cos(a), 0.04 + 0.11 * math.sin(a), 0.765),
                     rot=(0, 0, math.degrees(a))))
    # 四すみの 塔
    for sx in (1, -1):
        for sy in (1, -1):
            c = Vector((sx * 0.33, sy * 0.33, 0))
            p.append(cylinder(SAND, 0.115, 0.42, (c.x, c.y, 0.21), verts=14))
            for i in range(5):
                a = i / 5 * 2 * math.pi
                p.append(box(SAND, (0.05, 0.045, 0.05), (c.x + 0.095 * math.cos(a), c.y + 0.095 * math.sin(a), 0.445),
                             rot=(0, 0, math.degrees(a))))
            # まど
            p.append(box('#b8955a', (0.04, 0.02, 0.06), (c.x, c.y - 0.112, 0.31), bevel=0.008))
    # 門（正面 = -Y）
    gate = '#7a5833'
    arch = [(0.08, 0.0)] + [(0.08 * math.cos(i / 10 * math.pi), 0.1 + 0.08 * math.sin(i / 10 * math.pi))
                            for i in range(11)] + [(-0.08, 0.0)]
    p.append(prism(gate, arch, 0.0, 0.025, (0, -0.445, 0), rot=(90, 0, 0)))
    p.append(box(gate, (0.06, 0.03, 0.08), (0, -0.19, 0.4), bevel=0.01))
    return finalize(p, 'CastleMold', (0, 0, 0), floor=True, angle=40)


def build_fish():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=10, radius=1)
    body = bpy.context.active_object
    for v in body.data.vertices:
        if v.co.z < 0:
            v.co.z *= 0.15  # 底を 平らに
    place(body, SAND, (0.06, 0, 0.0), (0.24, 0.13, 0.1))
    tail = prism(SAND, [(-0.13, 0), (-0.30, 0.12), (-0.26, 0), (-0.30, -0.12)], 0, 0.06)
    add_mod(tail, 'BEVEL', width=0.015, segments=2)
    p = [body, tail,
         sphere('#b8955a', (0.2, -0.065, 0.055), (0.018, 0.012, 0.018), seg=10, rings=6),
         sphere('#b8955a', (0.2, 0.065, 0.055), (0.018, 0.012, 0.018), seg=10, rings=6)]
    # えらの 線
    return finalize(p, 'FishMold', (0, 0, 0), floor=True)


def build_star():
    bm = bmesh.new()
    ring_b, ring_t = [], []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        r = 0.3 if i % 2 == 0 else 0.13
        ring_b.append(bm.verts.new((r * math.cos(a), r * math.sin(a), 0)))
        ring_t.append(bm.verts.new((r * 0.92 * math.cos(a), r * 0.92 * math.sin(a), 0.06)))
    cb = bm.verts.new((0, 0, 0))
    ct = bm.verts.new((0, 0, 0.1))
    for i in range(10):
        j = (i + 1) % 10
        bm.faces.new((ring_b[j], ring_b[i], cb))
        bm.faces.new((ring_t[i], ring_t[j], ct))
        bm.faces.new((ring_b[i], ring_b[j], ring_t[j], ring_t[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = mesh_obj('star', bm, SAND)
    return finalize([o], 'StarMold', (0, 0, 0), floor=True, angle=35)


def build_flag():
    p = [cylinder('#f4f1ea', 0.007, 0.3, (0, 0, 0.15), verts=8),
         sphere('#ffd23f', (0, 0, 0.302), (0.012, 0.012, 0.012), seg=8, rings=6)]
    flag = prism('#e63b2e', [(0.0, 0.29), (0.0, 0.19), (0.13, 0.24)], -0.004, 0.004)
    flag.rotation_euler = (math.radians(90), 0, 0)
    flag.location = (0, 0, 0)
    p.append(flag)
    return finalize(p, 'Flag', (0, 0, 0))


def build_tunnel_arch():
    """トンネル入口の縁取り：外幅0.6 高さ0.45 厚み0.2、開口 幅0.4 高さ0.32（正面 = -Y = glTF +Z）。"""
    color = '#d9b77a'
    N = 16

    def outline(half_w, h):
        straight = h - half_w
        pts = [(half_w, 0.0)]
        for i in range(N + 1):
            a = i / N * math.pi
            pts.append((half_w * math.cos(a), straight + half_w * math.sin(a)))
        pts.append((-half_w, 0.0))
        return pts

    outer, inner = outline(0.3, 0.45), outline(0.2, 0.32)
    bm = bmesh.new()
    fo = [bm.verts.new((x, -0.1, z)) for x, z in outer]
    fi = [bm.verts.new((x, -0.1, z)) for x, z in inner]
    faces = [bm.faces.new((fo[i], fo[i + 1], fi[i + 1], fi[i])) for i in range(len(outer) - 1)]
    r = bmesh.ops.extrude_face_region(bm, geom=faces)
    bmesh.ops.translate(bm, verts=[e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)], vec=(0, 0.2, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    arch = mesh_obj('arch', bm, color)
    add_mod(arch, 'BEVEL', width=0.018, segments=1, limit_method='ANGLE')
    # 開口の奥を ふさぐ 暗い面（少し奥へ 引っこめる）
    bm = bmesh.new()
    vs = [bm.verts.new((x * 1.02, 0.085, z)) for x, z in inner]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    back = mesh_obj('hole', bm, '#3b2a1e')
    p = [arch, back]
    # 上に のせた 小石
    stones = [(-0.16, 0.41, 0.03, '#9a958c'), (-0.04, 0.455, 0.036, '#b5afa4'), (0.08, 0.452, 0.03, '#8d877e'),
              (0.18, 0.40, 0.026, '#a8a297'), (0.0, 0.45, 0.024, '#c4beb2')]
    for x, z, s, c in stones:
        st = sphere(c, (x, random.uniform(-0.05, 0.05), z + s * 0.4), (s * 1.2, s, s * 0.8), ico=2)
        st.rotation_euler = (0, 0, random.uniform(0, 3))
        p.append(st)
    return finalize(p, 'TunnelArch', (0, 0, 0), floor=True, angle=40)


def build_shell():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=27, ring_count=7, radius=1)
    o = bpy.context.active_object
    for v in o.data.vertices:
        if v.co.z < 0:
            v.co.z *= 0.2
        phi = math.atan2(v.co.x, v.co.y)
        k = 1 + 0.09 * math.cos(phi * 9) * (1 - abs(v.co.z))
        v.co.x *= k
        v.co.y *= k
        v.co.y -= 0.35 * (v.co.x ** 2)  # 扇形に
    place(o, '#ffc2b0', (0, 0.01, 0.0), (0.09, 0.08, 0.04))
    p = [o, box('#f2a28c', (0.05, 0.035, 0.022), (0, 0.075, 0.011), bevel=0.008)]
    return finalize(p, 'Shell', (0, 0, 0), floor=True)


def build_leaf():
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1)
    o = bpy.context.active_object
    for v in o.data.vertices:
        v.co.y *= (1 - 0.35 * abs(v.co.x)) * (1 - 0.2 * v.co.x)  # 先を とがらせる
        if v.co.z < 0:
            v.co.z *= 0.3
        v.co.z += 0.6 * v.co.x * v.co.x  # 少し そらす
    place(o, '#5fb548', (0, 0, 0), (0.11, 0.05, 0.015))
    p = [o, capsule('#3f8a35', (-0.13, 0, 0.012), (0.1, 0, 0.022), 0.006, seg=8, rings=4)]
    return finalize(p, 'Leaf', (0, 0, 0), floor=True)


def build_flower():
    p = [cylinder('#4f9a3f', 0.008, 0.16, (0, 0, 0.08), verts=8),
         sphere('#5fb548', (0.03, 0, 0.05), (0.035, 0.012, 0.018), seg=10, rings=6, rot=(0, -30, 0))]
    for i in range(5):
        a = i / 5 * 2 * math.pi
        p.append(sphere('#ff7eb0', (0.035 * math.cos(a), 0.035 * math.sin(a) - 0.01, 0.17),
                        (0.03, 0.022, 0.012), seg=8, rings=5, rot=(-25, 0, math.degrees(a))))
    p.append(sphere('#ffd23f', (0, -0.012, 0.175), (0.02, 0.02, 0.015), seg=10, rings=6))
    return finalize(p, 'Flower', (0, 0, 0), floor=True)


def build_rock():
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
    o = bpy.context.active_object
    for v in o.data.vertices:
        v.co *= 1 + random.uniform(-0.12, 0.12)
        if v.co.z < -0.2:
            v.co.z = -0.2
    place(o, '#a39e94', (0, 0, 0.2 * 0.07), (0.11, 0.09, 0.07))
    return finalize([o], 'Rock', (0, 0, 0), floor=True, angle=70)


def build_frame():
    wood, seat = '#b9824a', '#d6a265'
    W, H, T = 4.0, 0.35, 0.4
    p = [box(wood, (2 * (W + T), T, H), (0, W + T / 2, H / 2), bevel=0.04, segs=2),
         box(wood, (2 * (W + T), T, H), (0, -W - T / 2, H / 2), bevel=0.04, segs=2),
         box(wood, (T, 2 * W, H), (W + T / 2, 0, H / 2), bevel=0.04, segs=2),
         box(wood, (T, 2 * W, H), (-W - T / 2, 0, H / 2), bevel=0.04, segs=2)]
    # 板の すきま（線）
    for sgn in (1, -1):
        for x in (-2.0, 0.0, 2.0):
            p.append(box('#9a6a3a', (0.03, T + 0.01, 0.02), (x, sgn * (W + T / 2), H + 0.001)))
            p.append(box('#9a6a3a', (T + 0.01, 0.03, 0.02), (sgn * (W + T / 2), x, H + 0.001)))
    # 四すみの 座れる 角板（三角の板）
    for sx in (1, -1):
        for sy in (1, -1):
            o = W + T
            pts = [(sx * o, sy * o), (sx * (o - 1.3), sy * o), (sx * o, sy * (o - 1.3))]
            if sx * sy < 0:
                pts = [pts[0], pts[2], pts[1]]
            pr = prism(seat, pts, H, H + 0.06)
            add_mod(pr, 'BEVEL', width=0.02, segments=2, limit_method='ANGLE')
            p.append(pr)
    return finalize(p, 'Frame', (0, 0, 0), angle=40)


def build_tree(name, parent=None, loc=(0, 0, 0)):
    trunk = lathe('#8b5a2b', [(0, 0), (0.2, 0), (0.15, 0.1), (0.12, 0.6), (0.11, 1.5), (0, 1.5)], segs=12)
    p = [trunk,
         sphere('#5aa84a', (0, 0, 1.95), (0.85, 0.85, 0.72), ico=2),
         sphere('#6cbf5a', (0.35, -0.2, 2.15), (0.55, 0.55, 0.5), ico=2),
         sphere('#6cbf5a', (-0.35, 0.15, 2.2), (0.5, 0.5, 0.45), ico=2),
         sphere('#7fcf68', (0, 0, 2.6), (0.45, 0.45, 0.4), ico=2)]
    o = finalize(p, name, (0, 0, 0), angle=60)
    for poly in o.data.polygons:  # 葉っぱは ころっと 面で
        poly.use_smooth = poly.material_index == 0
    o.location = loc
    if parent:
        o.parent = parent
    return o


def build_ground():
    bm = bmesh.new()
    G, W = 10.0, 4.0
    xs = [-G, -W, W, G]
    v = [[bm.verts.new((x, y, 0)) for x in xs] for y in xs]
    for j in range(3):
        for i in range(3):
            if i == 1 and j == 1:
                continue  # 砂場の中は 穴（runtime の砂が入る）
            bm.faces.new((v[j][i], v[j][i + 1], v[j + 1][i + 1], v[j + 1][i]))
    o = mesh_obj('Ground', bm, '#8cc96b')
    o = finalize([o], 'Ground', (0, 0, 0))
    build_tree('GroundTree1', o, (-6.8, 6.2, 0))
    build_tree('GroundTree2', o, (7.2, 5.4, 0))
    return o


# ---------------------------------------------------------------- 書き出し後の なおし

def fix_node_names(path):
    """キャラの子ノード名「Inu.Head」→「Head」（契約どおり。glTF では同じ名前が あってよい）。"""
    import json
    import struct
    data = open(path, 'rb').read()
    magic, ver, _ = struct.unpack_from('<4sII', data, 0)
    jlen, jtype = struct.unpack_from('<I4s', data, 12)
    gj = json.loads(data[20:20 + jlen].decode('utf-8'))
    rest = data[20 + jlen:]
    for n in gj.get('nodes', []):
        if n.get('name', '').split('.')[0] in CHARS and '.' in n['name']:
            n['name'] = n['name'].split('.', 1)[1]
    js = json.dumps(gj, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    js += b' ' * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + len(rest)
    out = struct.pack('<4sII', magic, ver, total) + struct.pack('<I4s', len(js), jtype) + js + rest
    open(path, 'wb').write(out)


# ---------------------------------------------------------------- メイン

def main():
    clear_scene()
    layout_x = {'Inu': -2.0, 'Pen': -1.0, 'KidGirl': 0.0, 'KidBoy': 1.0, 'Kid': 2.0}
    for name, cfg in CHARS.items():
        root, parts = build_character(name, cfg)
        animate(name, parts)
        root.location = (layout_x[name], 1.5, 0)

    props = [build_shovel(), build_bucket(), build_watering_can(), build_flag(),
             build_shell(), build_leaf(), build_flower(), build_rock()]
    for i, o in enumerate(props):
        o.location = (-2.1 + i * 0.6, -0.6, 0)
    for o, x in ((build_castle(), -2.2), (build_fish(), -0.6), (build_star(), 0.6), (build_tunnel_arch(), 2.0)):
        o.location = (x, -2.4, 0)
    build_frame()
    build_ground()
    build_tree('Tree', None, (0, 9.0, 0))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    bpy.context.scene.frame_set(0)
    bpy.ops.export_scene.gltf(
        filepath=OUT, export_format='GLB', use_selection=False,
        export_apply=True, export_yup=True,
        export_texcoords=False, export_normals=True, export_tangents=False,
        export_vertex_color='NONE',
        export_materials='EXPORT', export_cameras=False, export_lights=False,
        export_animations=True, export_animation_mode='NLA_TRACKS',
        export_force_sampling=True, export_frame_step=2,
        # 一定の チャンネル（すわりの 脚の角度など）も消さずに残す。どのアニメも 全パーツを持つ
        export_optimize_animation_size=False, export_optimize_animation_keep_anim_object=True,
        export_anim_slide_to_zero=True,
        export_skins=False, export_morph=False, export_extras=False,
    )
    fix_node_names(OUT)
    tris = sum(len(p.vertices) - 2 for o in bpy.data.objects if o.type == 'MESH' for p in o.data.polygons)
    print('SUNABA_EXPORT', OUT, 'tris~', tris, 'bytes', os.path.getsize(OUT))


main()
