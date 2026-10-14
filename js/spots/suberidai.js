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
  const TOP = { x: 186, y: 106 };
  const EXIT = { x: 350, y: GROUND };
  const WAIT_SPOT = { x: 378, y: GROUND };
  const SLIDE_D = 'M208 106 C258 108 262 244 322 249 L352 253';
  const queueX = (i) => 120 - i * 26;

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
  <path class="suberidai-path" d="${SLIDE_D}" stroke="#ffd0d8" stroke-width="2.5" fill="none" stroke-linecap="round" transform="translate(0 -3)"/>
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
      function makeKid(opt) {
        const face = el('span', { class: 'suberidai-face' }, opt.emoji);
        const bubble = el('div', { class: 'suberidai-say' });
        const node = el('div', { class: 'suberidai-kid' + (opt.cls ? ' ' + opt.cls : '') }, bubble, face);
        const kid = { ...opt, node, face, bubble, x: opt.x ?? -30, y: opt.y ?? GROUND, sayTimer: 0 };
        place(kid, kid.x, kid.y);
        scene.append(node);
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
      function moveTo(kid, x, y, ms) {
        kid.node.classList.remove('notr');
        kid.node.style.transitionDuration = ms + 'ms';
        kid.node.classList.add('walk');
        place(kid, x, y);
        clearTimeout(kid.walkTimer);
        kid.walkTimer = setTimeout(() => kid.node.classList.remove('walk'), ms);
        timers.add(kid.walkTimer);
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

      const player = makeKid({ id: 'player', emoji: ctx.player.emoji || '🧒', player: true, cls: 'is-player', name: 'きみ' });
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
          moveTo(k, x, GROUND, Math.max(450, dist * 9));
        });
        updateWaitNote();
      }

      // ---- うごき ----
      async function climb(kid, stepMs = 190, follower = null) {
        await moveTo(kid, LADDER_X, GROUND, 350);
        if (!alive()) return false;
        for (let i = 0; i < RUNGS.length; i++) {
          if (follower && i >= 1) moveTo(follower, LADDER_X, RUNGS[i - 1] + 6, stepMs);
          await moveTo(kid, LADDER_X, RUNGS[i] - 4, stepMs);
          if (!alive()) return false;
          if (kid.player) sound('tap');
        }
        if (follower) moveTo(follower, LADDER_X + 8, TOP.y, 300);
        await moveTo(kid, TOP.x, TOP.y, 300);
        return alive();
      }

      function slideAlong(kids, ms = 1300) {
        // kids: [{kid, lead}]  lead＝すこし まえを すべる
        const L = pathEl.getTotalLength();
        kids.forEach(({ kid }) => { kid.node.classList.add('notr', 'sliding'); });
        return new Promise((resolve) => {
          const t0 = performance.now();
          let id = 0;
          const stepFn = (now) => {
            rafs.delete(id);
            if (!alive()) return;
            const t = Math.min(1, (now - t0) / ms);
            const e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
            kids.forEach(({ kid, lead = 0 }) => {
              const s = Math.max(0, Math.min(L, (e + lead) * L));
              const p = pathEl.getPointAtLength(s);
              const q = pathEl.getPointAtLength(Math.min(L, s + 2));
              const ang = Math.atan2(q.y - p.y, q.x - p.x) * (180 / Math.PI);
              place(kid, p.x, p.y - 1);
              kid.face.style.transform = `rotate(${ang * 0.45}deg)`;
            });
            if (t < 1) { id = requestAnimationFrame(stepFn); rafs.add(id); } else {
              kids.forEach(({ kid }) => { kid.node.classList.remove('sliding'); kid.face.style.transform = ''; });
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
        const ahead = queue.slice(0, i).reverse().map((k) => k.emoji).join('');
        waitNote.replaceChildren(el('span', { class: 'suberidai-wait-icon' }, '⏳'), el('span', { class: 'suberidai-wait-line' }, `${player.emoji} ${ahead} 🛝`));
        waitNote.classList.add('show');
      }

      // ---- ひよこちゃんとの おはなし（おともだち リストに いない ちいさい こ） ----
      function askHiyoko(say, choices) {
        return new Promise((resolve) => {
          const face = el('div', { class: 'talk-face' }, '🐥');
          const mood = el('div', { class: 'talk-mood' }, '😢');
          const bubble = el('div', { class: 'talk-bubble' }, say);
          const row = el('div', { class: 'talk-choices' });
          const sheet = el('div', { class: 'talk-overlay suberidai-ask', role: 'dialog', 'aria-label': 'ひよこちゃんと おはなし' },
            el('div', { class: 'talk-sheet' },
              el('div', { class: 'talk-friend', style: { background: '#f2b600' } }, face, mood, el('div', { class: 'talk-name' }, 'ひよこちゃん')),
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
                mood.textContent = '😊';
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

      async function eventCut() {
        const pi = queue.indexOf(player);
        const pen = makeKid({ id: 'pen', emoji: ctx.friend('pen').emoji, name: ctx.friend('pen').name, friend: true, guest: true, x: -30 });
        await moveTo(pen, queueX(pi) + 10, GROUND, 1300);
        if (!alive()) return;
        queue.splice(pi, 0, pen);
        layoutQueue();
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
        queue.splice(queue.indexOf(pen), 1);
        queue.push(pen);
        layoutQueue();
        kidSay(pen, 'うしろに ならぶね！');
        await pause(1200);
      }

      async function eventWait() {
        const pi = queue.indexOf(player);
        const front = queue[pi - 1];
        kidSay(player, '💭 はやく すべりたいな…', 3200);
        await speak('はやく すべりたいね。どう する？');
        if (!alive()) return;
        const c = await ctx.talk({
          friend: front.id, say: `つぎは ${PRONOUN[front.id] || 'ぼく'}の ばん だよ。わくわく するね！`,
          choices: [
            { emoji: '🏃', label: 'さきに いかせて！', good: false, hint: `${front.name}も ずっと まってたんだって。どうしたら いいかな？` },
            { emoji: '🔁', label: 'じゅんばんこ だね。うしろで まってるね', good: true, reply: 'ありがとう！ じゅんばんこ だと みんな たのしいね！' },
          ],
        });
        if (!c || !alive()) return;
        kidSay(front, 'ありがとう！');
      }

      // ひよこちゃん：じぶんの ばん に なったとき
      async function eventHiyoko() {
        const chick = makeKid({ id: 'hiyoko', emoji: '🐥', name: 'ひよこちゃん', cls: 'is-chick', x: LADDER_X + 2, y: GROUND });
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
        floatText(chick.x, chick.y - 40, '💖', 'heart');
        if (c.label === 'さきに どうぞ') {
          kidSay(player, 'がんばれー！');
          if (!(await climb(chick, 320))) return null;
          await pause(600);
          if (!alive()) return null;
          kidSay(chick, 'えいっ！');
          whoosh(1.4);
          floatText(310, 120, 'ひゅーん！', 'whoosh');
          await slideAlong([{ kid: chick }], 1600);
          if (!alive()) return null;
          await moveTo(chick, EXIT.x - 12, GROUND, 250);
          sound('correct');
          kidSay(chick, 'こわく なかった！ ありがとう！', 3000);
          await speak('こわく なかった！ ありがとう！');
          if (!alive()) return null;
          leave(chick);
          return null;
        }
        return chick; // いっしょに すべる
      }

      function leave(kid) {
        kidSay(kid, 'またね！', 1600);
        moveTo(kid, W + 40, GROUND, 2200).then(() => kid.node.remove());
      }

      function backToLine(kid) {
        if (kid.guest) { leave(kid); return; }
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
        await moveTo(kid, EXIT.x, GROUND, 220);
        if (queue[0] === player) {
          // つぎは きみの ばん → したで まっててくれる
          bottomWaiter = kid;
          moveTo(kid, WAIT_SPOT.x, GROUND, 400);
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
        if (chick) moveTo(chick, LADDER_X - 6, GROUND, 200);
        if (!(await climb(player, 230, chick))) return;
        await waitTap('slide', 'タップで すべろう！');
        if (!alive()) return;
        whoosh(1.2);
        speak('ひゅーん！');
        floatText(310, 120, 'ひゅーん！', 'whoosh');
        const riders = [{ kid: player }];
        if (chick) riders.push({ kid: chick, lead: 0.05 });
        await slideAlong(riders, 1350);
        if (!alive()) return;
        slides++;
        sound('fanfare');
        for (let i = 0; i < 5; i++) floatText(330 + Math.random() * 40, 230 - Math.random() * 30, ctx.shuffle(['✨', '⭐', '🎵'])[0], 'spark');
        if (chick) {
          moveTo(chick, EXIT.x + 14, GROUND, 250);
          await moveTo(player, EXIT.x - 6, GROUND, 250);
          if (!alive()) return;
          kidSay(chick, 'いっしょだと たのしいね！ ありがとう！', 3000);
          await speak('いっしょだと たのしいね！ ありがとう！');
          if (!alive()) return;
          leave(chick);
        } else {
          await moveTo(player, EXIT.x - 6, GROUND, 250);
          if (!alive()) return;
        }
        // ハイタッチ
        const friend = bottomWaiter;
        bottomWaiter = null;
        if (friend) {
          moveTo(friend, EXIT.x + 26, GROUND, 300);
          kidSay(friend, 'たのしかったね！ ハイタッチ！', 3000);
          friend.node.classList.add('hands-up');
          await waitTap('high5', 'たのしかったね！ ハイタッチ しよう！');
          if (!alive()) return;
          friend.node.classList.remove('hands-up');
          sound('correct');
          floatText(EXIT.x + 8, GROUND - 46, '🙌', 'clap');
          floatText(EXIT.x + 8, GROUND - 70, 'パチン！', 'pachin');
          kidSay(player, 'たのしかったね！', 1800);
          if (friend.friend && !highFived.has(friend.id)) {
            highFived.add(friend.id);
            ctx.addHeart(friend.id, 1);
          }
          await pause(1000);
          if (!alive()) return;
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
