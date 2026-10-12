// いろ あて クイズ：チーム交代で、いろ・もの・なきごえ の クイズに こたえる
(function () {
  'use strict';

  // ---- もんだいの たね ----
  const COLORS = [
    { name: 'あか', hex: '#ff3b30' },
    { name: 'あお', hex: '#2f7bff' },
    { name: 'きいろ', hex: '#ffd60a' },
    { name: 'みどり', hex: '#34c759' },
    { name: 'むらさき', hex: '#a352e0' },
    { name: 'オレンジ', hex: '#ff9500' },
    { name: 'ピンク', hex: '#ff7eb6' },
  ];

  // いろ別の もの（だれが みても その いろ だと わかる ものだけ）
  const THINGS = {
    red: { adj: 'あかい', items: [
      { e: '🍎', n: 'りんご', fruit: true }, { e: '🍓', n: 'いちご', fruit: true },
      { e: '🍒', n: 'さくらんぼ', fruit: true }, { e: '🍅', n: 'トマト' }] },
    yellow: { adj: 'きいろい', items: [
      { e: '🍌', n: 'バナナ', fruit: true }, { e: '🍋', n: 'レモン', fruit: true },
      { e: '🌻', n: 'ひまわり' }, { e: '🌽', n: 'とうもろこし' }] },
    green: { adj: 'みどりの', items: [
      { e: '🐸', n: 'かえる' }, { e: '🥦', n: 'ブロッコリー' }, { e: '🥒', n: 'きゅうり' }, { e: '🍀', n: 'クローバー' }] },
    purple: { adj: 'むらさきの', items: [
      { e: '🍇', n: 'ぶどう', fruit: true }, { e: '🍆', n: 'なす' }] },
    orange: { adj: 'オレンジいろの', items: [
      { e: '🍊', n: 'みかん', fruit: true }, { e: '🥕', n: 'にんじん' }] },
  };
  // 「〇〇い もの」として きく いろ（ほかの いろは まちがいの せんたくしに つかう）
  const ASK_THING_COLORS = ['red', 'yellow', 'green'];

  const ANIMALS = [
    { e: '🐶', n: 'いぬ', cry: 'ワンワン' },
    { e: '🐱', n: 'ねこ', cry: 'ニャーニャー' },
    { e: '🐮', n: 'うし', cry: 'モーモー' },
    { e: '🐷', n: 'ぶた', cry: 'ブーブー' },
    { e: '🐔', n: 'にわとり', cry: 'コケコッコー' },
    { e: '🐑', n: 'ひつじ', cry: 'メェメェ' },
    { e: '🐴', n: 'うま', cry: 'ヒヒーン' },
    { e: '🐭', n: 'ねずみ', cry: 'チューチュー' },
    { e: '🐸', n: 'かえる', cry: 'ケロケロ' },
  ];

  const sample = (arr, shuffle) => shuffle(arr)[0];

  // ---- もんだい つくり ----
  // 戻り値: { text(画面), say(よみあげ: チーム名の あと), choices:[{key, label|color}], answerKey, answerSay }
  function makeColorQ(shuffle, n) {
    const picks = shuffle(COLORS).slice(0, n);
    const ans = picks[0];
    return {
      text: `${ans.name} は どれかな？`,
      say: `${ans.name} いろ の まる は どれかな？`,
      choices: shuffle(picks).map((c) => ({ key: c.name, color: c.hex })),
      answerKey: ans.name,
      answerSay: `${ans.name} は これ だよ`,
    };
  }

  function makeThingQ(shuffle, n) {
    const colorKey = sample(ASK_THING_COLORS, shuffle);
    const group = THINGS[colorKey];
    // くだもの だけで そろえられるなら「くだもの」と きく
    const fruitOnly = Math.random() < 0.5 && group.items.some((i) => i.fruit);
    const pool = fruitOnly ? group.items.filter((i) => i.fruit) : group.items;
    const ans = sample(pool, shuffle);
    // まちがいの せんたくしは ほかの いろ から 1つずつ
    const others = shuffle(Object.keys(THINGS).filter((k) => k !== colorKey)).slice(0, n - 1).map((k) => {
      const items = THINGS[k].items.filter((i) => !fruitOnly || i.fruit);
      return sample(items.length ? items : THINGS[k].items, shuffle);
    });
    const word = fruitOnly ? 'くだもの' : 'もの';
    return {
      text: `${group.adj} ${word} は どれかな？`,
      say: `${group.adj} ${word} は どれかな？`,
      choices: shuffle([ans, ...others]).map((i) => ({ key: i.e, label: i.e })),
      answerKey: ans.e,
      answerSay: `${group.adj} ${word} は ${ans.n} だよ`,
    };
  }

  function makeAnimalQ(shuffle, n) {
    const picks = shuffle(ANIMALS).slice(0, n);
    const ans = picks[0];
    return {
      text: `「${ans.cry}」 って なく のは だれ？`,
      say: `${ans.cry} って なく のは だれかな？`,
      choices: shuffle(picks).map((a) => ({ key: a.e, label: a.e })),
      answerKey: ans.e,
      answerSay: `${ans.cry} は ${ans.n} さん だよ`,
    };
  }

  const MAKERS = [makeColorQ, makeThingQ, makeAnimalQ];

  Core.registerGame({
    id: 'color-quiz',
    title: 'いろ あて クイズ',
    emoji: '🎨',
    color: '#ffe0f0',
    start(ctx) {
      const { el, teams, shuffle } = ctx;
      const perTeam = teams.length >= 4 ? 3 : 4; // 4チームなら 3もんずつ（ながく なりすぎないように）
      const total = perTeam * teams.length;

      // もんだいの しゅるいを まんべんなく まぜる
      const kinds = [];
      while (kinds.length < total) kinds.push(...shuffle([0, 1, 2]));
      const usedTexts = new Set();
      function nextQuestion(i) {
        let q;
        for (let tries = 0; tries < 10; tries++) {
          q = MAKERS[kinds[i]](shuffle, Math.random() < 0.4 ? 3 : 4);
          if (!usedTexts.has(q.text)) break;
        }
        usedTexts.add(q.text);
        return q;
      }

      let qIndex = 0;
      let turnToken = 0;
      let busy = false;

      // 画面の わく
      const banner = el('div', { class: 'color-quiz-banner' });
      const qText = el('div', { class: 'color-quiz-question' });
      const speakerBtn = el('button', { class: 'color-quiz-speaker', 'aria-label': 'もういちど きく' }, '🔊');
      const choicesBox = el('div', { class: 'color-quiz-choices' });
      const toast = el('div', { class: 'color-quiz-toast', 'aria-live': 'polite' });
      const progress = el('div', { class: 'color-quiz-progress', 'aria-hidden': 'true' });
      const wrap = el('div', { class: 'color-quiz' },
        banner,
        el('div', { class: 'color-quiz-qrow' }, qText, speakerBtn, toast),
        choicesBox,
        progress,
      );
      ctx.stage.append(wrap);

      let current = null; // { q, team, teamIndex, misses, buttons }

      function sayQuestion() {
        if (!current || !ctx.isActive()) return Promise.resolve();
        return ctx.speak(`${current.team.name}さん、${current.q.say}`);
      }

      speakerBtn.addEventListener('click', () => {
        ctx.sound('tap');
        sayQuestion();
      });

      function showToast(text, kind) {
        toast.textContent = text;
        toast.className = `color-quiz-toast color-quiz-toast-${kind} color-quiz-show`;
      }
      function hideToast() {
        toast.className = 'color-quiz-toast';
      }

      function renderProgress() {
        progress.replaceChildren(
          ...Array.from({ length: total }, (_, i) =>
            el('span', {
              class: 'color-quiz-dot' + (i < qIndex ? ' color-quiz-dot-done' : i === qIndex ? ' color-quiz-dot-now' : ''),
              style: { background: i <= qIndex ? teams[i % teams.length].color : '' },
            }),
          ),
        );
      }

      async function startTurn() {
        if (!ctx.isActive()) return;
        const token = ++turnToken;
        const teamIndex = qIndex % teams.length;
        const team = teams[teamIndex];
        const q = nextQuestion(qIndex);

        banner.style.background = team.color;
        banner.replaceChildren(
          el('span', { class: 'color-quiz-banner-emoji' }, team.emoji),
          el('span', { class: 'color-quiz-banner-name' }, `${team.name} の ばん`),
        );
        banner.classList.remove('color-quiz-enter');
        void banner.offsetWidth;
        banner.classList.add('color-quiz-enter');
        qText.textContent = q.text;
        hideToast();
        renderProgress();

        const buttons = q.choices.map((c) => {
          const btn = el('button', {
            class: 'color-quiz-card' + (c.color ? ' color-quiz-card-color' : ''),
            'aria-label': c.color ? c.key : c.label,
            onclick: () => onChoose(token, c, btn),
          }, c.color
            ? el('span', { class: 'color-quiz-circle', style: { background: c.color } })
            : el('span', { class: 'color-quiz-emoji' }, c.label));
          btn.dataset.key = c.key;
          return btn;
        });
        choicesBox.dataset.count = String(buttons.length);
        choicesBox.replaceChildren(...buttons);

        current = { q, team, teamIndex, misses: 0, buttons };
        busy = false;
        await sayQuestion();
      }

      async function onChoose(token, choice, btn) {
        if (!ctx.isActive() || busy || token !== turnToken || btn.disabled) return;
        busy = true;
        const cur = current;

        if (choice.key === cur.q.answerKey) {
          ctx.sound('correct');
          btn.classList.add('color-quiz-correct');
          ctx.addScore(cur.teamIndex, 1);
          showToast('せいかい！ ⭐', 'good');
          await ctx.speak('せいかい！ すごいね！');
          if (!ctx.isActive() || token !== turnToken) return;
          await ctx.wait(500);
          return goNext(token);
        }

        cur.misses += 1;
        ctx.sound('wrong');
        btn.classList.add('color-quiz-tried');
        btn.disabled = true;

        if (cur.misses < 2) {
          showToast('おしい！ もういちど', 'try');
          await ctx.speak('おしい！ もういちど えらんでね');
          if (!ctx.isActive() || token !== turnToken) return;
          hideToast();
          busy = false;
          return;
        }

        // 2かい まちがえたら こたえを ひからせて おしえる
        const answerBtn = cur.buttons.find((b) => b.dataset.key === cur.q.answerKey);
        cur.buttons.forEach((b) => { if (b !== answerBtn) b.classList.add('color-quiz-dim'); });
        if (answerBtn) answerBtn.classList.add('color-quiz-shine');
        showToast('こたえは これ！ ✨', 'try');
        await ctx.speak(`おしい！ ${cur.q.answerSay}`);
        if (!ctx.isActive() || token !== turnToken) return;
        await ctx.wait(900);
        return goNext(token);
      }

      async function goNext(token) {
        if (!ctx.isActive() || token !== turnToken) return;
        qIndex += 1;
        if (qIndex >= total) {
          renderProgress();
          showToast('おしまい！ 🎉', 'good');
          ctx.sound('fanfare');
          await ctx.speak('これで おしまい！ みんな よく できました！');
          if (!ctx.isActive()) return;
          await ctx.wait(400);
          if (ctx.isActive()) ctx.end();
          return;
        }
        startTurn();
      }

      (async () => {
        banner.style.background = '#ffffff';
        banner.replaceChildren(el('span', { class: 'color-quiz-banner-emoji' }, '🎨'));
        qText.textContent = 'いろ あて クイズ！';
        renderProgress();
        await ctx.speak('いろ あて クイズ！ じゅんばんに こたえてね');
        if (!ctx.isActive()) return;
        startTurn();
      })();

      return () => {
        turnToken += 1; // のこっている ひどうき しょりを むこうに する
      };
    },
  });
})();
