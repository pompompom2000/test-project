// つみき：横から見た つみきあそび。かたちと いろを えらんで ドラッグで おく。
// グリッドに ぴたっと はまり、したに なにも ないと おちる（かんたんな じゅうりょく）。
// ぱんだくんが いっしょに つくりに きたり、「さんかく ほしいな」と いったり、うっかり ぶつかったりする。
(function () {
  'use strict';

  const COLS = 10;
  const ROWS = 10;

  // はこの なかの つみき（limit = はこに はいっている かず）
  const SHAPES = [
    { id: 'sikaku', name: 'しかく', w: 1, h: 1, limit: 12 },
    { id: 'naga', name: 'ながしかく', w: 2, h: 1, limit: 8 },
    { id: 'sankaku', name: 'さんかく', w: 2, h: 1, limit: 2 },
    { id: 'hanen', name: 'はんえん', w: 2, h: 1, limit: 3 },
    { id: 'arch', name: 'アーチ', w: 2, h: 1, limit: 3 },
    { id: 'enchu', name: 'えんちゅう', w: 1, h: 2, limit: 6 },
  ];
  const SHAPE = Object.fromEntries(SHAPES.map((s) => [s.id, s]));

  const COLORS = [
    { id: 'aka', name: 'あか', fill: '#ff6b6b', dark: '#d94848' },
    { id: 'ao', name: 'あお', fill: '#4d8dff', dark: '#2f66cc' },
    { id: 'kiiro', name: 'きいろ', fill: '#ffcf3d', dark: '#d9a400' },
    { id: 'midori', name: 'みどり', fill: '#43c66b', dark: '#2a9a4c' },
    { id: 'murasaki', name: 'むらさき', fill: '#a77bff', dark: '#7b52d6' },
    { id: 'ki', name: 'きのいろ', fill: '#e6b47a', dark: '#b9844a' },
  ];
  const COLOR = Object.fromEntries(COLORS.map((c) => [c.id, c]));

  function shapeSVG(shapeId, colorId) {
    const s = SHAPE[shapeId];
    const c = COLOR[colorId] || COLORS[0];
    const st = `fill="${c.fill}" stroke="${c.dark}" stroke-width="6" stroke-linejoin="round"`;
    const hl = 'fill="#fff" fill-opacity="0.38"';
    let body = '';
    switch (shapeId) {
      case 'sikaku':
        body = `<rect x="4" y="4" width="92" height="92" rx="10" ${st}/><rect x="14" y="14" width="30" height="12" rx="6" ${hl}/>`;
        break;
      case 'naga':
        body = `<rect x="4" y="4" width="192" height="92" rx="10" ${st}/><rect x="16" y="14" width="56" height="12" rx="6" ${hl}/>`;
        break;
      case 'sankaku':
        body = `<path d="M100 8 L195 95 L5 95 Z" ${st}/><path d="M100 30 L70 58" stroke="#fff" stroke-opacity="0.45" stroke-width="9" stroke-linecap="round" fill="none"/>`;
        break;
      case 'hanen':
        body = `<path d="M4 96 A96 92 0 0 1 196 96 Z" ${st}/><path d="M38 52 A70 60 0 0 1 82 22" stroke="#fff" stroke-opacity="0.45" stroke-width="9" stroke-linecap="round" fill="none"/>`;
        break;
      case 'arch':
        body = `<path d="M4 4 H196 V96 H154 A54 54 0 0 0 46 96 H4 Z" ${st}/><rect x="14" y="13" width="50" height="11" rx="5" ${hl}/>`;
        break;
      case 'enchu':
        body = `<path d="M6 22 V178 A44 16 0 0 0 94 178 V22 Z" ${st}/><rect x="16" y="46" width="11" height="116" rx="5" ${hl}/>` +
          `<ellipse cx="50" cy="22" rx="44" ry="16" ${st}/><ellipse cx="50" cy="22" rx="44" ry="16" fill="#fff" fill-opacity="0.3"/>`;
        break;
    }
    return `<svg viewBox="0 0 ${s.w * 100} ${s.h * 100}" width="100%" height="100%" aria-hidden="true" focusable="false">${body}</svg>`;
  }

  const PANDA_LINES = ['ここに おくね！', 'よいしょ！', 'どう かな？', 'たかく なるね！', 'いっしょだと たのしいね！'];

  Core.registerSpot({
    id: 'tsumiki',
    start(ctx) {
      const { el, speak, sound } = ctx;
      const rand = (n) => Math.floor(Math.random() * n);
      const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

      // ---- タイマー（後片付けで まとめて止める） ----
      const timers = new Set();
      function later(fn, ms) {
        const id = setTimeout(() => { timers.delete(id); if (ctx.isActive()) fn(); }, ms);
        timers.add(id);
        return id;
      }
      const pause = (ms) => new Promise((r) => later(r, ms));

      // ---- 保存されている さくひん ----
      let nextId = 1;
      let blocks = [];
      const saved = ctx.store.get('blocks', []);
      if (Array.isArray(saved)) {
        for (const b of saved) {
          if (!b || !SHAPE[b.s] || !COLOR[b.c]) continue;
          const s = SHAPE[b.s];
          const x = Math.round(b.x); const y = Math.round(b.y);
          if (!(x >= 0 && y >= 0 && x + s.w <= COLS && y + s.h <= ROWS)) continue;
          blocks.push({ id: nextId++, s: b.s, c: b.c, x, y, o: b.o === 'panda' ? 'panda' : 'me' });
        }
      }
      let colorId = COLOR[ctx.store.get('color', 'aka')] ? ctx.store.get('color', 'aka') : 'aka';

      function save() {
        ctx.store.set('blocks', blocks.map((b) => ({ s: b.s, c: b.c, x: b.x, y: b.y, o: b.o })));
      }

      // ---- グリッドの けいさん ----
      const occupiedBy = (cx, cy, except) =>
        blocks.find((b) => b !== except && cx >= b.x && cx < b.x + SHAPE[b.s].w && cy >= b.y && cy < b.y + SHAPE[b.s].h);
      function fits(x, y, w, h, except) {
        if (x < 0 || y < 0 || x + w > COLS || y + h > ROWS) return false;
        for (let i = 0; i < w; i++) for (let j = 0; j < h; j++) if (occupiedBy(x + i, y + j, except)) return false;
        return true;
      }
      // (x, y) から おとして、とまる ばしょ。いっぱいなら null
      function settle(x, y, w, h, except) {
        while (y <= ROWS - h && !fits(x, y, w, h, except)) y++;
        if (y > ROWS - h) return null;
        while (y > 0 && fits(x, y - 1, w, h, except)) y--;
        return { x, y };
      }
      // したに なにも ない つみきを ぜんぶ おとす
      function settleAll() {
        let changed = false;
        let again = true;
        while (again) {
          again = false;
          blocks.sort((a, b) => a.y - b.y);
          for (const b of blocks) {
            const s = SHAPE[b.s];
            while (b.y > 0 && fits(b.x, b.y - 1, s.w, s.h, b)) { b.y--; again = true; changed = true; }
          }
        }
        return changed;
      }
      // さんかく・はんえんの うえは つるっと すべって のらない
      const SLIPPERY = { sankaku: true, hanen: true };
      function onSlippery(x, y, w, except) {
        if (y === 0) return false;
        const under = [];
        for (let i = 0; i < w; i++) { const u = occupiedBy(x + i, y - 1, except); if (u) under.push(u); }
        return under.length > 0 && under.every((u) => SLIPPERY[u.s]);
      }
      const remaining = (sid) => SHAPE[sid].limit - blocks.filter((b) => b.s === sid).length;
      const hasOnTop = (b) => {
        const s = SHAPE[b.s];
        for (let i = 0; i < s.w; i++) if (occupiedBy(b.x + i, b.y + s.h, b)) return true;
        return false;
      };

      // ---- 画面 ----
      const board = el('div', { class: 'tsumiki-board', 'aria-label': 'つみきを おく ところ' });
      const preview = el('div', { class: 'tsumiki-preview', 'aria-hidden': 'true' });
      board.append(preview);
      const meNode = el('div', { class: 'tsumiki-me', 'aria-hidden': 'true' }, ctx.player.emoji || '🧒');
      const pandaNode = el('div', { class: 'tsumiki-panda', 'aria-hidden': 'true' }, '🐼');
      const pandaSay = el('div', { class: 'tsumiki-say', 'aria-hidden': 'true' });
      pandaNode.append(pandaSay);
      const floor = el('div', { class: 'tsumiki-floor' }, meNode, pandaNode);
      const boardWrap = el('div', { class: 'tsumiki-boardwrap' }, el('div', { class: 'tsumiki-boardcol' }, board, floor));

      const colorBtns = COLORS.map((c) =>
        el('button', {
          class: 'tsumiki-color', 'aria-label': c.name, style: { background: c.fill, borderColor: c.dark },
          onclick: () => {
            if (busy()) return;
            colorId = c.id;
            ctx.store.set('color', colorId);
            sound('tap');
            speak(c.name);
            updatePalette();
          },
        }));
      const shapeBtns = SHAPES.map((s) => {
        const pic = el('span', { class: `tsumiki-shape-pic tsumiki-pic-${s.id}` });
        const badge = el('span', { class: 'tsumiki-stock' });
        const btn = el('button', { class: 'tsumiki-shape', 'aria-label': s.name }, pic, badge);
        btn._pic = pic;
        btn._badge = badge;
        btn.addEventListener('pointerdown', (e) => startDrag(e, { shape: s.id, color: colorId }));
        return btn;
      });
      const trash = el('div', { class: 'tsumiki-trash', role: 'img', 'aria-label': 'ゴミばこ' }, '🗑️');
      const doneBtn = el('button', { class: 'tsumiki-done', onclick: () => showOff() }, el('span', { 'aria-hidden': 'true' }, '🎉'), 'できた！');

      const side = el('div', { class: 'tsumiki-side' },
        el('div', { class: 'tsumiki-colors' }, colorBtns),
        el('div', { class: 'tsumiki-shapes' }, shapeBtns),
        trash, doneBtn);
      const dragLayer = el('div', { class: 'tsumiki-draglayer', 'aria-hidden': 'true' });
      const root = el('div', { class: 'tsumiki-root' }, boardWrap, side, dragLayer);
      ctx.stage.append(root);

      function updatePalette() {
        colorBtns.forEach((b, i) => b.classList.toggle('selected', COLORS[i].id === colorId));
        shapeBtns.forEach((b, i) => {
          const s = SHAPES[i];
          b._pic.innerHTML = shapeSVG(s.id, colorId);
          const n = remaining(s.id);
          b._badge.textContent = String(n);
          b.classList.toggle('empty', n <= 0);
        });
      }

      // ---- つみきの えがき ----
      let cell = 40;
      const blockEls = new Map();
      function blockEl(b) {
        let node = blockEls.get(b.id);
        if (!node) {
          node = el('div', { class: `tsumiki-block tsumiki-b-${b.s}`, 'aria-label': SHAPE[b.s].name, role: 'img' });
          node.innerHTML = shapeSVG(b.s, b.c);
          node.addEventListener('pointerdown', (e) => startDrag(e, { shape: b.s, color: b.c, block: b }));
          blockEls.set(b.id, node);
          board.append(node);
        }
        return node;
      }
      function sizeNode(node, s, x, y) {
        node.style.width = s.w * cell + 'px';
        node.style.height = s.h * cell + 'px';
        node.style.left = x * cell + 'px';
        node.style.bottom = y * cell + 'px';
      }
      function renderAll(noAnim) {
        for (const [id, node] of blockEls) {
          if (!blocks.some((b) => b.id === id)) { node.remove(); blockEls.delete(id); }
        }
        for (const b of blocks) {
          const node = blockEl(b);
          if (noAnim) node.classList.add('no-anim');
          sizeNode(node, SHAPE[b.s], b.x, b.y);
          node.style.zIndex = String(2 + b.y);
        }
        if (noAnim) {
          void board.offsetWidth;
          for (const node of blockEls.values()) node.classList.remove('no-anim');
        }
        updatePalette();
      }
      // うえから ふわっと おちてくる
      function dropIn(b, fromY) {
        const node = blockEl(b);
        node.classList.add('no-anim');
        sizeNode(node, SHAPE[b.s], b.x, fromY);
        node.style.zIndex = String(2 + b.y);
        void node.offsetWidth;
        node.classList.remove('no-anim');
        sizeNode(node, SHAPE[b.s], b.x, b.y);
        node.classList.add('landed');
        later(() => node.classList.remove('landed'), 450);
      }

      // ---- 大きさ（たて・よこ どちらでも おさまるように） ----
      function layout() {
        const wide = root.clientWidth > root.clientHeight * 1.15;
        root.classList.toggle('is-wide', wide);
        const floorH = floor.offsetHeight || 56;
        const w = boardWrap.clientWidth - 8;
        const h = boardWrap.clientHeight - floorH - 8;
        const c = Math.max(16, Math.floor(Math.min(w / COLS, h / ROWS)));
        if (c !== cell || !board.style.width) {
          cell = c;
          board.style.width = cell * COLS + 'px';
          board.style.height = cell * ROWS + 'px';
          board.style.setProperty('--cell', cell + 'px');
          floor.style.width = cell * COLS + 'px';
          renderAll(true);
        }
      }
      const ro = new ResizeObserver(() => { if (ctx.isActive()) layout(); });
      ro.observe(root);
      ro.observe(boardWrap);
      layout();
      renderAll(true);

      // ---- ドラッグ ----
      let drag = null;
      let talking = false; // おはなし・みせる・なおす の あいだは さわれない
      const busy = () => talking || !!drag;

      function landingAt(d, cx, cy) {
        const s = SHAPE[d.shape];
        const r = board.getBoundingClientRect();
        const m = cell * 0.6;
        if (cx < r.left - m || cx > r.right + m || cy < r.top - m || cy > r.bottom + m) return null;
        const x = clamp(Math.round((cx - r.left) / cell - s.w / 2), 0, COLS - s.w);
        const y0 = clamp(Math.round((r.bottom - cy) / cell - s.h / 2), 0, ROWS - s.h);
        const p = settle(x, y0, s.w, s.h, d.block);
        return p ? { ...p, y0: Math.max(y0, p.y), slip: onSlippery(p.x, p.y, s.w, d.block) } : null;
      }
      const overTrash = (cx, cy) => {
        const r = trash.getBoundingClientRect();
        return cx >= r.left - 12 && cx <= r.right + 12 && cy >= r.top - 12 && cy <= r.bottom + 12;
      };

      function startDrag(e, d) {
        if (talking || drag || !ctx.isActive()) return;
        if (e.button != null && e.button > 0) return;
        e.preventDefault();
        if (!d.block && remaining(d.shape) <= 0) {
          sound('tap');
          speak(`${SHAPE[d.shape].name}は はこに もう ないよ。つかって いない つみきを ゴミばこに いれると、はこに もどるよ。`);
          return;
        }
        try { e.currentTarget.setPointerCapture(e.pointerId); } catch (err) { /* なくても うごく */ }
        drag = { ...d, pid: e.pointerId, sx: e.clientX, sy: e.clientY, moved: false, ghost: null, land: null, trash: false };
        sound('tap');
      }

      function onMove(e) {
        if (!drag || e.pointerId !== drag.pid) return;
        if (!drag.moved) {
          if (Math.hypot(e.clientX - drag.sx, e.clientY - drag.sy) < 8) return;
          drag.moved = true;
          const s = SHAPE[drag.shape];
          drag.ghost = el('div', { class: 'tsumiki-ghost' });
          drag.ghost.innerHTML = shapeSVG(drag.shape, drag.color);
          drag.ghost.style.width = s.w * cell + 'px';
          drag.ghost.style.height = s.h * cell + 'px';
          dragLayer.append(drag.ghost);
          preview.innerHTML = shapeSVG(drag.shape, drag.color);
          preview.style.width = s.w * cell + 'px';
          preview.style.height = s.h * cell + 'px';
          if (drag.block) blockEl(drag.block).classList.add('lifted');
          else speak(s.name);
          root.classList.add('dragging');
        }
        const s = SHAPE[drag.shape];
        const rr = root.getBoundingClientRect();
        drag.ghost.style.left = e.clientX - rr.left - (s.w * cell) / 2 + 'px';
        drag.ghost.style.top = e.clientY - rr.top - (s.h * cell) / 2 + 'px';
        drag.trash = overTrash(e.clientX, e.clientY);
        trash.classList.toggle('hot', drag.trash);
        drag.land = drag.trash ? null : landingAt(drag, e.clientX, e.clientY);
        if (drag.land) {
          preview.style.left = drag.land.x * cell + 'px';
          preview.style.bottom = drag.land.y * cell + 'px';
          preview.classList.add('show');
          preview.classList.toggle('slip', drag.land.slip);
        } else {
          preview.classList.remove('show');
        }
      }

      function endDrag(e, cancelled) {
        if (!drag || e.pointerId !== drag.pid) return;
        const d = drag;
        drag = null;
        if (d.ghost) d.ghost.remove();
        preview.classList.remove('show');
        trash.classList.remove('hot');
        root.classList.remove('dragging');
        if (d.block) blockEl(d.block).classList.remove('lifted');
        if (!d.moved) {
          if (cancelled) return;
          if (!d.block) quickDrop(d.shape, d.color);
          else { const n = blockEl(d.block); n.classList.remove('wiggle'); void n.offsetWidth; n.classList.add('wiggle'); }
          return;
        }
        if (cancelled) return;
        if (d.trash) {
          if (d.block) removeBlock(d.block);
          return;
        }
        if (!d.land) return; // おけない ところ → もとに もどる
        if (d.land.slip) {
          sound('tap');
          speak('とがった ところや まるい ところの うえは、つるっと すべっちゃうね。');
          return;
        }
        if (d.block) {
          d.block.x = d.land.x;
          d.block.y = d.land.y;
          sound('flip');
          settleAll();
          renderAll(false);
          save();
        } else {
          addBlock(d.shape, d.color, d.land.x, d.land.y, d.land.y0, 'me');
        }
      }
      const onUp = (e) => endDrag(e, false);
      const onCancel = (e) => endDrag(e, true);
      window.addEventListener('pointermove', onMove);
      window.addEventListener('pointerup', onUp);
      window.addEventListener('pointercancel', onCancel);

      function addBlock(shape, color, x, y, fromY, owner) {
        const b = { id: nextId++, s: shape, c: color, x, y, o: owner };
        blocks.push(b);
        dropIn(b, fromY);
        sound('flip');
        updatePalette();
        save();
        if (owner === 'me') onKidPlaced(b);
        return b;
      }

      function removeBlock(b) {
        blocks = blocks.filter((x) => x !== b);
        const node = blockEls.get(b.id);
        if (node) {
          blockEls.delete(b.id);
          node.classList.add('poof');
          later(() => node.remove(), 400);
        }
        sound('tap');
        settleAll();
        renderAll(false);
        save();
      }

      // タップだけの ときは、まんなかあたりに ぽとんと おとす
      function quickDrop(shape, color) {
        const s = SHAPE[shape];
        const mid = Math.floor((COLS - s.w) / 2);
        const order = [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5].map((o) => mid + o).filter((x) => x >= 0 && x <= COLS - s.w);
        const startOff = rand(3) - 1;
        for (const x0 of order) {
          const x = clamp(x0 + startOff, 0, COLS - s.w);
          const p = settle(x, ROWS - s.h, s.w, s.h);
          if (p && !onSlippery(p.x, p.y, s.w)) { addBlock(shape, color, p.x, p.y, ROWS - s.h, 'me'); return; }
        }
        speak('もう おく ところが ないみたい。');
      }

      // ---- ぱんだくん ----
      const soc = {
        t: 0, joined: false, placed: 0, lastTalk: -999,
        nextPlace: 0, triDone: false, triAt: Infinity, turnAt: Infinity,
        bumpDone: false, bumpAt: Infinity,
      };
      function pandaSays(text, ms = 2200) {
        pandaSay.textContent = text;
        pandaSay.classList.add('show');
        later(() => pandaSay.classList.remove('show'), ms);
        speak(text);
      }
      function hop(node) {
        node.classList.remove('hop');
        void node.offsetWidth;
        node.classList.add('hop');
      }

      // ぱんだくんが おく ばしょを さがす（なるべく つみきの うえに）
      function pandaSpot(shape) {
        const s = SHAPE[shape];
        const spots = [];
        for (let x = 0; x <= COLS - s.w; x++) {
          const p = settle(x, ROWS - s.h, s.w, s.h);
          if (p && p.y + s.h <= ROWS - 1 && !onSlippery(p.x, p.y, s.w)) spots.push(p);
        }
        if (!spots.length) return null;
        const stacked = spots.filter((p) => p.y > 0);
        if (stacked.length && Math.random() < 0.7) {
          stacked.sort((a, b) => b.y - a.y);
          return stacked[rand(Math.min(3, stacked.length))];
        }
        return spots[rand(spots.length)];
      }
      function pandaPlace(shape, line) {
        const p = pandaSpot(shape);
        if (!p) return false;
        hop(pandaNode);
        addBlock(shape, COLORS[rand(COLORS.length)].id, p.x, p.y, ROWS - SHAPE[shape].h, 'panda');
        const node = blockEls.get(blocks[blocks.length - 1].id);
        if (node) { node.classList.add('by-panda'); later(() => node.classList.remove('by-panda'), 1800); }
        pandaSays(line || PANDA_LINES[rand(PANDA_LINES.length)]);
        return true;
      }
      function pandaTurn() {
        const options = ['sikaku', 'naga', 'hanen', 'arch', 'enchu'].filter((id) => remaining(id) >= 2);
        if (options.length) pandaPlace(options[rand(options.length)]);
        soc.nextPlace = soc.t + 24 + rand(12);
      }
      function pandaTriangle(line) {
        if (remaining('sankaku') >= 1 && pandaPlace('sankaku', line)) return;
        pandaSays('さんかく、また こんど かしてね！');
      }

      function onKidPlaced(b) {
        soc.placed++;
        if (b.s === 'sankaku') {
          // さいごの 1こに なったら、ぱんだくんが「ほしいな」
          if (soc.joined && !soc.triDone && remaining('sankaku') === 1) soc.triAt = Math.min(soc.triAt, soc.t + 3);
          // じゅんばんこ の あとは、つかったら つぎは ぱんだくんの ばん
          if (soc.turnAt !== Infinity) soc.turnAt = Math.min(soc.turnAt, soc.t + 4);
        }
      }

      // (1) いっしょに つくって いい？
      async function invite() {
        talking = true;
        pandaNode.classList.add('in');
        hop(pandaNode);
        await pause(900);
        const r = await ctx.talk({
          friend: 'panda',
          say: 'わあ、すてき！ いっしょに つくって いい？',
          choices: [
            { emoji: '🙆', label: 'いいよ', good: true, reply: 'やったあ！ いっしょに つくろうね！' },
            { emoji: '🙅', label: 'ひとりで やる', good: false, hint: 'ぱんだくん、いっしょに つくりたいみたい。ふたりだと もっと たのしいかも？' },
          ],
        });
        if (!r || !ctx.isActive()) return;
        talking = false;
        soc.joined = true;
        soc.lastTalk = soc.t;
        soc.nextPlace = soc.t + 5;
        soc.triAt = soc.t + 55;
        pandaNode.classList.add('joined');
      }

      // (2) さんかく ほしいな
      async function askTriangle() {
        talking = true;
        hop(pandaNode);
        const r = await ctx.talk({
          friend: 'panda',
          say: 'さんかく ほしいな。ぼくも やねを つくりたいんだ。',
          choices: [
            { emoji: '🤲', label: 'どうぞ', good: true, reply: 'ありがとう！ うれしいな！' },
            { emoji: '🔁', label: 'じゅんばんこ に しよう', good: true, reply: 'うん！ じゅんばんこ ね。さきに つかって いいよ！' },
            { emoji: '🙅', label: 'あげない', good: false, hint: 'ぱんだくん、しょんぼり…。どうしたら ふたりとも にこにこ かな？' },
          ],
        });
        if (!r || !ctx.isActive()) return;
        talking = false;
        soc.triDone = true;
        soc.lastTalk = soc.t;
        soc.bumpAt = soc.t + 60;
        soc.nextPlace = Math.max(soc.nextPlace, soc.t + 20);
        if (r.label === 'どうぞ') later(() => pandaTriangle('やねが できた！ どうぞ して くれて ありがとう！'), 700);
        else soc.turnAt = soc.t + 15;
      }

      // (3) うっかり ぶつかって すこし くずれる
      async function bump() {
        // いちばん うえに のっている つみき（こどもの つみきを さきに）
        const cands = blocks.filter((b) => b.y >= 1 && !hasOnTop(b))
          .sort((a, b) => (a.o === 'me' ? 0 : 1) - (b.o === 'me' ? 0 : 1) || b.y - a.y);
        if (!cands.length) { soc.bumpAt = soc.t + 15; return; }
        const knocked = cands.slice(0, cands.length >= 2 && blocks.length >= 5 ? 2 : 1);
        talking = true;
        pandaNode.classList.add('bump');
        await pause(500);
        if (!ctx.isActive()) return;
        sound('flip');
        knocked.forEach((b, i) => {
          const node = blockEl(b);
          const dir = (b.x + SHAPE[b.s].w / 2 < COLS / 2 ? -1 : 1) * (i ? -1 : 1);
          node.style.setProperty('--dx', dir * cell * (0.8 + i * 0.6) + 'px');
          node.style.setProperty('--dy', b.y * cell + 'px');
          node.style.setProperty('--rot', dir * (70 + rand(30)) + 'deg');
          node.classList.add('tumble');
        });
        await pause(900);
        if (!ctx.isActive()) return;
        pandaNode.classList.remove('bump');
        const r = await ctx.talk({
          friend: 'panda',
          mood: '😣',
          say: 'あっ！ ぶつかっちゃった…。くずれちゃって ごめんね。',
          choices: [
            { emoji: '🙆', label: 'いいよ', good: true, reply: 'ゆるして くれて ありがとう。やさしいね。' },
            { emoji: '😠', label: 'おこる', good: false, hint: 'ぱんだくん、わざと じゃ なかったんだって。しょんぼり してるよ。なんて いったら いいかな？' },
          ],
        });
        if (!r || !ctx.isActive()) return;
        // いっしょに なおそう
        const fixBtn = el('button', { class: 'tsumiki-fix' }, el('span', { 'aria-hidden': 'true' }, '🤝'), 'いっしょに なおそう');
        const veil = el('div', { class: 'tsumiki-veil' }, fixBtn);
        root.append(veil);
        speak('いっしょに なおそう！');
        await new Promise((res) => fixBtn.addEventListener('click', res, { once: true }));
        if (!ctx.isActive()) return;
        sound('tap');
        fixBtn.disabled = true;
        for (let i = 0; i < knocked.length; i++) {
          hop(i % 2 ? meNode : pandaNode);
          hop(i % 2 ? pandaNode : meNode);
          blockEl(knocked[i]).classList.remove('tumble');
          sound('flip');
          await pause(700);
          if (!ctx.isActive()) return;
        }
        veil.remove();
        sound('correct');
        pandaSays('なおったね！ いっしょだと すぐ なおるね！', 2600);
        talking = false;
        soc.bumpDone = true;
        soc.lastTalk = soc.t;
        soc.nextPlace = Math.max(soc.nextPlace, soc.t + 15);
      }

      // ---- できた！ → おともだちに みせる ----
      function praises() {
        const list = [];
        if (!blocks.length) return ['これから なにを つくるのかな？ たのしみ！', 'つみき、いっぱい あるよ！'];
        const top = Math.max(...blocks.map((b) => b.y + SHAPE[b.s].h));
        const colors = new Set(blocks.map((b) => b.c)).size;
        if (top >= 6) list.push('たかーい！ おそらまで とどきそう！');
        if (colors >= 4) list.push('いろが いっぱいで きれい！');
        if (blocks.some((b) => b.s === 'arch')) list.push('アーチが かっこいいね！');
        if (blocks.some((b) => b.s === 'sankaku' && b.y > 0)) list.push('さんかくの やねが すてき！');
        if (blocks.some((b) => b.s === 'enchu')) list.push('えんちゅうの はしら、つよそう！');
        if (blocks.length >= 10) list.push('こんなに たくさん つんだの？ すごい！');
        list.push(...Core.shuffle(['わあ、すごい！ じょうずだね！', 'すてきな おうち みたい！', 'おしろ みたいで かっこいい！', 'どうやって つくったの？ おしえて！']));
        return list;
      }
      async function showOff() {
        if (busy() || !ctx.isActive()) return;
        talking = true;
        sound('fanfare');
        const ids = ctx.shuffle(['inu', 'neko', 'kitsune', 'pen']).slice(0, 2);
        if (soc.joined) ids.push('panda');
        const lines = praises();
        const guests = ids.map((id) => {
          const f = ctx.friend(id);
          const bubble = el('div', { class: 'tsumiki-guest-say' });
          const node = el('div', { class: 'tsumiki-guest' },
            el('div', { class: 'tsumiki-guest-face', style: { background: f.color } }, f.emoji), bubble);
          return { f, node, bubble };
        });
        const closeBtn = el('button', { class: 'tsumiki-close', 'aria-label': 'つづきを つくる' }, el('span', { 'aria-hidden': 'true' }, '🧱'), 'つづける');
        closeBtn.hidden = true;
        const sheet = el('div', { class: 'tsumiki-show' },
          el('div', { class: 'tsumiki-show-me' }, el('span', {}, ctx.player.emoji || '🧒'), el('span', { class: 'tsumiki-show-call' }, 'みて みて！')),
          el('div', { class: 'tsumiki-guests' }, guests.map((g) => g.node)),
          closeBtn);
        const veil = el('div', { class: 'tsumiki-veil show-veil' }, sheet);
        root.append(veil);
        let closed = false;
        const close = () => {
          if (closed) return;
          closed = true;
          veil.remove();
          talking = false;
        };
        closeBtn.addEventListener('click', () => { sound('tap'); close(); });
        await speak('みんなー！ みて みて！ できたよ！');
        for (let i = 0; i < guests.length; i++) {
          if (!ctx.isActive() || closed) return;
          const g = guests[i];
          g.node.classList.add('in');
          sound('correct');
          const line = g.f.id === 'panda' ? 'いっしょに つくれて たのしかった！' : lines[i % lines.length];
          g.bubble.textContent = line;
          await pause(350);
          await speak(line);
        }
        if (!ctx.isActive() || closed) return;
        closeBtn.hidden = false;
        later(close, 8000);
      }

      // ---- ときどき おこる できごと（1びょう ごと） ----
      const tick = setInterval(() => {
        if (!ctx.isActive() || busy()) return;
        soc.t++;
        const t = soc.t;
        if (!soc.joined) {
          if ((soc.placed >= 3 && t >= 8) || t >= 25) invite();
          return;
        }
        if (t >= soc.turnAt) { soc.turnAt = Infinity; pandaTriangle('ぼくの ばん だね！ さんかく つかうね。じゅんばんこ ありがとう！'); return; }
        if (!soc.triDone && t >= soc.triAt && t - soc.lastTalk >= 15 && remaining('sankaku') >= 1) { askTriangle(); return; }
        if (soc.triDone && !soc.bumpDone && t >= soc.bumpAt && t - soc.lastTalk >= 40) { bump(); return; }
        if (t >= soc.nextPlace) pandaTurn();
      }, 1000);

      speak(blocks.length
        ? 'つづきから つくろう！ つみきを ひっぱって、おいてね。'
        : 'つみきで あそぼう！ したの はこから つみきを ひっぱって、おいてね。');

      return () => {
        clearInterval(tick);
        timers.forEach(clearTimeout);
        timers.clear();
        ro.disconnect();
        window.removeEventListener('pointermove', onMove);
        window.removeEventListener('pointerup', onUp);
        window.removeEventListener('pointercancel', onCancel);
        drag = null;
      };
    },
  });
})();
