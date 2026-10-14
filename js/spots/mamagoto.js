// おままごと：おもちゃの キッチンで りょうりを つくって、おともだちに「どうぞ」する ごっこあそび
(function () {
  'use strict';

  // ---- たべもの ----
  const FOODS = [
    { id: 'carrot', e: '🥕', n: 'にんじん', t: 'veg' },
    { id: 'tomato', e: '🍅', n: 'トマト', t: 'veg' },
    { id: 'egg', e: '🥚', n: 'たまご', t: 'egg' },
    { id: 'bread', e: '🍞', n: 'パン', t: 'bread' },
    { id: 'cheese', e: '🧀', n: 'チーズ', t: 'cheese' },
    { id: 'straw', e: '🍓', n: 'いちご', t: 'fruit' },
    { id: 'banana', e: '🍌', n: 'バナナ', t: 'fruit' },
    { id: 'broc', e: '🥦', n: 'ブロッコリー', t: 'veg' },
    { id: 'rice', e: '🍙', n: 'ごはん', t: 'rice' },
    { id: 'meat', e: '🍖', n: 'おにく', t: 'meat' },
    { id: 'fish', e: '🐟', n: 'おさかな', t: 'fish' },
    { id: 'corn', e: '🌽', n: 'コーン', t: 'veg' },
  ];
  const FOOD = Object.fromEntries(FOODS.map((f) => [f.id, f]));

  const VESSELS = [
    { id: 'pot', name: 'おなべ', act: 'まぜまぜ', actEmoji: '🥄' },
    { id: 'pan', name: 'フライパン', act: 'やく', actEmoji: '🔥' },
    { id: 'plate', name: 'おさら', act: 'まぜまぜ', actEmoji: '🥄' },
  ];
  const MAX_ITEMS = 5;

  // おともだちの「たべたいな」（ぴったりで なくても よろこんで たべる）
  const ORDERS = [
    { b: '🍲', n: 'スープ' }, { b: '🍳', n: 'たまごやき' }, { b: '🥪', n: 'サンドイッチ' },
    { b: '🍕', n: 'ピザ' }, { b: '🥞', n: 'パンケーキ' }, { b: '🍛', n: 'カレー' },
    { b: '🥗', n: 'サラダ' }, { b: '🍨', n: 'パフェ' }, { b: '🍙', n: 'おにぎり' },
    { food: 'straw' }, { food: 'banana' }, { food: 'carrot' }, { food: 'cheese' }, { food: 'corn' }, { food: 'meat' },
  ];
  const orderEmoji = (o) => (o.food ? FOOD[o.food].e : o.b);
  const orderWord = (o) => (o.food ? `${FOOD[o.food].n}の はいった もの` : o.n);
  const orderMatch = (o, d) => (o.food ? d.ids.includes(o.food) : o.b === d.b);

  // ---- じゆう りょうり：なにを いれても かならず おいしそうな ものが できる ----
  function cook(tool, ids) {
    const uniq = [...new Set(ids)];
    const fs = uniq.map((id) => FOOD[id]);
    const has = (id) => uniq.includes(id);
    const types = new Set(fs.map((f) => f.t));
    const only = (...ts) => fs.every((f) => ts.includes(f.t));
    const single = uniq.length === 1;
    const names = fs.slice(0, 2).map((f) => f.n).join('と ');
    let b;
    let n;
    if (tool === 'pot') {
      if (only('fruit')) { b = '🍯'; n = `${fs[0].n} ジャム`; }
      else if ((has('meat') || has('fish')) && types.has('veg')) { b = '🍛'; n = has('cheese') ? 'チーズ カレー' : 'カレー'; }
      else if (has('rice')) { b = '🥣'; n = single ? 'おかゆ' : 'ぞうすい'; }
      else if (has('cheese')) { b = '🫕'; n = 'チーズ フォンデュ'; }
      else { b = '🍲'; n = `${names}の スープ`; }
    } else if (tool === 'pan') {
      if (only('fruit')) { b = '🥞'; n = `${fs[0].n} パンケーキ`; }
      else if (has('tomato') && has('cheese')) { b = '🍕'; n = 'ピザ'; }
      else if (has('bread')) { b = '🍞'; n = has('egg') ? 'フレンチ トースト' : has('cheese') ? 'チーズ トースト' : 'トースト'; }
      else if (has('egg')) { b = '🍳'; n = single ? 'めだまやき' : has('rice') ? 'オムライス' : 'オムレツ'; }
      else if (has('rice')) { b = single ? '🍙' : '🍚'; n = single ? 'やきおにぎり' : 'チャーハン'; }
      else if (has('meat')) { b = '🍖'; n = 'ハンバーグ'; }
      else if (has('fish')) { b = '🍤'; n = 'フライ'; }
      else { b = '🥘'; n = 'やさい いため'; }
    } else {
      if (has('bread')) { b = single ? '🍞' : '🥪'; n = single ? 'ふわふわ パン' : 'サンドイッチ'; }
      else if (only('fruit')) { b = '🍨'; n = `${fs[0].n} パフェ`; }
      else if (has('rice')) { b = single ? '🍙' : '🍱'; n = single ? 'おにぎり' : 'おべんとう'; }
      else if (only('veg', 'cheese', 'egg')) { b = '🥗'; n = 'サラダ'; }
      else { b = '🍱'; n = 'ごちそう プレート'; }
    }
    return { b, n, t: fs.map((f) => f.e), ids: uniq };
  }

  Core.registerSpot({
    id: 'mamagoto',
    start(ctx) {
      const { el, speak, sound, store } = ctx;
      const EVENT_GAP = 35000;

      // ---- タイマー（後片付けで まとめて とめる） ----
      const timers = new Set();
      const intervals = new Set();
      const later = (fn, ms) => {
        const id = setTimeout(() => { timers.delete(id); if (ctx.isActive()) fn(); }, ms);
        timers.add(id);
        return id;
      };
      const every = (fn, ms) => {
        const id = setInterval(() => { if (ctx.isActive()) fn(); }, ms);
        intervals.add(id);
        return id;
      };
      const stopEvery = (id) => { clearInterval(id); intervals.delete(id); };
      const sleep = (ms) => new Promise((r) => later(r, ms));
      let dragCleanup = null;

      // ---- じょうたい ----
      const saved = store.get('vessels', null);
      const S = {
        mode: 'play', // play | chef(おともだちが コックさん) | cleanup
        event: false,
        selected: 'pot',
        holding: null,
        vessels: {},
        book: store.get('book', []),
        totalServed: store.get('served', 0),
        dishesSinceClean: 0,
        servesSinceSwap: 0,
        lastEventAt: Date.now(),
        smallToggle: Math.random() < 0.5,
        requests: [],
      };
      VESSELS.forEach((v) => {
        const s = saved && saved[v.id];
        S.vessels[v.id] = {
          items: s && Array.isArray(s.items) ? s.items.filter((id) => FOOD[id]).slice(0, MAX_ITEMS) : [],
          dish: s && s.dish && s.dish.b ? s.dish : null,
          busy: false,
        };
      });
      const saveVessels = () => {
        const out = {};
        VESSELS.forEach((v) => { out[v.id] = { items: S.vessels[v.id].items, dish: S.vessels[v.id].dish }; });
        store.set('vessels', out);
      };

      // ---- おともだち（きつねちゃん ＋ 1〜2にん） ----
      const others = ctx.shuffle(ctx.friends.filter((f) => f.id !== 'kitsune'));
      const guests = [ctx.friend('kitsune'), ...others.slice(0, Math.random() < 0.5 ? 1 : 2)];
      const kitsune = ctx.friend('kitsune');

      // ---- がめん ----
      const root = el('div', { class: 'mamagoto-root' });
      const table = el('div', { class: 'mamagoto-table' });
      const work = el('div', { class: 'mamagoto-work' });
      const kitchen = el('div', { class: 'mamagoto-kitchen' });
      const pantry = el('div', { class: 'mamagoto-pantry' });
      const chefBadge = el('div', { class: 'mamagoto-chef', 'aria-hidden': 'true' });
      const bookBtn = el('button', { class: 'mamagoto-book-btn', 'aria-label': 'つくった りょうり', onclick: openBook }, '📖');
      work.append(kitchen, pantry);
      root.append(table, work);
      ctx.stage.append(root);

      // せき
      const seats = guests.map((f, i) => {
        const bubble = el('div', { class: 'mamagoto-bubble hidden' });
        const face = el('div', { class: 'mamagoto-face' }, f.emoji);
        const served = el('div', { class: 'mamagoto-served' });
        const node = el('button', {
          class: 'mamagoto-seat', 'data-seat': String(i), 'aria-label': f.name,
          style: { '--seat-color': f.color },
          onclick: () => onSeatTap(seat),
        }, bubble, face, served, el('div', { class: 'mamagoto-chair', 'aria-hidden': 'true' }));
        const seat = { f, node, bubble, face, served, order: null, status: 'idle', away: false };
        table.append(node);
        return seat;
      });
      const playerSeat = el('div', { class: 'mamagoto-seat mamagoto-player hidden', 'aria-hidden': 'true' },
        el('div', { class: 'mamagoto-face' }, ctx.player.emoji || '🧒'),
        el('div', { class: 'mamagoto-served' }),
        el('div', { class: 'mamagoto-chair', 'aria-hidden': 'true' }));
      table.append(playerSeat);

      // キッチン
      const vesselNodes = {};
      VESSELS.forEach((v) => {
        const contents = el('div', { class: 'mamagoto-contents' });
        const shape = el('div', { class: `mamagoto-shape mamagoto-shape-${v.id}` }, contents);
        const vessel = el('div', {
          class: 'mamagoto-vessel', 'data-vessel': v.id, role: 'button', 'aria-label': v.name,
        }, shape);
        const action = el('button', {
          class: 'mamagoto-action', 'aria-label': v.act,
          onclick: () => doCook(v.id),
        }, el('span', { class: 'mamagoto-action-emoji' }, v.actEmoji), el('span', { class: 'mamagoto-action-label' }, v.act));
        kitchen.append(el('div', { class: 'mamagoto-station' }, vessel, action));
        vesselNodes[v.id] = { vessel, contents, shape, action };
        dragify(vessel, {
          canDrag: () => S.mode === 'play' && !!S.vessels[v.id].dish,
          ghost: () => dishNode(S.vessels[v.id].dish),
          onTap: () => onVesselTap(v.id),
          onDrop: (target) => {
            const seatEl = target && target.closest('.mamagoto-seat[data-seat]');
            if (seatEl) serve(seats[Number(seatEl.dataset.seat)], v.id);
          },
        });
      });
      kitchen.append(chefBadge);
      table.append(bookBtn);

      // たべもの だな
      FOODS.forEach((f) => {
        const b = el('button', { class: 'mamagoto-food', 'aria-label': f.n }, f.e);
        pantry.append(b);
        dragify(b, {
          canDrag: () => S.mode === 'play',
          ghost: () => el('div', { class: 'mamagoto-ghost-food' }, f.e),
          onTap: () => onFoodTap(f),
          onDrop: (target) => {
            const vEl = target && target.closest('[data-vessel]');
            if (vEl) addFood(vEl.dataset.vessel, f);
          },
        });
      });

      // ---- ドラッグ（すこし うごかしたら ドラッグ、うごかさなければ タップ） ----
      function dragify(node, opts) {
        node.addEventListener('pointerdown', (e) => {
          if (e.button != null && e.button !== 0) return;
          if (dragCleanup) dragCleanup();
          const sx = e.clientX;
          const sy = e.clientY;
          let ghost = null;
          const move = (ev) => {
            if (!ghost) {
              if (Math.hypot(ev.clientX - sx, ev.clientY - sy) < 12 || !opts.canDrag()) return;
              ghost = el('div', { class: 'mamagoto-ghost' }, opts.ghost());
              document.body.append(ghost);
              node.classList.add('mamagoto-dragging');
            }
            ghost.style.left = ev.clientX + 'px';
            ghost.style.top = ev.clientY + 'px';
          };
          const end = (ev, cancelled) => {
            finish();
            if (cancelled || !ctx.isActive()) return;
            if (ghost) {
              const target = document.elementFromPoint(ev.clientX, ev.clientY);
              opts.onDrop(target);
            } else {
              opts.onTap();
            }
          };
          const up = (ev) => end(ev, false);
          const cancel = (ev) => end(ev, true);
          function finish() {
            window.removeEventListener('pointermove', move);
            window.removeEventListener('pointerup', up);
            window.removeEventListener('pointercancel', cancel);
            if (ghost) ghost.remove();
            node.classList.remove('mamagoto-dragging');
            dragCleanup = null;
          }
          dragCleanup = finish;
          window.addEventListener('pointermove', move);
          window.addEventListener('pointerup', up);
          window.addEventListener('pointercancel', cancel);
        });
      }

      // ---- びょうが ----
      function dishNode(d, extra = '') {
        return el('div', { class: 'mamagoto-dish ' + extra },
          el('span', { class: 'mamagoto-dish-base' }, d.b),
          el('span', { class: 'mamagoto-dish-tops' }, d.t.slice(0, 5).map((t, i) => el('span', { style: { animationDelay: `${i * -0.4}s` } }, t))));
      }

      function renderVessel(id) {
        const v = S.vessels[id];
        const n = vesselNodes[id];
        n.contents.replaceChildren();
        n.vessel.classList.toggle('selected', S.mode === 'play' && S.selected === id);
        n.vessel.classList.toggle('has-dish', !!v.dish);
        n.vessel.classList.toggle('holding', S.holding === id);
        if (v.dish) {
          n.contents.append(dishNode(v.dish));
        } else {
          v.items.forEach((fid, i) => n.contents.append(el('span', { class: 'mamagoto-item', style: { '--i': i } }, FOOD[fid].e)));
        }
        n.action.disabled = S.mode !== 'play' || v.busy || !!v.dish;
      }
      const renderAll = () => VESSELS.forEach((v) => renderVessel(v.id));

      function renderSeat(seat) {
        seat.node.classList.toggle('away', seat.away);
        seat.node.classList.toggle('eating', seat.status === 'eat');
        if (seat.order && seat.status === 'idle') {
          seat.bubble.replaceChildren('💭', el('span', { class: 'mamagoto-order' }, orderEmoji(seat.order)));
          seat.bubble.classList.remove('hidden');
        } else if (seat.status !== 'eat') {
          seat.bubble.classList.add('hidden');
        }
      }
      function seatSay(seat, text, ms = 2200) {
        seat.bubble.replaceChildren(text);
        seat.bubble.classList.remove('hidden');
        later(() => { if (seat.bubble.textContent === text) renderSeat(seat); }, ms);
      }
      function floatAt(node, text, cls = '') {
        const f = el('div', { class: 'mamagoto-float ' + cls, 'aria-hidden': 'true' }, text);
        node.append(f);
        later(() => f.remove(), 1500);
      }

      // ---- ちゅうもん ----
      function newOrder(seat, say = true) {
        if (seat.away) return;
        seat.order = ctx.shuffle(ORDERS)[0];
        seat.status = 'idle';
        renderSeat(seat);
        seat.node.classList.add('pop');
        later(() => seat.node.classList.remove('pop'), 500);
        if (say && !S.event && S.mode === 'play') speak(`${seat.f.name}「おなか すいた！ ${orderWord(seat.order)}が たべたいな」`);
      }

      // ---- そうさ ----
      function onVesselTap(id) {
        if (S.mode !== 'play') return;
        sound('tap');
        const v = S.vessels[id];
        if (v.dish) {
          S.holding = id;
          renderAll();
          speak(`${v.dish.n}！ おともだちに タッチして「どうぞ」しよう`);
          return;
        }
        S.selected = id;
        S.holding = null;
        renderAll();
        const def = VESSELS.find((x) => x.id === id);
        speak(v.items.length ? `${def.name}。「${def.act}」を おしてね` : `${def.name}に たべものを いれよう`);
      }

      function onFoodTap(f) {
        if (S.mode === 'chef') { requestFood(f); return; }
        if (S.mode !== 'play') return;
        addFood(S.selected, f);
      }

      function addFood(vid, f) {
        if (S.mode !== 'play') return;
        const v = S.vessels[vid];
        const def = VESSELS.find((x) => x.id === vid);
        S.selected = vid;
        if (v.busy) return;
        if (v.dish) {
          S.holding = vid;
          renderAll();
          speak(`${v.dish.n}が できてるよ。さきに おともだちに どうぞ しよう`);
          return;
        }
        if (v.items.length >= MAX_ITEMS) {
          renderAll();
          speak(`${def.name}は いっぱい！「${def.act}」を おしてね`);
          return;
        }
        v.items.push(f.id);
        sound('flip');
        renderAll();
        const last = vesselNodes[vid].contents.lastElementChild;
        if (last) last.classList.add('drop-in');
        saveVessels();
        speak(f.n);
      }

      async function doCook(vid, byFriend = false) {
        const v = S.vessels[vid];
        const def = VESSELS.find((x) => x.id === vid);
        if (v.busy || v.dish) return null;
        if (!byFriend && S.mode !== 'play') return null;
        if (!v.items.length) {
          sound('tap');
          S.selected = vid;
          renderAll();
          speak(`${def.name}に たべものを いれてね`);
          return null;
        }
        v.busy = true;
        S.holding = null;
        renderAll();
        sound('start');
        const n = vesselNodes[vid];
        n.shape.classList.add(vid === 'pan' ? 'cooking-fire' : 'cooking-mix');
        speak(vid === 'pan' ? 'じゅう じゅう…' : 'まぜ まぜ…');
        await sleep(1600);
        n.shape.classList.remove('cooking-fire', 'cooking-mix');
        const dish = cook(vid, v.items);
        v.items = [];
        v.dish = dish;
        v.busy = false;
        S.dishesSinceClean += 1;
        S.selected = vid;
        if (!byFriend) {
          S.holding = vid;
          rememberDish(dish);
        }
        renderAll();
        saveVessels();
        sound('correct');
        floatAt(n.vessel, '✨');
        if (!byFriend) speak(`${dish.n}が できた！ おともだちに もっていって「どうぞ」しよう`);
        return dish;
      }

      function rememberDish(dish) {
        S.book = [{ b: dish.b, t: dish.t, n: dish.n, ids: dish.ids }, ...S.book].slice(0, 24);
        store.set('book', S.book);
      }

      function onSeatTap(seat) {
        if (S.mode !== 'play' || seat.away) return;
        if (S.holding && S.vessels[S.holding].dish) { serve(seat, S.holding); return; }
        sound('tap');
        if (seat.status === 'eat') { speak(`${seat.f.name}は もぐもぐ ちゅう`); return; }
        if (seat.order) speak(`${seat.f.name}「${orderWord(seat.order)}が たべたいな」`);
        else speak(`${seat.f.name}「おいしかった！ ありがとう」`);
      }

      async function serve(seat, vid) {
        if (S.mode !== 'play' || seat.away) return;
        const v = S.vessels[vid];
        if (!v.dish) return;
        if (seat.status === 'eat') {
          speak(`${seat.f.name}は もぐもぐ ちゅう。ほかの おともだちに あげよう`);
          return;
        }
        const dish = v.dish;
        const order = seat.order;
        v.dish = null;
        S.holding = null;
        renderAll();
        saveVessels();
        seat.status = 'eat';
        seat.order = null;
        seat.served.replaceChildren(dishNode(dish, 'small'));
        renderSeat(seat);
        sound('tap');
        seatSay(seat, 'いただきます！', 2000);
        await speak('どうぞ！');
        await speak(`${seat.f.name}「いただきます！」`);
        await sleep(1400);
        const matched = order && orderMatch(order, dish);
        const reply = matched
          ? `わあ、たべたかった ${orderWord(order)}だ！ おいしい！ ごちそうさま！`
          : `${dish.n}、おいしい！ ごちそうさま！`;
        seat.served.replaceChildren();
        seatSay(seat, '😋 ごちそうさま！', 2600);
        floatAt(seat.node, '💖');
        sound('correct');
        ctx.addHeart(seat.f.id, 1);
        await speak(`${seat.f.name}「${reply}」`);
        seat.status = 'idle';
        renderSeat(seat);
        S.totalServed += 1;
        S.servesSinceSwap += 1;
        store.set('served', S.totalServed);
        later(() => { if (!seat.order && seat.status === 'idle') newOrder(seat); }, 5000 + Math.random() * 4000);
        maybeEvent();
      }

      // ---- しゃかいせいの できごと ----
      const gapOk = () => Date.now() - S.lastEventAt > EVENT_GAP;
      function maybeEvent() {
        if (S.mode !== 'play' || S.event) return;
        if (S.dishesSinceClean >= 5) { runEvent(cleanupEvent); return; }
        if (S.servesSinceSwap >= 4 && gapOk()) { runEvent(swapEvent); return; }
        if (gapOk() && Math.random() < 0.45) {
          S.smallToggle = !S.smallToggle;
          runEvent(S.smallToggle ? spillEvent : giftEvent);
        }
      }
      async function runEvent(fn) {
        S.event = true;
        await sleep(1200);
        try {
          await fn();
        } finally {
          S.event = false;
          S.lastEventAt = Date.now();
        }
      }

      async function eatBySelf(dish) {
        const node = el('div', { class: 'mamagoto-treat' }, dishNode(dish), el('div', { class: 'mamagoto-treat-face' }, ctx.player.emoji || '🧒'));
        root.append(node);
        await speak('もぐ もぐ…');
        if (!ctx.isActive()) return;
        node.classList.add('done');
        sound('correct');
        await speak('おいしい！ ごちそうさま！');
        later(() => node.remove(), 300);
      }

      // おともだちが つくって くれた
      async function offerDish(friend, dish, say) {
        const res = await ctx.talk({
          friend: friend.id, mood: '😊', say,
          choices: ctx.shuffle([
            { emoji: '🙏', label: 'いただきます', good: true, reply: 'どうぞ めしあがれ！' },
            { emoji: '🙅', label: 'いらない', good: false, hint: `${friend.name}が いっしょうけんめい つくって くれたよ。なんて いったら うれしいかな？` },
          ]),
        });
        if (!res || !ctx.isActive()) return false;
        await eatBySelf(dish);
        return ctx.isActive();
      }

      async function giftEvent() {
        const cand = seats.filter((s) => !s.away && s.status !== 'eat' && s.f.id !== 'kitsune');
        const seat = cand[0] || seats.find((s) => !s.away && s.status !== 'eat');
        if (!seat) return;
        const tool = ctx.shuffle(['pot', 'pan', 'plate'])[0];
        const dish = cook(tool, ctx.shuffle(FOODS).slice(0, 2).map((f) => f.id));
        seatSay(seat, dish.b + '🎁', 3000);
        await offerDish(seat.f, dish, `いつも ありがとう！ おれいに ${dish.n}を つくったの。どうぞ！`);
      }

      async function spillEvent() {
        const seat = ctx.shuffle(seats.filter((s) => !s.away))[0];
        if (!seat) return;
        const puddle = el('button', { class: 'mamagoto-puddle', 'aria-label': 'ふく' }, el('span', {}, '💦'), el('span', { class: 'mamagoto-puddle-cup' }, '🥛'));
        seat.node.append(puddle);
        seat.node.classList.add('sad');
        sound('wrong');
        const res = await ctx.talk({
          friend: seat.f.id, mood: '😢', say: 'あっ！ こぼしちゃった…。',
          choices: ctx.shuffle([
            { emoji: '🧽', label: 'だいじょうぶ？ いっしょに ふこう', good: true, reply: 'ありがとう！ いっしょに ふこう！' },
            { emoji: '😆', label: 'わらう', good: false, hint: `${seat.f.name}、かなしそう…。どうしたら いいかな？` },
          ]),
        });
        if (!res || !ctx.isActive()) return;
        seat.node.classList.remove('sad');
        speak('ふき ふき しよう！ みずを タッチしてね');
        await new Promise((resolve) => {
          let left = 5;
          const shrink = () => {
            left -= 1;
            puddle.style.setProperty('--left', String(Math.max(left, 0) / 5));
            floatAt(puddle, '🫧');
            if (left <= 0) { stopEvery(friendWipe); resolve(); }
          };
          puddle.addEventListener('pointerdown', (e) => { e.stopPropagation(); if (left > 0) { sound('flip'); shrink(); } });
          puddle.addEventListener('click', (e) => e.stopPropagation());
          const friendWipe = every(() => { if (left > 0) shrink(); }, 1500);
        });
        puddle.remove();
        sound('correct');
        seatSay(seat, '✨ ぴかぴか！', 2000);
        await speak(`${seat.f.name}「きれいに なったね！ ありがとう！」`);
      }

      async function swapEvent() {
        const res = await ctx.talk({
          friend: 'kitsune', mood: '🤩', say: 'つぎは わたしが コックさん やりたいな',
          choices: ctx.shuffle([
            { emoji: '🤝', label: 'いいよ、こうたい しよう', good: true, reply: 'やったあ！ ありがとう！ がんばって つくるね！' },
            { emoji: '🙅', label: 'ずっと ぼくが やる', good: false, hint: 'きつねちゃんも コックさん やって みたいんだって…。どうしたら いいかな？' },
          ]),
        });
        if (!res || !ctx.isActive()) return;
        await chefMode(kitsune);
      }

      async function chefMode(chef) {
        const chefSeat = seats.find((s) => s.f.id === chef.id);
        // キッチンを きれいに して こうたい
        VESSELS.forEach((v) => { S.vessels[v.id].items = []; S.vessels[v.id].dish = null; });
        S.mode = 'chef';
        S.holding = null;
        S.requests = [];
        root.classList.add('chef-mode');
        chefSeat.away = true;
        chefSeat.order = null;
        renderSeat(chefSeat);
        playerSeat.classList.remove('hidden');
        chefBadge.replaceChildren(el('span', { class: 'mamagoto-chef-face' }, chef.emoji), el('span', { class: 'mamagoto-chef-hat' }, '👨‍🍳'), el('span', {}, 'コックさん'));
        renderAll();
        saveVessels();
        await speak(`こんどは ${chef.name}が コックさん。きみは おきゃくさん だよ。たべたい ものを タッチして おねがい してみよう`);
        if (!ctx.isActive()) return;

        for (let round = 0; round < 2; round++) {
          const vid = ctx.shuffle(['pot', 'pan', 'plate'])[0];
          const v = S.vessels[vid];
          S.selected = vid;
          renderAll();
          const want = 3;
          let tries = 0;
          while (v.items.length < want && tries < 8) {
            tries += 1;
            await sleep(1500);
            const req = S.requests.shift();
            const fid = req || (Math.random() < 0.5 && tries < 4 ? null : ctx.shuffle(FOODS)[0].id);
            if (!fid) continue;
            v.items.push(fid);
            sound('flip');
            renderVessel(vid);
            const last = vesselNodes[vid].contents.lastElementChild;
            if (last) last.classList.add('drop-in');
            if (req) speak(`${chef.name}「${FOOD[fid].n}、いれるね！」`);
          }
          // まだ のこっている おねがいも いれる
          while (S.requests.length && v.items.length < MAX_ITEMS) { v.items.push(S.requests.shift()); renderVessel(vid); }
          await sleep(600);
          const dish = await doCook(vid, true);
          if (!dish || !ctx.isActive()) return;
          await sleep(900);
          if (round === 0) {
            const served = playerSeat.querySelector('.mamagoto-served');
            v.dish = null;
            renderVessel(vid);
            served.replaceChildren(dishNode(dish, 'small'));
            const ok = await offerDish(chef, dish, `${dish.n}が できたよ！ どうぞ！`);
            served.replaceChildren();
            if (!ok) return;
            rememberDish(dish);
          } else {
            // おともだちにも どうぞ（みんなで たのしむ ようすを みせる）
            const guest = seats.find((s) => !s.away) || null;
            v.dish = null;
            renderVessel(vid);
            if (guest) {
              guest.status = 'eat';
              guest.served.replaceChildren(dishNode(dish, 'small'));
              renderSeat(guest);
              await speak(`${chef.name}「${guest.f.name}も どうぞ！」`);
              seatSay(guest, 'いただきます！', 1800);
              await speak(`${guest.f.name}「いただきます！」`);
              await sleep(1200);
              guest.served.replaceChildren();
              guest.status = 'idle';
              seatSay(guest, '😋 おいしい！', 1800);
              await speak(`${guest.f.name}「おいしい！ ありがとう！」`);
              renderSeat(guest);
            }
          }
          if (!ctx.isActive()) return;
        }
        // こうたい おしまい
        await speak(`${chef.name}「コックさん たのしかった！ つぎは また きみの ばん ね！」`);
        if (!ctx.isActive()) return;
        S.mode = 'play';
        S.servesSinceSwap = 0;
        S.selected = 'pot';
        root.classList.remove('chef-mode');
        chefBadge.replaceChildren();
        playerSeat.classList.add('hidden');
        chefSeat.away = false;
        renderSeat(chefSeat);
        VESSELS.forEach((x) => { S.vessels[x.id].items = []; S.vessels[x.id].dish = null; });
        renderAll();
        saveVessels();
        later(() => newOrder(chefSeat), 2500);
        if (S.dishesSinceClean >= 5) later(() => { if (!S.event && S.mode === 'play') runEvent(cleanupEvent); }, 4000);
      }

      function requestFood(f) {
        sound('tap');
        if (S.requests.length >= 3) { speak(`${kitsune.name}「ちょっと まってね」`); return; }
        S.requests.push(f.id);
        speak(`「${f.n}を いれて！」`);
      }

      async function cleanupEvent() {
        const res = await ctx.talk({
          friend: 'kitsune', say: 'たくさん つくったね！ おかたづけ しよう！',
          choices: ctx.shuffle([
            { emoji: '🧺', label: 'うん、いっしょに やろう', good: true, reply: 'ありがとう！ みんなで やると はやいね！' },
            { emoji: '🙅', label: 'やだ、まだ あそぶ', good: false, hint: 'みんなで つかった キッチン だね。どうしたら いいかな？' },
          ]),
        });
        if (!res || !ctx.isActive()) return;
        S.mode = 'cleanup';
        S.holding = null;
        renderAll();

        const shelf = el('div', { class: 'mamagoto-shelf' });
        const mess = el('div', { class: 'mamagoto-mess' });
        const panel = el('div', { class: 'mamagoto-cleanup' },
          el('div', { class: 'mamagoto-shelf-wrap' }, el('div', { class: 'mamagoto-shelf-label', 'aria-hidden': 'true' }, '🗄️'), shelf),
          mess);
        work.append(panel);

        const used = [...new Set(S.book.slice(0, 3).flatMap((d) => d.ids || []))].map((id) => FOOD[id]).filter(Boolean);
        const foods = ctx.shuffle(used.length >= 3 ? used : FOODS).slice(0, 4).map((f) => f.e);
        const things = ctx.shuffle(['🍽️', '🥄', '🍴', '🥣', ...foods]);
        const spots = ctx.shuffle([[12, 22], [38, 18], [64, 24], [88, 20], [16, 70], [42, 74], [68, 66], [88, 72]]);
        let left = things.length;
        let resolveDone;
        const done = new Promise((r) => { resolveDone = r; });

        const putAway = (item, who) => {
          if (item._gone) return;
          item._gone = true;
          left -= 1;
          item.remove();
          const slot = el('div', { class: 'mamagoto-slot' }, item._emoji);
          if (who) slot.append(el('span', { class: 'mamagoto-slot-who' }, who.emoji));
          shelf.append(slot);
          sound('flip');
          if (left <= 0) resolveDone();
        };

        const items = things.map((t, i) => {
          const item = el('button', {
            class: 'mamagoto-mess-item', 'aria-label': 'かたづける',
            style: { left: spots[i][0] + '%', top: spots[i][1] + '%', '--r': `${Math.round(Math.random() * 40 - 20)}deg` },
          }, t);
          item._emoji = t;
          dragify(item, {
            canDrag: () => true,
            ghost: () => el('div', { class: 'mamagoto-ghost-food' }, t),
            onTap: () => putAway(item, null),
            onDrop: () => putAway(item, null),
          });
          mess.append(item);
          return item;
        });
        speak('たなに もどそう！ タッチしても いいよ');

        // おともだちも いっしょに かたづける
        const helpers = seats.filter((s) => !s.away);
        let h = 0;
        const helpId = every(() => {
          const rest = items.filter((it) => !it._gone);
          if (!rest.length) return;
          const seat = helpers[h % helpers.length];
          h += 1;
          const it = ctx.shuffle(rest)[0];
          it.classList.add('helped');
          it.append(el('span', { class: 'mamagoto-helper' }, seat.f.emoji));
          seatSay(seat, '🧺', 1200);
          later(() => putAway(it, seat.f), 700);
        }, 2600);

        await done;
        stopEvery(helpId);
        sound('fanfare');
        panel.classList.add('finished');
        helpers.filter((s) => s.f.id !== 'kitsune').forEach((s) => { ctx.addHeart(s.f.id, 1); floatAt(s.node, '💖'); });
        await speak('ぴかぴか！ みんなで おかたづけ できたね！ ありがとう！');
        if (!ctx.isActive()) return;
        panel.remove();
        VESSELS.forEach((x) => { S.vessels[x.id].items = []; S.vessels[x.id].dish = null; });
        S.dishesSinceClean = 0;
        S.mode = 'play';
        renderAll();
        saveVessels();
        speak('また りょうり しよう！');
      }

      // ---- つくった りょうり ノート（おともだちに みせる） ----
      function openBook() {
        if (S.mode === 'cleanup' || root.querySelector('.mamagoto-bookview')) return;
        sound('tap');
        let shown = false;
        const close = () => view.remove();
        const grid = el('div', { class: 'mamagoto-book-grid' });
        const view = el('div', { class: 'mamagoto-bookview', role: 'dialog', 'aria-label': 'つくった りょうり' },
          el('div', { class: 'mamagoto-book-head' },
            el('span', { class: 'mamagoto-book-title' }, '📖 つくった りょうり'),
            el('button', { class: 'mamagoto-book-close', 'aria-label': 'とじる', onclick: () => { sound('tap'); close(); } }, '✖️')),
          grid);
        if (!S.book.length) grid.append(el('div', { class: 'mamagoto-book-empty' }, '🍳❓'));
        S.book.forEach((d) => {
          grid.append(el('button', {
            class: 'mamagoto-book-item', 'aria-label': d.n,
            onclick: () => {
              sound('tap');
              const seat = ctx.shuffle(seats.filter((s) => !s.away))[0];
              const f = seat ? seat.f : kitsune;
              if (seat) seatSay(seat, '😍 ' + d.b, 2200);
              if (!shown) { shown = true; ctx.addHeart(f.id, 1); }
              speak(`${d.n}！ ${f.name}「わあ、おいしそう！ また つくってね！」`);
            },
          }, dishNode(d)));
        });
        root.append(view);
        speak(S.book.length ? 'つくった りょうり だよ。タッチして おともだちに みせよう' : 'まだ なにも ないよ。りょうりを つくってみよう');
      }

      // ---- はじまり ----
      renderAll();
      seats.forEach((s) => renderSeat(s));
      (async () => {
        if (S.book.length) {
          await speak(`また きてくれたね！ ${kitsune.name}「この まえの ${S.book[0].n}、おいしかったよ！」`);
        } else {
          await speak('おままごと しよう！ たべものを おなべや フライパンに いれて、りょうりを つくってね');
        }
        if (!ctx.isActive()) return;
        seats.forEach((s, i) => later(() => newOrder(s, i === 0), 400 + i * 900));
      })();

      return () => {
        timers.forEach((id) => clearTimeout(id));
        timers.clear();
        intervals.forEach((id) => clearInterval(id));
        intervals.clear();
        if (dragCleanup) dragCleanup();
        document.querySelectorAll('.mamagoto-ghost').forEach((g) => g.remove());
      };
    },
  });
})();
