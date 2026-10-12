// たまいれ タップ：運動会の玉入れ風。全チームが同じ画面で同時にあそぶ
(function () {
  'use strict';

  const GAME_SEC = 30;          // せいげんじかん
  const SPAWN_MS = 800;         // ボールがでる間隔（全チーム共通）
  const BALL_LIFE_MS = 3600;    // ボールが きえるまでの時間
  const MAX_BALLS = 4;          // 1エリアに同時に出るボールの最大数
  const NUM_WORDS = { 5: 'ご', 4: 'よん', 3: 'さん', 2: 'に', 1: 'いち' };

  Core.registerGame({
    id: 'tama-ire',
    title: 'たまいれ タップ',
    emoji: '🧺',
    color: '#dff3ff',
    start(ctx) {
      const { el, teams } = ctx;
      const timers = new Set();
      let rafId = 0;
      let playing = false;

      const later = (fn, ms) => {
        const id = setTimeout(() => { timers.delete(id); fn(); }, ms);
        timers.add(id);
        return id;
      };

      // ---- 画面づくり ----
      const timeNum = el('span', { class: 'tama-ire-time-num' }, String(GAME_SEC));
      const barFill = el('div', { class: 'tama-ire-bar-fill' });
      const timerRow = el('div', { class: 'tama-ire-timer' },
        el('span', { class: 'tama-ire-clock', 'aria-hidden': 'true' }, '⏰'),
        el('div', { class: 'tama-ire-bar' }, barFill),
        timeNum,
      );

      const field = el('div', { class: `tama-ire-field tama-ire-n${teams.length}` });
      const areas = teams.map((t, i) => {
        const countEl = el('span', { class: 'tama-ire-count' }, '0');
        const basket = el('div', { class: 'tama-ire-basket' },
          el('span', { class: 'tama-ire-basket-emoji', 'aria-hidden': 'true' }, '🧺'),
          countEl,
        );
        const node = el('div', { class: 'tama-ire-area', style: { background: t.color } },
          el('span', { class: 'tama-ire-team-emoji', 'aria-hidden': 'true' }, t.emoji),
          basket,
        );
        const area = { index: i, team: t, node, basket, countEl, balls: [], count: 0 };
        node.addEventListener('pointerdown', (e) => onTap(area, e));
        field.append(node);
        return area;
      });

      const overlay = el('div', { class: 'tama-ire-overlay' });
      const wrap = el('div', { class: 'tama-ire-wrap' }, timerRow, field, overlay);
      ctx.stage.append(wrap);

      function showOverlay(text, big = true) {
        overlay.replaceChildren(el('div', { class: 'tama-ire-overlay-text' + (big ? ' big' : '') }, text));
        overlay.classList.add('show');
      }
      function hideOverlay() {
        overlay.classList.remove('show');
        overlay.replaceChildren();
      }

      // ---- ボール ----
      function spawnBall(area) {
        if (area.balls.length >= MAX_BALLS) return;
        const w = area.node.clientWidth;
        const h = area.node.clientHeight;
        const size = Math.round(Math.max(84, Math.min(120, Math.min(w, h) * 0.24)));
        // かご（下のほう）と チームの絵（左上）を よけた はんいに出す
        const minX = 8, maxX = Math.max(minX, w - size - 8);
        const minY = Math.min(h * 0.12, 60), maxY = Math.max(minY, h * 0.62 - size);
        let x = 0, y = 0;
        for (let tries = 0; tries < 12; tries++) {
          x = minX + Math.random() * (maxX - minX);
          y = minY + Math.random() * (maxY - minY);
          const overlap = area.balls.some((b) => Math.hypot(b.x - x, b.y - y) < size * 0.9);
          if (!overlap) break;
        }
        const inner = el('div', { class: 'tama-ire-ball-inner', style: { animationDelay: `${-Math.random() * 2}s` } });
        const node = el('div', {
          class: 'tama-ire-ball',
          style: { left: `${x}px`, top: `${y}px`, width: `${size}px`, height: `${size}px` },
        }, inner);
        const ball = { node, x, y, size, done: false };
        ball.timer = later(() => removeBall(area, ball, true), BALL_LIFE_MS);
        area.balls.push(ball);
        area.node.append(node);
      }

      function removeBall(area, ball, fade) {
        if (ball.done) return;
        ball.done = true;
        area.balls = area.balls.filter((b) => b !== ball);
        if (fade) {
          ball.node.classList.add('fade');
          later(() => ball.node.remove(), 400);
        } else {
          ball.node.remove();
        }
      }

      function onTap(area, e) {
        e.preventDefault();
        if (!playing || !ctx.isActive()) return;
        const rect = area.node.getBoundingClientRect();
        const px = e.clientX - rect.left;
        const py = e.clientY - rect.top;
        // ちょっと はずれても入るよう、いちばん近いボールを さがす
        let best = null, bestD = Infinity;
        for (const b of area.balls) {
          const d = Math.hypot(b.x + b.size / 2 - px, b.y + b.size / 2 - py);
          if (d < bestD) { bestD = d; best = b; }
        }
        if (!best || bestD > best.size * 0.85) return;
        throwBall(area, best);
      }

      function throwBall(area, ball) {
        clearTimeout(ball.timer);
        timers.delete(ball.timer);
        ball.done = true;
        area.balls = area.balls.filter((b) => b !== ball);
        ctx.sound('tap');
        ctx.addScore(area.index, 1);
        area.count += 1;
        area.countEl.textContent = String(area.count);

        // かごへ とんでいく
        const ar = area.node.getBoundingClientRect();
        const br = area.basket.getBoundingClientRect();
        const tx = br.left - ar.left + br.width / 2 - (ball.x + ball.size / 2);
        const ty = br.top - ar.top + br.height * 0.35 - (ball.y + ball.size / 2);
        ball.node.classList.add('fly');
        ball.node.style.setProperty('--tx', `${tx}px`);
        ball.node.style.setProperty('--ty', `${ty}px`);
        later(() => {
          ball.node.remove();
          area.basket.classList.remove('catch');
          void area.basket.offsetWidth;
          area.basket.classList.add('catch');
        }, 520);
      }

      function clearBalls() {
        areas.forEach((a) => {
          a.balls.forEach((b) => b.node.remove());
          a.balls = [];
        });
      }

      // ---- じかん ----
      function runTimer() {
        return new Promise((resolve) => {
          const t0 = performance.now();
          let lastShown = GAME_SEC;
          let spawnAcc = 0;
          let lastT = t0;
          // さいしょに全チーム同時に1こずつ
          areas.forEach(spawnBall);
          const tick = (now) => {
            if (!ctx.isActive()) return resolve();
            const elapsed = (now - t0) / 1000;
            const left = Math.max(0, GAME_SEC - elapsed);
            barFill.style.width = `${(left / GAME_SEC) * 100}%`;
            const shown = Math.ceil(left);
            if (shown !== lastShown) {
              lastShown = shown;
              timeNum.textContent = String(shown);
              if (shown <= 5) {
                timerRow.classList.add('hurry');
                timeNum.classList.remove('pulse');
                void timeNum.offsetWidth;
                timeNum.classList.add('pulse');
                if (NUM_WORDS[shown]) ctx.speak(NUM_WORDS[shown]);
              }
            }
            spawnAcc += now - lastT;
            lastT = now;
            while (spawnAcc >= SPAWN_MS) {
              spawnAcc -= SPAWN_MS;
              areas.forEach(spawnBall); // どのチームにも同じタイミングで出す
            }
            if (left <= 0) return resolve();
            rafId = requestAnimationFrame(tick);
          };
          rafId = requestAnimationFrame(tick);
        });
      }

      // ---- ながれ ----
      (async () => {
        showOverlay('🧺', true);
        await ctx.speak('ボールを タッチして、かごに いれよう！ みんな いっしょに やるよ');
        if (!ctx.isActive()) return;
        showOverlay('よーい', false);
        await ctx.speak('よーい');
        if (!ctx.isActive()) return;
        for (const n of [3, 2, 1]) {
          showOverlay(String(n), true);
          ctx.sound('flip');
          ctx.speak(NUM_WORDS[n]);
          await ctx.wait(1000);
          if (!ctx.isActive()) return;
        }
        showOverlay('どん！', true);
        ctx.sound('start');
        ctx.speak('どん！');
        playing = true;
        later(hideOverlay, 700);

        await runTimer();
        if (!ctx.isActive()) return;
        playing = false;
        clearBalls();
        ctx.sound('fanfare');
        showOverlay('おしまい！', true);
        await ctx.speak('おしまい！');
        if (!ctx.isActive()) return;
        await ctx.wait(1200);
        if (!ctx.isActive()) return;
        ctx.end();
      })();

      return () => {
        playing = false;
        cancelAnimationFrame(rafId);
        timers.forEach((id) => clearTimeout(id));
        timers.clear();
      };
    },
  });
})();
