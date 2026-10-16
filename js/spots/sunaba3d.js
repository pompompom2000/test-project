// りったい すなば（3D 試作）：ななめ うえから みた すなばで、ほったり もりあげたり、トンネル・かたぬき・みず・かざりで じゆうに あそぶ
// しゃかいせい：いぬくん「スコップ かして？」→ どうぞ／じゅんばんこ → いぬくんが みぞを つなげて おみずを ながして かえしてくれる
// ぶひん：assets/models/sunaba.glb（Blender で つくった もの）。よめない ときは buildFallbackAssets() の かわりの ぶひんで うごく
(function () {
  'use strict';

  const MODEL_URL = 'assets/models/sunaba.glb';

  // ---- すなの たかさマップ（N×N の こうし。8m×8m） ----
  const N = 128;
  const HALF = 4;
  const CELL = (HALF * 2) / (N - 1);
  const SAND_Y = 0.3;          // たいらな すなの たかさ（ふちは 0.35）
  const H_MIN = -0.28;
  const H_MAX = 0.7;
  const DEG = Math.PI / 180;
  const PITCH_MIN = 25 * DEG;
  const PITCH_MAX = 70 * DEG;

  // トンネル
  const TUNNEL_R = 0.14;       // とおりみちの はば（はんけい）
  const TUNNEL_RISE = 0.22;    // おやまが まわりより これだけ たかいと ほれる
  const TUNNEL_CEIL = 0.2;     // ゆかから てんじょうの すなの うえまでが これより うすいと くずれる

  const PARTS = ['Body', 'Head', 'ArmL', 'ArmR', 'LegL', 'LegR', 'Tail'];
  const VERBS = ['idle', 'walk', 'dig', 'sit', 'cheer', 'hold', 'wave'];
  const KIND_NODE = { 'kid-girl': 'KidGirl', 'kid-boy': 'KidBoy', kid: 'Kid' };
  const ROOT_NODES = ['Inu', 'Pen', 'KidGirl', 'KidBoy', 'Kid', 'Shovel', 'Bucket', 'WateringCan', 'CastleMold', 'FishMold', 'StarMold',
    'Flag', 'Frame', 'Shell', 'Leaf', 'Flower', 'Rock', 'Ground', 'Tree', 'TunnelArch'];

  const SVG_SHOVEL = '<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="29" y="6" width="6" height="30" rx="3" fill="#b9793f"/><rect x="21" y="2" width="22" height="9" rx="4.5" fill="#ff6b6b"/><path d="M17 33h30v9c0 10-7 17-15 20-8-3-15-10-15-20z" fill="#4d8dff"/><path d="M22 38h20" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/></svg>';
  const SVG_CAN = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M20 28c0-15 20-15 20 0" fill="none" stroke="#2a9d5a" stroke-width="5"/><path d="M41 36l14-14 4 4-14 16z" fill="#3cc46b"/><rect x="51" y="13" width="11" height="9" rx="2" transform="rotate(45 56 18)" fill="#2a9d5a"/><path d="M12 28h30v25a5 5 0 0 1-5 5H17a5 5 0 0 1-5-5z" fill="#3cc46b"/><circle cx="60" cy="8" r="2.5" fill="#5ab8ff"/><circle cx="62" cy="14" r="2" fill="#5ab8ff"/></svg>';
  const SVG_TUNNEL = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M2 56C10 22 22 10 32 10s22 12 30 46z" fill="#e8c98a"/><path d="M2 56C10 22 22 10 32 10" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="3"/><path d="M19 56V45a13 13 0 0 1 26 0v11z" fill="#c9a46a"/><path d="M23 56V46a9 9 0 0 1 18 0v10z" fill="#4a3424"/><path d="M26 54h12" stroke="#5ab8ff" stroke-width="3" stroke-linecap="round"/></svg>';

  const TOOLS = [
    { id: 'dig', label: 'ほる', icon: SVG_SHOVEL, svg: true, say: 'スコップで ほろう。ゆびで なぞってね。' },
    { id: 'mound', label: 'もりあげる', icon: '✋', say: 'てのひらで おやまを つくろう。ゆびで なぞってね。' },
    { id: 'tunnel', label: 'トンネル', icon: SVG_TUNNEL, svg: true, say: 'トンネルを ほろう。おやまの こっちから むこうまで、ゆびで なぞってね。' },
    { id: 'bucket', label: 'バケツ', icon: '🪣', say: 'バケツで かたぬき！ かたちを えらんで、すなを タップしてね。' },
    { id: 'water', label: 'じょうろ', icon: SVG_CAN, svg: true, say: 'じょうろで おみず。おしている あいだ でるよ。' },
    { id: 'deco', label: 'かざり', icon: '🐚', say: 'かざりを おこう。タップした ところに おけるよ。' },
  ];
  const MOLDS = [
    { id: 'castle', node: 'CastleMold', emoji: '🏰', name: 'おしろ', r: 0.5 },
    { id: 'fish', node: 'FishMold', emoji: '🐟', name: 'さかな', r: 0.36 },
    { id: 'star', node: 'StarMold', emoji: '⭐', name: 'ほし', r: 0.36 },
  ];
  const DECOS = [
    { id: 'shell', node: 'Shell', emoji: '🐚', name: 'かいがら' },
    { id: 'leaf', node: 'Leaf', emoji: '🍃', name: 'はっぱ' },
    { id: 'flower', node: 'Flower', emoji: '🌸', name: 'おはな' },
    { id: 'rock', node: 'Rock', emoji: '🪨', name: 'いし' },
  ];
  const MOLD_BY = Object.fromEntries(MOLDS.map((m) => [m.id, m]));
  const DECO_BY = Object.fromEntries(DECOS.map((d) => [d.id, d]));

  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const lerp = (a, b, t) => a + (b - a) * t;
  const col = (hex) => new THREE.Color(hex).convertSRGBToLinear();
  const angleDiff = (a, b) => { let d = (b - a) % (Math.PI * 2); if (d > Math.PI) d -= Math.PI * 2; if (d < -Math.PI) d += Math.PI * 2; return d; };

  // ---- Float32Array ⇔ base64（ほぞん よう） ----
  function encodeF32(a) {
    const u8 = new Uint8Array(a.buffer, a.byteOffset, a.byteLength);
    let s = '';
    for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
    return btoa(s);
  }
  function decodeF32(str, len) {
    try {
      const bin = atob(str);
      if (bin.length !== len * 4) return null;
      const u8 = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
      const out = new Float32Array(u8.buffer);
      for (let i = 0; i < len; i++) if (!Number.isFinite(out[i])) return null;
      return out;
    } catch (e) { return null; }
  }

  // ---- glb の よみこみ（いちど よめたら おぼえておく） ----
  let glbCache = null;
  let glbPending = null;
  function loadGlb() {
    if (glbCache) return Promise.resolve(glbCache);
    if (glbPending) return glbPending;
    glbPending = new Promise((resolve) => {
      if (!THREE.GLTFLoader) { glbPending = null; resolve(null); return; }
      let done = false;
      const finish = (g) => { if (done) return; done = true; clearTimeout(timer); glbPending = null; if (g) glbCache = g; resolve(g); };
      const timer = setTimeout(() => finish(null), 8000);
      try {
        new THREE.GLTFLoader().load(MODEL_URL, (g) => finish(g), undefined, () => finish(null));
      } catch (e) { finish(null); }
    });
    return glbPending;
  }

  // ---- かわりの ぶひん（three.js の きほんの かたち。glb と おなじ なまえ） ----
  function buildFallbackAssets() {
    const mats = {};
    const M = (hex, flat) => {
      const k = hex + (flat ? 'f' : '');
      if (!mats[k]) mats[k] = new THREE.MeshToonMaterial({ color: col(hex) });
      if (flat) mats[k].flatShading = true;
      return mats[k];
    };
    const mesh = (geo, hex, x = 0, y = 0, z = 0, flat) => {
      const m = new THREE.Mesh(geo, M(hex, flat));
      m.position.set(x, y, z);
      m.castShadow = true;
      m.receiveShadow = true;
      return m;
    };
    const group = (name, x = 0, y = 0, z = 0) => { const g = new THREE.Group(); g.name = name; g.position.set(x, y, z); return g; };
    const sphere = (r, ws = 18, hs = 12) => new THREE.SphereGeometry(r, ws, hs);
    const nodes = {};

    // キャラ（あしもとが げんてん、+Z が まえ）
    function person(name, o) {
      const root = group(name);
      const body = group('Body');
      body.add(mesh(new THREE.CylinderGeometry(0.16, 0.24, 0.42, 18), o.smock, 0, 0.5, 0));
      const collar = mesh(new THREE.TorusGeometry(0.12, 0.03, 8, 18), '#ffffff', 0, 0.7, 0);
      collar.rotation.x = Math.PI / 2;
      body.add(collar);
      // ポケット
      body.add(mesh(new THREE.BoxGeometry(0.12, 0.08, 0.02), '#ffffff', 0.07, 0.42, 0.2));
      root.add(body);

      const head = group('Head', 0, 0.7, 0);
      const skin = o.skin;
      head.add(mesh(sphere(0.21, 22, 16), o.headColor || skin, 0, 0.2, 0));
      const eye = sphere(0.026, 10, 8);
      head.add(mesh(eye, '#2b2118', -0.075, 0.23, 0.19), mesh(eye, '#2b2118', 0.075, 0.23, 0.19));
      if (o.head === 'kid') {
        const cheek = sphere(0.03, 10, 8);
        const c1 = mesh(cheek, '#ff9fae', -0.12, 0.16, 0.16); c1.scale.set(1, 0.6, 0.4);
        const c2 = mesh(cheek, '#ff9fae', 0.12, 0.16, 0.16); c2.scale.set(1, 0.6, 0.4);
        head.add(c1, c2);
        const cap = mesh(new THREE.SphereGeometry(0.225, 22, 12, 0, Math.PI * 2, 0, Math.PI * (o.style === 'short' ? 0.42 : 0.52)), o.hair, 0, 0.2, -0.01);
        cap.rotation.x = -0.32;
        head.add(cap);
        if (o.style === 'pigtails') {
          head.add(mesh(sphere(0.075), o.hair, -0.22, 0.15, -0.06), mesh(sphere(0.075), o.hair, 0.22, 0.15, -0.06));
          head.add(mesh(sphere(0.03), '#ff5d8f', -0.19, 0.22, -0.05), mesh(sphere(0.03), '#ff5d8f', 0.19, 0.22, -0.05));
        } else if (o.style === 'bob') {
          const back = mesh(new THREE.SphereGeometry(0.228, 22, 12, Math.PI * 0.75, Math.PI * 1.5, 0, Math.PI * 0.62), o.hair, 0, 0.2, 0);
          head.add(back);
        }
      } else if (o.head === 'dog') {
        const ear = sphere(0.1, 14, 10);
        const e1 = mesh(ear, o.dark, -0.2, 0.17, -0.01); e1.scale.set(0.45, 1, 0.3); e1.rotation.z = -0.35;
        const e2 = mesh(ear, o.dark, 0.2, 0.17, -0.01); e2.scale.set(0.45, 1, 0.3); e2.rotation.z = 0.35;
        const muzzle = mesh(sphere(0.1, 16, 12), '#fff6ea', 0, 0.13, 0.16); muzzle.scale.set(1.1, 0.8, 0.85);
        head.add(e1, e2, muzzle, mesh(sphere(0.035, 10, 8), '#1d1712', 0, 0.17, 0.25));
      } else if (o.head === 'pen') {
        const face = mesh(sphere(0.17, 18, 12), '#ffffff', 0, 0.18, 0.07); face.scale.set(1, 0.95, 0.85);
        const beak = mesh(new THREE.ConeGeometry(0.045, 0.1, 10), '#ffa62b', 0, 0.16, 0.24); beak.rotation.x = Math.PI / 2;
        head.add(face, beak);
      }
      root.add(head);

      const arm = (nm, x) => {
        const g = group(nm, x, 0.66, 0);
        const sleeve = mesh(new THREE.CylinderGeometry(0.055, 0.06, 0.2, 10), o.smock, 0, -0.1, 0);
        g.add(sleeve, mesh(sphere(0.06, 12, 10), o.hand || skin, 0, -0.25, 0));
        return g;
      };
      root.add(arm('ArmL', 0.215), arm('ArmR', -0.215));
      const leg = (nm, x) => {
        const g = group(nm, x, 0.3, 0);
        g.add(mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.24, 10), o.leg || skin, 0, -0.13, 0));
        g.add(mesh(new THREE.BoxGeometry(0.12, 0.07, 0.18), o.shoe || '#ffffff', 0, -0.265, 0.03));
        return g;
      };
      root.add(leg('LegL', 0.09), leg('LegR', -0.09));
      if (o.tail) {
        const tail = group('Tail', 0, 0.36, -0.2);
        const cone = mesh(new THREE.ConeGeometry(0.045, 0.2, 10), o.headColor, 0, 0.08, -0.04);
        cone.rotation.x = -0.7;
        tail.add(cone);
        root.add(tail);
      }
      return root;
    }
    nodes.Inu = person('Inu', { head: 'dog', headColor: '#d9a066', dark: '#a86b3c', smock: '#c98b4f', skin: '#d9a066', leg: '#d9a066', shoe: '#f4e3c8', tail: true });
    nodes.Pen = person('Pen', { head: 'pen', headColor: '#2f4a6d', smock: '#3a6ea5', skin: '#2f4a6d', leg: '#2f4a6d', shoe: '#ffa62b' });
    nodes.KidGirl = person('KidGirl', { head: 'kid', skin: '#ffdcbf', smock: '#ff8fb1', hair: '#5b3a29', style: 'pigtails', shoe: '#ff6b6b' });
    nodes.KidBoy = person('KidBoy', { head: 'kid', skin: '#ffd6b3', smock: '#6aa8ff', hair: '#3b2a20', style: 'short', shoe: '#ffd23f' });
    nodes.Kid = person('Kid', { head: 'kid', skin: '#f6cfa8', smock: '#6cc77a', hair: '#4a2f22', style: 'bob', shoe: '#4d8dff' });

    // どうぐ
    const shovel = group('Shovel');
    shovel.add(mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.3, 8), '#e04848', 0, 0.31, 0));
    shovel.add(mesh(new THREE.BoxGeometry(0.1, 0.035, 0.035), '#e04848', 0, 0.475, 0));
    const blade = mesh(sphere(0.08, 14, 10), '#4d8dff', 0, 0.1, 0); blade.scale.set(1, 1.35, 0.35);
    shovel.add(blade);
    nodes.Shovel = shovel;

    const bucket = group('Bucket');
    bucket.add(mesh(new THREE.CylinderGeometry(0.15, 0.11, 0.3, 20), '#4d8dff', 0, 0.15, 0));
    const rim = mesh(new THREE.TorusGeometry(0.15, 0.016, 8, 24), '#2f6fd6', 0, 0.3, 0); rim.rotation.x = Math.PI / 2;
    const bh = mesh(new THREE.TorusGeometry(0.15, 0.01, 6, 20, Math.PI), '#ffd23f', 0, 0.3, 0);
    bucket.add(rim, bh);
    nodes.Bucket = bucket;

    const can = group('WateringCan');
    can.add(mesh(new THREE.CylinderGeometry(0.11, 0.12, 0.2, 18), '#3cc46b', 0, 0.1, 0));
    const spout = mesh(new THREE.CylinderGeometry(0.016, 0.022, 0.26, 8), '#2a9d5a', 0, 0.17, 0.17); spout.rotation.x = 0.95;
    const rose = mesh(new THREE.ConeGeometry(0.04, 0.05, 10), '#2a9d5a', 0, 0.255, 0.28); rose.rotation.x = 0.95;
    const handle = mesh(new THREE.TorusGeometry(0.08, 0.014, 6, 14, Math.PI), '#2a9d5a', 0, 0.2, -0.02); handle.rotation.y = Math.PI / 2;
    can.add(spout, rose, handle);
    nodes.WateringCan = can;

    // かた（すないろ）
    const SAND = '#e8c98a';
    const castle = group('CastleMold');
    castle.add(mesh(new THREE.BoxGeometry(0.66, 0.42, 0.66), SAND, 0, 0.21, 0));
    for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      castle.add(mesh(new THREE.CylinderGeometry(0.12, 0.14, 0.6, 14), SAND, x * 0.32, 0.3, z * 0.32));
      castle.add(mesh(new THREE.CylinderGeometry(0.15, 0.13, 0.08, 14), SAND, x * 0.32, 0.64, z * 0.32));
      castle.add(mesh(new THREE.ConeGeometry(0.1, 0.12, 12), '#dcb574', x * 0.32, 0.74, z * 0.32));
    }
    for (const x of [-0.16, 0, 0.16]) {
      castle.add(mesh(new THREE.BoxGeometry(0.08, 0.08, 0.08), SAND, x, 0.46, 0.3));
      castle.add(mesh(new THREE.BoxGeometry(0.08, 0.08, 0.08), SAND, x, 0.46, -0.3));
    }
    castle.add(mesh(new THREE.BoxGeometry(0.2, 0.24, 0.02), '#a8814d', 0, 0.12, 0.335));
    nodes.CastleMold = castle;

    const fish = group('FishMold');
    const fb = mesh(sphere(0.21, 20, 12), SAND, 0.06, 0.06, 0); fb.scale.set(1, 0.32, 0.55);
    const tail = mesh(new THREE.ConeGeometry(0.12, 0.2, 3), SAND, -0.2, 0.05, 0, true); tail.rotation.z = -Math.PI / 2; tail.scale.set(1, 1, 0.4);
    fish.add(fb, tail, mesh(sphere(0.022, 8, 6), '#b08a52', 0.18, 0.08, 0.06));
    fish.rotation.y = 0;
    nodes.FishMold = fish;

    const starShape = new THREE.Shape();
    for (let k = 0; k < 10; k++) {
      const r = k % 2 ? 0.13 : 0.3;
      const a = Math.PI / 2 + (k * Math.PI) / 5;
      if (k) starShape.lineTo(Math.cos(a) * r, Math.sin(a) * r); else starShape.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    }
    const starGeo = new THREE.ExtrudeGeometry(starShape, { depth: 0.08, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 2 });
    starGeo.rotateX(-Math.PI / 2);
    starGeo.translate(0, 0.02, 0);
    const star = group('StarMold');
    star.add(mesh(starGeo, SAND));
    nodes.StarMold = star;

    const flag = group('Flag');
    flag.add(mesh(new THREE.CylinderGeometry(0.008, 0.008, 0.3, 6), '#8a6a4a', 0, 0.15, 0));
    const tri = new THREE.Shape(); tri.moveTo(0, 0); tri.lineTo(0.14, -0.045); tri.lineTo(0, -0.09);
    const fl = new THREE.Mesh(new THREE.ShapeGeometry(tri), new THREE.MeshToonMaterial({ color: col('#ff4d4d'), side: THREE.DoubleSide }));
    fl.position.set(0.005, 0.3, 0); fl.castShadow = true;
    flag.add(fl);
    nodes.Flag = flag;

    // すなばの ふち（うちがわ 8×8、はば 0.4、たかさ 0.35、よすみに すわれる いた）
    const frame = group('Frame');
    const WOOD = '#c48a52';
    frame.add(mesh(new THREE.BoxGeometry(8.8, 0.35, 0.4), WOOD, 0, 0.175, 4.2));
    frame.add(mesh(new THREE.BoxGeometry(8.8, 0.35, 0.4), WOOD, 0, 0.175, -4.2));
    frame.add(mesh(new THREE.BoxGeometry(0.4, 0.35, 8), WOOD, 4.2, 0.175, 0));
    frame.add(mesh(new THREE.BoxGeometry(0.4, 0.35, 8), WOOD, -4.2, 0.175, 0));
    for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) frame.add(mesh(new THREE.BoxGeometry(0.72, 0.05, 0.72), '#dba56b', x * 4.2, 0.375, z * 4.2));
    nodes.Frame = frame;

    // かざり
    const shell = group('Shell');
    const sc = mesh(new THREE.ConeGeometry(0.11, 0.06, 9), '#ffc6d3', 0, 0.03, 0, true); sc.scale.set(1, 1, 0.8);
    shell.add(sc);
    nodes.Shell = shell;
    const leaf = group('Leaf');
    const lf = mesh(sphere(0.1, 14, 8), '#5cbf4a', 0, 0.015, 0); lf.scale.set(0.55, 0.15, 1.1);
    leaf.add(lf, mesh(new THREE.BoxGeometry(0.012, 0.012, 0.22), '#3f8f33', 0, 0.025, 0));
    nodes.Leaf = leaf;
    const flower = group('Flower');
    for (let k = 0; k < 5; k++) {
      const a = (k / 5) * Math.PI * 2;
      const p = mesh(sphere(0.05, 12, 8), '#ff8fb1', Math.cos(a) * 0.065, 0.03, Math.sin(a) * 0.065); p.scale.set(1, 0.35, 1);
      flower.add(p);
    }
    flower.add(mesh(sphere(0.04, 12, 8), '#ffd23f', 0, 0.045, 0));
    nodes.Flower = flower;
    const rock = group('Rock');
    const rk = mesh(new THREE.DodecahedronGeometry(0.1), '#a3a7ad', 0, 0.05, 0, true); rk.scale.set(1, 0.65, 0.9);
    rock.add(rk);
    nodes.Rock = rock;

    // しばふ と き
    const ground = group('Ground');
    const lawn = new THREE.Mesh(new THREE.PlaneGeometry(20, 20), M('#8fd36b'));
    lawn.rotation.x = -Math.PI / 2;
    lawn.receiveShadow = true;
    ground.add(lawn);
    nodes.Ground = ground;
    const tree = group('Tree');
    tree.add(mesh(new THREE.CylinderGeometry(0.13, 0.18, 1.5, 10), '#8a5a33', 0, 0.75, 0));
    tree.add(mesh(sphere(0.85, 16, 12), '#4caf50', 0, 1.9, 0), mesh(sphere(0.6, 14, 10), '#5cc260', 0.35, 2.45, 0.1), mesh(sphere(0.55, 14, 10), '#43a047', -0.4, 2.3, -0.1));
    nodes.Tree = tree;

    // トンネルの いりぐち（はんえんの アーチ。はば0.6 たかさ0.45 あつみ0.2、そこが y=0、+Z むき）
    const arch = group('TunnelArch');
    const archGeo = new THREE.TorusGeometry(0.22, 0.075, 10, 22, Math.PI);
    const ring = mesh(archGeo, '#c9a46a', 0, 0, 0, true);
    ring.scale.set(1, 1.6, 1.4);
    arch.add(ring);
    arch.add(mesh(new THREE.BoxGeometry(0.15, 0.06, 0.2), '#b8945c', 0.22, 0.03, 0), mesh(new THREE.BoxGeometry(0.15, 0.06, 0.2), '#b8945c', -0.22, 0.03, 0));
    nodes.TunnelArch = arch;

    return { nodes, clips: {}, mats };
  }

  // glb と かわりの ぶひんを あわせる（glb に ある ものは glb を つかう）
  function buildAssets(gltf) {
    const fb = buildFallbackAssets();
    const nodes = { ...fb.nodes };
    const clips = {};
    const fromGlb = new Set();
    let trees = null;
    if (gltf && gltf.scene) {
      const scene = gltf.scene;
      scene.updateMatrixWorld(true);
      for (const name of ROOT_NODES) {
        const n = scene.getObjectByName(name);
        if (!n || name === 'Tree') continue;
        nodes[name] = n;
        fromGlb.add(name);
      }
      // き（Ground の なかに なければ、シーン直下の Tree... を その ばしょに）
      let inGround = false;
      if (fromGlb.has('Ground')) nodes.Ground.traverse((o) => { if (o !== nodes.Ground && /Tree/.test(o.userData.name || o.name)) inGround = true; });
      if (inGround) trees = [];
      else {
        const list = scene.children.filter((o) => /^Tree/.test(o.userData.name || o.name));
        if (list.length) trees = list;
      }
      for (const a of gltf.animations || []) {
        const m = /^(.+)_(idle|walk|dig|sit|cheer|hold|wave)$/i.exec(a.name);
        if (!m) continue;
        (clips[m[1]] = clips[m[1]] || {})[m[2].toLowerCase()] = a;
      }
      for (const name of fromGlb) {
        nodes[name].traverse((o) => {
          if (!o.isMesh) return;
          o.castShadow = name !== 'Ground';
          o.receiveShadow = true;
        });
      }
    }
    const source = ['Inu', 'Frame', 'CastleMold'].some((n) => fromGlb.has(n)) ? 'glb' : 'fallback';
    return { nodes, clips, trees, fromGlb, source, fallbackMats: fb.mats };
  }

  // こどもの ノード（Head_1 など なまえが かわっても、userData.name で さがす）
  function findPart(root, part) {
    let hit = null;
    root.traverse((o) => { if (!hit && o !== root && (o.userData.name || o.name) === part) hit = o; });
    if (hit) return hit;
    const re = new RegExp(`(^|_)${part}(_?\\d+)?$`);
    root.traverse((o) => { if (!hit && o !== root && re.test(o.name)) hit = o; });
    return hit;
  }

  function hasWebGL() {
    try {
      const c = document.createElement('canvas');
      return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
    } catch (e) { return false; }
  }

  Core.registerSpot({
    id: 'sunaba3d',
    start(ctx) {
      const { el, speak, sound, store } = ctx;
      const alive = () => ctx.isActive();
      const timers = new Set();
      const later = (fn, ms) => { const t = setTimeout(() => { timers.delete(t); if (alive()) fn(); }, ms); timers.add(t); return t; };
      const pause = (ms) => new Promise((r) => later(r, ms));

      // ---- WebGL が つかえない とき ----
      function cannotUse() {
        const msg = 'この タブレットでは りったい すなばが つかえないよ';
        ctx.stage.append(el('div', { class: 's3d-msg' }, el('span', { class: 's3d-msg-emoji' }, '🏝️'), el('span', {}, msg)));
        Promise.race([speak(msg), new Promise((r) => setTimeout(r, 5000))]).then(() => { if (alive()) ctx.exit(); });
        return () => {};
      }
      if (typeof THREE === 'undefined' || !hasWebGL()) return cannotUse();
      let renderer;
      try {
        renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
      } catch (e) {
        return cannotUse();
      }
      renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      const canvas = renderer.domElement;
      canvas.className = 's3d-canvas';

      // ---- がめん ----
      const view = el('div', { class: 's3d-view' }, canvas);
      const bubbleLayer = el('div', { class: 's3d-bubbles', 'aria-hidden': 'true' });
      const loading = el('div', { class: 's3d-loading', 'aria-hidden': 'true' }, '🏝️');
      view.append(bubbleLayer, loading);

      const camBtn = (label, icon, fn) => el('button', { class: 's3d-cambtn', 'aria-label': label, onclick: () => { sound('tap'); fn(); } }, icon);
      const camBar = el('div', { class: 's3d-cam' },
        camBtn('ひだりに まわす', '↺', () => { cam.yawT += Math.PI / 6; }),
        camBtn('みぎに まわす', '↻', () => { cam.yawT -= Math.PI / 6; }),
        camBtn('ちかく', '＋', () => { cam.distT = clamp(cam.distT * 0.8, cam.minD, cam.maxD); }),
        camBtn('とおく', '－', () => { cam.distT = clamp(cam.distT * 1.25, cam.minD, cam.maxD); }));
      const flatBtn = el('button', { class: 's3d-flat', 'aria-label': 'ならす', onclick: () => askFlatten() },
        el('span', { class: 's3d-flat-icon' }, '🧹'), el('span', { class: 's3d-flat-label' }, 'ならす'));
      view.append(camBar, flatBtn);

      let tool = 'dig';
      let mold = 'castle';
      let deco = 'shell';
      let lending = false;
      const toolBtns = {};
      const toolBar = el('div', { class: 's3d-tools', role: 'toolbar' },
        TOOLS.map((t) => {
          const icon = el('span', { class: 's3d-tool-icon' });
          if (t.svg) icon.innerHTML = t.icon; else icon.textContent = t.icon;
          const b = el('button', { class: 's3d-tool', 'aria-label': t.label, 'data-tool': t.id, onclick: () => selectTool(t.id) },
            icon, el('span', { class: 's3d-tool-label' }, t.label),
            el('span', { class: 's3d-tool-badge', 'aria-hidden': 'true' }, ctx.character('inu', { pose: 'hold' })));
          toolBtns[t.id] = b;
          return b;
        }));
      const subBar = el('div', { class: 's3d-sub' });
      const root = el('div', { class: 's3d-root' }, view, el('div', { class: 's3d-toolwrap' }, subBar, toolBar));
      ctx.stage.append(root);

      function renderSub() {
        subBar.replaceChildren();
        subBar.classList.toggle('open', tool === 'bucket' || tool === 'deco');
        const list = tool === 'bucket' ? MOLDS : tool === 'deco' ? DECOS : [];
        const cur = tool === 'bucket' ? mold : deco;
        list.forEach((m) => subBar.append(el('button', {
          class: 's3d-subbtn' + (cur === m.id ? ' on' : ''), 'aria-label': m.name,
          onclick: () => { if (tool === 'bucket') mold = m.id; else deco = m.id; sound('tap'); speak(m.name); renderSub(); },
        }, m.emoji)));
      }

      function selectTool(id, quiet) {
        if (id === 'dig' && lending) {
          sound('tap');
          say('inu', 'いま スコップ つかわせて もらってるよ。ありがとう！');
          return;
        }
        tool = id;
        Object.entries(toolBtns).forEach(([k, b]) => b.classList.toggle('on', k === id));
        renderSub();
        if (player) player.hold(handTool());
        if (!quiet) {
          sound('tap');
          speak(TOOLS.find((t) => t.id === id).say);
        }
      }
      const handTool = () => (tool === 'dig' || tool === 'tunnel' ? (lending ? null : 'Shovel') : tool === 'water' ? 'WateringCan' : tool === 'bucket' ? 'Bucket' : null);

      // ---- three.js の シーン ----
      const scene = new THREE.Scene();
      const SKY = '#bfe6ff';
      scene.background = col(SKY);
      scene.fog = new THREE.Fog(col(SKY), 26, 60);
      const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 120);
      const hemi = new THREE.HemisphereLight(col('#e9f6ff'), col('#c8a878'), 0.75);
      const sun = new THREE.DirectionalLight(col('#fff4e0'), 0.85);
      sun.position.set(-6, 11, 1.5);
      sun.castShadow = true;
      sun.shadow.mapSize.set(1024, 1024);
      Object.assign(sun.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
      sun.shadow.bias = -0.0008;
      sun.shadow.normalBias = 0.02;
      scene.add(hemi, sun, sun.target);
      const farLawn = new THREE.Mesh(new THREE.CircleGeometry(60, 40), new THREE.MeshLambertMaterial({ color: col('#86c95f') }));
      farLawn.rotation.x = -Math.PI / 2;
      farLawn.position.y = -0.02;
      scene.add(farLawn);
      const disposables = [farLawn.geometry, farLawn.material];

      // ---- すな と みず の データ ----
      const h = new Float32Array(N * N);
      const w = new Float32Array(N * N);
      const wet = new Float32Array(N * N);
      const dw = new Float32Array(N * N);
      const tf = new Float32Array(N * N).fill(1e9); // トンネルの ゆか（ない ところは とても たかい）
      const grain = new Float32Array(N * N);
      for (let i = 0; i < N * N; i++) grain[i] = 0.97 + Math.random() * 0.06;
      function flatSand() {
        const p = [Math.random() * 6, Math.random() * 6, Math.random() * 6];
        for (let z = 0; z < N; z++) {
          for (let x = 0; x < N; x++) {
            const i = z * N + x;
            h[i] = 0.012 * (Math.sin(x * 0.11 + p[0]) * Math.cos(z * 0.09 + p[1]) + 0.5 * Math.sin((x + z) * 0.21 + p[2]));
            w[i] = 0; wet[i] = 0;
          }
        }
      }
      flatSand();

      // すなの メッシュ（PlaneGeometry を へんけい）
      const sandGeo = new THREE.PlaneGeometry(HALF * 2, HALF * 2, N - 1, N - 1);
      sandGeo.rotateX(-Math.PI / 2);
      sandGeo.setAttribute('color', new THREE.BufferAttribute(new Float32Array(N * N * 3), 3));
      const sandMat = new THREE.MeshLambertMaterial({ vertexColors: true });
      const sandMesh = new THREE.Mesh(sandGeo, sandMat);
      sandMesh.receiveShadow = true;
      sandMesh.frustumCulled = false;
      scene.add(sandMesh);
      const waterGeo = new THREE.PlaneGeometry(HALF * 2, HALF * 2, N - 1, N - 1);
      waterGeo.rotateX(-Math.PI / 2);
      const waterMat = new THREE.MeshLambertMaterial({ color: col('#4fb0ff'), emissive: col('#0b3a66'), transparent: true, opacity: 0.74 });
      const waterMesh = new THREE.Mesh(waterGeo, waterMat);
      waterMesh.frustumCulled = false;
      waterMesh.renderOrder = 2;
      scene.add(waterMesh);
      disposables.push(sandGeo, sandMat, waterGeo, waterMat);

      const SAND_LIN = col('#ecd09a');
      const WET_LIN = col('#a98552');
      const DEEP_LIN = col('#b88f58');
      const sPos = sandGeo.attributes.position.array;
      const sNor = sandGeo.attributes.normal.array;
      const sCol = sandGeo.attributes.color.array;
      const wPos = waterGeo.attributes.position.array;
      const wNor = waterGeo.attributes.normal.array;
      const ground = (i) => (h[i] < tf[i] ? h[i] : tf[i]);

      // かわった ところ だけ なおす
      const R0 = () => ({ x0: N, x1: -1, z0: N, z1: -1 });
      let sandDirty = R0();
      let waterDirty = R0();
      const grow = (r, x0, x1, z0, z1) => { r.x0 = Math.min(r.x0, x0); r.x1 = Math.max(r.x1, x1); r.z0 = Math.min(r.z0, z0); r.z1 = Math.max(r.z1, z1); };
      const isEmpty = (r) => r.x0 > r.x1 || r.z0 > r.z1;
      function updateSand(r) {
        const x0 = Math.max(0, r.x0 - 1); const x1 = Math.min(N - 1, r.x1 + 1);
        const z0 = Math.max(0, r.z0 - 1); const z1 = Math.min(N - 1, r.z1 + 1);
        for (let z = z0; z <= z1; z++) {
          for (let x = x0; x <= x1; x++) {
            const i = z * N + x;
            const hi = h[i];
            sPos[i * 3 + 1] = SAND_Y + hi;
            const hl = h[x > 0 ? i - 1 : i]; const hr = h[x < N - 1 ? i + 1 : i];
            const hu = h[z > 0 ? i - N : i]; const hd = h[z < N - 1 ? i + N : i];
            let nx = (hl - hr) / (2 * CELL); let nz = (hu - hd) / (2 * CELL);
            const l = 1 / Math.sqrt(nx * nx + 1 + nz * nz);
            sNor[i * 3] = nx * l; sNor[i * 3 + 1] = l; sNor[i * 3 + 2] = nz * l;
            // いろ：たかい ところは あかるく、ひくい・ぬれた ところは くらく
            const up = clamp(hi, -0.3, 0.7);
            const lit = (up >= 0 ? 1 + up * 0.3 : 1 + up * 1.1) * grain[i];
            const dk = up < 0 ? clamp(-up * 5, 0, 1) : 0;
            const wt = wet[i];
            for (let c = 0; c < 3; c++) {
              const k = c === 0 ? 'r' : c === 1 ? 'g' : 'b';
              let v = lerp(SAND_LIN[k], DEEP_LIN[k], dk * 0.85);
              v = lerp(v, WET_LIN[k], wt * 0.8);
              sCol[i * 3 + c] = v * lit;
            }
          }
        }
        const a = sandGeo.attributes;
        for (const att of [a.position, a.normal, a.color]) {
          att.updateRange.offset = z0 * N * 3;
          att.updateRange.count = (z1 - z0 + 1) * N * 3;
          att.needsUpdate = true;
        }
      }
      const WATER_SHOW = 0.0025;
      function updateWater(r) {
        const x0 = Math.max(0, r.x0 - 1); const x1 = Math.min(N - 1, r.x1 + 1);
        const z0 = Math.max(0, r.z0 - 1); const z1 = Math.min(N - 1, r.z1 + 1);
        for (let z = z0; z <= z1; z++) {
          for (let x = x0; x <= x1; x++) {
            const i = z * N + x;
            const s = ground(i) + w[i];
            wPos[i * 3 + 1] = w[i] > WATER_SHOW ? SAND_Y + s + 0.004 : SAND_Y + ground(i) - 0.035;
            const sl = ground(x > 0 ? i - 1 : i) + w[x > 0 ? i - 1 : i]; const sr = ground(x < N - 1 ? i + 1 : i) + w[x < N - 1 ? i + 1 : i];
            const su = ground(z > 0 ? i - N : i) + w[z > 0 ? i - N : i]; const sd = ground(z < N - 1 ? i + N : i) + w[z < N - 1 ? i + N : i];
            const nx = (sl - sr) / (2 * CELL); const nz = (su - sd) / (2 * CELL);
            const l = 1 / Math.sqrt(nx * nx + 1 + nz * nz);
            wNor[i * 3] = nx * l; wNor[i * 3 + 1] = l; wNor[i * 3 + 2] = nz * l;
          }
        }
        const a = waterGeo.attributes;
        for (const att of [a.position, a.normal]) {
          att.updateRange.offset = z0 * N * 3;
          att.updateRange.count = (z1 - z0 + 1) * N * 3;
          att.needsUpdate = true;
        }
      }
      updateSand({ x0: 0, x1: N - 1, z0: 0, z1: N - 1 });
      updateWater({ x0: 0, x1: N - 1, z0: 0, z1: N - 1 });

      const toGrid = (v) => (v + HALF) / CELL;
      function sampleArr(arr, x, z) {
        const gx = clamp(toGrid(x), 0, N - 1.001); const gz = clamp(toGrid(z), 0, N - 1.001);
        const ix = Math.floor(gx); const iz = Math.floor(gz);
        const fx = gx - ix; const fz = gz - iz;
        const i = iz * N + ix;
        return lerp(lerp(arr[i], arr[i + 1], fx), lerp(arr[i + N], arr[i + N + 1], fx), fz);
      }
      const sampleH = (x, z) => sampleArr(h, x, z);
      const cellAt = (x, z) => clamp(Math.round(toGrid(z)), 0, N - 1) * N + clamp(Math.round(toGrid(x)), 0, N - 1);
      function groundY(x, z) {
        const ax = Math.abs(x); const az = Math.abs(z);
        if (ax <= HALF && az <= HALF) return SAND_Y + sampleH(x, z);
        if (ax > HALF && az > HALF && ax <= HALF + 0.45 && az <= HALF + 0.45) return 0.41; // よすみの いた
        if (ax <= HALF + 0.4 && az <= HALF + 0.4) return 0.35;
        return 0;
      }

      // ---- ブラシ（ほる・もりあげる） ----
      function brush(cx, cz, reach, fn) {
        const r = reach / CELL;
        const gx = toGrid(cx); const gz = toGrid(cz);
        const x0 = Math.max(0, Math.floor(gx - r)); const x1 = Math.min(N - 1, Math.ceil(gx + r));
        const z0 = Math.max(0, Math.floor(gz - r)); const z1 = Math.min(N - 1, Math.ceil(gz + r));
        if (x0 > x1 || z0 > z1) return null;
        for (let z = z0; z <= z1; z++) {
          const pz = z * CELL - HALF;
          for (let x = x0; x <= x1; x++) {
            const px = x * CELL - HALF;
            const d = Math.hypot(px - cx, pz - cz);
            if (d > reach) continue;
            const edge = Math.min(HALF - Math.abs(px), HALF - Math.abs(pz));
            const ef = clamp((edge - 0.04) / 0.3, 0, 1);
            fn(z * N + x, d, ef);
          }
        }
        const rect = { x0, x1, z0, z1 };
        grow(sandDirty, x0, x1, z0, z1);
        grow(waterRect, x0, x1, z0, z1);
        return rect;
      }
      const DIG_R = 0.3;
      const kidDug = new Uint8Array(N * N); // こどもが ほった ところ
      function digAt(cx, cz, amt) {
        const rect = brush(cx, cz, DIG_R * 1.8, (i, d, ef) => {
          const u = d / DIG_R;
          if (u < 1) { const k = (1 - u * u) * (1 - u * u); h[i] = Math.max(H_MIN, h[i] - amt * k * ef); kidDug[i] = 1; }
          else { h[i] = Math.min(H_MAX, h[i] + amt * 0.2 * Math.sin(Math.PI * (u - 1) / 0.8) * ef); }
        });
        if (rect) afterDig(cx, cz, rect);
      }
      function moundAt(cx, cz, amt, R = 0.5) {
        brush(cx, cz, R, (i, d, ef) => {
          const u = d / R; const k = (1 - u * u) * (1 - u * u);
          h[i] = Math.min(H_MAX, h[i] + amt * k * ef);
        });
        // すこし ならして、すなの おやまらしく
        brush(cx, cz, R, (i, d) => {
          if (i % N === 0 || i % N === N - 1 || i < N || i >= N * (N - 1)) return;
          const avg = (h[i - 1] + h[i + 1] + h[i - N] + h[i + N]) * 0.25;
          h[i] += (avg - h[i]) * 0.18 * (1 - d / R);
        });
        itemsFollow(cx, cz, R);
      }
      // めあての ふかさまで ほる（いぬくんの かわ）
      function digTo(cx, cz, depth, R) {
        const rect = brush(cx, cz, R, (i, d, ef) => {
          const u = d / R; const k = (1 - u * u) * (1 - u * u) * ef;
          if (h[i] > depth) h[i] += (depth - h[i]) * k * 0.7;
        });
        if (rect) afterDig(cx, cz, rect, true);
      }
      function afterDig(cx, cz, rect, gentle) {
        // ほった ところの かたは くずれて すなに もどる
        if (!gentle) {
          for (const it of items.slice()) {
            if (it.k === 'mold' && Math.hypot(it.x - cx, it.z - cz) < 0.28) {
              removeItem(it, true);
              moundAt(it.x, it.z, 0.1, 0.4);
              sound('flip');
            }
          }
        }
        itemsFollow(cx, cz, DIG_R * 1.8);
        if (!gentle) deepenTunnelEnds(cx, cz);
        checkCollapse(rect);
      }
      // トンネルの いりぐちの まえを ふかく ほったら、トンネルの ゆかも そこに あわせる（みぞと つながる）
      function deepenTunnelEnds(cx, cz) {
        for (const t of tunnels.slice()) {
          for (const end of ['A', 'B']) {
            const m = t['mouth' + end];
            const ext = end === 'A' ? t.def.ea : t.def.eb;
            const s = (cx - m.x) * m.ox + (cz - m.z) * m.oz;
            const d = Math.abs((cx - m.x) * -m.oz + (cz - m.z) * m.ox);
            if (s < -0.1 || s > ext + 0.35 || d > 0.4) continue;
            const hh = sampleH(cx, cz);
            const key = end === 'A' ? 'fa' : 'fb';
            if (hh < t.def[key] - 0.04) {
              const def = { ...t.def, [key]: Math.max(H_MIN + 0.02, hh + 0.02) };
              removeTunnel(t, false);
              buildTunnel(def, true);
              return;
            }
          }
        }
      }

      // ---- みず（2つめの たかさマップ。ひくい ほうへ ながれて、たまって、すこしずつ しみこむ） ----
      let waterRect = R0();
      let wetRect = R0();
      let waterOn = false;
      const FLOW_K = 0.12;
      const ABSORB = 0.0035;
      function addWater(cx, cz, amount, R = 0.22) {
        const gx = toGrid(cx); const gz = toGrid(cz); const r = R / CELL;
        const x0 = Math.max(0, Math.floor(gx - r)); const x1 = Math.min(N - 1, Math.ceil(gx + r));
        const z0 = Math.max(0, Math.floor(gz - r)); const z1 = Math.min(N - 1, Math.ceil(gz + r));
        for (let z = z0; z <= z1; z++) {
          for (let x = x0; x <= x1; x++) {
            const d = Math.hypot(x * CELL - HALF - cx, z * CELL - HALF - cz) / R;
            if (d < 1) w[z * N + x] += amount * (1 - d * d);
          }
        }
        grow(waterRect, x0, x1, z0, z1);
        waterOn = true;
      }
      // パイプ モデル：となりへの ながれ（fl,fr,fu,fd）を おぼえておくので、みずが いきおいよく すすむ
      const fl = new Float32Array(N * N); const fr = new Float32Array(N * N);
      const fu = new Float32Array(N * N); const fd = new Float32Array(N * N);
      const FRICTION = 0.985;
      function waterStep(dt) {
        if (isEmpty(waterRect)) { waterOn = false; return; }
        const { x0, x1, z0, z1 } = waterRect;
        const ax0 = Math.max(0, x0 - 1); const ax1 = Math.min(N - 1, x1 + 1);
        const az0 = Math.max(0, z0 - 1); const az1 = Math.min(N - 1, z1 + 1);
        for (let z = z0; z <= z1; z++) {
          for (let x = x0; x <= x1; x++) {
            const i = z * N + x;
            const wi = w[i];
            if (wi <= 0) { fl[i] = fr[i] = fu[i] = fd[i] = 0; continue; }
            const s = ground(i) + wi;
            let a0 = x > 0 ? fl[i] * FRICTION + FLOW_K * (s - ground(i - 1) - w[i - 1]) : 0;
            let a1 = x < N - 1 ? fr[i] * FRICTION + FLOW_K * (s - ground(i + 1) - w[i + 1]) : 0;
            let a2 = z > 0 ? fu[i] * FRICTION + FLOW_K * (s - ground(i - N) - w[i - N]) : 0;
            let a3 = z < N - 1 ? fd[i] * FRICTION + FLOW_K * (s - ground(i + N) - w[i + N]) : 0;
            if (a0 < 0) a0 = 0; if (a1 < 0) a1 = 0; if (a2 < 0) a2 = 0; if (a3 < 0) a3 = 0;
            const sum = a0 + a1 + a2 + a3;
            if (sum > wi) { const k = wi / sum; a0 *= k; a1 *= k; a2 *= k; a3 *= k; }
            fl[i] = a0; fr[i] = a1; fu[i] = a2; fd[i] = a3;
          }
        }
        const nr = R0();
        const absorb = ABSORB * dt;
        for (let z = az0; z <= az1; z++) {
          for (let x = ax0; x <= ax1; x++) {
            const i = z * N + x;
            const inside = x >= x0 && x <= x1 && z >= z0 && z <= z1;
            let v = w[i];
            if (inside) v -= fl[i] + fr[i] + fu[i] + fd[i];
            if (x > 0) v += fr[i - 1];
            if (x < N - 1) v += fl[i + 1];
            if (z > 0) v += fd[i - N];
            if (z < N - 1) v += fu[i + N];
            v -= absorb;
            if (v < 1e-4) v = 0;
            dw[i] = v;
          }
        }
        for (let z = az0; z <= az1; z++) {
          for (let x = ax0; x <= ax1; x++) {
            const i = z * N + x;
            const v = dw[i];
            w[i] = v;
            if (v > 0) {
              if (x < nr.x0) nr.x0 = x; if (x > nr.x1) nr.x1 = x;
              if (z < nr.z0) nr.z0 = z; if (z > nr.z1) nr.z1 = z;
              const wt = Math.min(1, v * 30);
              if (wt > wet[i]) wet[i] = wt;
            } else { fl[i] = fr[i] = fu[i] = fd[i] = 0; }
          }
        }
        grow(waterDirty, ax0, ax1, az0, az1);
        grow(wetRect, ax0, ax1, az0, az1);
        if (isEmpty(nr)) { waterRect = R0(); waterOn = false; saveSoon(); return; }
        waterRect = { x0: Math.max(0, nr.x0 - 1), x1: Math.min(N - 1, nr.x1 + 1), z0: Math.max(0, nr.z0 - 1), z1: Math.min(N - 1, nr.z1 + 1) };
      }
      // ぬれた すなは ゆっくり かわく
      function dryStep(dt) {
        if (isEmpty(wetRect)) return;
        const nr = R0();
        const k = dt * 0.02;
        for (let z = wetRect.z0; z <= wetRect.z1; z++) {
          for (let x = wetRect.x0; x <= wetRect.x1; x++) {
            const i = z * N + x;
            if (wet[i] <= 0) continue;
            if (w[i] <= 0) wet[i] = Math.max(0, wet[i] - k);
            if (wet[i] > 0) { if (x < nr.x0) nr.x0 = x; if (x > nr.x1) nr.x1 = x; if (z < nr.z0) nr.z0 = z; if (z > nr.z1) nr.z1 = z; }
          }
        }
        grow(sandDirty, wetRect.x0, wetRect.x1, wetRect.z0, wetRect.z1);
        wetRect = nr;
      }

      // ---- アセット と キャラ ----
      let assets = null;
      let ready = false;
      let player = null; let inu = null; let pen = null;
      const chars = [];
      const tmpV = new THREE.Vector3();

      function cloneNode(name) {
        const tpl = assets.nodes[name];
        const o = tpl.clone(true);
        o.position.set(0, 0, 0);
        o.rotation.set(0, 0, 0);
        return o;
      }

      function makeChar(nodeName, id) {
        const tpl = assets.nodes[nodeName];
        const model = tpl.clone(true);
        const holder = new THREE.Group();
        const pose = new THREE.Group();
        const offset = new THREE.Group();
        offset.position.copy(tpl.position).negate();
        holder.add(pose); pose.add(offset); offset.add(model);
        model.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
        const parts = {}; const rest = {};
        for (const p of PARTS) { parts[p] = findPart(model, p); rest[p] = parts[p] ? parts[p].rotation.clone() : null; }
        holder.updateMatrixWorld(true);
        // て の ばしょ（みぎうでの さき）
        const hand = new THREE.Group();
        if (parts.ArmR) {
          const box = new THREE.Box3().setFromObject(parts.ArmR);
          const wp = parts.ArmR.getWorldPosition(new THREE.Vector3());
          const hy = box.isEmpty() ? wp.y - 0.25 : box.min.y + 0.05;
          hand.position.copy(parts.ArmR.worldToLocal(new THREE.Vector3(wp.x, hy, wp.z + 0.03)));
          parts.ArmR.add(hand);
        } else {
          hand.position.set(-0.22, 0.42, 0.12);
          model.add(hand);
        }
        const clips = assets.clips[nodeName] || {};
        const mixer = Object.keys(clips).length ? new THREE.AnimationMixer(model) : null;
        const c = {
          id, nodeName, holder, model, pose, parts, rest, hand, mixer, clips,
          x: 0, z: 0, y: 0, heading: 0, look: null,
          target: null, resolve: null, speed: 1.5, walkVerb: 'walk', onStep: null,
          verb: 'idle', shown: null, action: null, t: Math.random() * 10,
          prop: null, propName: null, bubble: null, bubbleTimer: 0,
          place(x, z, heading) { this.x = x; this.z = z; this.y = groundY(x, z); if (heading != null) this.heading = heading; this.sync(); },
          sync() { holder.position.set(this.x, this.y, this.z); holder.rotation.y = this.heading; },
          walkTo(x, z, opts = {}) {
            if (this.resolve) this.resolve(false);
            this.target = { x, z };
            this.speed = opts.speed || 1.5;
            this.walkVerb = opts.verb || 'walk';
            this.onStep = opts.onStep || null;
            this.faceDir = opts.faceDir;
            return new Promise((r) => { this.resolve = r; });
          },
          stop() { if (this.resolve) this.resolve(false); this.resolve = null; this.target = null; this.onStep = null; },
          act(verb) { this.verb = verb; },
          face(x, z) { this.look = { x, z }; },
          hold(name) {
            if (this.propName === name) return;
            if (this.prop) { this.prop.parent.remove(this.prop); this.prop = null; }
            this.propName = name;
            if (!name) return;
            const inner = cloneNode(name);
            inner.traverse((o) => { if (o.isMesh) o.castShadow = true; });
            const box = new THREE.Box3().setFromObject(inner);
            const pivot = new THREE.Group();
            if (name === 'Shovel') { inner.position.y = -Math.max(0.3, box.max.y - 0.06); pivot.rotation.x = 0.55; }
            else { inner.position.y = -Math.max(0.12, box.max.y * 0.92); pivot.rotation.x = 0.15; }
            pivot.add(inner);
            this.hand.add(pivot);
            this.prop = pivot;
          },
        };
        scene.add(holder);
        chars.push(c);
        return c;
      }

      // てつづきで うごかす アニメ（glb に その うごきが ない とき）
      function procPose(c, verb, dt) {
        const t = c.t;
        const P = c.parts;
        const tg = { ArmL: [0, 0, 0], ArmR: [0, 0, 0], LegL: [0, 0, 0], LegR: [0, 0, 0], Head: [0, 0, 0], Tail: [0, Math.sin(t * 11) * 0.6, 0], Body: [0, 0, 0] };
        let bob = 0; let lean = 0;
        switch (verb) {
          case 'walk': {
            const s = Math.sin(t * 9);
            tg.LegL[0] = s * 0.6; tg.LegR[0] = -s * 0.6; tg.ArmL[0] = -s * 0.5; tg.ArmR[0] = s * 0.5;
            bob = Math.abs(Math.cos(t * 9)) * 0.035; break;
          }
          case 'dig': {
            const s = Math.sin(t * 7);
            tg.ArmR[0] = -0.9 + s * 0.55; tg.ArmL[0] = -0.75 + s * 0.45;
            tg.LegL[0] = -0.5; tg.LegR[0] = -0.5;
            lean = 0.32; bob = -0.07; tg.Head[0] = 0.2; break;
          }
          case 'sit':
            tg.LegL[0] = -1.45; tg.LegR[0] = -1.45; tg.ArmL[0] = -0.35; tg.ArmR[0] = -0.35; bob = -0.25;
            tg.Head[2] = Math.sin(t * 1.4) * 0.06; break;
          case 'cheer': {
            const s = Math.sin(t * 12);
            tg.ArmL[2] = 2.5 + s * 0.25; tg.ArmR[2] = -2.5 - s * 0.25;
            bob = Math.abs(Math.sin(t * 6)) * 0.13; break;
          }
          case 'hold':
            tg.ArmL[0] = -1.2; tg.ArmR[0] = -1.2; tg.ArmL[2] = -0.12; tg.ArmR[2] = 0.12; bob = Math.sin(t * 2) * 0.006; break;
          case 'wave':
            tg.ArmR[2] = -2.45 + Math.sin(t * 9) * 0.45; tg.Head[2] = 0.1; bob = Math.sin(t * 3) * 0.01; break;
          default:
            bob = Math.sin(t * 2) * 0.008; tg.Head[2] = Math.sin(t * 1.3) * 0.07; tg.ArmL[2] = 0.08; tg.ArmR[2] = -0.08;
        }
        const k = 1 - Math.exp(-dt * 14);
        for (const p of PARTS) {
          const n = P[p]; if (!n) continue;
          const r = c.rest[p]; const v = tg[p] || [0, 0, 0];
          n.rotation.x = lerp(n.rotation.x, r.x + v[0], k);
          n.rotation.y = lerp(n.rotation.y, r.y + v[1], k);
          n.rotation.z = lerp(n.rotation.z, r.z + v[2], k);
        }
        c.pose.position.y = lerp(c.pose.position.y, bob, k);
        c.pose.rotation.x = lerp(c.pose.rotation.x, lean, k);
      }

      function showVerb(c, verb) {
        if (c.shown === verb) return;
        c.shown = verb;
        const clip = c.clips[verb];
        if (c.mixer && clip) {
          const next = c.mixer.clipAction(clip);
          next.reset().setEffectiveWeight(1).fadeIn(0.25).play();
          if (c.action && c.action !== next) c.action.fadeOut(0.25);
          c.action = next;
          c.useProc = false;
        } else {
          if (c.action) { c.action.fadeOut(0.25); c.action = null; }
          c.useProc = true;
        }
      }

      function updateChar(c, dt) {
        c.t += dt;
        let verb = c.verb;
        if (c.target) {
          const dx = c.target.x - c.x; const dz = c.target.z - c.z;
          const d = Math.hypot(dx, dz);
          if (d < 0.03) {
            c.x = c.target.x; c.z = c.target.z; c.target = null; c.onStep = null;
            const r = c.resolve; c.resolve = null; if (r) r(true);
          } else {
            const step = Math.min(d, c.speed * dt);
            c.x += (dx / d) * step; c.z += (dz / d) * step;
            const want = c.faceDir != null ? c.faceDir : Math.atan2(dx, dz);
            c.heading += angleDiff(c.heading, want) * Math.min(1, dt * 10);
            verb = c.walkVerb;
            if (c.onStep) c.onStep(c);
          }
        }
        if (!c.target && c.look) {
          const want = Math.atan2(c.look.x - c.x, c.look.z - c.z);
          if (Math.hypot(c.look.x - c.x, c.look.z - c.z) > 0.05) c.heading += angleDiff(c.heading, want) * Math.min(1, dt * 8);
        }
        const gy = groundY(c.x, c.z);
        c.y += (gy - c.y) * Math.min(1, dt * 12);
        c.sync();
        showVerb(c, verb);
        if (c.mixer && !c.useProc) {
          c.mixer.update(dt);
          c.pose.position.y *= 0.9; c.pose.rotation.x *= 0.9;
        } else {
          if (c.mixer) c.mixer.update(dt);
          procPose(c, verb, dt);
        }
        // ふきだし
        if (c.bubble && c.bubbleTimer > 0) {
          c.bubbleTimer -= dt;
          tmpV.set(c.x, c.y + 1.3, c.z).project(camera);
          const vis = tmpV.z < 1 && c.bubbleTimer > 0;
          c.bubble.classList.toggle('show', vis);
          if (vis) {
            c.bubble.style.left = ((tmpV.x + 1) / 2) * viewW + 'px';
            c.bubble.style.top = ((1 - tmpV.y) / 2) * viewH + 'px';
          }
        }
      }

      // ふきだし＋よみあげ
      function say(id, text, quiet) {
        const c = id === 'inu' ? inu : id === 'pen' ? pen : null;
        if (!c) return quiet ? Promise.resolve() : speak(text);
        if (!c.bubble) { c.bubble = el('div', { class: 's3d-bubble' }); bubbleLayer.append(c.bubble); }
        c.bubble.textContent = text;
        c.bubbleTimer = Math.max(3.5, text.length * 0.16);
        return quiet ? Promise.resolve() : speak(text);
      }

      // ---- おいた もの ----
      let items = [];
      function itemY(it) {
        if (it.k === 'mold') {
          let m = 0; const r = MOLD_BY[it.s].r * 0.5;
          for (const [ox, oz] of [[0, 0], [r, 0], [-r, 0], [0, r], [0, -r]]) m += sampleH(it.x + ox, it.z + oz);
          return SAND_Y + m / 5 - 0.015;
        }
        return SAND_Y + sampleH(it.x, it.z);
      }
      function spawnItem(it, pop) {
        const node = it.k === 'mold' ? MOLD_BY[it.s].node : DECO_BY[it.s].node;
        const o = cloneNode(node);
        o.traverse((m) => { if (m.isMesh) { m.castShadow = true; m.receiveShadow = true; } });
        if (it.s === 'castle') {
          const f = cloneNode('Flag');
          f.position.copy(castleTop);
          o.add(f);
        }
        o.position.set(it.x, itemY(it), it.z);
        o.rotation.y = it.r || 0;
        scene.add(o);
        it.obj = o;
        if (pop) tween(0.45, (k) => { const s = k < 0.7 ? lerp(0.3, 1.15, k / 0.7) : lerp(1.15, 1, (k - 0.7) / 0.3); o.scale.setScalar(s); });
        return it;
      }
      function removeItem(it, anim) {
        items = items.filter((x) => x !== it);
        const o = it.obj;
        if (!o) return;
        if (anim) tween(0.35, (k) => { o.scale.set(1 + k * 0.3, 1 - k, 1 + k * 0.3); if (k >= 1) scene.remove(o); });
        else scene.remove(o);
      }
      function itemsFollow(cx, cz, R) {
        for (const it of items) if (it.obj && Math.hypot(it.x - cx, it.z - cz) < R + 0.5) it.obj.position.y = itemY(it);
      }
      let castleTop = new THREE.Vector3(0.32, 0.8, 0.32);
      function measureCastle() {
        const o = cloneNode('CastleMold');
        o.updateMatrixWorld(true);
        const rc = new THREE.Raycaster();
        const box = new THREE.Box3().setFromObject(o);
        const tx = box.isEmpty() ? 0.32 : box.max.x * 0.7; const tz = box.isEmpty() ? 0.32 : box.max.z * 0.7;
        for (const [x, z] of [[tx, tz], [0, 0]]) {
          rc.set(new THREE.Vector3(x, 5, z), new THREE.Vector3(0, -1, 0));
          const hit = rc.intersectObject(o, true)[0];
          if (hit) { castleTop = new THREE.Vector3(x, hit.point.y - 0.02, z); return; }
        }
        if (!box.isEmpty()) castleTop = new THREE.Vector3(0, box.max.y, 0);
      }

      // ---- うごき（tween）と つぶ ----
      const tweens = [];
      function tween(dur, fn) { return new Promise((r) => tweens.push({ t: 0, dur, fn, r })); }
      const dropGeo = new THREE.SphereGeometry(0.025, 8, 6);
      const dropMat = new THREE.MeshBasicMaterial({ color: col('#7cc8ff'), transparent: true, opacity: 0.9 });
      const sparkMat = new THREE.MeshBasicMaterial({ color: col('#ffffff'), transparent: true, opacity: 0.95 });
      disposables.push(dropGeo, dropMat, sparkMat);
      const particles = [];
      function particle(mat, from, vel, life, size = 1) {
        let p = particles.find((q) => q.life <= 0 && q.mesh.material === mat);
        if (!p) {
          if (particles.length > 160) return;
          p = { mesh: new THREE.Mesh(dropGeo, mat), life: 0 };
          scene.add(p.mesh);
          particles.push(p);
        }
        p.mesh.visible = true;
        p.mesh.position.copy(from);
        p.mesh.scale.setScalar(size);
        p.vel = vel.clone();
        p.life = life; p.max = life; p.grav = mat === dropMat;
      }
      function updateParticles(dt) {
        for (const p of particles) {
          if (p.life <= 0) continue;
          p.life -= dt;
          if (p.grav) p.vel.y -= 9 * dt;
          p.mesh.position.addScaledVector(p.vel, dt);
          if (p.grav && p.mesh.position.y < groundY(p.mesh.position.x, p.mesh.position.z)) p.life = 0;
          if (!p.grav) p.mesh.scale.setScalar(Math.max(0.01, p.life / p.max) * 1.1);
          if (p.life <= 0) p.mesh.visible = false;
        }
      }

      // ---- カメラ ----
      const cam = { yaw: 0, pitch: 50 * DEG, dist: 12, yawT: 0, pitchT: 50 * DEG, distT: 12, minD: 6, maxD: 16, fit: 12 };
      let viewW = 1; let viewH = 1;
      function fitCamera() {
        const r = view.getBoundingClientRect();
        viewW = Math.max(1, r.width); viewH = Math.max(1, r.height);
        renderer.setSize(viewW, viewH, false);
        camera.aspect = viewW / viewH;
        camera.updateProjectionMatrix();
        const tv = Math.tan((camera.fov * DEG) / 2);
        const fit = Math.max(4.3 / tv, 4.75 / (tv * camera.aspect));
        const ratio = cam.distT / cam.fit;
        cam.fit = fit; cam.minD = fit * 0.5; cam.maxD = fit * 1.3;
        cam.distT = clamp(fit * ratio, cam.minD, cam.maxD);
        if (!started) cam.dist = cam.distT;
      }
      function updateCamera(dt) {
        const k = 1 - Math.exp(-dt * 8);
        cam.pitchT = clamp(cam.pitchT, PITCH_MIN, PITCH_MAX);
        cam.yaw += (cam.yawT - cam.yaw) * k;
        cam.pitch += (cam.pitchT - cam.pitch) * k;
        cam.dist += (cam.distT - cam.dist) * k;
        const cp = Math.cos(cam.pitch);
        camera.position.set(Math.sin(cam.yaw) * cp * cam.dist, 0.3 + Math.sin(cam.pitch) * cam.dist, Math.cos(cam.yaw) * cp * cam.dist);
        camera.lookAt(Math.sin(cam.yaw) * 0.45, 0.1, Math.cos(cam.yaw) * 0.45);
      }
      let started = false;
      const ro = new ResizeObserver(() => fitCamera());
      ro.observe(view);
      fitCamera();
      started = true;

      // がめんの てん → すなの うえの てん
      const raycaster = new THREE.Raycaster();
      const ndc = new THREE.Vector2();
      function hitSand(clientX, clientY) {
        const r = canvas.getBoundingClientRect();
        ndc.set(((clientX - r.left) / r.width) * 2 - 1, -((clientY - r.top) / r.height) * 2 + 1);
        raycaster.setFromCamera(ndc, camera);
        const o = raycaster.ray.origin; const d = raycaster.ray.direction;
        if (d.y >= -1e-3) return null;
        const top = SAND_Y + H_MAX + 0.05; const bot = SAND_Y + H_MIN - 0.05;
        let t = Math.max(0, (top - o.y) / d.y); const tEnd = (bot - o.y) / d.y;
        const surf = (tt) => { const x = o.x + d.x * tt; const z = o.z + d.z * tt; const ins = Math.abs(x) <= HALF && Math.abs(z) <= HALF; return { x, z, below: ins && o.y + d.y * tt <= SAND_Y + sampleH(x, z) }; };
        let prev = t;
        for (; t <= tEnd; t += 0.03) {
          if (surf(t).below) {
            let a = prev; let b = t;
            for (let k = 0; k < 8; k++) { const m = (a + b) / 2; if (surf(m).below) b = m; else a = m; }
            const p = surf(b);
            return { x: clamp(p.x, -HALF + 0.02, HALF - 0.02), z: clamp(p.z, -HALF + 0.02, HALF - 0.02) };
          }
          prev = t;
        }
        // すなに あたらない ときは、すなの たかさの ひらめんで
        const tp = (SAND_Y - o.y) / d.y;
        const x = o.x + d.x * tp; const z = o.z + d.z * tp;
        if (Math.abs(x) <= HALF + 0.3 && Math.abs(z) <= HALF + 0.3) return { x: clamp(x, -HALF + 0.02, HALF - 0.02), z: clamp(z, -HALF + 0.02, HALF - 0.02) };
        return null;
      }

      // ---- ゆびの そうさ ----
      const ptrs = new Map();
      let gesture = null;
      let gestureLock = false;
      let stroke = null;
      let talking = 0;
      let busy = false;          // できごとの とちゅう
      let seq = false;           // トンネル かいつうの えんしゅつ ちゅう
      let lastTouch = Date.now();
      const pours = new Set();

      function startGesture() {
        const [a, b] = [...ptrs.values()];
        gesture = {
          a0: Math.atan2(b.y - a.y, b.x - a.x), d0: Math.max(20, Math.hypot(b.x - a.x, b.y - a.y)),
          mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2, yaw: cam.yawT, pitch: cam.pitchT, dist: cam.distT,
        };
      }
      function moveGesture() {
        const [a, b] = [...ptrs.values()];
        const ang = Math.atan2(b.y - a.y, b.x - a.x);
        const d = Math.max(20, Math.hypot(b.x - a.x, b.y - a.y));
        const mx = (a.x + b.x) / 2; const my = (a.y + b.y) / 2;
        cam.yawT = gesture.yaw - angleDiff(gesture.a0, ang) - (mx - gesture.mx) * 0.008;
        cam.pitchT = clamp(gesture.pitch + (my - gesture.my) * 0.006, PITCH_MIN, PITCH_MAX);
        cam.distT = clamp(gesture.dist * (gesture.d0 / d), cam.minD, cam.maxD);
      }
      function cancelStroke() {
        if (!stroke) return;
        pours.delete(stroke);
        stroke = null;
        if (player && !seq) player.act('idle');
      }
      canvas.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        try { canvas.setPointerCapture(e.pointerId); } catch (err) { /* なにもしない */ }
        ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
        lastTouch = Date.now();
        if (ptrs.size >= 2) { cancelStroke(); startGesture(); gestureLock = true; return; }
        if (gestureLock || talking || !ready || seq || confirmOpen) return;
        stroke = { id: e.pointerId, sx: e.clientX, sy: e.clientY, x: e.clientX, y: e.clientY, t0: performance.now(), on: false, moved: 0, tool, last: null, pts: [] };
      });
      canvas.addEventListener('pointermove', (e) => {
        const p = ptrs.get(e.pointerId);
        if (!p) return;
        p.x = e.clientX; p.y = e.clientY;
        lastTouch = Date.now();
        if (gesture && ptrs.size >= 2) { moveGesture(); return; }
        if (stroke && stroke.id === e.pointerId) {
          stroke.moved = Math.max(stroke.moved, Math.hypot(e.clientX - stroke.sx, e.clientY - stroke.sy));
          stroke.x = e.clientX; stroke.y = e.clientY;
          if (stroke.tool === 'tunnel') { const hp = hitSand(e.clientX, e.clientY); if (hp) stroke.pts.push(hp); }
        }
      });
      function endPointer(e) {
        if (!ptrs.has(e.pointerId)) return;
        ptrs.delete(e.pointerId);
        if (ptrs.size < 2) gesture = null;
        if (!ptrs.size) gestureLock = false;
        if (stroke && stroke.id === e.pointerId) {
          const s = stroke;
          stroke = null;
          pours.delete(s);
          if (e.type !== 'pointercancel') finishStroke(s);
          else if (player) player.act('idle');
        }
      }
      canvas.addEventListener('pointerup', endPointer);
      canvas.addEventListener('pointercancel', endPointer);
      canvas.addEventListener('lostpointercapture', endPointer);
      canvas.addEventListener('wheel', (e) => { e.preventDefault(); cam.distT = clamp(cam.distT * (e.deltaY > 0 ? 1.1 : 0.9), cam.minD, cam.maxD); }, { passive: false });
      canvas.addEventListener('contextmenu', (e) => e.preventDefault());

      // プレイヤーが しごとを する ところへ あるく
      function workAt(p, verb) {
        if (!player || seq) return;
        const fx = -Math.sin(cam.yaw); const fz = -Math.cos(cam.yaw);
        let sx = p.x + fx * 0.6; let sz = p.z + fz * 0.6;
        sx = clamp(sx, -HALF - 0.2, HALF + 0.2); sz = clamp(sz, -HALF - 0.2, HALF + 0.2);
        const tx = player.target ? player.target.x : player.x; const tz = player.target ? player.target.z : player.z;
        if (Math.hypot(sx - tx, sz - tz) > 0.45) player.walkTo(sx, sz, { speed: 2 });
        player.face(p.x, p.z);
        player.act(verb);
      }

      function applyStroke(dt) {
        const s = stroke;
        if (!s) return;
        if (!s.on) {
          if (s.moved > 8 || performance.now() - s.t0 > 90) s.on = true; else return;
        }
        if (s.tool === 'bucket' || s.tool === 'deco') return;
        // ゆびが とまっている ときは おなじ ところを ほりつづける（ほった あなの おくに ずれないように）
        const still = s.last && s.ls && Math.hypot(s.x - s.ls.x, s.y - s.ls.y) < 4;
        const p = still ? s.last : hitSand(s.x, s.y);
        if (!p) return;
        if (!still) s.ls = { x: s.x, y: s.y };
        lastTouch = Date.now();
        const mv = s.last ? Math.hypot(p.x - s.last.x, p.z - s.last.z) : 0;
        s.last = p;
        if (s.tool === 'dig') {
          digAt(p.x, p.z, dt * 0.22 + Math.min(mv, 0.3) * 0.12);
          workAt(p, 'dig');
          if (Math.random() < dt * 4) sound('tap');
        } else if (s.tool === 'mound') {
          moundAt(p.x, p.z, dt * 0.2 + Math.min(mv, 0.3) * 0.1);
          workAt(p, 'hold');
        } else if (s.tool === 'water') {
          s.at = p;
          pours.add(s);
          workAt(p, 'hold');
        } else if (s.tool === 'tunnel') {
          if (!s.pts.length) s.pts.push(p);
          if (s.pts.length === 1) workAt(p, 'dig');
        }
      }

      function finishStroke(s) {
        if (seq) return;
        if (s.tool === 'bucket' || s.tool === 'deco') {
          if (s.moved > 24) return;
          const p = hitSand(s.x, s.y);
          if (!p) return;
          if (s.tool === 'bucket') placeMold(p); else placeDeco(p);
          return;
        }
        if (s.tool === 'tunnel') { tryTunnel(s); return; }
        later(() => { if (!stroke && player && !seq) player.act('idle'); }, 500);
        saveSoon();
      }

      // ---- かたぬき ----
      async function placeMold(p) {
        const m = MOLD_BY[mold];
        sound('flip');
        workAt(p, 'hold');
        const it = { k: 'mold', s: mold, x: p.x, z: p.z, r: cam.yaw + (Math.random() - 0.5) * 0.4 };
        // かたの したを たいらに、まわりを すこし もる
        const hb = sampleH(p.x, p.z);
        const rect = brush(p.x, p.z, m.r * 1.7, (i, d) => {
          const u = d / m.r;
          if (u < 0.85) h[i] = lerp(h[i], hb, 0.85);
          else h[i] = Math.min(H_MAX, h[i] + 0.06 * Math.sin(Math.PI * (u - 0.85) / 0.85));
        });
        if (rect) checkCollapse(rect);
        // バケツを さかさに して ぽん
        const b = cloneNode('Bucket');
        b.rotation.x = Math.PI;
        const by = SAND_Y + hb;
        const bh = new THREE.Box3().setFromObject(b).getSize(new THREE.Vector3()).y || 0.3;
        const scale = (m.r * 2) / 0.32;
        b.scale.setScalar(scale);
        scene.add(b);
        await tween(0.3, (k) => b.position.set(p.x, by + bh * scale + (1 - k) * 1.1, p.z));
        await tween(0.12, (k) => b.scale.set(scale * (1 + 0.08 * Math.sin(k * Math.PI)), scale, scale * (1 + 0.08 * Math.sin(k * Math.PI))));
        items.push(it);
        spawnItem(it, true);
        itemsFollow(p.x, p.z, m.r);
        trimItems();
        tween(0.4, (k) => { b.position.y = by + bh * scale + k * 1.2; b.scale.setScalar(scale * (1 - k * 0.6)); if (k >= 1) scene.remove(b); });
        if (player) { player.act('cheer'); later(() => { if (!stroke && !seq) player.act('idle'); }, 1200); }
        reactToBuild(p, m.id);
        saveSoon();
      }
      function placeDeco(p) {
        sound('tap');
        workAt(p, 'hold');
        const it = { k: 'deco', s: deco, x: p.x, z: p.z, r: Math.random() * Math.PI * 2 };
        items.push(it);
        spawnItem(it, true);
        trimItems();
        later(() => { if (!stroke && player && !seq) player.act('idle'); }, 700);
        saveSoon();
      }
      function trimItems() {
        while (items.length > 60) removeItem(items[0], true);
      }

      // ---- トンネル ----
      let tunnels = [];
      let tunnelFlowSaid = false;
      function rebuildTf() {
        tf.fill(1e9);
        for (const t of tunnels) for (let k = 0; k < t.cells.length; k++) { const i = t.cells[k]; if (t.floors[k] < tf[i]) tf[i] = t.floors[k]; }
      }
      // なぞった せんを しらべる
      function analyzeTunnel(pts) {
        if (pts.length < 2) return { ok: false, why: 'cross' };
        const P0 = pts[0]; const P1 = pts[pts.length - 1];
        const len = Math.hypot(P1.x - P0.x, P1.z - P0.z);
        let peakAll = -1;
        for (const p of pts) peakAll = Math.max(peakAll, sampleH(p.x, p.z));
        if (len < 0.6) return { ok: false, why: peakAll < TUNNEL_RISE ? 'low' : 'cross' };
        const M = Math.ceil(len / (CELL * 0.7));
        const hs = []; const xs = []; const zs = [];
        for (let k = 0; k <= M; k++) {
          const t = k / M; const x = lerp(P0.x, P1.x, t); const z = lerp(P0.z, P1.z, t);
          xs.push(x); zs.push(z); hs.push(sampleH(x, z));
        }
        let pk = 0;
        for (let k = 1; k <= M; k++) if (hs[k] > hs[pk]) pk = k;
        const baseA = hs[0]; const baseB = hs[M];
        const rise = hs[pk] - Math.max(baseA, baseB);
        if (rise < TUNNEL_RISE) return { ok: false, why: hs[pk] - Math.min(baseA, baseB) >= TUNNEL_RISE || peakAll >= TUNNEL_RISE + 0.05 ? 'cross' : 'low' };
        // ふもと（あしもと）
        let ia = pk; while (ia > 0 && hs[ia] > baseA + 0.05) ia--;
        let ib = pk; while (ib < M && hs[ib] > baseB + 0.05) ib++;
        const minNear = (from, dir) => { let m = hs[from]; for (let k = 0; k < 5; k++) { const j = from + dir * k; if (j < 0 || j > M) break; m = Math.min(m, hs[j]); } return m; };
        const fa = minNear(ia, -1); const fb = minNear(ib, 1);
        const top = hs[pk] - Math.max(fa, fb);
        const mouthH = (f) => f + Math.min(0.3, top * 0.55);
        let ma = ia; while (ma < pk && hs[ma] < mouthH(fa)) ma++;
        let mb = ib; while (mb > pk && hs[mb] < mouthH(fb)) mb--;
        if (mb - ma < 2) { ma = Math.max(ia, pk - 2); mb = Math.min(ib, pk + 2); }
        return {
          ok: true,
          def: {
            ax: xs[ma], az: zs[ma], bx: xs[mb], bz: zs[mb], fa, fb,
            ea: Math.hypot(xs[ma] - xs[ia], zs[ma] - zs[ia]) + 0.25, eb: Math.hypot(xs[mb] - xs[ib], zs[mb] - zs[ib]) + 0.25,
            s: clamp((top * 0.85) / 0.45, 0.5, 1),
            footA: { x: xs[ia], z: zs[ia] }, footB: { x: xs[ib], z: zs[ib] },
          },
        };
      }
      // トンネルを つくる（carve=true のときは いりぐちを ほる）
      function buildTunnel(def, carve) {
        const L = Math.hypot(def.bx - def.ax, def.bz - def.az) || 0.01;
        const ux = (def.bx - def.ax) / L; const uz = (def.bz - def.az) / L;
        const floorAt = (t) => lerp(def.fa, def.fb, clamp(t, 0, 1)) - 0.01;
        const sA = -def.ea; const sB = L + def.eb;
        const pad = TUNNEL_R + 0.3;
        const xs = [def.ax + ux * sA, def.ax + ux * sB]; const zs = [def.az + uz * sA, def.az + uz * sB];
        const x0 = Math.max(0, Math.floor(toGrid(Math.min(...xs) - pad))); const x1 = Math.min(N - 1, Math.ceil(toGrid(Math.max(...xs) + pad)));
        const z0 = Math.max(0, Math.floor(toGrid(Math.min(...zs) - pad))); const z1 = Math.min(N - 1, Math.ceil(toGrid(Math.max(...zs) + pad)));
        if (carve) {
          // いりぐちの くぼみ と、そとの みち
          for (let z = z0; z <= z1; z++) {
            for (let x = x0; x <= x1; x++) {
              const px = x * CELL - HALF; const pz = z * CELL - HALF;
              const s = (px - def.ax) * ux + (pz - def.az) * uz;
              const d = Math.abs((px - def.ax) * -uz + (pz - def.az) * ux);
              const i = z * N + x;
              const f = floorAt(s / L);
              if ((s < 0 || s > L) && s > sA && s < sB && d < TUNNEL_R * 1.4) {
                const k = d / (TUNNEL_R * 1.4);
                h[i] = Math.min(h[i], f + 0.005 + k * k * 0.05);
              }
              const NR = Math.min(0.24, L * 0.32);
              for (const [mx, mz, dir] of [[def.ax, def.az, 1], [def.bx, def.bz, -1]]) {
                const along = (px - mx) * ux * dir + (pz - mz) * uz * dir; // おやまの なかへの ふかさ
                if (along > 0.08) continue;
                const dd = Math.hypot(px - mx, pz - mz);
                if (dd < NR) {
                  const k = dd / NR;
                  h[i] = Math.min(h[i], f + 0.01 + k * k * 0.3);
                }
              }
            }
          }
          grow(sandDirty, x0, x1, z0, z1);
        }
        const cells = []; const floors = []; const interior = [];
        for (let z = z0; z <= z1; z++) {
          for (let x = x0; x <= x1; x++) {
            const px = x * CELL - HALF; const pz = z * CELL - HALF;
            const s = (px - def.ax) * ux + (pz - def.az) * uz;
            if (s < sA || s > sB) continue;
            const d = Math.abs((px - def.ax) * -uz + (pz - def.az) * ux);
            if (d >= TUNNEL_R) continue;
            const i = z * N + x;
            const f = floorAt(s / L) - 0.012 * (1 - (d / TUNNEL_R) ** 2);
            cells.push(i); floors.push(f);
            if (s > 0.05 && s < L - 0.05 && h[i] - f > TUNNEL_CEIL + 0.04) interior.push(i, f);
          }
        }
        const t = { def, ux, uz, L, cells, floors, interior, objs: [], firstSide: null, passed: false, rect: { x0, x1, z0, z1 }, mid: cellAt((def.ax + def.bx) / 2, (def.az + def.bz) / 2) };
        // いりぐちの ぶひん
        for (const [mx, mz, dir, f] of [[def.ax, def.az, -1, def.fa], [def.bx, def.bz, 1, def.fb]]) {
          const g = new THREE.Group();
          const arch = cloneNode('TunnelArch');
          arch.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
          g.add(arch);
          g.add(mouthMesh());
          const outX = ux * dir; const outZ = uz * dir;
          g.position.set(mx + outX * 0.04, SAND_Y + f - 0.01, mz + outZ * 0.04);
          g.rotation.y = Math.atan2(outX, outZ);
          g.scale.setScalar(def.s || 0.7);
          scene.add(g);
          t.objs.push(g);
          t[dir < 0 ? 'mouthA' : 'mouthB'] = { x: mx + outX * 0.12, z: mz + outZ * 0.12, ox: outX, oz: outZ, f, i: cellAt(mx + outX * 0.12, mz + outZ * 0.12), g };
        }
        tunnels.push(t);
        rebuildTf();
        grow(waterRect, x0, x1, z0, z1);
        grow(waterDirty, x0, x1, z0, z1);
        return t;
      }
      // いりぐちの くらい あな（はんえん と おくへ つづく はんぶんの つつ）
      const mouthMats = { dark: new THREE.MeshBasicMaterial({ color: col('#3a2716') }), inner: new THREE.MeshLambertMaterial({ color: col('#7a5a35'), side: THREE.BackSide }) };
      const mouthGeos = {
        disc: new THREE.CircleGeometry(0.2, 20, 0, Math.PI),
        tube: new THREE.CylinderGeometry(0.2, 0.2, 0.5, 16, 1, true, -Math.PI / 2, Math.PI),
      };
      mouthGeos.tube.rotateX(Math.PI / 2);
      mouthGeos.tube.rotateZ(Math.PI);
      disposables.push(mouthMats.dark, mouthMats.inner, mouthGeos.disc, mouthGeos.tube);
      function mouthMesh() {
        const g = new THREE.Group();
        const disc = new THREE.Mesh(mouthGeos.disc, mouthMats.dark);
        disc.scale.set(1, 1.55, 1);
        disc.position.z = -0.42;
        const tube = new THREE.Mesh(mouthGeos.tube, mouthMats.inner);
        tube.scale.set(1, 1.55, 1);
        tube.position.z = -0.2;
        g.add(tube, disc);
        return g;
      }
      function removeTunnel(t, anim) {
        tunnels = tunnels.filter((x) => x !== t);
        for (const o of t.objs) {
          if (anim) tween(0.5, (k) => { o.scale.setScalar((t.def.s || 0.7) * (1 - k)); if (k >= 1) scene.remove(o); });
          else scene.remove(o);
        }
        // なかの みずは うえに でてくる
        for (const i of t.cells) if (tf[i] < h[i] && w[i] > 0) w[i] *= 0.3;
        rebuildTf();
        grow(waterRect, t.rect.x0, t.rect.x1, t.rect.z0, t.rect.z1);
        grow(waterDirty, t.rect.x0, t.rect.x1, t.rect.z0, t.rect.z1);
      }
      let collapseSaidAt = 0;
      function checkCollapse(rect) {
        let broke = false;
        for (const t of tunnels.slice()) {
          const r = t.rect;
          if (rect.x1 < r.x0 || rect.x0 > r.x1 || rect.z1 < r.z0 || rect.z0 > r.z1) continue;
          for (let k = 0; k < t.interior.length; k += 2) {
            const i = t.interior[k];
            if (h[i] - t.interior[k + 1] < TUNNEL_CEIL) { removeTunnel(t, true); broke = true; break; }
          }
        }
        if (broke) {
          sound('flip');
          saveSoon();
          if (Date.now() - collapseSaidAt > 4000) {
            collapseSaidAt = Date.now();
            speak('あっ、トンネルが くずれちゃった。もういちど つくろう！');
          }
        }
        return broke;
      }

      let lastTunnelHint = 0;
      async function tryTunnel(s) {
        const pts = s.pts.length ? s.pts : [hitSand(s.x, s.y)].filter(Boolean);
        const res = analyzeTunnel(pts);
        if (!res.ok) {
          if (player) player.act('idle');
          sound('tap');
          if (Date.now() - lastTunnelHint < 1500) return;
          lastTunnelHint = Date.now();
          if (res.why === 'low') {
            toolBtns.mound.classList.remove('hint'); void toolBtns.mound.offsetWidth; toolBtns.mound.classList.add('hint');
            speak('もっと たかい おやまを つくってから ほってみよう。「もりあげる」で おやまを つくってね。');
          } else {
            speak('おやまの こっちがわから むこうがわまで、ゆびで なぞってね。');
          }
          return;
        }
        if (tunnels.length >= 3) removeTunnel(tunnels[0], true);
        await tunnelSequence(res.def);
      }
      async function tunnelSequence(def) {
        seq = true;
        const helper = inu && inuMode === 'free' && !busy && !lending;
        try {
          const L = Math.hypot(def.bx - def.ax, def.bz - def.az) || 1;
          const ux = (def.bx - def.ax) / L; const uz = (def.bz - def.az) / L;
          // こどもは こっちがわ、いぬくんは むこうがわ から ほる
          const pa = { x: clamp(def.ax - ux * 0.55, -HALF + 0.1, HALF - 0.1), z: clamp(def.az - uz * 0.55, -HALF + 0.1, HALF - 0.1) };
          const pb = { x: clamp(def.bx + ux * 0.55, -HALF + 0.1, HALF - 0.1), z: clamp(def.bz + uz * 0.55, -HALF + 0.1, HALF - 0.1) };
          if (player) { player.hold(lending ? null : 'Shovel'); player.walkTo(pa.x, pa.z, { speed: 2.2 }); player.face(def.ax, def.az); player.act('dig'); }
          if (helper) {
            inuMode = 'tunnel';
            inu.walkTo(pb.x, pb.z, { speed: 2.4 }); inu.face(def.bx, def.bz); inu.act('dig');
            say('inu', 'むこうから ぼくも ほるね！', true);
          }
          for (let k = 0; k < 4; k++) {
            sound('tap');
            await pause(380);
            if (!alive()) return;
          }
          if (helper) await Promise.race([new Promise((r) => { const chk = () => (!inu.target || !alive() ? r() : later(chk, 100)); chk(); }), pause(2500)]);
          const t = buildTunnel(def, true);
          t.objs.forEach((o) => { const s = def.s || 0.7; tween(0.4, (k) => o.scale.setScalar(s * (k < 0.7 ? k / 0.7 * 1.15 : lerp(1.15, 1, (k - 0.7) / 0.3)))); });
          for (let k = 0; k < 14; k++) particle(sparkMat, new THREE.Vector3(lerp(def.ax, def.bx, Math.random()), SAND_Y + lerp(def.fa, def.fb, 0.5) + 0.3 + Math.random() * 0.3, lerp(def.az, def.bz, Math.random())), new THREE.Vector3((Math.random() - 0.5) * 0.6, 0.8 + Math.random() * 0.6, (Math.random() - 0.5) * 0.6), 0.9, 1.4);
          sound('fanfare');
          saveSoon();
          if (player) player.act('wave');
          if (helper) { inu.act('wave'); say('inu', 'こんにちは！ トンネルの なかで てが あったね！', true); }
          if (pen) penCheer();
          await speak('トンネル かいつう！');
          if (helper && alive()) await say('inu', 'こんにちは！ トンネルの なかで てが あったね！');
          await pause(800);
        } finally {
          seq = false;
          if (alive()) {
            if (player) { player.act('idle'); player.hold(handTool()); }
            if (helper && inuMode === 'tunnel') { inu.act('idle'); inuMode = 'free'; }
          }
        }
      }
      // トンネルの なかを みずが とおったか みる・あわを だす
      let tunnelTick = 0;
      function watchTunnels(dt) {
        tunnelTick += dt;
        const tick = tunnelTick > 0.12;
        if (tick) tunnelTick = 0;
        for (const t of tunnels) {
          const wa = w[t.mouthA.i] > WATER_SHOW; const wb = w[t.mouthB.i] > WATER_SHOW;
          const inside = w[t.mid] > 0.003;
          if (tick && inside) {
            for (const m of [t.mouthA, t.mouthB]) {
              if (w[m.i] <= WATER_SHOW) continue;
              const y = SAND_Y + m.f + w[m.i] + 0.03;
              particle(sparkMat, new THREE.Vector3(m.x - m.ox * 0.25 + (Math.random() - 0.5) * 0.1, y, m.z - m.oz * 0.25 + (Math.random() - 0.5) * 0.1),
                new THREE.Vector3(m.ox * 0.7, 0.05 + Math.random() * 0.1, m.oz * 0.7), 0.9, 0.6 + Math.random() * 0.5);
            }
          }
          if (!t.firstSide) {
            if (wa && !wb) t.firstSide = 'a'; else if (wb && !wa) t.firstSide = 'b'; else if (wa && wb) t.firstSide = 'both';
          } else if (!t.passed && ((t.firstSide === 'a' && wb) || (t.firstSide === 'b' && wa)) && inside) {
            t.passed = true;
            if (!tunnelFlowSaid) {
              tunnelFlowSaid = true;
              sound('correct');
              speak('みずが トンネルを とおったよ！');
              if (player && !stroke && !seq) { player.act('cheer'); later(() => { if (!stroke && !seq) player.act('idle'); }, 1500); }
              if (pen) penCheer();
            }
          }
        }
      }

      // ---- ほぞん ----
      let saveTimer = 0;
      function saveNow() {
        clearTimeout(saveTimer);
        try {
          store.set('sand', {
            v: 1, h: encodeF32(h), w: encodeF32(w),
            items: items.map((it) => ({ k: it.k, s: it.s, x: +it.x.toFixed(3), z: +it.z.toFixed(3), r: +(it.r || 0).toFixed(3) })),
            tunnels: tunnels.map((t) => t.def),
          });
        } catch (e) { /* ほぞん できない ときは あきらめる */ }
      }
      function saveSoon() {
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => { if (alive()) saveNow(); }, 900);
      }
      function restore() {
        const saved = store.get('sand', null);
        if (!saved || saved.v !== 1) return;
        const hh = decodeF32(saved.h, N * N);
        if (hh) h.set(hh);
        const ww = saved.w ? decodeF32(saved.w, N * N) : null;
        if (ww) {
          w.set(ww);
          for (let i = 0; i < N * N; i++) { wet[i] = Math.min(1, w[i] * 30); }
          waterRect = { x0: 0, x1: N - 1, z0: 0, z1: N - 1 };
          wetRect = { x0: 0, x1: N - 1, z0: 0, z1: N - 1 };
          waterOn = true;
        }
        items = (Array.isArray(saved.items) ? saved.items : [])
          .filter((it) => it && ((it.k === 'mold' && MOLD_BY[it.s]) || (it.k === 'deco' && DECO_BY[it.s])) && Number.isFinite(it.x) && Number.isFinite(it.z))
          .map((it) => ({ k: it.k, s: it.s, x: it.x, z: it.z, r: it.r || 0 }));
        items.forEach((it) => spawnItem(it, false));
        for (const d of Array.isArray(saved.tunnels) ? saved.tunnels : []) {
          if (d && ['ax', 'az', 'bx', 'bz', 'fa', 'fb', 'ea', 'eb'].every((k) => Number.isFinite(d[k]))) buildTunnel(d, false);
        }
        grow(sandDirty, 0, N - 1, 0, N - 1);
        grow(waterDirty, 0, N - 1, 0, N - 1);
      }

      // ---- いぬくん・ぺんぎんくん ----
      let inuMode = 'free';
      let lastSelfDig = Date.now() - 20000;
      const randIn = (r) => (Math.random() * 2 - 1) * r;
      async function inuLife() {
        await pause(2500);
        while (alive()) {
          if (inuMode !== 'free' || talking) { await pause(400); continue; }
          const r = Math.random();
          if (Date.now() - lastSelfDig > 30000 && r < 0.5) await inuSelfDig();
          else if (r < 0.8) await inuWander();
          else await inuRest();
          if (inuMode === 'free') await pause(600 + Math.random() * 1200);
        }
      }
      function farFromPlayer(x, z, d) { return !player || Math.hypot(player.x - x, player.z - z) > d; }
      async function inuWander() {
        for (let k = 0; k < 8; k++) {
          const x = randIn(3.2); const z = randIn(3.2);
          if (farFromPlayer(x, z, 1.4)) {
            inu.act('idle');
            await inu.walkTo(x, z, { speed: 1.1 });
            return;
          }
        }
        await pause(1200);
      }
      async function inuRest() {
        if (inuMode !== 'free') return;
        inu.act(Math.random() < 0.5 ? 'sit' : 'idle');
        await pause(3000);
        if (inuMode === 'free') inu.act('idle');
      }
      // じぶんで みぞを ほって かわを つくる
      async function inuSelfDig() {
        for (let k = 0; k < 14; k++) {
          const sx = randIn(3.0); const sz = randIn(3.0);
          const a = Math.random() * Math.PI * 2; const len = 1.3 + Math.random() * 0.8;
          const ex = sx + Math.cos(a) * len; const ez = sz + Math.sin(a) * len;
          if (Math.abs(ex) > 3.3 || Math.abs(ez) > 3.3) continue;
          let ok = farFromPlayer(sx, sz, 1.3) && farFromPlayer(ex, ez, 1.3);
          for (let j = 0; ok && j <= 10; j++) {
            const x = lerp(sx, ex, j / 10); const z = lerp(sz, ez, j / 10);
            if (Math.abs(sampleH(x, z)) > 0.06 || tf[cellAt(x, z)] < 1e8) ok = false;
            if (items.some((it) => Math.hypot(it.x - x, it.z - z) < 0.75)) ok = false;
          }
          if (!ok) continue;
          lastSelfDig = Date.now();
          const ux = Math.cos(a); const uz = Math.sin(a);
          const back = 0.32;
          const arrived = await inu.walkTo(sx - ux * back, sz - uz * back, { speed: 1.2 });
          if (!arrived || inuMode !== 'free') return;
          inu.act('dig');
          await inu.walkTo(ex - ux * back, ez - uz * back, {
            speed: 0.42, verb: 'dig', faceDir: Math.atan2(ux, uz),
            onStep: (c) => { if (inuMode === 'free') digTo(c.x + ux * back, c.z + uz * back, -0.12, 0.2); },
          });
          if (inuMode !== 'free') return;
          saveSoon();
          inu.act('cheer');
          if (Math.random() < 0.5) say('inu', 'かわ できた！', true);
          await pause(1400);
          if (inuMode === 'free') inu.act('idle');
          return;
        }
      }
      let penTimer = 0;
      function penCheer() {
        if (!pen) return;
        pen.act('cheer');
        clearTimeout(penTimer);
        penTimer = later(() => pen.act('sit'), 2200);
      }
      let lastReact = 0;
      function reactToBuild(p, kind) {
        if (!inu || inuMode !== 'free' || Date.now() - lastReact < 12000) return;
        if (Math.hypot(inu.x - p.x, inu.z - p.z) > 3.2) return;
        lastReact = Date.now();
        inu.stop();
        inu.face(p.x, p.z);
        inu.act('cheer');
        say('inu', kind === 'castle' ? 'わあ、おしろ！ かっこいい！' : 'わあ、すてき！', true);
        later(() => { if (inuMode === 'free') inu.act('idle'); }, 1600);
      }

      // ---- しゃかいせい：スコップ かして ----
      async function talk(opts) {
        talking++;
        cancelStroke();
        try { return await ctx.talk(opts); } finally { talking--; }
      }
      async function inuComeToPlayer() {
        inu.stop();
        const dx = inu.x - player.x; const dz = inu.z - player.z; const d = Math.hypot(dx, dz) || 1;
        const tx = clamp(player.x + (dx / d) * 0.9, -HALF + 0.2, HALF - 0.2); const tz = clamp(player.z + (dz / d) * 0.9, -HALF + 0.2, HALF - 0.2);
        await Promise.race([inu.walkTo(tx, tz, { speed: 1.8 }), pause(5000)]);
        inu.stop();
        inu.face(player.x, player.z);
        player.face(inu.x, inu.z);
      }
      async function eventScoop() {
        if (!inu || !player || lending) return;
        inuMode = 'event';
        await inuComeToPlayer();
        if (!alive()) return;
        inu.act('hold');
        const c = await talk({
          friend: 'inu', say: 'ねえねえ、スコップ かして？',
          choices: [
            { emoji: '🤲', label: 'どうぞ', good: true, reply: 'ありがとう！ きみの みぞに つなげて ほるね！' },
            { emoji: '🔁', label: 'じゅんばんこ ね', good: true, reply: 'うん！ じゅんばんこ ね。つぎ かしてね！' },
            { emoji: '🙅', label: 'だめ', good: false, hint: 'いぬくん、かなしそう…。スコップで あそびたいんだって。なんて いったら いいかな？' },
          ],
        });
        if (!alive()) return;
        if (!c) { inu.act('idle'); inuMode = 'free'; return; }
        if (c.label !== 'どうぞ') {
          inu.act('idle');
          inuMode = 'free';
          await pause(14000);
          if (!alive()) return;
          while (talking || seq) { await pause(500); if (!alive()) return; }
          inuMode = 'event';
          await inuComeToPlayer();
          if (!alive()) return;
          inu.act('hold');
          await say('inu', 'じゅんばんこ。こんどは ぼくの ばん だね。スコップ かりるね！');
          if (!alive()) return;
        }
        await lendScoop();
      }

      // こどもの みぞ（ふかく ほった ところ）を あつめる
      function trenchCells() {
        const list = [];
        let any = false;
        for (let i = 0; i < N * N; i++) if (kidDug[i]) { any = true; break; }
        for (let z = 6; z < N - 6; z += 2) {
          for (let x = 6; x < N - 6; x += 2) {
            const i = z * N + x;
            if (h[i] > -0.09 || tf[i] < 1e8 || (any && !kidDug[i])) continue;
            list.push({ x: x * CELL - HALF, z: z * CELL - HALF, h: h[i] });
          }
        }
        return list;
      }
      async function lendScoop() {
        lending = true;
        toolBtns.dig.classList.add('lent');
        if (tool === 'dig') selectTool('mound', true);
        player.hold(handTool());
        player.act('idle');
        inu.hold('Shovel');
        speak('いぬくんが スコップで ほってるよ。ほかの どうぐで あそんでね。');
        const cells = trenchCells();
        let T = cells.length ? cells.reduce((a, c) => (Math.min(HALF - Math.abs(c.x), HALF - Math.abs(c.z)) < Math.min(HALF - Math.abs(a.x), HALF - Math.abs(a.z)) ? c : a)) : null;
        const pond = !T;
        if (pond) {
          for (let k = 0; k < 20 && !T; k++) {
            const x = randIn(2.2); const z = randIn(2.2);
            if (items.every((it) => Math.hypot(it.x - x, it.z - z) > 1)) T = { x, z, h: 0 };
          }
          if (!T) T = { x: 0, z: 0, h: 0 };
        }
        // かわの はじまりは、すなばの ふちの ちかく
        let S = null; let bestD = -1;
        for (let k = 0; k < 32; k++) {
          const a = (k / 32) * Math.PI * 2;
          const r = 3.4;
          const x = clamp(Math.cos(a) * r * 1.4, -3.4, 3.4); const z = clamp(Math.sin(a) * r * 1.4, -3.4, 3.4);
          const d = Math.hypot(x - T.x, z - T.z);
          let score = d >= 1.8 && d <= 3.4 ? 10 - Math.abs(d - 2.4) : -Math.abs(d - 2.4);
          if (items.some((it) => Math.hypot(it.x - (x + T.x) / 2, it.z - (z + T.z) / 2) < 0.6)) score -= 3;
          if (score > bestD) { bestD = score; S = { x, z }; }
        }
        // みぞの なかで、はじまりに いちばん ちかい ところに つなげる
        if (!pond) T = cells.reduce((a, c) => (Math.hypot(c.x - S.x, c.z - S.z) < Math.hypot(a.x - S.x, a.z - S.z) ? c : a));
        const endDepth = pond ? -0.2 : Math.max(H_MIN + 0.02, T.h);
        const startDepth = Math.min(-0.08, endDepth + 0.07);
        const L = Math.hypot(T.x - S.x, T.z - S.z) || 1;
        const ux = (T.x - S.x) / L; const uz = (T.z - S.z) / L;
        const back = 0.32;
        await inu.walkTo(S.x - ux * back, S.z - uz * back, { speed: 1.6 });
        if (!alive()) return;
        inu.act('dig');
        await inu.walkTo(T.x - ux * back, T.z - uz * back, {
          speed: 0.5, verb: 'dig', faceDir: Math.atan2(ux, uz),
          onStep: (c) => {
            const px = c.x + ux * back; const pz = c.z + uz * back;
            const t = clamp(Math.hypot(px - S.x, pz - S.z) / L, 0, 1);
            digTo(px, pz, lerp(startDepth, endDepth, t), 0.22);
            if (Math.random() < 0.05) sound('tap');
          },
        });
        if (!alive()) return;
        digTo(T.x, T.z, endDepth, 0.24);
        if (pond) {
          for (let a = 0; a < 14; a++) {
            digTo(T.x + Math.cos(a * 0.45) * 0.35, T.z + Math.sin(a * 0.45) * 0.35, endDepth, 0.28);
            await pause(70);
            if (!alive()) return;
          }
        }
        // じょうろで おみずを ながす
        inu.hold('WateringCan');
        await inu.walkTo(S.x - ux * 0.5, S.z - uz * 0.5, { speed: 1.6 });
        if (!alive()) return;
        inu.face(T.x, T.z);
        inu.act('hold');
        const src = { at: { x: S.x, z: S.z }, inu: true };
        pours.add(src);
        say('inu', 'おみず ながすね！', true);
        const t0 = Date.now();
        while (alive() && Date.now() - t0 < 9000) {
          await pause(250);
          if (w[cellAt(T.x, T.z)] > 0.01 && Date.now() - t0 > 2500) break;
        }
        await pause(1200);
        pours.delete(src);
        if (!alive()) return;
        sound('correct');
        inu.act('cheer');
        if (pen) penCheer();
        await say('inu', pond ? 'いけが できたよ！ つながったね！' : 'つながったね！ かわに おみずが ながれてる！');
        if (!alive()) return;
        // スコップを かえす
        inu.hold('Shovel');
        await inuComeToPlayer();
        if (!alive()) return;
        inu.act('hold');
        lending = false;
        toolBtns.dig.classList.remove('lent');
        sound('flip');
        await say('inu', 'スコップ かしてくれて ありがとう！ かえすね！');
        if (!alive()) return;
        inu.hold(null);
        player.hold(handTool());
        player.act('cheer');
        later(() => { if (!stroke && !seq) player.act('idle'); }, 1200);
        inu.act('idle');
        inuMode = 'free';
        saveSoon();
      }

      async function runEvent() {
        if (busy || !ready) return;
        busy = true;
        try { await eventScoop(); } finally { busy = false; if (inu && inuMode === 'event' && alive()) { inuMode = 'free'; inu.act('idle'); } }
      }
      let playSec = 0;
      let nextAt = 40;
      const ticker = setInterval(() => {
        if (!alive() || !ready) return;
        const idle = Date.now() - lastTouch > 9000;
        if (!idle && !busy && !talking && !seq) playSec++;
        if (playSec >= nextAt && !busy && !talking && !seq && !stroke && !lending) {
          nextAt = playSec + 150;
          runEvent();
        }
      }, 1000);

      // ---- ならす（かくにん つき） ----
      let confirmOpen = false;
      function askFlatten() {
        if (talking || !alive() || confirmOpen || seq) return;
        sound('tap');
        if (busy) { speak('いまは いぬくんと あそんでる とちゅう だよ。'); return; }
        cancelStroke();
        confirmOpen = true;
        const close = () => { if (confirmOpen) { confirmOpen = false; dlg.remove(); } };
        const dlg = el('div', { class: 's3d-confirm', role: 'dialog', 'aria-label': 'ぜんぶ たいらに する？' },
          el('div', { class: 's3d-confirm-card' },
            el('div', { class: 's3d-confirm-title' }, '🧹 ぜんぶ たいらに する？'),
            el('div', { class: 's3d-confirm-row' },
              el('button', { class: 's3d-confirm-btn yes', 'aria-label': 'たいらに する', onclick: () => { close(); flatten(); } },
                el('span', {}, '🏖️'), el('span', {}, 'たいらに する')),
              el('button', { class: 's3d-confirm-btn no', 'aria-label': 'やめる', onclick: () => { sound('tap'); close(); speak('このまま あそぼう！'); } },
                el('span', {}, '↩️'), el('span', {}, 'やめる')))));
        root.append(dlg);
        speak('ぜんぶ たいらに する？');
      }
      async function flatten() {
        sound('flip');
        seq = true;
        const hadTunnel = tunnels.length > 0;
        try {
          for (const it of items.slice()) removeItem(it, true);
          for (let k = 0; k < 14; k++) {
            for (let i = 0; i < N * N; i++) { h[i] *= 0.78; w[i] *= 0.7; kidDug[i] = 0; }
            if (k === 3) for (const t of tunnels.slice()) removeTunnel(t, true);
            grow(sandDirty, 0, N - 1, 0, N - 1);
            grow(waterRect, 0, N - 1, 0, N - 1);
            grow(waterDirty, 0, N - 1, 0, N - 1);
            await pause(45);
            if (!alive()) return;
          }
          for (const t of tunnels.slice()) removeTunnel(t, false);
          flatSand();
          items = [];
          wetRect = R0();
          grow(sandDirty, 0, N - 1, 0, N - 1);
          grow(waterDirty, 0, N - 1, 0, N - 1);
          saveNow();
          speak(hadTunnel ? 'たいらに なったよ。トンネルも くずれちゃった。もういちど つくろう！' : 'たいらに なったよ。また なにを つくろうかな？');
        } finally { seq = false; }
      }

      // ---- まいフレーム ----
      let raf = 0;
      let lastT = performance.now();
      let waterAcc = 0;
      let frameNo = 0;
      const canTmp = new THREE.Vector3();
      function frame(now) {
        raf = requestAnimationFrame(frame);
        const dt = Math.min(0.1, Math.max(0.001, (now - lastT) / 1000));
        lastT = now;
        frameNo++;
        updateCamera(dt);
        if (ready) {
          applyStroke(dt);
          for (const s of pours) {
            if (!s.at) continue;
            addWater(s.at.x, s.at.z, dt * 0.3);
            // じょうろから しずく
            const who = s.inu ? inu : player;
            if (who && who.prop) who.prop.getWorldPosition(canTmp); else canTmp.set(s.at.x, SAND_Y + 1, s.at.z);
            for (let k = 0; k < 2; k++) {
              const from = new THREE.Vector3(lerp(canTmp.x, s.at.x, 0.5) + randIn(0.08), Math.max(canTmp.y, SAND_Y + 0.6) + 0.1, lerp(canTmp.z, s.at.z, 0.5) + randIn(0.08));
              const v = new THREE.Vector3((s.at.x - from.x) * 1.4 + randIn(0.2), 0.3, (s.at.z - from.z) * 1.4 + randIn(0.2));
              particle(dropMat, from, v, 1.2, 0.8 + Math.random() * 0.5);
            }
          }
          if (waterOn || !isEmpty(waterRect)) {
            waterAcc += dt;
            let n = 0;
            while (waterAcc >= 1 / 60 && n < 4) { waterStep(1 / 60); waterAcc -= 1 / 60; n++; }
            if (n === 4) waterAcc = 0;
          }
          if (frameNo % 5 === 0) dryStep(dt * 5);
          watchTunnels(dt);
          if (!isEmpty(sandDirty)) { updateSand(sandDirty); sandDirty = R0(); }
          if (!isEmpty(waterDirty)) { updateWater(waterDirty); waterDirty = R0(); }
          for (let k = tweens.length - 1; k >= 0; k--) {
            const tw = tweens[k];
            tw.t += dt;
            const p = Math.min(1, tw.t / tw.dur);
            tw.fn(p);
            if (p >= 1) { tweens.splice(k, 1); tw.r(); }
          }
          updateParticles(dt);
          for (const c of chars) updateChar(c, dt);
        }
        renderer.render(scene, camera);
      }
      raf = requestAnimationFrame(frame);

      // ---- じゅんび（glb → だめなら かわりの ぶひん） ----
      loadGlb().then((gltf) => {
        if (!alive()) return;
        assets = buildAssets(gltf);
        const frameObj = cloneNode('Frame');
        scene.add(frameObj, cloneNode('Ground'));
        if (assets.trees) {
          for (const t of assets.trees) { const o = t.clone(true); o.traverse((m) => { if (m.isMesh) m.castShadow = true; }); scene.add(o); }
        } else {
          for (const [x, z, s] of [[-7, -5.5, 1], [6.8, -6.5, 1.1]]) { const o = cloneNode('Tree'); o.position.set(x, 0, z); o.scale.setScalar(s); scene.add(o); }
        }
        measureCastle();
        restore();
        player = makeChar(KIND_NODE[ctx.player && ctx.player.kind] || 'Kid', 'player');
        player.place(0.6, HALF + 0.2, Math.PI);
        inu = makeChar('Inu', 'inu');
        inu.place(-1.2, -0.8, 0.4);
        pen = makeChar('Pen', 'pen');
        pen.place(-HALF - 0.2, -HALF - 0.2, Math.PI / 4);
        pen.act('sit');
        selectTool('dig', true);
        loading.remove();
        ready = true;
        inuLife();
        later(() => { pen.act('wave'); say('pen', 'やっほー！', true); later(() => pen.act('sit'), 2000); }, 1500);
        speak('りったい すなば だよ！ ゆびで なぞって ほったり、おやまを つくったり しよう。2ほんの ゆびで まわせるよ。');
      });

      // テスト・かくにん よう
      ctx.stage.__sunaba3d = {
        runEvent: () => runEvent(),
        setNextEvent: (sec) => { nextAt = playSec + sec; },
        state: () => ({
          ready, frames: frameNo, tool, lending, busy, seq, talking, items: items.length, tunnels: tunnels.length, tunnelPassed: tunnelFlowSaid,
          source: assets && assets.source, glbNodes: assets ? [...assets.fromGlb] : [], clips: assets ? Object.keys(assets.clips) : [],
          inuMode, cam: { yaw: cam.yawT, pitch: cam.pitchT, dist: cam.distT },
          player: player && { x: player.x, z: player.z, verb: player.shown, prop: player.propName, node: player.nodeName, mixer: !!player.mixer, proc: !!player.useProc },
          inu: inu && { x: inu.x, z: inu.z, verb: inu.shown, prop: inu.propName, mixer: !!inu.mixer, proc: !!inu.useProc },
          water: (() => { let s = 0; for (let i = 0; i < N * N; i++) s += w[i]; return s; })(),
        }),
        sampleH: (x, z) => sampleH(x, z),
        hit: (x, y) => hitSand(x, y),
        stroke: () => stroke && { tool: stroke.tool, on: stroke.on, last: stroke.last },
        water: (x, z) => w[cellAt(x, z)],
        floor: (x, z) => tf[cellAt(x, z)],
        project: (x, z, y) => { tmpV.set(x, y != null ? y : SAND_Y + sampleH(x, z), z).project(camera); const r = canvas.getBoundingClientRect(); return { x: r.left + ((tmpV.x + 1) / 2) * r.width, y: r.top + ((1 - tmpV.y) / 2) * r.height }; },
        setCam: (o) => { Object.assign(cam, o); if (o.yaw != null) cam.yawT = o.yaw; if (o.pitch != null) cam.pitchT = o.pitch; if (o.dist != null) cam.distT = o.dist; },
        partRot: (who, part) => { const c = who === 'inu' ? inu : player; const p = c && c.parts[part]; return p ? [p.rotation.x, p.rotation.y, p.rotation.z, p.quaternion.w] : null; },
        tunnelInfo: () => tunnels.map((t) => ({ def: t.def, interior: t.interior.length / 2, mouthA: { x: t.mouthA.x, z: t.mouthA.z, w: w[t.mouthA.i] }, mouthB: { x: t.mouthB.x, z: t.mouthB.z, w: w[t.mouthB.i] }, mid: w[t.mid] })),
      };

      return () => {
        clearInterval(ticker);
        cancelAnimationFrame(raf);
        ro.disconnect();
        timers.forEach((t) => clearTimeout(t));
        timers.clear();
        clearTimeout(penTimer);
        try { if (ready) saveNow(); } catch (e) { /* なにもしない */ }
        clearTimeout(saveTimer);
        for (const c of chars) { if (c.mixer) c.mixer.stopAllAction(); if (c.resolve) c.resolve(false); }
        disposables.forEach((d) => d.dispose());
        if (assets) Object.values(assets.fallbackMats).forEach((m) => m.dispose());
        renderer.dispose();
        try { renderer.forceContextLoss(); } catch (e) { /* なにもしない */ }
        delete ctx.stage.__sunaba3d;
      };
    },
  });
})();
