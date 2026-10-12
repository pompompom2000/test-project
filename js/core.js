// 共通部品：チーム定義・音声読み上げ・効果音・ゲーム登録
(function () {
  'use strict';

  // 使えるチーム（文字が読めなくても分かるよう、動物と色で区別する）
  const TEAM_PRESETS = [
    { id: 'usagi', name: 'うさぎチーム', emoji: '🐰', color: '#ff6b9a' },
    { id: 'kuma', name: 'くまチーム', emoji: '🐻', color: '#4d8dff' },
    { id: 'kaeru', name: 'かえるチーム', emoji: '🐸', color: '#3cc46b' },
    { id: 'hiyoko', name: 'ひよこチーム', emoji: '🐥', color: '#ffb400' },
  ];

  // ---- 音声読み上げ ----
  let jaVoice = null;
  function pickVoice() {
    if (!('speechSynthesis' in window)) return;
    const voices = speechSynthesis.getVoices();
    jaVoice = voices.find((v) => v.lang === 'ja-JP') || voices.find((v) => v.lang.startsWith('ja')) || null;
  }
  if ('speechSynthesis' in window) {
    pickVoice();
    speechSynthesis.addEventListener('voiceschanged', pickVoice);
  }

  // 文章をやさしく読み上げる。読み終わったら resolve する（音声非対応なら即 resolve）
  function speak(text) {
    return new Promise((resolve) => {
      if (!('speechSynthesis' in window) || !Core.settings.voice) return resolve();
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'ja-JP';
      if (jaVoice) u.voice = jaVoice;
      u.rate = 0.9;
      u.pitch = 1.2;
      let done = false;
      const finish = () => { if (!done) { done = true; resolve(); } };
      u.onend = finish;
      u.onerror = finish;
      // 一部ブラウザで onend が来ないことがあるので保険
      setTimeout(finish, 600 + text.length * 250);
      speechSynthesis.speak(u);
    });
  }

  function stopSpeaking() {
    if ('speechSynthesis' in window) speechSynthesis.cancel();
  }

  // ---- 効果音（WebAudio で合成。音声ファイル不要） ----
  let audioCtx = null;
  function ctx() {
    if (!audioCtx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      audioCtx = new AC();
    }
    if (audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
  }

  function tone(freq, start, dur, type = 'sine', gain = 0.2) {
    const ac = ctx();
    if (!ac) return;
    const t0 = ac.currentTime + start;
    const osc = ac.createOscillator();
    const g = ac.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, t0);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.exponentialRampToValueAtTime(gain, t0 + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    osc.connect(g).connect(ac.destination);
    osc.start(t0);
    osc.stop(t0 + dur + 0.05);
  }

  // type: 'tap' | 'correct' | 'wrong' | 'fanfare' | 'start' | 'flip'
  function sound(type) {
    if (!Core.settings.sound) return;
    switch (type) {
      case 'tap': tone(880, 0, 0.08, 'triangle', 0.15); break;
      case 'flip': tone(600, 0, 0.06, 'triangle', 0.12); tone(900, 0.05, 0.06, 'triangle', 0.12); break;
      case 'correct': tone(784, 0, 0.12, 'triangle'); tone(1047, 0.12, 0.25, 'triangle'); break;
      // 不正解でも怖くない、やわらかい音にする
      case 'wrong': tone(392, 0, 0.18, 'sine', 0.15); tone(330, 0.15, 0.25, 'sine', 0.12); break;
      case 'start': [523, 659, 784].forEach((f, i) => tone(f, i * 0.12, 0.15, 'triangle')); break;
      case 'fanfare': [523, 659, 784, 1047, 784, 1047].forEach((f, i) => tone(f, i * 0.14, i === 5 ? 0.6 : 0.16, 'square', 0.1)); break;
    }
  }

  // ---- 小物 ----
  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') node.className = v;
      else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
      else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
      else if (v !== false && v != null) node.setAttribute(k, v);
    }
    for (const c of children.flat()) {
      if (c == null || c === false) continue;
      node.append(c instanceof Node ? c : document.createTextNode(String(c)));
    }
    return node;
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function wait(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  // ---- ゲーム登録 ----
  const games = [];
  function registerGame(game) {
    games.push(game);
  }

  const Core = {
    TEAM_PRESETS,
    settings: { sound: true, voice: true },
    speak,
    stopSpeaking,
    sound,
    el,
    shuffle,
    wait,
    games,
    registerGame,
  };

  window.Core = Core;
})();
