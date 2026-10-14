// すなば：うえから みた すなばで、ほったり もりあげたり、かたぬき・みず・かざりで じゆうに あそぶ
// しゃかいせい：いぬくん「スコップ かして？」／「いっしょに おおきい おしろ」／ぺんぎんくん「いれて」
(function () {
  'use strict';

  // ---- すなの たかさマップ（N×N マス） ----
  const N = 160;
  const H_MIN = -1.1;
  const H_MAX = 1.6;

  const SVG_SHOVEL = '<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="29" y="6" width="6" height="30" rx="3" fill="#b9793f"/><rect x="21" y="2" width="22" height="9" rx="4.5" fill="#ff6b6b"/><path d="M17 33h30v9c0 10-7 17-15 20-8-3-15-10-15-20z" fill="#4d8dff"/><path d="M22 38h20" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/></svg>';
  const SVG_CAN = '<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M20 28c0-15 20-15 20 0" fill="none" stroke="#2a9d5a" stroke-width="5"/><path d="M41 36l14-14 4 4-14 16z" fill="#3cc46b"/><rect x="51" y="13" width="11" height="9" rx="2" transform="rotate(45 56 18)" fill="#2a9d5a"/><path d="M12 28h30v25a5 5 0 0 1-5 5H17a5 5 0 0 1-5-5z" fill="#3cc46b"/><circle cx="60" cy="8" r="2.5" fill="#5ab8ff"/><circle cx="62" cy="14" r="2" fill="#5ab8ff"/></svg>';

  const TOOLS = [
    { id: 'dig', label: 'ほる', icon: SVG_SHOVEL, svg: true, say: 'スコップで ほろう。ゆびで なぞってね。' },
    { id: 'mound', label: 'もりあげる', icon: '✋', say: 'てのひらで こすると、おやまが できるよ。' },
    { id: 'bucket', label: 'バケツ', icon: '🪣', say: 'バケツで かたぬき！ すきな かたちを えらんで、タップしてね。' },
    { id: 'water', label: 'じょうろ', icon: SVG_CAN, svg: true, say: 'じょうろで おみず。ほった みぞに ながれるよ。' },
    { id: 'deco', label: 'かざり', icon: '🐚', say: 'かざりを おこう。タップした ところに おけるよ。' },
  ];
  const MOLDS = [
    { id: 'castle', emoji: '🏰', name: 'おしろ' },
    { id: 'fish', emoji: '🐟', name: 'さかな' },
    { id: 'star', emoji: '⭐', name: 'ほし' },
  ];
  const DECOS = [
    { e: '🐚', name: 'かいがら' },
    { e: '🌿', name: 'はっぱ' },
    { e: '🌸', name: 'おはな' },
    { e: '🪨', name: 'いし' },
  ];

  // ---- かたぬきの かたち（100×100 の なかに、あかるさ＝たかさ で かく） ----
  function drawMold(g, shape) {
    const gray = (v) => `rgb(${v},${v},${v})`;
    if (shape === 'castle') {
      g.fillStyle = gray(150);
      g.fillRect(18, 42, 64, 50);
      g.fillStyle = gray(205);
      g.fillRect(8, 24, 20, 68);
      g.fillRect(72, 24, 20, 68);
      g.fillRect(39, 14, 22, 36);
      // ぎざぎざ
      g.fillStyle = gray(150);
      [[8, 24], [72, 24]].forEach(([x, y]) => { g.fillRect(x + 5, y, 4, 6); g.fillRect(x + 12, y, 3, 6); });
      g.fillRect(44, 14, 4, 6);
      g.fillRect(53, 14, 4, 6);
      g.fillStyle = gray(165);
      for (let x = 30; x < 70; x += 10) if (x < 39 || x > 58) g.fillRect(x, 36, 6, 6);
      // まど と もん
      g.fillStyle = gray(95);
      g.fillRect(15, 44, 6, 9);
      g.fillRect(79, 44, 6, 9);
      g.fillRect(47, 26, 6, 9);
      g.beginPath();
      g.moveTo(41, 92); g.lineTo(41, 76); g.arc(50, 76, 9, Math.PI, 0); g.lineTo(59, 92); g.closePath();
      g.fill();
    } else if (shape === 'fish') {
      g.fillStyle = gray(150);
      g.beginPath(); g.moveTo(66, 50); g.lineTo(96, 26); g.lineTo(90, 50); g.lineTo(96, 74); g.closePath(); g.fill();
      g.fillStyle = gray(180);
      g.beginPath(); g.ellipse(42, 50, 34, 23, 0, 0, Math.PI * 2); g.fill();
      g.fillStyle = gray(150);
      g.beginPath(); g.moveTo(36, 28); g.lineTo(52, 16); g.lineTo(58, 30); g.closePath(); g.fill();
      g.strokeStyle = gray(125);
      g.lineWidth = 3;
      g.beginPath(); g.arc(30, 50, 14, -1.1, 1.1); g.stroke();
      for (let i = 0; i < 3; i++) { g.beginPath(); g.arc(50 + i * 9, 50, 7, -1.2, 1.2); g.stroke(); }
      g.fillStyle = gray(85);
      g.beginPath(); g.arc(20, 45, 4, 0, Math.PI * 2); g.fill();
    } else {
      const star = (R, r, v) => {
        g.fillStyle = gray(v);
        g.beginPath();
        for (let i = 0; i < 10; i++) {
          const a = -Math.PI / 2 + (i * Math.PI) / 5;
          const rr = i % 2 ? r : R;
          g.lineTo(50 + Math.cos(a) * rr, 52 + Math.sin(a) * rr);
        }
        g.closePath();
        g.fill();
      };
      star(48, 20, 160);
      star(28, 12, 205);
    }
  }

  const maskCache = {};
  function moldMask(shape, M) {
    const key = shape + M;
    if (maskCache[key]) return maskCache[key];
    const c = document.createElement('canvas');
    c.width = c.height = M;
    const g = c.getContext('2d');
    g.fillStyle = '#000';
    g.fillRect(0, 0, M, M);
    g.scale(M / 100, M / 100);
    drawMold(g, shape);
    const d = g.getImageData(0, 0, M, M).data;
    const out = new Float32Array(M * M);
    for (let i = 0; i < M * M; i++) out[i] = d[i * 4] / 255;
    maskCache[key] = out;
    return out;
  }

  Core.registerSpot({
    id: 'sunaba',
    start(ctx) {
      const { el, speak, sound, store } = ctx;
      const alive = () => ctx.isActive();
      const timers = new Set();
      const later = (fn, ms) => { const t = setTimeout(() => { timers.delete(t); if (alive()) fn(); }, ms); timers.add(t); return t; };
      const pause = (ms) => new Promise((r) => later(r, ms));

      // ---- データ ----
      const h = new Float32Array(N * N);
      const w = new Float32Array(N * N);
      const wet = new Float32Array(N * N);
      const dw = new Float32Array(N * N);
      const grain = new Float32Array(N * N);
      for (let i = 0; i < N * N; i++) grain[i] = 0.965 + Math.random() * 0.07;
      let items = [];
      let castlesBuilt = 0;

      function flatSand() {
        // ほんの すこし でこぼこ した、ふつうの すなば
        const p = [Math.random() * 6, Math.random() * 6, Math.random() * 6, Math.random() * 6];
        for (let y = 0; y < N; y++) {
          for (let x = 0; x < N; x++) {
            const i = y * N + x;
            h[i] = 0.035 * Math.sin(x * 0.09 + p[0]) * Math.sin(y * 0.07 + p[1]) + 0.02 * Math.sin((x + y) * 0.21 + p[2]) + 0.015 * Math.sin((x - y) * 0.17 + p[3]);
            w[i] = 0;
            wet[i] = 0;
          }
        }
      }
      flatSand();

      // ---- がめん ----
      const canvas = el('canvas', { class: 'sunaba-canvas' });
      const dctx = canvas.getContext('2d');
      const off = document.createElement('canvas');
      off.width = off.height = N;
      const octx = off.getContext('2d');
      const img = octx.createImageData(N, N);
      const grainTex = document.createElement('canvas');
      grainTex.width = grainTex.height = 96;
      {
        const g = grainTex.getContext('2d');
        const gd = g.createImageData(96, 96);
        for (let i = 0; i < 96 * 96; i++) {
          const v = Math.random() < 0.5 ? 0 : 255;
          gd.data[i * 4] = gd.data[i * 4 + 1] = gd.data[i * 4 + 2] = v;
          gd.data[i * 4 + 3] = Math.random() * 120;
        }
        g.putImageData(gd, 0, 0);
      }
      const grainPattern = dctx.createPattern(grainTex, 'repeat');

      const itemLayer = el('div', { class: 'sunaba-items', 'aria-hidden': 'true' });
      const fxLayer = el('div', { class: 'sunaba-fx', 'aria-hidden': 'true' });
      const box = el('div', { class: 'sunaba-box' }, canvas, el('div', { class: 'sunaba-rim', 'aria-hidden': 'true' }), itemLayer, fxLayer);
      const boxCell = el('div', { class: 'sunaba-boxcell' }, box);

      // となりの おともだち
      function makePal(id) {
        const f = ctx.friend(id);
        const bubble = el('div', { class: 'sunaba-bubble' });
        // ふだんの ポーズ：いぬくんは すなばの ふちに すわる、ぺんぎんくんは たって あそぶ
        const rest = id === 'inu' ? 'sit' : 'stand';
        const body = ctx.character(f.id, { pose: rest });
        const face = el('div', { class: 'sunaba-pal-face', 'aria-hidden': 'true' }, body);
        const node = el('div', { class: `sunaba-pal sunaba-pal-${id} is-${rest}` }, bubble, face, el('div', { class: 'sunaba-pal-pile', 'aria-hidden': 'true' }));
        return { id, node, bubble, face, body, rest, timer: 0, poseTimer: 0 };
      }
      const pals = { inu: makePal('inu'), pen: makePal('pen') };
      pals.pen.node.classList.add('away');

      // ポーズを かえる（ms を わたすと、そのあと ふだんの ポーズに もどる）
      function pose(id, p, mood = 'normal', ms = 0) {
        const pal = pals[id];
        if (!pal) return;
        clearTimeout(pal.poseTimer);
        pal.body.setPose(p).setMood(mood);
        pal.node.classList.toggle('is-sit', p === 'sit');
        pal.node.classList.toggle('is-stand', p !== 'sit');
        if (ms) {
          pal.poseTimer = setTimeout(() => { if (alive()) pose(id, pal.rest); }, ms);
          timers.add(pal.poseTimer);
        }
      }
      const restPose = (id) => pose(id, pals[id].rest);

      const showBtn = el('button', { class: 'sunaba-side-btn sunaba-show', 'aria-label': 'みせる', onclick: () => showOff() },
        el('span', { class: 'sunaba-side-icon' }, '👀'), el('span', { class: 'sunaba-side-label' }, 'みせる'));
      const flatBtn = el('button', { class: 'sunaba-side-btn sunaba-flat', 'aria-label': 'ならす', onclick: () => askFlatten() },
        el('span', { class: 'sunaba-side-icon' }, '🧹'), el('span', { class: 'sunaba-side-label' }, 'ならす'));
      const side = el('div', { class: 'sunaba-side' },
        el('div', { class: 'sunaba-pals' }, pals.inu.node, pals.pen.node),
        el('div', { class: 'sunaba-side-btns' }, showBtn, flatBtn));

      // どうぐ
      let tool = 'dig';
      let mold = 'castle';
      let deco = DECOS[0].e;
      let lending = false;
      const toolBtns = {};
      const toolBar = el('div', { class: 'sunaba-tools', role: 'toolbar' },
        TOOLS.map((t) => {
          const icon = el('span', { class: 'sunaba-tool-icon' });
          if (t.svg) icon.innerHTML = t.icon; else icon.textContent = t.icon;
          const b = el('button', { class: 'sunaba-tool', 'aria-label': t.label, 'data-tool': t.id, onclick: () => selectTool(t.id) },
            icon, el('span', { class: 'sunaba-tool-label' }, t.label), el('span', { class: 'sunaba-tool-badge', 'aria-hidden': 'true' }, ctx.character('inu', { pose: 'hold' })));
          toolBtns[t.id] = b;
          return b;
        }));
      const subBar = el('div', { class: 'sunaba-sub' });
      const root = el('div', { class: 'sunaba-root' }, boxCell, side, el('div', { class: 'sunaba-toolwrap' }, subBar, toolBar));
      ctx.stage.append(root);
      ctx.stage.__sunaba = { runEvent: (k) => runEvent(k), state: () => ({ tool, lending, items: items.length, project: !!project, penJoined }) };

      function renderSub() {
        subBar.replaceChildren();
        subBar.classList.toggle('open', tool === 'bucket' || tool === 'deco');
        if (tool === 'bucket') {
          MOLDS.forEach((m) => subBar.append(el('button', {
            class: 'sunaba-subbtn' + (mold === m.id ? ' on' : ''), 'aria-label': m.name,
            onclick: () => { mold = m.id; sound('tap'); speak(m.name); renderSub(); },
          }, m.emoji)));
        } else if (tool === 'deco') {
          DECOS.forEach((d) => subBar.append(el('button', {
            class: 'sunaba-subbtn' + (deco === d.e ? ' on' : ''), 'aria-label': d.name,
            onclick: () => { deco = d.e; sound('tap'); speak(d.name); renderSub(); },
          }, d.e)));
        }
      }

      function selectTool(id, quiet) {
        if (id === 'dig' && lending) {
          sound('tap');
          say('inu', 'いま スコップ つかわせて もらってるよ。ありがとう！');
          helperBody.setPose('wave');
          later(() => { if (helper.isConnected) helperBody.setPose('walk'); }, 1600);
          return;
        }
        tool = id;
        Object.entries(toolBtns).forEach(([k, b]) => b.classList.toggle('on', k === id));
        renderSub();
        if (!quiet) {
          sound('tap');
          speak(TOOLS.find((t) => t.id === id).say);
        }
      }
      selectTool('dig', true);

      // ふきだし＋よみあげ
      function say(id, text) {
        const p = pals[id];
        if (!p) return Promise.resolve();
        p.bubble.textContent = text;
        p.node.classList.add('talking');
        clearTimeout(p.timer);
        p.timer = setTimeout(() => p.node.classList.remove('talking'), 3800);
        timers.add(p.timer);
        return speak(text);
      }

      // ---- キャンバスの おおきさ ----
      function fitCanvas() {
        const r = canvas.getBoundingClientRect();
        const dpr = Math.min(2, window.devicePixelRatio || 1);
        const cw = Math.max(1, Math.round(r.width * dpr));
        const ch = Math.max(1, Math.round(r.height * dpr));
        if (canvas.width !== cw || canvas.height !== ch) {
          canvas.width = cw;
          canvas.height = ch;
          dirty = true;
        }
      }
      const ro = new ResizeObserver(fitCanvas);
      ro.observe(canvas);

      // ---- かく ----
      let dirty = true;
      const clampH = (v) => (v < H_MIN ? H_MIN : v > H_MAX ? H_MAX : v);
      function render() {
        const d = img.data;
        for (let y = 0; y < N; y++) {
          const ym = y > 0 ? y - 1 : y;
          const yp = y < N - 1 ? y + 1 : y;
          for (let x = 0; x < N; x++) {
            const i = y * N + x;
            const xm = x > 0 ? x - 1 : x;
            const xp = x < N - 1 ? x + 1 : x;
            const hv = h[i];
            // ひだりうえ から ひかり
            const gx = h[y * N + xm] - h[y * N + xp];
            const gy = h[ym * N + x] - h[yp * N + x];
            let s = 1 - (gx * 0.9 + gy * 1.25) * 1.5;
            s = s < 0.5 ? 0.5 : s > 1.45 ? 1.45 : s;
            let r; let g; let b;
            if (hv < 0) {
              const t = Math.min(1, -hv);
              r = 238 - 62 * t; g = 207 - 82 * t; b = 146 - 70 * t;
            } else {
              const t = Math.min(1, hv / 1.6) * 0.6;
              r = 238 + 12 * t; g = 207 + 21 * t; b = 146 + 30 * t;
            }
            const wt = wet[i];
            if (wt > 0) { r -= 52 * wt; g -= 50 * wt; b -= 36 * wt; }
            const gr = grain[i] * s;
            r *= gr; g *= gr; b *= gr;
            const wv = w[i];
            if (wv > 0.006) {
              const lv = wv + hv;
              const lx = (w[y * N + xm] + h[y * N + xm]) - (w[y * N + xp] + h[y * N + xp]);
              const ly = (w[ym * N + x] + h[ym * N + x]) - (w[yp * N + x] + h[yp * N + x]);
              const ws = 1 - (lx + ly) * 3;
              const a = Math.min(0.82, 0.3 + wv * 2.2);
              let wr = 78 * ws; let wg = 160 * ws; let wb = 228 * ws;
              const spark = ((x * 7 + y * 13 + (frameNo >> 3)) % 47 === 0) && lv > -2 ? 70 : 0;
              wr += spark; wg += spark; wb += spark;
              r = r * (1 - a) + wr * a;
              g = g * (1 - a) + wg * a;
              b = b * (1 - a) + wb * a;
            }
            const j = i * 4;
            d[j] = r; d[j + 1] = g; d[j + 2] = b; d[j + 3] = 255;
          }
        }
        octx.putImageData(img, 0, 0);
        dctx.imageSmoothingEnabled = true;
        dctx.imageSmoothingQuality = 'high';
        dctx.globalAlpha = 1;
        dctx.drawImage(off, 0, 0, canvas.width, canvas.height);
        if (grainPattern) {
          dctx.globalAlpha = 0.09;
          dctx.fillStyle = grainPattern;
          dctx.fillRect(0, 0, canvas.width, canvas.height);
          dctx.globalAlpha = 1;
        }
      }

      // ---- みず ----
      let waterOn = false;
      const pours = new Map(); // pointerId -> {gx, gy}
      let dogPour = null;
      function addWater(gx, gy, amt) {
        const R = 4;
        for (let y = Math.max(0, Math.floor(gy - R)); y <= Math.min(N - 1, Math.ceil(gy + R)); y++) {
          for (let x = Math.max(0, Math.floor(gx - R)); x <= Math.min(N - 1, Math.ceil(gx + R)); x++) {
            const dd = Math.hypot(x - gx, y - gy);
            if (dd < R) w[y * N + x] += amt * (1 - dd / R);
          }
        }
        waterOn = true;
      }
      function simulate() {
        for (const p of pours.values()) addWater(p.gx, p.gy, 0.22);
        if (dogPour) addWater(dogPour.gx, dogPour.gy, 0.22);
        dw.fill(0);
        let total = 0;
        let anyWet = false;
        for (let y = 0; y < N; y++) {
          for (let x = 0; x < N; x++) {
            const i = y * N + x;
            const wi = w[i];
            if (wi <= 0.0004) continue;
            const L = h[i] + wi;
            let d1 = 0; let d2 = 0; let d3 = 0; let d4 = 0;
            if (x < N - 1) d1 = Math.max(0, L - h[i + 1] - w[i + 1]);
            if (x > 0) d2 = Math.max(0, L - h[i - 1] - w[i - 1]);
            if (y < N - 1) d3 = Math.max(0, L - h[i + N] - w[i + N]);
            if (y > 0) d4 = Math.max(0, L - h[i - N] - w[i - N]);
            const sum = d1 + d2 + d3 + d4;
            if (sum <= 0) continue;
            const move = Math.min(wi, sum * 0.5) * 0.5;
            const k = move / sum;
            if (d1) dw[i + 1] += d1 * k;
            if (d2) dw[i - 1] += d2 * k;
            if (d3) dw[i + N] += d3 * k;
            if (d4) dw[i - N] += d4 * k;
            dw[i] -= move;
          }
        }
        for (let i = 0; i < N * N; i++) {
          let v = w[i] + dw[i];
          if (v > 0) {
            // たいらな ところでは すなに しみこむ。ほった ところには たまる
            v -= h[i] > -0.12 ? 0.0028 : 0.00008;
            if (v < 0) v = 0;
            const t = v * 9;
            if (t > wet[i]) wet[i] = t > 1 ? 1 : t;
          }
          w[i] = v;
          total += v;
          if (wet[i] > 0) {
            if (v < 0.01) wet[i] = Math.max(0, wet[i] - 0.0012);
            anyWet = true;
          }
        }
        waterOn = total > 0.02 || pours.size > 0 || !!dogPour || anyWet;
        if (!waterOn && total > 0) w.fill(0);
        dirty = true;
      }

      // ---- ほる・もりあげる ----
      function dig(gx, gy, power = 1) {
        const r = 5.5;
        const R = r * 1.6;
        for (let y = Math.max(0, Math.floor(gy - R)); y <= Math.min(N - 1, Math.ceil(gy + R)); y++) {
          for (let x = Math.max(0, Math.floor(gx - R)); x <= Math.min(N - 1, Math.ceil(gx + R)); x++) {
            const dd = Math.hypot(x - gx, y - gy);
            const i = y * N + x;
            if (dd < r) {
              const f = 1 - (dd / r) * (dd / r);
              h[i] = Math.max(-1, h[i] - 0.075 * f * power);
            } else if (dd < R) {
              // ほった すなが まわりに すこし もりあがる
              h[i] = Math.min(H_MAX, h[i] + 0.011 * (1 - (dd - r) / (R - r)) * power);
            }
          }
        }
        dirty = true;
      }
      function mound(gx, gy) {
        const r = 7.5;
        const x0 = Math.max(1, Math.floor(gx - r)); const x1 = Math.min(N - 2, Math.ceil(gx + r));
        const y0 = Math.max(1, Math.floor(gy - r)); const y1 = Math.min(N - 2, Math.ceil(gy + r));
        for (let y = y0; y <= y1; y++) {
          for (let x = x0; x <= x1; x++) {
            const dd = Math.hypot(x - gx, y - gy);
            if (dd >= r) continue;
            const i = y * N + x;
            const f = 1 - (dd / r) * (dd / r);
            h[i] = Math.min(H_MAX, h[i] + 0.042 * f);
            // ぺたぺた ならして まるく
            const avg = (h[i - 1] + h[i + 1] + h[i - N] + h[i + N]) / 4;
            h[i] = h[i] * 0.88 + avg * 0.12;
            if (w[i] > 0) w[i] *= 0.6;
          }
        }
        dirty = true;
      }

      function stamp(shape, gx, gy, M, base = 0, scale = 1.35) {
        const mask = moldMask(shape, M);
        const ox = Math.round(gx - M / 2);
        const oy = Math.round(gy - M / 2);
        for (let my = 0; my < M; my++) {
          const y = oy + my;
          if (y < 0 || y >= N) continue;
          for (let mx = 0; mx < M; mx++) {
            const x = ox + mx;
            if (x < 0 || x >= N) continue;
            const v = mask[my * M + mx];
            if (v < 0.03) continue;
            const i = y * N + x;
            const t = base + v * scale;
            h[i] = Math.min(H_MAX, Math.max(h[i] * (1 - Math.min(1, v * 3)) + t * Math.min(1, v * 3), h[i]));
            w[i] = 0;
          }
        }
        dirty = true;
      }

      // ---- おいた もの ----
      function itemNode(it) {
        const n = el('div', { class: `sunaba-item sunaba-item-${it.k}`, style: { left: it.x * 100 + '%', top: it.y * 100 + '%' } }, it.e);
        return n;
      }
      function addItem(it, pop = true) {
        items.push(it);
        const n = itemNode(it);
        if (pop) n.classList.add('pop');
        itemLayer.append(n);
      }
      function renderItems() {
        itemLayer.replaceChildren(...items.map(itemNode));
      }

      // ---- ほぞん ----
      let saveTimer = 0;
      function encodeMap() {
        const c = document.createElement('canvas');
        c.width = c.height = N;
        const g = c.getContext('2d');
        const im = g.createImageData(N, N);
        for (let i = 0; i < N * N; i++) {
          const v = Math.round(((clampH(h[i]) - H_MIN) / (H_MAX - H_MIN)) * 65535);
          const j = i * 4;
          im.data[j] = v >> 8;
          im.data[j + 1] = v & 255;
          im.data[j + 2] = Math.round(Math.min(1, w[i]) * 255);
          im.data[j + 3] = 255;
        }
        g.putImageData(im, 0, 0);
        return c.toDataURL('image/png');
      }
      function saveNow() {
        clearTimeout(saveTimer);
        try {
          store.set('sand', { v: 1, map: encodeMap(), items, castles: castlesBuilt });
        } catch (e) { /* ほぞん できない ときは あきらめる */ }
      }
      function saveSoon() {
        clearTimeout(saveTimer);
        saveTimer = setTimeout(() => { if (alive()) saveNow(); }, 900);
      }
      function restore() {
        const saved = store.get('sand', null);
        if (!saved || !saved.map) return;
        items = Array.isArray(saved.items) ? saved.items.filter((it) => it && typeof it.e === 'string') : [];
        castlesBuilt = saved.castles || 0;
        renderItems();
        const im = new Image();
        im.onload = () => {
          if (!alive()) return;
          const c = document.createElement('canvas');
          c.width = c.height = N;
          const g = c.getContext('2d');
          g.drawImage(im, 0, 0);
          const d = g.getImageData(0, 0, N, N).data;
          for (let i = 0; i < N * N; i++) {
            const j = i * 4;
            h[i] = H_MIN + (((d[j] << 8) | d[j + 1]) / 65535) * (H_MAX - H_MIN);
            w[i] = d[j + 2] / 255;
            wet[i] = Math.min(1, w[i] * 9);
          }
          waterOn = true;
          dirty = true;
        };
        im.src = saved.map;
      }
      restore();

      // ---- まいフレーム ----
      let raf = 0;
      let frameNo = 0;
      function frame() {
        raf = requestAnimationFrame(frame);
        frameNo++;
        if (waterOn && frameNo % 2 === 0) simulate();
        if (dirty) { dirty = false; render(); }
      }
      raf = requestAnimationFrame(frame);

      // ---- ゆびの そうさ ----
      let lastTouch = 0;
      const strokes = new Map();
      const toGrid = (e) => {
        const r = canvas.getBoundingClientRect();
        const nx = (e.clientX - r.left) / r.width;
        const ny = (e.clientY - r.top) / r.height;
        return { nx, ny, gx: nx * N, gy: ny * N };
      };
      function burst(nx, ny, emoji, cls) {
        const n = el('div', { class: `sunaba-burst ${cls || ''}`, style: { left: nx * 100 + '%', top: ny * 100 + '%' } }, emoji);
        fxLayer.append(n);
        setTimeout(() => n.remove(), 900);
      }
      const canIn = el('div', { class: 'sunaba-can', 'aria-hidden': 'true' });
      canIn.innerHTML = SVG_CAN;

      function applyAt(p) {
        if (tool === 'dig') dig(p.gx, p.gy);
        else if (tool === 'mound') {
          mound(p.gx, p.gy);
          rubProject(p);
        }
      }

      box.addEventListener('pointerdown', (e) => {
        if (!alive()) return;
        e.preventDefault();
        try { box.setPointerCapture(e.pointerId); } catch (err) { /* なにもしない */ }
        lastTouch = Date.now();
        const p = toGrid(e);
        if (p.nx < 0 || p.nx > 1 || p.ny < 0 || p.ny > 1) return;
        if (tool === 'bucket') {
          stamp(mold, p.gx, p.gy, 36);
          burst(p.nx, p.ny, '🪣', 'flip');
          sound('flip');
          saveSoon();
          return;
        }
        if (tool === 'deco') {
          addItem({ e: deco, x: p.nx, y: p.ny, k: 'deco' });
          sound('tap');
          saveSoon();
          return;
        }
        if (tool === 'water') {
          pours.set(e.pointerId, p);
          waterOn = true;
          if (!canIn.isConnected) fxLayer.append(canIn);
          canIn.style.left = p.nx * 100 + '%';
          canIn.style.top = p.ny * 100 + '%';
          sound('flip');
          return;
        }
        strokes.set(e.pointerId, p);
        applyAt(p);
        if (Math.random() < 0.5) sound('tap');
      });
      box.addEventListener('pointermove', (e) => {
        if (!alive()) return;
        const p = toGrid(e);
        if (pours.has(e.pointerId)) {
          pours.set(e.pointerId, p);
          canIn.style.left = p.nx * 100 + '%';
          canIn.style.top = p.ny * 100 + '%';
          lastTouch = Date.now();
          return;
        }
        const last = strokes.get(e.pointerId);
        if (!last) return;
        lastTouch = Date.now();
        const dist = Math.hypot(p.gx - last.gx, p.gy - last.gy);
        const steps = Math.max(1, Math.ceil(dist / 1.3));
        for (let s = 1; s <= steps; s++) {
          const t = s / steps;
          applyAt({ gx: last.gx + (p.gx - last.gx) * t, gy: last.gy + (p.gy - last.gy) * t, seg: dist / steps });
        }
        strokes.set(e.pointerId, p);
      });
      const endPointer = (e) => {
        if (strokes.delete(e.pointerId) || pours.delete(e.pointerId)) saveSoon();
        if (!pours.size) canIn.remove();
      };
      box.addEventListener('pointerup', endPointer);
      box.addEventListener('pointercancel', endPointer);
      box.addEventListener('lostpointercapture', endPointer);

      // ---- おともだちとの できごと ----
      let busy = false;       // できごとの とちゅう
      let talking = 0;        // かいわ・かくにん が ひらいている
      let penJoined = false;
      let penDecos = 0;
      let project = null;
      async function talk(opts) {
        talking++;
        strokes.clear();
        pours.clear();
        canIn.remove();
        try { return await ctx.talk(opts); } finally { talking--; }
      }

      // (1) スコップ かして
      async function eventScoop() {
        // てを まえに だして「かして？」
        pose('inu', 'hold');
        const c = await talk({
          friend: 'inu', say: 'ねえねえ、スコップ かして？',
          choices: [
            { emoji: '🤲', label: 'どうぞ', good: true, reply: 'ありがとう！ となりから かわを ほって つなげるね！' },
            { emoji: '🔁', label: 'じゅんばんこ ね', good: true, reply: 'うん！ じゅんばんこ ね。つぎ かしてね！' },
            { emoji: '🙅', label: 'だめ', good: false, hint: 'いぬくん、かなしそう…。スコップで あそびたいんだって。なんて いったら いいかな？' },
          ],
        });
        if (!c || !alive()) return;
        if (c.label !== 'どうぞ') {
          restPose('inu');
          await pause(14000);
          if (!alive()) return;
          pose('inu', 'hold');
          await say('inu', 'じゅんばんこ。こんどは ぼくの ばん だね。スコップ かりるね！');
          if (!alive()) return;
        }
        await lendScoop();
      }

      // スコップを もって すなばの なかを あるく いぬくん
      const helperBody = ctx.character('inu', { pose: 'walk', face: 'left' });
      const helper = el('div', { class: 'sunaba-helper', 'aria-hidden': 'true' }, helperBody);
      helper.append(el('span', { class: 'sunaba-helper-tool' }));
      helper.lastChild.innerHTML = SVG_SHOVEL;

      async function lendScoop() {
        lending = true;
        toolBtns.dig.classList.add('lent');
        if (tool === 'dig') selectTool('mound', true);
        pals.inu.node.classList.add('away');
        // こどもが ほった ところ（いちばん みぎ）を さがす
        let tx = -1; let ty = -1;
        for (let x = N - 1; x >= 0 && tx < 0; x--) {
          for (let y = 4; y < N - 4; y++) if (h[y * N + x] < -0.3) { tx = x; ty = y; break; }
        }
        const pond = tx < 0;
        if (pond) { tx = N * 0.45; ty = N * 0.5; }
        const sx = N - 2;
        const sy = Math.max(12, Math.min(N - 12, ty + (Math.random() * 50 - 25)));
        const cx = (sx + tx) / 2;
        const cy = (sy + ty) / 2 + (Math.random() < 0.5 ? -18 : 18);
        helper.style.left = (sx / N) * 100 + '%';
        helper.style.top = (sy / N) * 100 + '%';
        helperBody.setPose('walk').setMood('normal').face(tx < sx ? 'left' : 'right');
        helper.classList.remove('pouring');
        fxLayer.append(helper);
        speak('いぬくんが となりから ほってるよ。ほかの どうぐで あそんでね。');
        const steps = 90;
        for (let k = 0; k <= steps; k++) {
          if (!alive()) return;
          const t = k / steps;
          const x = (1 - t) * (1 - t) * sx + 2 * (1 - t) * t * cx + t * t * tx;
          const y = (1 - t) * (1 - t) * sy + 2 * (1 - t) * t * cy + t * t * ty;
          const dx = 2 * (1 - t) * (cx - sx) + 2 * t * (tx - cx);
          if (Math.abs(dx) > 0.5) helperBody.face(dx < 0 ? 'left' : 'right');
          dig(x, y, 1.6);
          helper.style.left = (x / N) * 100 + '%';
          helper.style.top = (y / N) * 100 + '%';
          if (k % 15 === 0) sound('tap');
          await pause(70);
        }
        if (pond) {
          for (let a = 0; a < 12; a++) {
            dig(tx + Math.cos(a) * 6, ty + Math.sin(a) * 6, 1.4);
            await pause(60);
            if (!alive()) return;
          }
        }
        dogPour = { gx: sx, gy: sy };
        waterOn = true;
        helper.style.left = (sx / N) * 100 + '%';
        helper.style.top = (sy / N) * 100 + '%';
        // とまって、おみずを りょうてで ながす
        helperBody.setPose('hold').setMood('happy').face('left');
        helper.classList.add('pouring');
        sound('correct');
        await say('inu', pond ? 'いけが できたよ！ おみず いれるね！' : 'かわが つながったよ！ おみず ながすね！');
        await pause(6000);
        if (!alive()) return;
        dogPour = null;
        helper.remove();
        pals.inu.node.classList.remove('away');
        // スコップを りょうてで かえす
        pose('inu', 'hold', 'happy', 4200);
        lending = false;
        toolBtns.dig.classList.remove('lent');
        sound('flip');
        saveSoon();
        await say('inu', 'スコップ かしてくれて ありがとう！ かえすね！');
      }

      // (2) いっしょに おおきい おしろ
      async function eventCastle() {
        pose('inu', 'wave');
        const c = await talk({
          friend: 'inu', say: 'いっしょに おおきい おしろ つくろう！',
          choices: [
            { emoji: '🙆', label: 'いいよ', good: true, reply: 'やったー！ まるの なかを てのひらで こすってね！' },
            { emoji: '🙅', label: 'ひとりで あそぶ', good: false, hint: 'いぬくん、いっしょに あそびたいんだって。なんて いったら いいかな？' },
          ],
        });
        if (!c || !alive()) { if (alive()) restPose('inu'); return; }
        // いちばん あいている ばしょ
        const spots = ctx.shuffle([[0.5, 0.48], [0.32, 0.35], [0.68, 0.36], [0.33, 0.66], [0.67, 0.65]]);
        let best = spots[0]; let bestScore = Infinity;
        for (const s of spots) {
          const score = items.reduce((a, it) => a + (Math.hypot(it.x - s[0], it.y - s[1]) < 0.22 ? 1 : 0), 0);
          if (score < bestScore) { bestScore = score; best = s; }
        }
        const zone = el('div', { class: 'sunaba-zone', style: { left: best[0] * 100 + '%', top: best[1] * 100 + '%' } },
          el('div', { class: 'sunaba-zone-hint' }, '✋'));
        fxLayer.append(zone);
        project = { gx: best[0] * N, gy: best[1] * N, r: 24, p: 0, step: 0, zone, done: null };
        selectTool('mound', true);
        startWork();
        speak('まるの なかを、てのひらで ごしごし こすってね。');
        await new Promise((r) => { project.done = r; });
      }

      // おしろを つくる あいだ：すなを もって（hold）→ もりあげる（cheer）を くりかえす
      let workTimer = 0;
      function startWork() {
        stopWork();
        pals.inu.node.classList.add('working');
        let k = 0;
        const step = () => {
          if (!alive() || !project || project.finished) return;
          pose('inu', k % 2 ? 'cheer' : 'hold');
          k++;
          workTimer = later(step, 650);
        };
        step();
      }
      function stopWork() {
        clearTimeout(workTimer);
        timers.delete(workTimer);
        pals.inu.node.classList.remove('working');
      }

      function raiseDome(amount) {
        const { gx, gy, r } = project;
        const top = 0.15 + 0.6 * project.p;
        for (let y = Math.max(0, Math.floor(gy - r)); y <= Math.min(N - 1, Math.ceil(gy + r)); y++) {
          for (let x = Math.max(0, Math.floor(gx - r)); x <= Math.min(N - 1, Math.ceil(gx + r)); x++) {
            const dd = Math.hypot(x - gx, y - gy) / r;
            if (dd >= 1) continue;
            const target = top * (1 - dd * dd);
            const i = y * N + x;
            if (h[i] < target) h[i] += (target - h[i]) * amount;
          }
        }
        dirty = true;
      }

      function rubProject(p) {
        if (!project || project.finished) return;
        if (Math.hypot(p.gx - project.gx, p.gy - project.gy) > project.r) return;
        project.p = Math.min(1, project.p + (p.seg || 0.5) / 420);
        updateProject();
      }

      function updateProject() {
        if (!project || project.finished) return;
        raiseDome(0.08);
        project.zone.style.setProperty('--p', String(project.p));
        const step = Math.floor(project.p * 4);
        if (step > project.step && step < 4) {
          project.step = step;
          sound('flip');
          pose('inu', 'cheer');
          say('inu', ['', 'いいかんじ！', 'どんどん おおきく なってきた！', 'もう すこし！'][step]);
        }
        if (project.p >= 1) finishProject();
      }

      async function finishProject() {
        const pr = project;
        pr.finished = true;
        raiseDome(1);
        stamp('castle', pr.gx, pr.gy - 2, 64, 0.35, 1.1);
        pr.zone.classList.add('done');
        const S = 64 / N;
        const fx = (u) => pr.gx / N + (u / 100 - 0.5) * S;
        const fy = (v) => (pr.gy - 2) / N + (v / 100 - 0.5) * S;
        [[18, 22], [82, 22], [50, 12]].forEach(([u, v]) => addItem({ e: '🚩', x: fx(u), y: fy(v) - 0.03, k: 'flag' }));
        castlesBuilt++;
        stopWork();
        pose('inu', 'cheer', 'happy', 6000);
        sound('fanfare');
        for (let i = 0; i < 8; i++) burst(pr.gx / N + (Math.random() - 0.5) * 0.3, pr.gy / N + (Math.random() - 0.5) * 0.3, '✨', 'spark');
        saveSoon();
        await say('inu', 'できたー！ ふたりで つくった おおきい おしろ！ いっしょに つくると たのしいね！');
        if (!alive()) return;
        ctx.addHeart('inu', 1);
        pr.zone.remove();
        project = null;
        if (pr.done) pr.done();
      }

      // (3) ぺんぎんくん「いれて」
      async function eventPen() {
        // あるいて ちかづいて きて、てを ふる
        pals.pen.node.classList.remove('away');
        pals.pen.node.classList.add('visiting');
        pose('pen', 'walk');
        pals.pen.body.face('left');
        await pause(1500);
        if (!alive()) return;
        pals.pen.body.face('right');
        pose('pen', 'wave');
        say('pen', 'おーい！');
        await pause(1300);
        if (!alive()) return;
        const c = await talk({
          friend: 'pen', say: 'たのしそう！ ぼくも いれて！',
          choices: [
            { emoji: '🙆', label: 'いいよ', good: true, reply: 'わーい！ ありがとう！ かいがら もってきたよ！' },
            { emoji: '🙅', label: 'だめ', good: false, hint: 'ぺんぎんくん、さみしそう…。いっしょに あそびたいんだって。なんて いったら いいかな？' },
          ],
        });
        if (!c || !alive()) return;
        pals.pen.node.classList.remove('visiting');
        penJoined = true;
        penPlace('🐚');
        pose('pen', 'cheer', 'happy', 3500);
        say('pen', 'さんにんで あそぶと たのしいね！');
      }
      function penPlace(e) {
        const x = 0.12 + Math.random() * 0.76;
        const y = 0.12 + Math.random() * 0.76;
        addItem({ e, x, y, k: 'deco' });
        burst(x, y, '✨', 'spark');
        sound('tap');
        penDecos++;
        if (penJoined && !pals.pen.node.classList.contains('visiting')) pose('pen', 'hold', 'happy', 1600);
        saveSoon();
      }

      const ORDER = ['scoop', 'castle', 'pen'];
      let eventNo = 0;
      function nextEvent() {
        let k = eventNo < ORDER.length ? ORDER[eventNo] : (eventNo % 2 ? 'castle' : 'scoop');
        if (k === 'pen' && penJoined) k = 'castle';
        eventNo++;
        return k;
      }
      async function runEvent(kind) {
        if (busy || !alive()) return;
        busy = true;
        try {
          if (kind === 'scoop') await eventScoop();
          else if (kind === 'castle') await eventCastle();
          else if (kind === 'pen') await eventPen();
        } finally {
          busy = false;
        }
      }

      let playSec = 0;
      let nextAt = 35;
      const ticker = setInterval(() => {
        if (!alive()) return;
        const idle = Date.now() - lastTouch > 9000;
        if (!idle && !busy && !talking) playSec++;
        if (project && !project.finished && !talking) {
          // いぬくんも すこしずつ てつだって くれる
          project.p = Math.min(1, project.p + 0.004);
          updateProject();
        }
        if (penJoined && !busy && !talking && !idle && playSec % 40 === 0 && penDecos < 6) {
          penPlace(ctx.shuffle(DECOS)[0].e);
        }
        if (playSec >= nextAt && !busy && !talking && !strokes.size && !pours.size) {
          nextAt = playSec + 75;
          runEvent(nextEvent());
        }
      }, 1000);

      // ---- みせる ----
      let lastShowTalk = 0;
      async function showOff() {
        if (talking || !alive()) return;
        sound('tap');
        let dug = 0; let high = 0; let water = 0;
        for (let i = 0; i < N * N; i++) {
          if (h[i] < -0.3) dug++;
          if (h[i] > 0.5) high++;
          if (w[i] > 0.05) water++;
        }
        const decoN = items.filter((it) => it.k === 'deco').length;
        const lines = [];
        if (castlesBuilt) lines.push('ふたりで つくった おしろ、かっこいいね！');
        if (water > 300) lines.push('わあ！ かわに おみずが ながれてる！');
        if (high > 400) lines.push('すてきな かたちが いっぱい！ おやまも おおきいね！');
        if (dug > 400) lines.push('ながい みぞ だね！ すごい！');
        if (decoN) lines.push('かざりが きらきら、とっても きれい！');
        const viewer = penJoined && Math.random() < 0.5 ? 'pen' : 'inu';
        const p = pals[viewer];
        p.face.classList.remove('jump');
        void p.face.offsetWidth;
        p.face.classList.add('jump');
        const back = project ? 1200 : 3500;
        if (!lines.length) {
          pose(viewer, 'wave', 'normal', back);
          say(viewer, 'まだ まっさら だね。なにを つくるのかな？ たのしみ！');
          return;
        }
        // ほめる：ばんざい＋にこにこ
        pose(viewer, 'cheer', 'happy', back);
        const praise = ctx.shuffle(lines)[0];
        if (Date.now() - lastShowTalk > 45000) {
          lastShowTalk = Date.now();
          await talk({
            friend: viewer, say: `みせて みせて！ ${praise}`,
            choices: [
              { emoji: '🙏', label: 'ありがとう', good: true, reply: 'また みせてね！' },
              { emoji: '😶', label: 'しらんぷり', good: false, hint: 'ほめて もらったら、なんて いうんだっけ？' },
            ],
          });
        } else {
          sound('correct');
          say(viewer, praise);
        }
      }

      // ---- ならす（かくにん つき） ----
      function askFlatten() {
        if (talking || !alive()) return;
        sound('tap');
        if (project) { speak('いまは いぬくんと おしろを つくってるよ。'); return; }
        talking++;
        let closed = false;
        const close = () => { if (!closed) { closed = true; talking--; dlg.remove(); } };
        const dlg = el('div', { class: 'sunaba-confirm', role: 'dialog', 'aria-label': 'ぜんぶ たいらに する？' },
          el('div', { class: 'sunaba-confirm-card' },
            el('div', { class: 'sunaba-confirm-title' }, '🧹 ぜんぶ たいらに する？'),
            el('div', { class: 'sunaba-confirm-row' },
              el('button', { class: 'sunaba-confirm-btn yes', 'aria-label': 'たいらに する', onclick: () => { close(); flatten(); } },
                el('span', {}, '🏖️'), el('span', {}, 'たいらに する')),
              el('button', { class: 'sunaba-confirm-btn no', 'aria-label': 'やめる', onclick: () => { sound('tap'); close(); speak('このまま あそぼう！'); } },
                el('span', {}, '↩️'), el('span', {}, 'やめる')))));
        root.append(dlg);
        speak('ぜんぶ たいらに する？');
      }
      async function flatten() {
        sound('flip');
        itemLayer.classList.add('fade');
        for (let k = 0; k < 16; k++) {
          for (let i = 0; i < N * N; i++) { h[i] *= 0.8; w[i] *= 0.7; wet[i] *= 0.85; }
          dirty = true;
          await pause(40);
          if (!alive()) return;
        }
        flatSand();
        items = [];
        castlesBuilt = 0;
        itemLayer.classList.remove('fade');
        renderItems();
        dirty = true;
        saveNow();
        speak('たいらに なったよ。また なにを つくろうかな？');
      }

      speak('すなばだよ！ スコップで ほったり、てのひらで おやまを つくったり しよう。');

      return () => {
        clearInterval(ticker);
        clearTimeout(workTimer);
        Object.values(pals).forEach((pl) => clearTimeout(pl.poseTimer));
        cancelAnimationFrame(raf);
        ro.disconnect();
        timers.forEach((t) => clearTimeout(t));
        timers.clear();
        try { saveNow(); } catch (e) { /* なにもしない */ }
        clearTimeout(saveTimer);
      };
    },
  });
})();
