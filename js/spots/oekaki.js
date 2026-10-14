// おえかき：じゆうに かける キャンバス。かして・どうぞ、みせて・ほめる の ばめん つき
(function () {
  'use strict';

  // かみの おおきさ（えがく ときの ざひょう。ほんとうの がめんの おおきさとは べつ）
  const W = 1000;
  const H = 750;
  const MAX_WORKS = 12;
  const PAPER = '#ffffff';

  const COLORS = [
    { id: 'aka', hex: '#e53935', name: 'あか', crayon: 'あかい クレヨン' },
    { id: 'orange', hex: '#fb8c00', name: 'オレンジ', crayon: 'オレンジの クレヨン' },
    { id: 'kiiro', hex: '#fdd835', name: 'きいろ', crayon: 'きいろい クレヨン' },
    { id: 'midori', hex: '#43a047', name: 'みどり', crayon: 'みどりの クレヨン' },
    { id: 'ao', hex: '#1e6fd9', name: 'あお', crayon: 'あおい クレヨン' },
    { id: 'pink', hex: '#f06292', name: 'ピンク', crayon: 'ピンクの クレヨン' },
    { id: 'chairo', hex: '#8d5524', name: 'ちゃいろ', crayon: 'ちゃいろい クレヨン' },
    { id: 'kuro', hex: '#37302a', name: 'くろ', crayon: 'くろい クレヨン' },
  ];
  const colorById = (id) => COLORS.find((c) => c.id === id);

  const SIZES = [
    { id: 's', name: 'ほそい', pen: 8, eraser: 34, stamp: 60, dot: 12 },
    { id: 'm', name: 'ふつう', pen: 18, eraser: 64, stamp: 96, dot: 24 },
    { id: 'l', name: 'ふとい', pen: 36, eraser: 120, stamp: 150, dot: 40 },
  ];

  const STAMPS = [
    { e: '⭐', name: 'おほしさま' },
    { e: '🌸', name: 'おはな' },
    { e: '🐟', name: 'おさかな' },
    { e: '🍎', name: 'りんご' },
    { e: '🦋', name: 'ちょうちょ' },
    { e: '🚗', name: 'くるま' },
    { e: '❤️', name: 'ハート' },
    { e: '🌈', name: 'にじ' },
  ];
  const stampName = (e) => (STAMPS.find((s) => s.e === e) || { name: 'スタンプ' }).name;

  // おともだちが かいた え（えもじで つくった かんたんな え）
  const FRIEND_ART = {
    inu: [['☀️', '☁️', '☁️'], ['🌳', '🏠', '🐕'], ['🌷', '🌷', '🌷']],
    neko: [['🌙', '⭐', '✨'], ['🐟', '🐱', '🐟'], ['🌸', '🌸', '🌸']],
    panda: [['☀️', '🌈', '☁️'], ['🎋', '🐼', '🎋'], ['🍃', '🍃', '🍃']],
    kitsune: [['🍂', '☀️', '🍁'], ['🍄', '🦊', '🌰'], ['🌾', '🌾', '🌾']],
    pen: [['❄️', '☁️', '❄️'], ['🐧', '⛄', '🐧'], ['🌊', '🐟', '🌊']],
  };
  const SELF_WORD = { inu: 'ぼく', panda: 'ぼく', pen: 'ぼく', neko: 'わたし', kitsune: 'わたし' };

  Core.registerSpot({
    id: 'oekaki',
    start(ctx) {
      const { el, speak, sound } = ctx;

      // ---- タイマー（あとかたづけで まとめて とめる） ----
      const timers = new Set();
      const later = (fn, ms) => {
        const t = setTimeout(() => { timers.delete(t); if (ctx.isActive()) fn(); }, ms);
        timers.add(t);
        return t;
      };
      const pause = (ms) => new Promise((r) => later(r, ms));

      // ---- じょうたい ----
      const st = {
        color: 'aka',
        size: 1,
        mode: 'pen', // pen | eraser | stamp
        stamp: '⭐',
        dirty: false,
        lent: null, // かしている いろの id
        strokes: 0,
        colors: new Set(),
        stamps: new Set(),
        strokesSinceEvent: 0,
        lastEventAt: 0,
        events: 0,
        busyTalk: false,
      };
      const pointers = new Map(); // pointerId -> {x, y}

      // ---- がめん ----
      const canvas = el('canvas', { class: 'oekaki-canvas', 'aria-label': 'おえかきの かみ' });
      const g = canvas.getContext('2d');
      const visitor = el('div', { class: 'oekaki-visitor', 'aria-hidden': 'true' });
      const paper = el('div', { class: 'oekaki-paper' }, canvas, visitor);
      const wrap = el('div', { class: 'oekaki-paper-wrap' }, paper);

      const colorBtns = COLORS.map((c) =>
        el('button', {
          class: 'oekaki-btn oekaki-color',
          'aria-label': c.name,
          'data-color': c.id,
          onclick: () => pickColor(c.id),
        }, el('span', { class: 'oekaki-crayon' }), el('span', { class: 'oekaki-lent-badge' })),
      );
      // カスタムプロパティは style オブジェクトでは せっていできないので setProperty で
      colorBtns.forEach((b, i) => b.style.setProperty('--c', COLORS[i].hex));
      const palette = el('div', { class: 'oekaki-palette' }, colorBtns);

      const sizeBtns = SIZES.map((s, i) =>
        el('button', {
          class: 'oekaki-btn oekaki-size',
          'aria-label': s.name,
          onclick: () => { sound('tap'); st.size = i; speak(s.name); refresh(); },
        }, el('span', { class: 'oekaki-size-dot', style: { width: s.dot + 'px', height: s.dot + 'px' } })),
      );
      const stampBtn = el('button', { class: 'oekaki-btn oekaki-tool', 'aria-label': 'スタンプ', onclick: openStampPicker }, '⭐');
      const eraserBtn = el('button', {
        class: 'oekaki-btn oekaki-tool', 'aria-label': 'けしゴム',
        onclick: () => { sound('tap'); st.mode = 'eraser'; speak('けしゴム'); refresh(); },
      }, el('span', { class: 'oekaki-eraser' }));
      const trashBtn = el('button', { class: 'oekaki-btn oekaki-tool', 'aria-label': 'ぜんぶ けす', onclick: confirmClear }, '🗑️');
      const galleryBtn = el('button', { class: 'oekaki-btn oekaki-tool', 'aria-label': 'さくひん ギャラリー', onclick: openGallery }, '🖼️');
      const doneBtn = el('button', { class: 'oekaki-btn oekaki-done', 'aria-label': 'できた', onclick: finish },
        el('span', { class: 'oekaki-done-emoji' }, '✨'), el('span', { class: 'oekaki-done-text' }, 'できた！'));
      const tools = el('div', { class: 'oekaki-tools' }, sizeBtns, stampBtn, eraserBtn, trashBtn, galleryBtn, doneBtn);

      const root = el('div', { class: 'oekaki-root' }, palette, wrap, tools);
      ctx.stage.append(root);

      function refresh() {
        const c = colorById(st.color);
        colorBtns.forEach((b) => b.classList.toggle('is-on', st.mode === 'pen' && b.dataset.color === st.color));
        sizeBtns.forEach((b, i) => {
          b.classList.toggle('is-on', i === st.size);
          b.firstChild.style.background = st.mode === 'eraser' ? '#bbb' : c.hex;
        });
        stampBtn.textContent = st.stamp;
        stampBtn.classList.toggle('is-on', st.mode === 'stamp');
        eraserBtn.classList.toggle('is-on', st.mode === 'eraser');
        canvas.dataset.mode = st.mode;
      }

      function pickColor(id) {
        sound('tap');
        if (id === st.lent) {
          const f = ctx.friend(currentBorrower);
          speak(`いまは ${f ? f.name : 'おともだち'}が つかってるよ。 もうすこし まってね。`);
          return;
        }
        st.color = id;
        st.mode = 'pen';
        speak(colorById(id).name);
        refresh();
      }

      // ---- かみ（canvas）の おおきさ。devicePixelRatio に あわせる ----
      let sized = false;
      function fit() {
        const r = wrap.getBoundingClientRect();
        if (r.width < 10 || r.height < 10) return;
        let w = r.width;
        let h = (w * H) / W;
        if (h > r.height) { h = r.height; w = (h * W) / H; }
        w = Math.floor(w); h = Math.floor(h);
        paper.style.width = w + 'px';
        paper.style.height = h + 'px';
        const dpr = Math.min(window.devicePixelRatio || 1, 3);
        const bw = Math.round(w * dpr);
        const bh = Math.round(h * dpr);
        if (sized && canvas.width === bw && canvas.height === bh) return;
        let old = null;
        if (sized) {
          old = document.createElement('canvas');
          old.width = canvas.width; old.height = canvas.height;
          old.getContext('2d').drawImage(canvas, 0, 0);
        }
        canvas.width = bw;
        canvas.height = bh;
        g.setTransform(1, 0, 0, 1, 0, 0);
        g.fillStyle = PAPER;
        g.fillRect(0, 0, bw, bh);
        if (old) g.drawImage(old, 0, 0, bw, bh);
        g.setTransform(bw / W, 0, 0, bh / H, 0, 0);
        sized = true;
      }
      const ro = new ResizeObserver(() => fit());
      ro.observe(wrap);
      fit();

      function clearPaper() {
        g.save();
        g.setTransform(1, 0, 0, 1, 0, 0);
        g.fillStyle = PAPER;
        g.fillRect(0, 0, canvas.width, canvas.height);
        g.restore();
        st.dirty = false;
        st.strokes = 0;
        st.colors.clear();
        st.stamps.clear();
      }

      // ---- えがく（マルチタッチ） ----
      function toPaper(e) {
        const r = canvas.getBoundingClientRect();
        return { x: ((e.clientX - r.left) / r.width) * W, y: ((e.clientY - r.top) / r.height) * H };
      }
      function inkStyle() {
        const s = SIZES[st.size];
        if (st.mode === 'eraser') return { color: PAPER, width: s.eraser };
        return { color: colorById(st.color).hex, width: s.pen };
      }
      function dot(p, ink) {
        g.fillStyle = ink.color;
        g.beginPath();
        g.arc(p.x, p.y, ink.width / 2, 0, Math.PI * 2);
        g.fill();
      }
      function line(a, b, ink) {
        g.strokeStyle = ink.color;
        g.lineWidth = ink.width;
        g.lineCap = 'round';
        g.lineJoin = 'round';
        g.beginPath();
        g.moveTo(a.x, a.y);
        g.lineTo(b.x, b.y);
        g.stroke();
      }
      function placeStamp(p) {
        const size = SIZES[st.size].stamp;
        g.save();
        g.font = `${size}px "Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",sans-serif`;
        g.textAlign = 'center';
        g.textBaseline = 'middle';
        g.fillText(st.stamp, p.x, p.y);
        g.restore();
        st.stamps.add(st.stamp);
        st.dirty = true;
        sound('flip');
      }

      canvas.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        const p = toPaper(e);
        if (st.mode === 'stamp') {
          placeStamp(p);
          countStroke();
          return;
        }
        try { canvas.setPointerCapture(e.pointerId); } catch (err) { /* むし */ }
        const ink = inkStyle();
        pointers.set(e.pointerId, { p, ink });
        dot(p, ink);
        st.dirty = true;
        if (st.mode === 'pen') st.colors.add(st.color);
      });
      canvas.addEventListener('pointermove', (e) => {
        const cur = pointers.get(e.pointerId);
        if (!cur) return;
        const list = typeof e.getCoalescedEvents === 'function' ? e.getCoalescedEvents() : [];
        const evs = list.length ? list : [e];
        for (const ev of evs) {
          const p = toPaper(ev);
          line(cur.p, p, cur.ink);
          cur.p = p;
        }
      });
      const endPointer = (e) => {
        if (!pointers.has(e.pointerId)) return;
        pointers.delete(e.pointerId);
        countStroke();
      };
      canvas.addEventListener('pointerup', endPointer);
      canvas.addEventListener('pointercancel', endPointer);
      canvas.addEventListener('lostpointercapture', endPointer);
      canvas.addEventListener('contextmenu', (e) => e.preventDefault());

      function countStroke() {
        st.strokes++;
        st.strokesSinceEvent++;
        later(maybeBorrow, 700);
      }

      // ---- パネル（あそびばの なかに かさねる） ----
      const panels = new Set();
      function openPanel(cls, ...children) {
        const node = el('div', { class: 'oekaki-panel ' + cls }, ...children);
        ctx.stage.append(node);
        panels.add(node);
        return () => { node.remove(); panels.delete(node); };
      }
      const busy = () => panels.size > 0 || st.busyTalk || pointers.size > 0;

      // ---- スタンプ えらび ----
      function openStampPicker() {
        sound('tap');
        let close;
        close = openPanel('oekaki-stamp-panel',
          el('div', { class: 'oekaki-card' },
            el('div', { class: 'oekaki-stamp-grid' },
              STAMPS.map((s) => el('button', {
                class: 'oekaki-btn oekaki-stamp' + (s.e === st.stamp ? ' is-on' : ''),
                'aria-label': s.name,
                onclick: () => {
                  sound('tap');
                  st.stamp = s.e;
                  st.mode = 'stamp';
                  refresh();
                  close();
                  speak(`${s.name}の スタンプ。 かみを タッチしてね。`);
                },
              }, s.e)),
            ),
          ),
        );
        speak('どの スタンプに する？');
      }

      // ---- ぜんぶ けす（かくにん つき） ----
      function confirmClear() {
        sound('tap');
        if (!st.dirty) { speak('まだ まっしろ だよ。'); return; }
        let close;
        close = openPanel('oekaki-confirm-panel',
          el('div', { class: 'oekaki-card' },
            el('div', { class: 'oekaki-confirm-pic', 'aria-hidden': 'true' }, '🖼️', el('span', { class: 'oekaki-confirm-arrow' }, '➡'), '🗑️'),
            el('div', { class: 'oekaki-row' },
              el('button', {
                class: 'oekaki-btn oekaki-big oekaki-yes', 'aria-label': 'けす',
                onclick: () => { sound('flip'); clearPaper(); close(); speak('まっしろに なったよ。'); },
              }, '⭕'),
              el('button', {
                class: 'oekaki-btn oekaki-big oekaki-no', 'aria-label': 'やめる',
                onclick: () => { sound('tap'); close(); speak('やめたよ。 つづきを かこう。'); },
              }, '↩️'),
            ),
          ),
        );
        speak('ぜんぶ けしても いい？ けすなら まる。 やめるなら やじるし。');
      }

      // ---- ほぞん ----
      function snapshot() {
        const c = document.createElement('canvas');
        c.width = 640; c.height = 480;
        const cg = c.getContext('2d');
        cg.fillStyle = PAPER;
        cg.fillRect(0, 0, 640, 480);
        cg.drawImage(canvas, 0, 0, 640, 480);
        return c.toDataURL('image/jpeg', 0.82);
      }
      const loadWorks = () => {
        const w = ctx.store.get('works', []);
        return Array.isArray(w) ? w : [];
      };
      function saveWork(work) {
        const works = loadWorks();
        works.push(work);
        while (works.length > MAX_WORKS) works.shift(); // ふるい ものから けす
        ctx.store.set('works', works);
      }
      function updateWork(id, fn) {
        const works = loadWorks();
        const w = works.find((x) => x.id === id);
        if (w) { fn(w); ctx.store.set('works', works); }
      }

      // かきかけを のこす / もどす
      function saveDraft() {
        if (!sized) return;
        if (!st.dirty) { ctx.store.set('draft', null); return; }
        ctx.store.set('draft', {
          img: snapshot(), strokes: st.strokes, colors: [...st.colors], stamps: [...st.stamps],
        });
      }
      function restoreDraft() {
        const d = ctx.store.get('draft', null);
        if (!d || !d.img) return;
        const img = new Image();
        img.onload = () => {
          if (!ctx.isActive()) return;
          g.drawImage(img, 0, 0, W, H);
          st.dirty = true;
          st.strokes = d.strokes || 0;
          (d.colors || []).forEach((c) => st.colors.add(c));
          (d.stamps || []).forEach((s) => st.stamps.add(s));
        };
        img.src = d.img;
      }

      // ---- できた！ ----
      function finish() {
        sound('tap');
        if (!st.dirty) { speak('なにか かいてから 「できた」を おしてね。'); return; }
        const work = {
          id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
          img: snapshot(),
          at: Date.now(),
          strokes: st.strokes,
          colors: [...st.colors],
          stamps: [...st.stamps],
          shown: [],
        };
        saveWork(work);
        sound('fanfare');
        showDonePanel(work);
      }

      function frame(src, extra = '') {
        return el('div', { class: 'oekaki-frame ' + extra }, el('img', { class: 'oekaki-frame-img', src, alt: 'さくひん' }));
      }

      function friendPicker(onPick) {
        return el('div', { class: 'oekaki-friends' },
          ctx.friends.map((f) => el('button', {
            class: 'oekaki-btn oekaki-friend', 'aria-label': `${f.name}に みせる`, style: { background: f.color },
            onclick: () => { sound('tap'); onPick(f); },
          }, f.emoji)),
        );
      }

      function showDonePanel(work) {
        let close;
        close = openPanel('oekaki-done-panel',
          el('div', { class: 'oekaki-card oekaki-done-card' },
            el('div', { class: 'oekaki-done-head', 'aria-hidden': 'true' }, '🎉'),
            frame(work.img, 'oekaki-frame-big'),
            el('div', { class: 'oekaki-label' }, '👀 だれに みせる？'),
            friendPicker((f) => { close(); showToFriend(f, work, () => showDonePanel(loadWorks().find((w) => w.id === work.id) || work)); }),
            el('div', { class: 'oekaki-row' },
              el('button', {
                class: 'oekaki-btn oekaki-wide', 'aria-label': 'つづきを かく',
                onclick: () => { sound('tap'); close(); speak('つづきを かこう！'); },
              }, '✏️'),
              el('button', {
                class: 'oekaki-btn oekaki-wide', 'aria-label': 'あたらしい かみ',
                onclick: () => { sound('flip'); clearPaper(); close(); speak('あたらしい かみ だよ。 なにを かこうかな？'); },
              }, '📄✨'),
            ),
          ),
        );
        speak('すてきな えが できたね！ かべに かざったよ。 おともだちに みせてみよう。');
      }

      // ---- おともだちに みせる → ほめてもらう → おともだちの えを みる ----
      function praiseFor(work) {
        const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
        const cols = (work.colors || []).map(colorById).filter(Boolean);
        const colorWords = [];
        if (cols.length >= 4) colorWords.push('いろが いっぱいで、にじ みたい！');
        else if (cols.length >= 2) colorWords.push('いろの くみあわせが すてき！');
        if (cols.length) colorWords.push(`${pick(cols).name}の いろが とっても きれい！`);
        const list = [];
        if (colorWords.length) list.push(pick(colorWords));
        const stamps = work.stamps || [];
        if (stamps.length) list.push(`${stampName(pick(stamps))}が かわいいね！`);
        if ((work.strokes || 0) >= 15) list.push('たくさん かいたね！ がんばったね！');
        if (!list.length) list.push('のびのび かけてるね！ すてき！');
        return 'わあ！ ' + ctx.shuffle(list).slice(0, 2).join(' ');
      }

      async function showToFriend(f, work, after) {
        const word = SELF_WORD[f.id] || 'ぼく';
        let close;
        const showcase = el('div', { class: 'oekaki-showcase' },
          frame(work.img, 'oekaki-frame-show'),
          el('div', { class: 'oekaki-looker', style: { background: f.color } }, f.emoji),
        );
        close = openPanel('oekaki-show-panel', showcase);
        st.busyTalk = true;
        try {
          await pause(500);
          const r1 = await ctx.talk({
            friend: f.id,
            mood: '😍',
            say: praiseFor(work),
            choices: [
              { emoji: '😶', label: 'だまってる', good: false, hint: 'ほめて もらったね。 そんな ときは なんて いうんだっけ？' },
              { emoji: '🙏', label: 'ありがとう', good: true, reply: 'どういたしまして！ また みせてね！' },
            ],
          });
          if (!r1 || !ctx.isActive()) return;
          updateWork(work.id, (w) => { if (!w.shown.includes(f.id)) w.shown.push(f.id); });

          // おかえしに おともだちの え
          const art = FRIEND_ART[f.id] || FRIEND_ART.inu;
          showcase.replaceChildren(
            el('div', { class: 'oekaki-frame oekaki-frame-show oekaki-friend-art' },
              el('div', { class: 'oekaki-art-grid' }, art.flat().map((e) => el('span', {}, e))),
            ),
            el('div', { class: 'oekaki-looker', style: { background: f.color } }, f.emoji),
          );
          sound('flip');
          await pause(400);
          const r2 = await ctx.talk({
            friend: f.id,
            say: `${word}も えを かいたよ！ みて みて！ どうかな？`,
            choices: [
              { emoji: '🤪', label: 'へんなの', good: false, hint: `${f.name}、しょんぼり しちゃった。 いっしょうけんめい かいたんだって。 なんて いったら うれしいかな？` },
              { emoji: '😍', label: 'すてき！', good: true, reply: 'ほんと？ うれしい！ ありがとう！' },
            ],
          });
          if (!r2 || !ctx.isActive()) return;
        } finally {
          st.busyTalk = false;
        }
        close();
        if (after) after();
      }

      // ---- さくひん ギャラリー ----
      function openGallery() {
        sound('tap');
        const works = loadWorks();
        let close;
        const wall = el('div', { class: 'oekaki-wall' });
        if (!works.length) {
          wall.append(el('div', { class: 'oekaki-empty', 'aria-hidden': 'true' }, '🖼️❓'));
        }
        works.slice().reverse().forEach((w) => {
          wall.append(el('button', {
            class: 'oekaki-wall-item', 'aria-label': 'さくひん',
            onclick: () => { sound('tap'); close(); openWork(w.id); },
          },
            el('span', { class: 'oekaki-pin', 'aria-hidden': 'true' }),
            frame(w.img),
            el('span', { class: 'oekaki-shown', 'aria-hidden': 'true' }, (w.shown || []).map((id) => (ctx.friend(id) || {}).emoji || '').join('')),
          ));
        });
        close = openPanel('oekaki-gallery-panel',
          el('div', { class: 'oekaki-gallery' },
            el('div', { class: 'oekaki-gallery-head' },
              el('div', { class: 'oekaki-gallery-title' }, '🖼️ さくひん ギャラリー'),
              el('button', { class: 'oekaki-btn oekaki-close', 'aria-label': 'とじる', onclick: () => { sound('tap'); close(); } }, '✖'),
            ),
            wall,
          ),
        );
        speak(works.length
          ? `${works.length}まい かざって あるよ。 みたい えを タッチしてね。`
          : 'まだ なにも ないよ。 えを かいたら、 「できた」を おしてね。');
      }

      function openWork(id) {
        const w = loadWorks().find((x) => x.id === id);
        if (!w) return openGallery();
        let close;
        close = openPanel('oekaki-done-panel',
          el('div', { class: 'oekaki-card oekaki-done-card' },
            frame(w.img, 'oekaki-frame-big'),
            el('div', { class: 'oekaki-label' }, '👀 だれに みせる？'),
            friendPicker((f) => { close(); showToFriend(f, w, () => openWork(id)); }),
            el('div', { class: 'oekaki-row' },
              el('button', { class: 'oekaki-btn oekaki-wide', 'aria-label': 'ギャラリーに もどる', onclick: () => { sound('tap'); close(); openGallery(); } }, '🖼️'),
              el('button', { class: 'oekaki-btn oekaki-wide', 'aria-label': 'おえかきに もどる', onclick: () => { sound('tap'); close(); } }, '✏️'),
            ),
          ),
        );
        speak('おともだちに みせてみる？');
      }

      // ---- かして？（かいている とちゅうに おともだちが くる） ----
      let currentBorrower = null;
      const BORROW_ORDER = ['neko', 'kitsune', 'inu', 'panda', 'pen'];

      function maybeBorrow() {
        if (st.lent || busy()) return;
        const first = st.events === 0;
        if (first ? st.strokesSinceEvent < 8 : (st.strokesSinceEvent < 20 || Date.now() - st.lastEventAt < 90000)) return;
        borrowEvent();
      }

      function flyCrayon(fromEl, toEl, hex) {
        const sr = ctx.stage.getBoundingClientRect();
        const a = fromEl.getBoundingClientRect();
        const b = toEl.getBoundingClientRect();
        const fly = el('div', { class: 'oekaki-fly' }, el('span', { class: 'oekaki-crayon' }));
        fly.style.setProperty('--c', hex);
        fly.style.left = (a.left - sr.left + a.width / 2) + 'px';
        fly.style.top = (a.top - sr.top + a.height / 2) + 'px';
        ctx.stage.append(fly);
        void fly.offsetWidth;
        fly.style.transform = `translate(calc(-50% + ${b.left + b.width / 2 - a.left - a.width / 2}px), calc(-50% + ${b.top + b.height / 2 - a.top - a.height / 2}px)) rotate(360deg)`;
        return pause(750).then(() => fly.remove());
      }

      async function borrowEvent() {
        const fid = BORROW_ORDER[st.events % BORROW_ORDER.length];
        const f = ctx.friend(fid);
        st.events++;
        st.strokesSinceEvent = 0;
        st.lastEventAt = Date.now();
        // つかった ことの ある いろ（いま もっている いろ いがい）を かりにくる
        const used = [...st.colors].filter((c) => c !== st.color);
        const pool = used.length ? used : COLORS.map((c) => c.id).filter((c) => c !== st.color);
        const want = colorById(ctx.shuffle(pool)[0]);
        const btn = colorBtns.find((b) => b.dataset.color === want.id);

        currentBorrower = fid;
        visitor.replaceChildren(
          el('span', { class: 'oekaki-visitor-face' }, f.emoji),
          el('span', { class: 'oekaki-visitor-hand' }),
          el('span', { class: 'oekaki-visitor-bubble' }, '❓'),
        );
        visitor.style.setProperty('--c', want.hex);
        visitor.classList.remove('is-leaving', 'has-crayon');
        visitor.classList.add('is-here');
        st.busyTalk = true;
        let res;
        try {
          await pause(900);
          res = await ctx.talk({
            friend: fid,
            say: `${want.crayon}、かして？`,
            choices: [
              { emoji: '🖍️', label: 'どうぞ', good: true, reply: 'わあい！ ありがとう！ ちょっと かりるね。' },
              { emoji: '🙅', label: 'だめ', good: false, hint: `${f.name}、かなしそう…。 ${want.crayon}で かきたいんだって。 なんて いったら いいかな？` },
            ],
          });
        } finally {
          st.busyTalk = false;
        }
        if (!res || !ctx.isActive()) return;

        // クレヨンが おともだちの てもとへ
        st.lent = want.id;
        btn.classList.add('oekaki-lent');
        btn.querySelector('.oekaki-lent-badge').textContent = f.emoji;
        if (st.color === want.id) {
          st.color = COLORS.find((c) => c.id !== want.id).id;
          refresh();
        }
        sound('flip');
        await flyCrayon(btn, visitor.querySelector('.oekaki-visitor-hand'), want.hex);
        visitor.classList.add('has-crayon');
        visitor.querySelector('.oekaki-visitor-bubble').textContent = '🎵';

        await pause(12000);
        // かえしに くる
        visitor.querySelector('.oekaki-visitor-bubble').textContent = '🙏';
        const thanks = 'ありがとう！ かえすね。';
        speak(thanks);
        visitor.classList.add('is-talking');
        visitor.dataset.say = thanks;
        await pause(900);
        visitor.classList.remove('has-crayon');
        sound('flip');
        await flyCrayon(visitor.querySelector('.oekaki-visitor-hand'), btn, want.hex);
        btn.classList.remove('oekaki-lent');
        btn.querySelector('.oekaki-lent-badge').textContent = '';
        st.lent = null;
        currentBorrower = null;
        btn.classList.add('oekaki-back');
        later(() => btn.classList.remove('oekaki-back'), 900);
        await pause(1500);
        visitor.classList.remove('is-talking');
        visitor.classList.add('is-leaving');
        await pause(700);
        visitor.classList.remove('is-here', 'is-leaving');
      }

      // ---- はじめ ----
      refresh();
      restoreDraft();
      speak('おえかき しよう！ ゆびで じゆうに かいてね。 できたら きらきらの ボタンを おしてね。');

      return () => {
        try { saveDraft(); } catch (e) { /* ほぞん できなくても つづける */ }
        timers.forEach((t) => clearTimeout(t));
        timers.clear();
        ro.disconnect();
        pointers.clear();
        panels.forEach((p) => p.remove());
        panels.clear();
      };
    },
  });
})();
