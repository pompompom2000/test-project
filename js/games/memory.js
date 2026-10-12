// えあわせ カード：チーム交代制の しんけいすいじゃく（6ペア・12まい）
(function () {
  'use strict';

  // 絵と よみ（チームの どうぶつ 🐰🐻🐸🐥 とは かぶらないものだけ）
  const PICTURES = [
    { emoji: '🐶', name: 'いぬ' },
    { emoji: '🐱', name: 'ねこ' },
    { emoji: '🐘', name: 'ぞう' },
    { emoji: '🐼', name: 'ぱんだ' },
    { emoji: '🐷', name: 'ぶた' },
    { emoji: '🦁', name: 'らいおん' },
    { emoji: '🐧', name: 'ぺんぎん' },
    { emoji: '🍎', name: 'りんご' },
    { emoji: '🍌', name: 'ばなな' },
    { emoji: '🍓', name: 'いちご' },
    { emoji: '🍇', name: 'ぶどう' },
    { emoji: '🍊', name: 'みかん' },
    { emoji: '🍉', name: 'すいか' },
    { emoji: '🍒', name: 'さくらんぼ' },
  ];
  const PAIRS = 6;
  const MISS_SHOW_MS = 1200;

  Core.registerGame({
    id: 'memory',
    title: 'えあわせ カード',
    emoji: '🃏',
    color: '#e3dcff',
    start(ctx) {
      const { el, teams } = ctx;
      let turn = 0;            // いまの チーム
      let first = null;        // 1まいめ
      let busy = false;        // 2まいめ を はんてい中は タップを むし
      let matchedPairs = 0;
      let observer = null;

      // どうぶつ と くだもの を まぜて 6しゅるい えらぶ
      const animals = ctx.shuffle(PICTURES.filter((p) => !/[🍎🍌🍓🍇🍊🍉🍒]/u.test(p.emoji)));
      const fruits = ctx.shuffle(PICTURES.filter((p) => /[🍎🍌🍓🍇🍊🍉🍒]/u.test(p.emoji)));
      const chosen = animals.slice(0, PAIRS / 2).concat(fruits.slice(0, PAIRS / 2));
      const deck = ctx.shuffle(chosen.concat(chosen));

      // ---- ばん の ひょうじ ----
      const turnEmoji = el('span', { class: 'memory-turn-emoji' });
      const turnText = el('span', { class: 'memory-turn-text' });
      const banner = el('div', { class: 'memory-turn' }, turnEmoji, turnText);

      function showTurn() {
        const t = teams[turn];
        banner.style.setProperty('--team', t.color);
        turnEmoji.textContent = t.emoji;
        turnText.textContent = `${t.name}さんの ばん`;
        banner.classList.remove('memory-turn-change');
        void banner.offsetWidth;
        banner.classList.add('memory-turn-change');
      }

      // ---- カード ----
      const cards = deck.map((pic, i) => {
        const node = el('button', { class: 'memory-card', 'aria-label': 'カード', 'data-index': i },
          el('span', { class: 'memory-inner' },
            el('span', { class: 'memory-face memory-back' }, '❓'),
            el('span', { class: 'memory-face memory-front' }, pic.emoji),
          ),
        );
        const card = { pic, node, up: false, matched: false };
        node.addEventListener('click', () => onTap(card));
        return card;
      });
      const board = el('div', { class: 'memory-board' }, cards.map((c) => c.node));
      const wrap = el('div', { class: 'memory-wrap' }, board);

      ctx.stage.append(el('div', { class: 'memory-root' }, banner, wrap));

      // ---- がめん の むき に あわせて ならべかた と おおきさ を きめる ----
      function layout() {
        const w = wrap.clientWidth;
        const h = wrap.clientHeight;
        if (!w || !h) return;
        const gap = Math.max(8, Math.min(16, Math.min(w, h) * 0.02));
        const opts = [[4, 3], [3, 4], [6, 2], [2, 6]];
        let best = null;
        for (const [cols, rows] of opts) {
          const cw = (w - gap * (cols - 1)) / cols;
          const ch = (h - gap * (rows - 1)) / rows;
          // カードは たて 1.25 : よこ 1
          const size = Math.min(cw, ch / 1.25);
          if (!best || size > best.size) best = { cols, rows, size };
        }
        // 6x2 / 2x6 は かなり よこなが・たてなが の ときだけ
        if (best.cols === 6 || best.cols === 2) {
          const alt = best.cols === 6 ? [4, 3] : [3, 4];
          const cw = (w - gap * (alt[0] - 1)) / alt[0];
          const ch = (h - gap * (alt[1] - 1)) / alt[1];
          const s = Math.min(cw, ch / 1.25);
          if (s > best.size * 0.85) best = { cols: alt[0], rows: alt[1], size: s };
        }
        const cardW = Math.floor(best.size);
        board.style.gridTemplateColumns = `repeat(${best.cols}, ${cardW}px)`;
        board.style.gridAutoRows = `${Math.floor(cardW * 1.25)}px`;
        board.style.gap = `${gap}px`;
        board.style.setProperty('--card-w', `${cardW}px`);
      }
      if ('ResizeObserver' in window) {
        observer = new ResizeObserver(layout);
        observer.observe(wrap);
      } else {
        window.addEventListener('resize', layout);
      }
      requestAnimationFrame(layout);

      function flip(card, up) {
        card.up = up;
        card.node.classList.toggle('memory-up', up);
      }

      function sayName(card) {
        // なまえ を よみあげ（ながく またない）
        return Promise.race([ctx.speak(card.pic.name), ctx.wait(1100)]);
      }

      async function onTap(card) {
        if (!ctx.isActive() || busy || card.up || card.matched) return;
        ctx.sound('flip');
        flip(card, true);

        if (!first) {
          first = card;
          sayName(card);
          return;
        }

        // 2まいめ
        const a = first;
        const b = card;
        first = null;
        busy = true;
        await Promise.all([sayName(b), ctx.wait(650)]);
        if (!ctx.isActive()) return;

        if (a.pic === b.pic) {
          const t = teams[turn];
          [a, b].forEach((c) => {
            c.matched = true;
            c.node.style.setProperty('--team', t.color);
            c.node.classList.add('memory-matched', 'memory-sparkle');
            c.node.setAttribute('aria-label', c.pic.name);
          });
          ctx.sound('correct');
          ctx.addScore(turn, 1);
          matchedPairs++;
          if (matchedPairs === PAIRS) {
            await ctx.speak('そろった！ ぜんぶ そろったよ！');
            if (!ctx.isActive()) return;
            await ctx.wait(500);
            if (!ctx.isActive()) return;
            ctx.end();
            return;
          }
          banner.classList.add('memory-again');
          await Promise.race([ctx.speak(`そろった！ ${t.name}さん、もういっかい！`), ctx.wait(2200)]);
          if (!ctx.isActive()) return;
          banner.classList.remove('memory-again');
          busy = false;
        } else {
          ctx.sound('wrong');
          const next = (turn + 1) % teams.length;
          ctx.speak(`おしい！ つぎは ${teams[next].name}さん`);
          await ctx.wait(MISS_SHOW_MS);
          if (!ctx.isActive()) return;
          flip(a, false);
          flip(b, false);
          await ctx.wait(450); // うらがえる アニメ の あいだ
          if (!ctx.isActive()) return;
          turn = next;
          showTurn();
          busy = false;
          ctx.speak(`${teams[turn].name}さんの ばん だよ`);
        }
      }

      // ---- はじまり ----
      showTurn();
      ctx.speak(`おなじ えを 2まい さがしてね。${teams[turn].name}さんの ばん だよ`);

      return () => {
        if (observer) observer.disconnect();
        else window.removeEventListener('resize', layout);
      };
    },
  });
})();
