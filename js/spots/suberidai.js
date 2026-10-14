// すべりだい：よこから みた すべりだい。かいだんの まえに みんなで ならんで、じゅんばんに すべる（おわりなし）
// しゃかいせい：わりこみ／さきに いきたい →「じゅんばんこ」、こわがる ひよこちゃん →「さきに どうぞ」「いっしょに」、すべったら ハイタッチ
(function () {
  'use strict';

  // ばめんの ざひょう（viewBox 400×300）
  const W = 400;
  const HGT = 300;
  const GROUND = 262;
  const LADDER_X = 159;
  const RUNGS = [237, 212, 187, 162, 137, 112];
  const TOP = { x: 174, y: 106 }; // はしごを のぼりきって だいに あがる ところ
  const EXIT = { x: 350, y: GROUND };
  const WAIT_SPOT = { x: 378, y: GROUND };
  const HI5_X = 374; // ハイタッチ する ところ（ふたりは CSS で すこし はなれる）
  const SLIDE_D = 'M208 106 C258 108 262 244 322 249 L352 253';
  // すわる ところ（だい の うえ）と、そこから すべりおりる みち
  const SEAT = 5; // すべりめん の あつみ の はんぶん
  const SIT = { x: 188, y: 105 };
  const RIDE_D = `M${SIT.x} ${SIT.y + SEAT} L208 ${106} ${SLIDE_D.replace(/^M208 106 /, '')}`;
  const queueX = (i) => 126 - i * 28;

  const PRONOUN = { neko: 'わたし', kitsune: 'わたし', panda: 'ぼく', pen: 'ぼく', inu: 'ぼく' };

  const SCENE_SVG = `
<svg class="suberidai-svg" viewBox="0 0 ${W} ${HGT}" preserveAspectRatio="none" aria-hidden="true">
  <defs>
    <linearGradient id="suberidai-sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fd8ff"/><stop offset="1" stop-color="#e3f5ff"/></linearGradient>
    <linearGradient id="suberidai-slide" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff8a8a"/><stop offset="1" stop-color="#ff5e7e"/></linearGradient>
  </defs>
  <rect width="${W}" height="${HGT}" fill="url(#suberidai-sky)"/>
  <circle cx="44" cy="40" r="20" fill="#ffd54f"/>
  <circle cx="44" cy="40" r="27" fill="#ffd54f" opacity=".25"/>
  <g fill="#fff" opacity=".95">
    <ellipse cx="300" cy="40" rx="30" ry="11"/><ellipse cx="318" cy="32" rx="18" ry="12"/><ellipse cx="284" cy="34" rx="14" ry="9"/>
    <ellipse cx="120" cy="58" rx="22" ry="8"/><ellipse cx="132" cy="52" rx="13" ry="9"/>
  </g>
  <!-- き -->
  <rect x="20" y="170" width="10" height="70" rx="4" fill="#a8723f"/>
  <circle cx="25" cy="160" r="30" fill="#6cc25a"/><circle cx="8" cy="176" r="18" fill="#5bb04b"/><circle cx="44" cy="174" r="20" fill="#5bb04b"/>
  <!-- じめん -->
  <rect y="${GROUND - 4}" width="${W}" height="${HGT - GROUND + 4}" fill="#8fd16a"/>
  <rect y="${GROUND - 4}" width="${W}" height="5" fill="#7cc257"/>
  <ellipse cx="350" cy="${GROUND + 6}" rx="44" ry="7" fill="#f3d79c"/>
  <g fill="#ffffff" opacity=".6"><circle cx="70" cy="282" r="2"/><circle cx="220" cy="288" r="2"/><circle cx="300" cy="280" r="2"/></g>
  <!-- あし -->
  <rect x="200" y="106" width="6" height="${GROUND - 106}" fill="#4d8dff"/>
  <rect x="268" y="180" width="5" height="${GROUND - 180}" fill="#4d8dff"/>
  <!-- だい -->
  <rect x="140" y="104" width="70" height="9" rx="3" fill="#ffb400"/>
  <path d="M142 104 V78 M206 104 V78 M142 80 H206" stroke="#4d8dff" stroke-width="4" fill="none" stroke-linecap="round"/>
  <path d="M174 78 V52" stroke="#a8723f" stroke-width="3"/>
  <path d="M174 52 L198 59 L174 66 Z" fill="#ff6b9a"/>
  <!-- はしご -->
  <path d="M146 ${GROUND} V104 M172 ${GROUND} V104" stroke="#4d8dff" stroke-width="5" stroke-linecap="round"/>
  ${RUNGS.map((y) => `<path d="M146 ${y} H172" stroke="#3a6ea5" stroke-width="4" stroke-linecap="round"/>`).join('')}
  <!-- すべるところ -->
  <path d="${SLIDE_D}" stroke="#c2185b" stroke-width="12" fill="none" stroke-linecap="round" transform="translate(0 4)"/>
  <path d="${SLIDE_D}" stroke="url(#suberidai-slide)" stroke-width="10" fill="none" stroke-linecap="round"/>
  <path d="${SLIDE_D}" stroke="#ffd0d8" stroke-width="2.5" fill="none" stroke-linecap="round" transform="translate(0 -3)"/>
  <path class="suberidai-path" d="${RIDE_D}" stroke="none" fill="none"/>
</svg>`;

  // ---- ひゅーん（すべる おと） ----
  let ac = null;
  function whoosh(dur = 1.1) {
    if (!Core.settings.sound) return;
    try {
      if (!ac) {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        ac = new AC();
      }
      if (ac.state === 'suspended') ac.resume();
      const t0 = ac.currentTime;
      const o = ac.createOscillator();
      const g = ac.createGain();
      o.type = 'sine';
      o.frequency.setValueAtTime(1300, t0);
      o.frequency.exponentialRampToValueAtTime(280, t0 + dur);
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(0.16, t0 + 0.05);
      g.gain.setValueAtTime(0.16, t0 + dur * 0.7);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
      o.connect(g).connect(ac.destination);
      o.start(t0);
      o.stop(t0 + dur + 0.05);
    } catch (e) { /* おとが でない ときは なにもしない */ }
  }

  Core.registerSpot({
    id: 'suberidai',
    start(ctx) {
      const { el, speak, sound } = ctx;
      const alive = () => ctx.isActive();
      const timers = new Set();
      const rafs = new Set();
      const pause = (ms) => new Promise((resolve) => {
        const t = setTimeout(() => { timers.delete(t); if (alive()) resolve(); }, ms);
        timers.add(t);
      });

      // ---- がめん ----
      const scene = el('div', { class: 'suberidai-scene' });
      scene.innerHTML = SCENE_SVG;
      const pathEl = scene.querySelector('.suberidai-path');
      const fx = el('div', { class: 'suberidai-fx', 'aria-hidden': 'true' });
      scene.append(fx);
      const actionBtn = el('button', { class: 'suberidai-action', onclick: () => tapAction() });
      const waitNote = el('div', { class: 'suberidai-wait', 'aria-live': 'polite' });
      const bar = el('div', { class: 'suberidai-bar' }, actionBtn, waitNote);
      const root = el('div', { class: 'suberidai-root' }, el('div', { class: 'suberidai-scenecell' }, el('div', { class: 'suberidai-frame' }, scene)), bar);
      ctx.stage.append(root);

      // ---- こども と おともだち ----
      // からだ（Core.character）。face は すべるときに かたむける いれもの
      function makeKid(opt) {
        const body = ctx.character(opt.kind || opt.emoji, { pose: opt.pose || 'stand', mood: opt.mood || 'normal', face: opt.dir || 'right' });
        const face = el('span', { class: 'suberidai-face' }, body);
        const bubble = el('div', { class: 'suberidai-say' });
        const node = el('div', { class: 'suberidai-kid' + (opt.cls ? ' ' + opt.cls : '') }, bubble, face);
        const kid = { ...opt, node, face, body, bubble, x: opt.x ?? -30, y: opt.y ?? GROUND, sayTimer: 0 };
        place(kid, kid.x, kid.y);
        scene.append(node);
        return kid;
      }
      // ポーズ・きもち・むき を まとめて かえる
      function pose(kid, p, mood, dir) {
        clearTimeout(kid.walkTimer);
        kid.body.setPose(p);
        if (mood) kid.body.setMood(mood);
        if (dir) kid.body.face(dir);
        kid.node.classList.toggle('on-ladder', p === 'climb');
        kid.node.classList.toggle('seated', p === 'sit' || p === 'slide');
        return kid;
      }
      function place(kid, x, y) {
        kid.x = x;
        kid.y = y;
        kid.node.style.left = (x / W) * 100 + '%';
        kid.node.style.top = (y / HGT) * 100 + '%';
        kid.node.style.zIndex = String(Math.round(y) + (kid.player ? 1 : 0));
        kid.node.classList.toggle('edge-r', x > 300);
        kid.node.classList.toggle('edge-l', x < 70);
      }
      // opt.pose: うごいている あいだの ポーズ（walk）。opt.end: ついたら（stand、null なら そのまま）
      // opt.dir: ついた あとの むき（'right' など）
      function moveTo(kid, x, y, ms, opt = {}) {
        const movePose = opt.pose || 'walk';
        const endPose = opt.end === undefined ? 'stand' : opt.end;
        kid.node.classList.remove('notr', 'peek');
        kid.node.style.transitionDuration = ms + 'ms';
        const dx = x - kid.x;
        pose(kid, movePose, null, movePose === 'walk' && Math.abs(dx) > 1 ? (dx < 0 ? 'left' : 'right') : null);
        place(kid, x, y);
        if (endPose || opt.dir) {
          kid.walkTimer = setTimeout(() => {
            timers.delete(kid.walkTimer);
            if (endPose) pose(kid, endPose);
            if (opt.dir) kid.body.face(opt.dir);
          }, ms);
          timers.add(kid.walkTimer);
        }
        return pause(ms);
      }
      function kidSay(kid, text, ms = 2600) {
        kid.bubble.textContent = text;
        kid.node.classList.add('saying');
        clearTimeout(kid.sayTimer);
        kid.sayTimer = setTimeout(() => kid.node.classList.remove('saying'), ms);
        timers.add(kid.sayTimer);
      }
      function floatText(x, y, text, cls = '') {
        const n = el('div', { class: 'suberidai-float ' + cls, style: { left: (x / W) * 100 + '%', top: (y / HGT) * 100 + '%' } }, text);
        fx.append(n);
        setTimeout(() => n.remove(), 1500);
      }

      const player = makeKid({ id: 'player', emoji: ctx.player.emoji || '🧒', kind: ctx.player.kind, player: true, cls: 'is-player', name: 'きみ' });
      player.node.addEventListener('click', () => tapAction());
      const regulars = ['neko', 'panda', 'kitsune'].map((id) => {
        const f = ctx.friend(id);
        return makeKid({ id, emoji: f.emoji, name: f.name, friend: true });
      });
      let queue = [regulars[0], regulars[1], player, regulars[2]];
      queue.forEach((k, i) => place(k, queueX(i), GROUND));

      function layoutQueue() {
        queue.forEach((k, i) => {
          const x = queueX(i);
          if (Math.abs(k.x - x) < 0.5 && k.y === GROUND) return;
          const dist = Math.hypot(k.x - x, k.y - GROUND);
          // れつでは みんな まえ（はしご の ほう＝みぎ）を むく
          moveTo(k, x, GROUND, Math.max(450, dist * 9), { dir: 'right' });
        });
        updateWaitNote();
      }

      // ---- うごき ----
      // はしご：1だんずつ 足を かけて のぼる。うえに ついたら すわる
      const LEAD = 18; // いっしょに すべる とき、ひよこちゃんは すこし まえ
      const FOOT = 2; // あしの うら と 要素の した の ずれ（かげの ぶん）
      async function climb(kid, stepMs = 190, follower = null) {
        await moveTo(kid, LADDER_X, GROUND, 350, { end: null });
        if (!alive()) return false;
        const climbOpt = { pose: 'climb', end: null };
        pose(kid, 'climb', null, 'right');
        if (follower) pose(follower, 'climb', null, 'right');
        for (let i = 0; i < RUNGS.length; i++) {
          if (follower && i >= 1) moveTo(follower, LADDER_X, RUNGS[i - 1] + FOOT, stepMs, climbOpt);
          await moveTo(kid, LADDER_X, RUNGS[i] + FOOT, stepMs, climbOpt);
          if (!alive()) return false;
          if (kid.player) sound('tap');
          // 1だん のぼったら ひとやすみ
          await pause(Math.round(stepMs * 0.45));
          if (!alive()) return false;
        }
        // だい の うえへ。たちあがって あるき、すわる
        if (follower) {
          moveTo(follower, LADDER_X, RUNGS[RUNGS.length - 1] + FOOT, stepMs, climbOpt).then(() => {
            if (alive()) moveTo(follower, SIT.x + LEAD, SIT.y, 300, { end: 'sit', dir: 'right' });
          });
        }
        await moveTo(kid, TOP.x, TOP.y, 200, { end: null });
        if (!alive()) return false;
        await moveTo(kid, SIT.x, SIT.y, 220, { end: 'sit', dir: 'right' });
        return alive();
      }

      function slideAlong(kids, ms = 1300) {
        // kids: [{kid, lead}]  lead＝すこし まえを すべる（ざひょうの ながさ）
        const L = pathEl.getTotalLength();
        kids.forEach(({ kid }) => {
          kid.node.classList.add('notr', 'sliding');
          pose(kid, 'slide', 'happy', 'right'); // りょうてを あげて すべる
        });
        return new Promise((resolve) => {
          const t0 = performance.now();
          let id = 0;
          const stepFn = (now) => {
            rafs.delete(id);
            if (!alive()) return;
            const t = Math.min(1, (now - t0) / ms);
            const e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
            kids.forEach(({ kid, lead = 0 }) => {
              const s = Math.max(0, Math.min(L, e * L + lead));
              const p = pathEl.getPointAtLength(s);
              const q = pathEl.getPointAtLength(Math.min(L, s + 2));
              const ang = Math.atan2(q.y - p.y, q.x - p.x) * (180 / Math.PI);
              // すべりめんの うえに おしりを のせ、かたむきに あわせて からだを まわす。
              // からだは すこし うしろに もたれ（かたむきの はんぶん）、あしは すべりめんに そって のばす
              const rad = ang * (Math.PI / 180);
              place(kid, p.x + Math.sin(rad) * SEAT, p.y - Math.cos(rad) * SEAT);
              const lean = Math.max(-8, Math.min(34, ang * 0.5));
              kid.face.style.transform = `rotate(${lean}deg)`;
              kid.node.style.setProperty('--legs', `${Math.max(0, Math.min(45, ang - lean))}deg`);
            });
            if (t < 1) { id = requestAnimationFrame(stepFn); rafs.add(id); } else {
              kids.forEach(({ kid }) => { kid.node.classList.remove('sliding'); kid.face.style.transform = ''; kid.node.style.removeProperty('--legs'); });
              resolve();
            }
          };
          id = requestAnimationFrame(stepFn);
          rafs.add(id);
        });
      }

      // ---- じぶんの ばん の タップ ----
      let tapWaiter = null;
      let actionMode = null;
      const ACTIONS = {
        climb: { icon: '🪜', label: 'のぼる' },
        slide: { icon: '🛝', label: 'すべる' },
        high5: { icon: '🙌', label: 'ハイタッチ' },
      };
      function setAction(mode) {
        actionMode = mode;
        player.node.classList.toggle('my-turn', !!mode);
        if (!mode) {
          actionBtn.classList.remove('show');
          updateWaitNote();
          return;
        }
        const a = ACTIONS[mode];
        actionBtn.replaceChildren(el('span', { class: 'suberidai-action-icon' }, a.icon), el('span', {}, a.label));
        actionBtn.setAttribute('aria-label', a.label);
        actionBtn.classList.add('show');
        waitNote.classList.remove('show');
      }
      function waitTap(mode, prompt) {
        setAction(mode);
        speak(prompt);
        return new Promise((resolve) => {
          tapWaiter = resolve;
          // しばらく タップが なければ、やさしく もういちど
          const remind = () => {
            const t = setTimeout(() => {
              timers.delete(t);
              if (!alive() || tapWaiter !== resolve) return;
              speak(prompt);
              remind();
            }, 14000);
            timers.add(t);
          };
          remind();
        });
      }
      function tapAction() {
        if (!tapWaiter || !alive()) return;
        const r = tapWaiter;
        tapWaiter = null;
        sound('tap');
        setAction(null);
        r(true);
      }
      function updateWaitNote() {
        if (actionMode) return;
        const i = queue.indexOf(player);
        if (i < 0) { waitNote.classList.remove('show'); return; }
        // まえに なんにん いるか を えで みせる
        const mini = (k) => ctx.character(k.kind || k.emoji, { pose: 'stand', face: 'right' });
        const ahead = queue.slice(0, i).reverse().map(mini);
        waitNote.replaceChildren(el('span', { class: 'suberidai-wait-icon' }, '⏳'),
          el('span', { class: 'suberidai-wait-line' }, mini(player), el('span', { class: 'suberidai-wait-gap' }), ...ahead, el('span', {}, '🛝')));
        waitNote.classList.add('show');
      }

      // ---- ひよこちゃんとの おはなし（おともだち リストに いない ちいさい こ） ----
      function askHiyoko(say, choices) {
        return new Promise((resolve) => {
          // こわくて ないている ひよこちゃん（しょんぼり＋なみだ）
          const body = ctx.character('hiyoko', { pose: 'sad', mood: 'sad' });
          const face = el('div', { class: 'talk-face' }, body);
          const bubble = el('div', { class: 'talk-bubble' }, say);
          const row = el('div', { class: 'talk-choices' });
          const sheet = el('div', { class: 'talk-overlay suberidai-ask', role: 'dialog', 'aria-label': 'ひよこちゃんと おはなし' },
            el('div', { class: 'talk-sheet' },
              el('div', { class: 'talk-friend', style: { background: '#fff3c4', color: '#b88a00' } }, face, el('div', { class: 'talk-name' }, 'ひよこちゃん')),
              el('div', { class: 'talk-body' },
                el('div', { class: 'talk-line' }, bubble,
                  el('button', { class: 'talk-repeat', 'aria-label': 'もういちど きく', onclick: () => speak(bubble.textContent) }, '🔊')),
                row)));
          let done = false;
          const btns = choices.map((c) => el('button', {
            class: 'talk-choice',
            onclick: async (e) => {
              if (done || !alive()) return;
              const b = e.currentTarget;
              if (c.good) {
                done = true;
                btns.forEach((x) => (x.disabled = true));
                b.classList.add('chosen');
                sound('correct');
                body.setPose('cheer').setMood('happy');
                face.classList.add('happy');
                await speak(c.label);
                if (!alive()) return;
                bubble.textContent = c.reply;
                await speak(c.reply);
                await pause(400);
                sheet.remove();
                resolve(c);
              } else {
                sound('wrong');
                b.disabled = true;
                b.classList.add('dimmed');
                body.setPose('sad').setMood('sad');
                bubble.textContent = c.hint;
                await speak(c.hint);
              }
            },
          }, el('span', { class: 'talk-choice-emoji' }, c.emoji), el('span', { class: 'talk-choice-label' }, c.label)));
          row.append(...btns);
          root.append(sheet);
          speak(`${say}  ${choices.map((c) => c.label).join('？ ')}？`);
        });
      }

      // ---- できごと ----
      let slides = 0;
      let pending = null;
      const EVENT_CYCLE = ['cut', 'hiyoko', 'wait'];
      let eventNo = 0;
      let bottomWaiter = null;
      const highFived = new Set();

      // しばらく ポーズを かえて、あとで もとに もどす
      function posePulse(kid, p, mood, ms = 1500, back = 'stand') {
        pose(kid, p, mood);
        kid.walkTimer = setTimeout(() => {
          timers.delete(kid.walkTimer);
          if (alive()) pose(kid, back, 'normal');
        }, ms);
        timers.add(kid.walkTimer);
      }

      // れつで まっている こは、ときどき まえの こ（すべりだい の ほう）を のぞきこむ
      function peekLoop() {
        const t = setTimeout(() => {
          timers.delete(t);
          if (!alive()) return;
          const idle = queue.filter((k, i) => i > 0 && k.y === GROUND && Math.abs(k.x - queueX(i)) < 0.5
            && k.body.classList.contains('pose-stand') && !k.node.classList.contains('peek') && k !== player);
          if (idle.length) {
            const k = ctx.shuffle(idle)[0];
            k.body.face('right');
            k.node.classList.add('peek');
            const u = setTimeout(() => { timers.delete(u); k.node.classList.remove('peek'); }, 1500);
            timers.add(u);
          }
          peekLoop();
        }, 1800 + Math.random() * 1600);
        timers.add(t);
      }

      async function eventCut() {
        const pi = queue.indexOf(player);
        const pen = makeKid({ id: 'pen', emoji: ctx.friend('pen').emoji, kind: 'pen', name: ctx.friend('pen').name, friend: true, guest: true, x: -30 });
        await moveTo(pen, queueX(pi) + 10, GROUND, 1300, { dir: 'right' });
        if (!alive()) return;
        queue.splice(pi, 0, pen);
        layoutQueue();
        await pause(500);
        if (!alive()) return;
        // ぺんぎんくんは りょうてを まえに「おねがい」。きみは びっくり
        pose(pen, 'hold', 'normal', 'left');
        pose(player, 'stand', 'wow');
        kidSay(pen, 'さきに いれて！', 2000);
        await pause(700);
        if (!alive()) return;
        const c = await ctx.talk({
          friend: 'pen', say: 'ねえ、さきに いれて！ はやく すべりたいんだ。',
          choices: [
            { emoji: '🙅', label: 'だめ！ あっち いって', good: false, hint: 'ぺんぎんくん、しょんぼり…。じゅんばんを やさしく おしえて あげよう。' },
            { emoji: '🔁', label: 'じゅんばんこ だよ。うしろに ならぼう', good: true, reply: 'そっか！ じゅんばんこ だね。うしろに ならぶね！' },
          ],
        });
        if (!c || !alive()) return;
        pose(player, 'stand', 'normal');
        pose(pen, 'wave', 'happy');
        kidSay(pen, 'うしろに ならぶね！');
        await pause(800);
        if (!alive()) return;
        queue.splice(queue.indexOf(pen), 1);
        queue.push(pen);
        pen.body.setMood('normal');
        layoutQueue();
        await pause(1200);
      }

      async function eventWait() {
        const pi = queue.indexOf(player);
        const front = queue[pi - 1];
        // まちきれなくて まえを のぞきこむ
        player.body.face('right');
        player.node.classList.add('peek');
        kidSay(player, '💭 はやく すべりたいな…', 3200);
        await speak('はやく すべりたいね。どう する？');
        if (!alive()) return;
        // まえの こが ふりかえる
        pose(front, 'stand', 'normal', 'left');
        const c = await ctx.talk({
          friend: front.id, say: `つぎは ${PRONOUN[front.id] || 'ぼく'}の ばん だよ。わくわく するね！`,
          choices: [
            { emoji: '🏃', label: 'さきに いかせて！', good: false, hint: `${front.name}も ずっと まってたんだって。どうしたら いいかな？` },
            { emoji: '🔁', label: 'じゅんばんこ だね。うしろで まってるね', good: true, reply: 'ありがとう！ じゅんばんこ だと みんな たのしいね！' },
          ],
        });
        player.node.classList.remove('peek');
        if (!c || !alive()) return;
        posePulse(player, 'wave', 'happy', 1500);
        posePulse(front, 'cheer', 'happy', 1500);
        kidSay(front, 'ありがとう！');
        await pause(1500);
        if (!alive()) return;
        front.body.face('right');
      }

      // ひよこちゃん：じぶんの ばん に なったとき
      async function eventHiyoko() {
        const chick = makeKid({ id: 'hiyoko', emoji: '🐥', kind: 'hiyoko', name: 'ひよこちゃん', cls: 'is-chick', x: LADDER_X + 2, y: GROUND, pose: 'sad', mood: 'sad', dir: 'left' });
        chick.node.classList.add('crying');
        kidSay(chick, 'えーん、こわいよう…', 3000);
        await pause(900);
        if (!alive()) return null;
        const c = await askHiyoko('すべりだい、たかくて こわいよう…。えーん。', [
          { emoji: '🙇', label: 'さきに どうぞ', good: true, reply: 'ありがとう！ がんばって みる！' },
          { emoji: '🤝', label: 'いっしょに すべろう', good: true, reply: 'うん！ いっしょなら こわくない！' },
          { emoji: '😤', label: 'はやく して', good: false, hint: 'ひよこちゃん、こわくて ないてるよ。どうしたら いいかな？' },
        ]);
        if (!c || !alive()) return null;
        chick.node.classList.remove('crying');
        pose(chick, 'cheer', 'happy');
        floatText(chick.x, chick.y - 40, '💖', 'heart');
        await pause(700);
        if (!alive()) return null;
        if (c.label === 'さきに どうぞ') {
          posePulse(player, 'wave', 'happy', 2200);
          kidSay(player, 'がんばれー！');
          pose(chick, 'stand', 'normal', 'right');
          if (!(await climb(chick, 320))) return null;
          await pause(600);
          if (!alive()) return null;
          kidSay(chick, 'えいっ！');
          whoosh(1.4);
          floatText(318, 72, 'ひゅーん！', 'whoosh');
          await slideAlong([{ kid: chick }], 1600);
          if (!alive()) return null;
          await landAt(chick, EXIT.x - 12);
          if (!alive()) return null;
          pose(chick, 'cheer', 'happy');
          sound('correct');
          kidSay(chick, 'こわく なかった！ ありがとう！', 3000);
          await speak('こわく なかった！ ありがとう！');
          if (!alive()) return null;
          leave(chick);
          return null;
        }
        // いっしょに すべる：きみの となりで まつ
        pose(chick, 'stand', 'happy', 'left');
        return chick;
      }

      // すべりおりたら、たちあがって じめんに おりる
      async function landAt(kid, x) {
        pose(kid, 'stand', 'happy');
        await moveTo(kid, x, GROUND, 260, { pose: 'stand' });
        return alive();
      }

      function leave(kid) {
        pose(kid, 'wave', 'happy', 'left');
        kidSay(kid, 'またね！', 1600);
        const t = setTimeout(() => {
          timers.delete(t);
          if (!alive()) return;
          kid.body.setMood('normal');
          moveTo(kid, W + 40, GROUND, 2200).then(() => kid.node.remove());
        }, 700);
        timers.add(t);
      }

      function backToLine(kid) {
        if (kid.guest) { leave(kid); return; }
        kid.body.setMood('normal');
        queue.push(kid);
        layoutQueue();
      }

      // ---- じゅんばん ----
      async function friendTurn(kid) {
        // わりこみ・さきに いきたい は、ともだちが のぼる まえに
        if (pending === 'cut' && queue.indexOf(player) >= 2) { pending = null; await eventCut(); if (!alive()) return; }
        else if (pending === 'wait' && queue.indexOf(player) >= 2) { pending = null; await eventWait(); if (!alive()) return; }
        if (queue[0] !== kid) return;
        queue.shift();
        layoutQueue();
        if (!(await climb(kid))) return;
        await pause(250);
        if (!alive()) return;
        if (Math.random() < 0.5) kidSay(kid, ctx.shuffle(['わーい！', 'いくよー！', 'ひゅーん！'])[0], 1500);
        whoosh(1.1);
        await slideAlong([{ kid }], 1300);
        if (!alive()) return;
        if (!(await landAt(kid, EXIT.x))) return;
        await pause(250);
        if (!alive()) return;
        if (queue[0] === player) {
          // つぎは きみの ばん → したで まっててくれる（すべりだい の ほうを みる）
          bottomWaiter = kid;
          moveTo(kid, WAIT_SPOT.x, GROUND, 400, { dir: 'left' });
          kidSay(kid, 'したで まってるね！', 2000);
        } else {
          backToLine(kid);
        }
      }

      async function playerTurn() {
        let chick = null;
        if (pending === 'hiyoko') { pending = null; chick = await eventHiyoko(); if (!alive()) return; }
        await waitTap('climb', 'じゅんばんが きたよ！ タップして かいだんを のぼろう！');
        if (!alive()) return;
        queue.shift();
        layoutQueue();
        if (chick) moveTo(chick, LADDER_X - 6, GROUND, 200, { dir: 'right' });
        if (!(await climb(player, 230, chick))) return;
        await waitTap('slide', 'タップで すべろう！');
        if (!alive()) return;
        whoosh(1.2);
        speak('ひゅーん！');
        floatText(318, 72, 'ひゅーん！', 'whoosh');
        const riders = [{ kid: player }];
        if (chick) riders.push({ kid: chick, lead: LEAD });
        await slideAlong(riders, 1350);
        if (!alive()) return;
        slides++;
        sound('fanfare');
        for (let i = 0; i < 5; i++) floatText(330 + Math.random() * 40, 230 - Math.random() * 30, ctx.shuffle(['✨', '⭐', '🎵'])[0], 'spark');
        if (chick) {
          landAt(chick, EXIT.x + 16);
          if (!(await landAt(player, EXIT.x - 6))) return;
          pose(chick, 'cheer', 'happy', 'left');
          posePulse(player, 'cheer', 'happy', 2400);
          kidSay(chick, 'いっしょだと たのしいね！ ありがとう！', 3000);
          await speak('いっしょだと たのしいね！ ありがとう！');
          if (!alive()) return;
          leave(chick);
          pose(player, 'stand', 'normal');
        } else {
          if (!(await landAt(player, EXIT.x - 6))) return;
        }
        // ハイタッチ：むかいあって、てを あげて まつ
        const friend = bottomWaiter;
        bottomWaiter = null;
        if (friend) {
          friend.node.classList.add('hi5-r');
          player.node.classList.add('hi5-l');
          moveTo(friend, HI5_X, GROUND, 350, { end: 'wave', dir: 'left' });
          await moveTo(player, HI5_X, GROUND, 300, { dir: 'right' });
          if (!alive()) return;
          kidSay(friend, 'たのしかったね！ ハイタッチ！', 3000);
          await waitTap('high5', 'たのしかったね！ ハイタッチ しよう！');
          if (!alive()) return;
          // パチン！ ふたりの てが あう
          pose(player, 'wave', 'happy');
          pose(friend, 'wave', 'happy');
          player.node.classList.add('clap');
          friend.node.classList.add('clap');
          sound('correct');
          await pause(260);
          if (!alive()) return;
          floatText(HI5_X, GROUND - 46, '🙌', 'clap');
          floatText(HI5_X, GROUND - 70, 'パチン！', 'pachin');
          await pause(500);
          if (!alive()) return;
          player.node.classList.remove('clap');
          friend.node.classList.remove('clap');
          pose(player, 'cheer', 'happy');
          pose(friend, 'cheer', 'happy');
          kidSay(player, 'たのしかったね！', 1800);
          if (friend.friend && !highFived.has(friend.id)) {
            highFived.add(friend.id);
            ctx.addHeart(friend.id, 1);
          }
          await pause(1000);
          if (!alive()) return;
          player.node.classList.remove('hi5-l');
          friend.node.classList.remove('hi5-r');
        }
        // また うしろに ならぶ
        backToLine(player);
        if (friend) {
          await pause(250);
          if (!alive()) return;
          backToLine(friend);
        }
        if (slides % 2 === 1) pending = EVENT_CYCLE[eventNo++ % EVENT_CYCLE.length];
      }

      async function loop() {
        await pause(1200);
        while (alive()) {
          const k = queue[0];
          if (!k) { await pause(400); continue; }
          if (k === player) await playerTurn();
          else await friendTurn(k);
          if (!alive()) return;
          await pause(300);
        }
      }

      ctx.stage.__suberidai = {
        setPending: (k) => { pending = k; },
        state: () => ({ slides, pending, mode: actionMode, queue: queue.map((k) => k.id) }),
      };

      updateWaitNote();
      peekLoop();
      speak('すべりだい だよ！ じゅんばんに ならんで すべろう。');
      loop();

      return () => {
        timers.forEach((t) => clearTimeout(t));
        timers.clear();
        rafs.forEach((r) => cancelAnimationFrame(r));
        rafs.clear();
        tapWaiter = null;
      };
    },
  });
})();
