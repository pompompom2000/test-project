// ようちえん：キャラをタップで歩かせて、あそびばや おともだちのところへ行く
(function () {
  'use strict';

  const { el, speak, stopSpeaking, sound } = Core;

  // ---- 保存（ブラウザに保存できないときは、その回だけ覚えておく） ----
  const PREFIX = 'minna-asobo:';
  const memory = {};
  const store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(PREFIX + key);
        if (raw != null) return JSON.parse(raw);
      } catch (e) { /* 保存できない環境 */ }
      return key in memory ? memory[key] : fallback;
    },
    set(key, value) {
      memory[key] = value;
      try { localStorage.setItem(PREFIX + key, JSON.stringify(value)); } catch (e) { /* 保存できない環境 */ }
    },
  };

  // ---- おともだち ----
  const FRIENDS = [
    { id: 'inu', name: 'いぬくん', emoji: '🐶', color: '#c98b4f' },
    { id: 'neko', name: 'ねこちゃん', emoji: '🐱', color: '#f2a541' },
    { id: 'panda', name: 'ぱんだくん', emoji: '🐼', color: '#6b6f7a' },
    { id: 'kitsune', name: 'きつねちゃん', emoji: '🦊', color: '#e8743b' },
    { id: 'pen', name: 'ぺんぎんくん', emoji: '🐧', color: '#3a6ea5' },
  ];
  const friendById = (id) => FRIENDS.find((f) => f.id === id);

  const AVATARS = ['👧', '👦', '🧒'];

  // なかよし度（ハートの数）で変わる呼び名
  function friendshipLabel(n) {
    if (n >= 15) return 'しんゆう';
    if (n >= 8) return 'だいなかよし';
    if (n >= 3) return 'なかよし';
    return 'はじめまして';
  }

  // ---- 地図（位置は地図の幅・高さに対する %） ----
  const SPOT_LAYOUT = {
    oekaki: { x: 13, y: 20, name: 'おえかき', emoji: '🎨' },
    tsumiki: { x: 37, y: 20, name: 'つみき', emoji: '🧱' },
    mamagoto: { x: 63, y: 20, name: 'おままごと', emoji: '🍳' },
    yuugi: { x: 87, y: 20, name: 'ゆうぎしつ', emoji: '🎪' },
    sunaba: { x: 24, y: 74, name: 'すなば', emoji: '🏖️' },
    suberidai: { x: 74, y: 72, name: 'すべりだい', emoji: '🛝' },
    sunaba3d: { x: 50, y: 84, name: 'りったい すなば', emoji: '🏝️' },
  };
  const FRIEND_HOME = {
    inu: { x: 36, y: 84 },
    neko: { x: 22, y: 36 },
    panda: { x: 46, y: 36 },
    kitsune: { x: 72, y: 36 },
    pen: { x: 86, y: 84 },
  };
  const START = { x: 50, y: 58 };
  const DECOR = [
    { e: '🌳', x: 5, y: 58 }, { e: '🌳', x: 95, y: 58 }, { e: '🌷', x: 4, y: 80 },
    { e: '🌼', x: 96, y: 94 }, { e: '🌷', x: 63, y: 93 }, { e: '🦋', x: 10, y: 92 },
    { e: '🪟', x: 25, y: 4 }, { e: '🪟', x: 75, y: 4 }, { e: '🕰️', x: 50, y: 4 },
  ];

  // ---- あそびばの登録 ----
  const spots = {};
  function registerSpot(spot) {
    spots[spot.id] = spot;
  }

  // ---- 状態 ----
  const state = {
    avatar: store.get('avatar', null),
    hearts: store.get('hearts', {}),
    pos: { ...START },
    greeted: false,
  };
  const heartsOf = (id) => state.hearts[id] || 0;

  // ---- 重ねて出す画面（会話・なかよしノート） ----
  const overlays = new Set();
  function openOverlay(node) {
    document.body.append(node);
    overlays.add(node);
    return () => { node.remove(); overlays.delete(node); };
  }
  function closeAllOverlays() {
    for (const o of overlays) {
      o.remove();
      if (o._cancel) o._cancel();
    }
    overlays.clear();
  }

  function floatHeart(n = 1) {
    const h = el('div', { class: 'float-heart', 'aria-hidden': 'true' }, n > 1 ? `💖×${n}` : '💖');
    document.body.append(h);
    setTimeout(() => h.remove(), 1400);
  }

  function addHeart(friendId, n = 1) {
    if (!friendById(friendId)) return;
    state.hearts[friendId] = heartsOf(friendId) + n;
    store.set('hearts', state.hearts);
    floatHeart(n);
    document.querySelectorAll(`[data-hearts-of="${friendId}"]`).forEach((b) => { b.textContent = `💖${heartsOf(friendId)}`; });
  }

  // おともだちとの会話。よい えらびかたを するまで続き、えらんだものを返す
  // opts: { friend, say, mood?, choices: [{ emoji, label, good, reply?, hint?, hearts? }] }
  function talk(opts) {
    const friend = friendById(opts.friend);
    return new Promise((resolve) => {
      const startMood = moodFromEmoji(opts.mood);
      const body = Core.character(friend.id, { mood: startMood, pose: startMood === 'sad' ? 'sad' : 'stand' });
      const face = el('div', { class: 'talk-face' }, body);
      const mood = { set textContent(v) { const m = moodFromEmoji(v); body.setMood(m); body.setPose(m === 'happy' ? 'cheer' : m === 'sad' ? 'sad' : 'stand'); } };
      const bubble = el('div', { class: 'talk-bubble' }, opts.say);
      const choiceRow = el('div', { class: 'talk-choices' });
      const sheet = el('div', { class: 'talk-overlay', role: 'dialog', 'aria-label': `${friend.name}と おはなし` },
        el('div', { class: 'talk-sheet' },
          el('div', { class: 'talk-friend', style: { background: `color-mix(in srgb, ${friend.color} 30%, #fff)`, color: friend.color } }, face,
            el('div', { class: 'talk-name' }, friend.name)),
          el('div', { class: 'talk-body' },
            el('div', { class: 'talk-line' }, bubble,
              el('button', { class: 'talk-repeat', 'aria-label': 'もういちど きく', onclick: () => speak(bubble.textContent) }, '🔊')),
            choiceRow),
        ),
      );
      let done = false;
      const close = openOverlay(sheet);
      sheet._cancel = () => { if (!done) { done = true; resolve(null); } };

      const buttons = opts.choices.map((c) =>
        el('button', {
          class: 'talk-choice',
          onclick: async (e) => {
            if (done) return;
            const btn = e.currentTarget;
            if (c.good) {
              done = true;
              buttons.forEach((b) => (b.disabled = true));
              btn.classList.add('chosen');
              sound('correct');
              mood.textContent = '😊';
              face.classList.add('happy');
              await speak(c.label);
              const reply = c.reply || 'ありがとう！';
              bubble.textContent = reply;
              addHeart(friend.id, c.hearts || 1);
              await speak(reply);
              await Core.wait(500);
              close();
              resolve(c);
            } else {
              sound('wrong');
              btn.disabled = true;
              btn.classList.add('dimmed');
              mood.textContent = '😢';
              const hint = c.hint || `${friend.name}、かなしそう…。なんて いったら いいかな？`;
              bubble.textContent = hint;
              await speak(hint);
            }
          },
        },
          el('span', { class: 'talk-choice-emoji' }, c.emoji),
          el('span', { class: 'talk-choice-label' }, c.label),
        ),
      );
      choiceRow.append(...buttons);
      speak(`${opts.say}  ${opts.choices.map((c) => c.label).join('？ ')}？`);
    });
  }

  // 会話で使う絵文字の きもちを、キャラの表情に
  function moodFromEmoji(e) {
    if (!e) return 'normal';
    if (/[😢😣😭😞😟🥺😥]/u.test(e)) return 'sad';
    if (/[😊😄😆🥰😍🤗]/u.test(e)) return 'happy';
    if (/[😮😲😯]/u.test(e)) return 'wow';
    return 'normal';
  }

  // ---- ちずの上で おともだちを タップしたときの おはなし ----
  const MAP_TALKS = [
    (f) => ({
      friend: f.id, say: 'おはよう！',
      choices: [
        { emoji: '👋', label: 'おはよう', good: true, reply: 'きょうも いっしょに あそぼうね！' },
        { emoji: '🙈', label: 'しらんぷり', good: false, hint: `${f.name}、さみしそう…。なんて いったら いいかな？` },
      ],
    }),
    (f) => ({
      friend: f.id, mood: '😢', say: 'ころんじゃった…。いたいよう。',
      choices: [
        { emoji: '🏃', label: 'いっちゃう', good: false, hint: `${f.name}、ないてるよ。どうしたら いいかな？` },
        { emoji: '🩹', label: 'だいじょうぶ？', good: true, reply: 'ありがとう！ げんき でた！' },
      ],
    }),
    (f) => ({
      friend: f.id, say: 'ボールで あそんでるんだ。⚽',
      choices: [
        { emoji: '✋', label: 'とっちゃう', good: false, hint: 'とられたら かなしいね。なんて いえば いいかな？' },
        { emoji: '🙋', label: 'いれて', good: true, reply: 'いいよ！ いっしょに あそぼ！' },
      ],
    }),
    (f) => ({
      friend: f.id, mood: '😣', say: 'あっ、ぶつかっちゃったね。',
      choices: [
        { emoji: '🙇', label: 'ごめんね', good: true, reply: 'いいよ！ だいじょうぶ！' },
        { emoji: '😝', label: 'しらない', good: false, hint: `${f.name}、いたかったみたい。なんて いったら いいかな？` },
      ],
    }),
    (f) => ({
      friend: f.id, say: 'みて みて！ おはな みつけたよ。🌷 あげる！',
      choices: [
        { emoji: '🙏', label: 'ありがとう', good: true, reply: 'どういたしまして！' },
        { emoji: '😶', label: 'だまって もらう', good: false, hint: 'もらった ときは、なんて いうんだっけ？' },
      ],
    }),
  ];

  // ---- 画面づくり ----
  let mapToken = 0; // 歩いている途中で ほかの場所を タップしたら、前の行き先は取り消す

  function settingsButtons() {
    const toggle = (key, on, off, label) =>
      el('button', {
        class: 'icon-btn', 'aria-label': label,
        onclick: (e) => {
          Core.settings[key] = !Core.settings[key];
          e.currentTarget.textContent = Core.settings[key] ? on : off;
          if (key === 'voice' && !Core.settings.voice) stopSpeaking();
        },
      }, Core.settings[key] ? on : off);
    return [toggle('sound', '🔔', '🔕', 'こうかおん'), toggle('voice', '🗣️', '🤐', 'よみあげ')];
  }

  function enter() {
    mapToken++;
    closeAllOverlays();
    if (!state.avatar) return avatarScreen();
    worldScreen();
  }

  function avatarScreen() {
    App.show(
      el('section', { class: 'screen' },
        el('button', { class: 'back-btn', onclick: () => App.titleScreen(), 'aria-label': 'もどる' }, '⬅'),
        el('h2', {}, 'きみは どの こ？'),
        el('div', { class: 'avatar-row' },
          AVATARS.map((a) => el('button', {
            class: 'avatar-btn',
            'aria-label': a,
            onclick: (e) => {
              sound('start');
              e.currentTarget.firstChild.setPose('cheer').setMood('happy');
              state.avatar = a;
              store.set('avatar', a);
              setTimeout(worldScreen, 500);
            },
          }, Core.character(a, { pose: 'wave' }))),
        ),
      ),
    );
    speak('きみは どの こ？');
  }

  function worldScreen() {
    const map = el('div', { class: 'world-map' });
    const me = Core.character(state.avatar);
    const avatar = el('div', { class: 'world-avatar', 'aria-hidden': 'true' }, me);

    const place = (node, p) => {
      node.style.left = p.x + '%';
      node.style.top = p.y + '%';
      node.style.zIndex = String(10 + Math.round(p.y));
    };

    // 床と庭
    map.append(
      el('div', { class: 'world-indoor' }),
      el('div', { class: 'world-yard' }),
      el('div', { class: 'world-sand' }),
      el('div', { class: 'world-door', 'aria-hidden': 'true' }),
    );
    DECOR.forEach((d) => {
      const n = el('div', { class: 'world-decor', 'aria-hidden': 'true' }, d.e);
      place(n, d);
      map.append(n);
    });

    function walkTo(target, then) {
      const token = ++mapToken;
      const rect = map.getBoundingClientRect();
      const dx = ((target.x - state.pos.x) / 100) * rect.width;
      const dy = ((target.y - state.pos.y) / 100) * rect.height;
      const dist = Math.hypot(dx, dy);
      const ms = Math.max(150, Math.min(1800, dist * 2.6));
      if (Math.abs(dx) > 2) me.face(dx < 0 ? 'left' : 'right');
      avatar.style.transitionDuration = ms + 'ms';
      me.setPose('walk');
      state.pos = { ...target };
      place(avatar, target);
      setTimeout(() => {
        if (token !== mapToken) return;
        me.setPose('stand');
        if (then) then();
      }, ms);
    }

    // あそびば
    for (const [id, s] of Object.entries(SPOT_LAYOUT)) {
      const ready = id === 'yuugi' || !!spots[id];
      const node = el('button', {
        class: 'world-spot' + (ready ? '' : ' not-ready'),
        'aria-label': s.name,
        onclick: (e) => {
          e.stopPropagation();
          sound('tap');
          if (!ready) { speak(`${s.name}は じゅんびちゅう だよ`); return; }
          speak(s.name);
          walkTo({ x: s.x, y: s.y + 9 }, () => openSpot(id));
        },
      },
        el('span', { class: 'world-spot-emoji' }, s.emoji),
        el('span', { class: 'world-spot-name' }, s.name),
      );
      place(node, s);
      map.append(node);
    }

    // おともだち（すこし うろうろする）
    const friendNodes = FRIENDS.map((f) => {
      const home = FRIEND_HOME[f.id];
      const node = el('button', {
        class: 'world-friend',
        'aria-label': f.name,
        style: { animationDelay: `${Math.random() * -2}s` },
        onclick: (e) => {
          e.stopPropagation();
          sound('tap');
          const p = node._pos;
          walkTo({ x: p.x + (state.pos.x < p.x ? -7 : 7), y: p.y }, () => {
            const scene = Core.shuffle(MAP_TALKS)[0](f);
            talk(scene);
          });
        },
      }, Core.character(f.id));
      node._pos = { ...home };
      place(node, home);
      map.append(node);
      return { f, node, home };
    });

    const wander = setInterval(() => {
      if (!map.isConnected) return clearInterval(wander);
      if (overlays.size) return;
      const { node, home } = Core.shuffle(friendNodes)[0];
      const p = { x: home.x + (Math.random() * 10 - 5), y: home.y + (Math.random() * 6 - 3) };
      const body = node.firstChild;
      body.face(p.x < node._pos.x ? 'left' : 'right').setPose('walk');
      setTimeout(() => body.setPose('stand'), 1400);
      node._pos = p;
      place(node, p);
    }, 2500);

    place(avatar, state.pos);
    map.append(avatar);

    // 床を タップしたら そこへ歩く
    map.addEventListener('pointerdown', (e) => {
      if (e.target !== map && !e.target.classList.contains('world-indoor') && !e.target.classList.contains('world-yard') && !e.target.classList.contains('world-sand') && !e.target.classList.contains('world-door')) return;
      const r = map.getBoundingClientRect();
      const x = Math.min(97, Math.max(3, ((e.clientX - r.left) / r.width) * 100));
      const y = Math.min(96, Math.max(8, ((e.clientY - r.top) / r.height) * 100));
      walkTo({ x, y });
    });

    App.show(
      el('section', { class: 'screen world-screen' },
        el('div', { class: 'world-header' },
          el('button', { class: 'icon-btn', 'aria-label': 'タイトルへ', onclick: () => { mapToken++; App.titleScreen(); } }, '🏠'),
          el('button', { class: 'nakayoshi-btn', onclick: nakayoshiBook }, '💖 なかよし'),
          el('div', { class: 'world-header-right' }, settingsButtons()),
        ),
        el('div', { class: 'world-wrap' }, map),
      ),
    );

    if (!state.greeted) {
      state.greeted = true;
      speak('ようちえんに ついたよ！ どこで あそぶ？ おともだちにも はなしかけてみよう。');
    } else {
      speak('つぎは どこで あそぶ？');
    }
  }

  // ---- なかよしノート ----
  function nakayoshiBook() {
    sound('tap');
    let close;
    const sheet = el('div', { class: 'talk-overlay', role: 'dialog', 'aria-label': 'なかよし ノート', onclick: (e) => { if (e.target === sheet) close(); } },
      el('div', { class: 'book-sheet' },
        el('h2', {}, '💖 なかよし ノート'),
        el('div', { class: 'book-list' },
          FRIENDS.map((f) => {
            const n = heartsOf(f.id);
            return el('div', { class: 'book-row' },
              el('span', { class: 'book-face', style: { background: f.color } }, Core.character(f.id, { mood: n >= 3 ? 'happy' : 'normal' })),
              el('span', { class: 'book-name' }, f.name),
              el('span', { class: 'book-hearts' }, n ? '💖'.repeat(Math.min(n, 10)) + (n > 10 ? `+${n - 10}` : '') : '🤍'),
              el('span', { class: 'book-level' }, friendshipLabel(n)),
            );
          }),
        ),
        el('button', { class: 'big-btn primary', onclick: () => close() }, 'とじる'),
      ),
    );
    close = openOverlay(sheet);
    const total = FRIENDS.reduce((s, f) => s + heartsOf(f.id), 0);
    speak(total ? `ハートが ${total}こ あつまったよ！ みんなと なかよし だね。` : 'おともだちに やさしく すると、ハートが ふえるよ。');
  }

  // ---- あそびばに入る ----
  function openSpot(id) {
    if (id === 'yuugi') { App.teamScreen(); return; }
    const spot = spots[id];
    const layout = SPOT_LAYOUT[id];
    const stage = el('div', { class: 'stage spot-stage' });
    let active = true;
    let cleanup = null;

    const ctx = {
      stage,
      el, speak, sound,
      shuffle: Core.shuffle,
      wait: Core.wait,
      isActive: () => active,
      player: { emoji: state.avatar, kind: Core.characterKind(state.avatar) },
      character: Core.character,
      friends: FRIENDS,
      friend: friendById,
      hearts: heartsOf,
      addHeart: (fid, n) => { if (active) addHeart(fid, n); },
      talk: (opts) => (active ? talk(opts) : Promise.resolve(null)),
      store: {
        get: (k, d) => store.get(`spot:${id}:${k}`, d),
        set: (k, v) => store.set(`spot:${id}:${k}`, v),
      },
      exit,
    };

    function exit() {
      if (!active) return;
      active = false;
      stopSpeaking();
      closeAllOverlays();
      if (typeof cleanup === 'function') cleanup();
      enter();
    }

    App.show(
      el('section', { class: 'screen game-screen spot-screen' },
        el('div', { class: 'game-header' },
          el('button', { class: 'back-btn inline', 'aria-label': 'ようちえんに もどる', onclick: () => { sound('tap'); exit(); } }, '🏫'),
          el('div', { class: 'spot-title' }, `${layout.emoji} ${layout.name}`),
          el('button', { class: 'nakayoshi-btn small', onclick: nakayoshiBook }, '💖'),
        ),
        stage,
      ),
    );
    cleanup = spot.start(ctx) || null;
  }

  Core.store = store;
  Core.registerSpot = registerSpot;
  Core.FRIENDS = FRIENDS;
  window.World = { enter, spots, talk, addHeart };
})();
