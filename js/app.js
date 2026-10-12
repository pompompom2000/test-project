// 画面遷移：タイトル → チームわけ → ゲームえらび → ゲーム → けっか
(function () {
  'use strict';

  const { el, speak, stopSpeaking, sound, TEAM_PRESETS } = Core;
  const app = document.getElementById('app');

  const state = {
    teamCount: 2,
    teams: [],
    currentGame: null,
    cleanup: null,
  };

  function show(...nodes) {
    app.replaceChildren(...nodes);
  }

  function makeTeams(count) {
    return TEAM_PRESETS.slice(0, count).map((t) => ({ ...t, score: 0 }));
  }

  function settingsBar() {
    const toggle = (key, on, off) =>
      el('button', {
        class: 'icon-btn',
        'aria-label': key === 'sound' ? 'こうかおん' : 'よみあげ',
        onclick: (e) => {
          Core.settings[key] = !Core.settings[key];
          e.currentTarget.textContent = Core.settings[key] ? on : off;
          if (key === 'voice' && !Core.settings.voice) stopSpeaking();
        },
      }, Core.settings[key] ? on : off);
    return el('div', { class: 'settings' }, toggle('sound', '🔔', '🔕'), toggle('voice', '🗣️', '🤐'));
  }

  // ---- タイトル ----
  function titleScreen() {
    show(
      el('section', { class: 'screen title-screen' },
        settingsBar(),
        el('div', { class: 'title-emojis', 'aria-hidden': 'true' }, '🐰🐻🐸🐥'),
        el('h1', { class: 'title' }, 'みんなで あそぼ！'),
        el('button', {
          class: 'big-btn primary bounce',
          onclick: () => { sound('start'); teamScreen(); },
        }, '▶ はじめる'),
      ),
    );
  }

  // ---- チームわけ ----
  function teamScreen() {
    const preview = el('div', { class: 'team-preview' });
    const renderPreview = () => {
      preview.replaceChildren(
        ...makeTeams(state.teamCount).map((t) =>
          el('div', { class: 'team-chip', style: { background: t.color } },
            el('span', { class: 'team-emoji' }, t.emoji),
            el('span', { class: 'team-name' }, t.name),
          ),
        ),
      );
    };

    const countButtons = [2, 3, 4].map((n) =>
      el('button', {
        class: 'count-btn' + (n === state.teamCount ? ' selected' : ''),
        onclick: (e) => {
          sound('tap');
          state.teamCount = n;
          countButtons.forEach((b) => b.classList.remove('selected'));
          e.currentTarget.classList.add('selected');
          renderPreview();
          speak(`${n}チームで あそぶよ`);
        },
      }, `${n}`),
    );

    renderPreview();
    show(
      el('section', { class: 'screen' },
        el('button', { class: 'back-btn', onclick: titleScreen, 'aria-label': 'もどる' }, '⬅'),
        el('h2', {}, 'いくつの チームに わける？'),
        el('div', { class: 'count-row' }, countButtons),
        preview,
        el('button', {
          class: 'big-btn primary',
          onclick: () => {
            sound('tap');
            state.teams = makeTeams(state.teamCount);
            gameSelectScreen();
          },
        }, 'けってい！'),
      ),
    );
    speak('いくつの チームに わける？');
  }

  // ---- ゲームえらび ----
  function gameSelectScreen() {
    show(
      el('section', { class: 'screen' },
        el('button', { class: 'back-btn', onclick: teamScreen, 'aria-label': 'もどる' }, '⬅'),
        el('h2', {}, 'どの ゲームで あそぶ？'),
        el('div', { class: 'game-list' },
          Core.games.map((g) =>
            el('button', {
              class: 'game-card',
              style: { background: g.color || '#fff' },
              onclick: () => { sound('start'); startGame(g); },
            },
              el('span', { class: 'game-emoji' }, g.emoji),
              el('span', { class: 'game-title' }, g.title),
            ),
          ),
        ),
      ),
    );
    speak('どの ゲームで あそぶ？');
  }

  // ---- ゲーム ----
  function scoreBar() {
    const bar = el('div', { class: 'scorebar' },
      state.teams.map((t, i) =>
        el('div', { class: 'score', style: { background: t.color }, 'data-team': i },
          el('span', { class: 'team-emoji' }, t.emoji),
          el('span', { class: 'score-num' }, String(t.score)),
        ),
      ),
    );
    return bar;
  }

  function startGame(game) {
    state.teams.forEach((t) => (t.score = 0));
    state.currentGame = game;

    const bar = scoreBar();
    const stage = el('div', { class: 'stage' });
    let active = true;

    const ctx = {
      stage,
      teams: state.teams,
      speak,
      sound,
      el,
      shuffle: Core.shuffle,
      wait: Core.wait,
      isActive: () => active,
      addScore(teamIndex, n = 1) {
        if (!active) return;
        const team = state.teams[teamIndex];
        team.score = Math.max(0, team.score + n);
        const box = bar.querySelector(`[data-team="${teamIndex}"]`);
        box.querySelector('.score-num').textContent = String(team.score);
        box.classList.remove('pop');
        void box.offsetWidth; // アニメーションを毎回やり直す
        box.classList.add('pop');
      },
      end() {
        if (!active) return;
        stopGame();
        resultScreen();
      },
    };

    function stopGame() {
      active = false;
      stopSpeaking();
      if (typeof state.cleanup === 'function') state.cleanup();
      state.cleanup = null;
    }

    show(
      el('section', { class: 'screen game-screen' },
        el('div', { class: 'game-header' },
          el('button', {
            class: 'back-btn inline',
            'aria-label': 'やめる',
            onclick: () => { stopGame(); gameSelectScreen(); },
          }, '✖'),
          bar,
        ),
        stage,
      ),
    );

    state.cleanup = game.start(ctx) || null;
  }

  // ---- けっか ----
  function resultScreen() {
    const max = Math.max(...state.teams.map((t) => t.score));
    const winners = state.teams.filter((t) => t.score === max);
    const ranked = state.teams.slice().sort((a, b) => b.score - a.score);
    const allTie = winners.length === state.teams.length;

    const message = allTie
      ? 'ひきわけ！ みんな すごい！'
      : `${winners.map((w) => w.name).join('と ')}の かち！`;

    show(
      el('section', { class: 'screen result-screen' },
        el('div', { class: 'confetti', 'aria-hidden': 'true' }, '🎉'),
        el('h2', { class: 'result-title' }, message),
        el('div', { class: 'result-list' },
          ranked.map((t) =>
            el('div', {
              class: 'result-row' + (t.score === max ? ' winner' : ''),
              style: { background: t.color },
            },
              el('span', { class: 'team-emoji' }, t.emoji),
              el('span', { class: 'team-name' }, t.name),
              el('span', { class: 'result-score' }, `${t.score}てん`),
              t.score === max ? el('span', { class: 'crown' }, '👑') : null,
            ),
          ),
        ),
        el('p', { class: 'praise' }, 'みんな よく がんばったね！'),
        el('div', { class: 'btn-row' },
          el('button', { class: 'big-btn primary', onclick: () => startGame(state.currentGame) }, '🔁 もういちど'),
          el('button', { class: 'big-btn', onclick: gameSelectScreen }, '🎮 ほかの ゲーム'),
        ),
      ),
    );
    sound('fanfare');
    speak(`${message} みんな よく がんばったね！`);
  }

  titleScreen();

  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }
})();
