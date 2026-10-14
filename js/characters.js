// 体のある キャラクター（SVG）。人間の子も 動物の子も、幼稚園の スモックを着ている。
// 使い方: const c = Core.character('inu', { pose: 'walk' }); parent.append(c);
//         c.setPose('sit'); c.setMood('happy'); c.face('left');
// 大きさは font-size で決まる（絵文字と同じように 1em ≒ 背の高さ）。
(function () {
  'use strict';

  const NS = 'http://www.w3.org/2000/svg';

  // 種類ごとの色と特徴
  const KINDS = {
    'kid-girl': { skin: '#ffdcbf', smock: '#ff8fb1', hair: '#5b3a29', head: 'human', style: 'pigtails' },
    'kid-boy': { skin: '#ffd6b3', smock: '#6aa8ff', hair: '#3b2a20', head: 'human', style: 'short' },
    kid: { skin: '#f6cfa8', smock: '#6cc77a', hair: '#4a2f22', head: 'human', style: 'bob' },
    inu: { fur: '#d9a066', dark: '#a86b3c', smock: '#c98b4f', head: 'inu' },
    neko: { fur: '#f4b04f', dark: '#d98a1f', smock: '#f2a541', head: 'neko' },
    panda: { fur: '#ffffff', dark: '#2f2f35', smock: '#6b6f7a', head: 'panda' },
    kitsune: { fur: '#ef7d3c', dark: '#b8501c', smock: '#e8743b', head: 'kitsune' },
    pen: { fur: '#2f4a6d', dark: '#1e3350', smock: '#3a6ea5', head: 'pen' },
    hiyoko: { fur: '#ffd23f', dark: '#f0b400', smock: '#ffe98a', head: 'hiyoko' },
  };

  // これまでの絵文字から キャラの種類へ
  const FROM_EMOJI = {
    '👧': 'kid-girl', '👦': 'kid-boy', '🧒': 'kid',
    '🐶': 'inu', '🐱': 'neko', '🐼': 'panda', '🦊': 'kitsune', '🐧': 'pen', '🐥': 'hiyoko',
  };

  function svg(tag, attrs = {}, children = []) {
    const n = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
    for (const c of children) n.append(c);
    return n;
  }
  const g = (cls, children, attrs = {}) => svg('g', { class: cls, ...attrs }, children);

  function headParts(k) {
    const c = KINDS[k];
    const skin = c.skin || c.fur;
    const back = [];  // 頭の うしろ（耳・しっぽ・髪）
    const front = []; // 頭の まえ（もよう・鼻）
    let headFill = skin;
    let headStroke = 'none';

    switch (c.head) {
      case 'human':
        if (c.style === 'pigtails') {
          back.push(svg('circle', { cx: 19, cy: 44, r: 10, fill: c.hair }), svg('circle', { cx: 81, cy: 44, r: 10, fill: c.hair }),
            svg('circle', { cx: 26, cy: 38, r: 3.5, fill: '#ff5c8a' }), svg('circle', { cx: 74, cy: 38, r: 3.5, fill: '#ff5c8a' }));
          front.push(svg('path', { d: 'M22 40 Q22 10 50 10 Q78 10 78 40 Q70 26 56 24 Q50 32 40 26 Q28 28 22 40Z', fill: c.hair }));
        } else if (c.style === 'short') {
          front.push(svg('path', { d: 'M22 38 Q20 10 50 9 Q80 10 78 38 Q74 24 64 22 L60 28 L54 22 L46 28 L42 22 Q28 24 22 38Z', fill: c.hair }));
        } else {
          back.push(svg('path', { d: 'M20 40 Q18 8 50 8 Q82 8 80 40 L80 58 Q76 62 72 58 L72 40 L28 40 L28 58 Q24 62 20 58Z', fill: c.hair }));
          front.push(svg('path', { d: 'M22 38 Q22 10 50 10 Q78 10 78 38 Q72 30 50 30 Q28 30 22 38Z', fill: c.hair }));
        }
        break;
      case 'inu':
        back.push(svg('ellipse', { cx: 23, cy: 40, rx: 9, ry: 18, fill: c.dark, transform: 'rotate(18 23 40)' }),
          svg('ellipse', { cx: 77, cy: 40, rx: 9, ry: 18, fill: c.dark, transform: 'rotate(-18 77 40)' }));
        front.push(svg('ellipse', { cx: 50, cy: 54, rx: 13, ry: 9, fill: '#fff4e6' }),
          svg('ellipse', { cx: 63, cy: 30, rx: 7, ry: 6, fill: c.dark, opacity: 0.55 }),
          svg('ellipse', { cx: 50, cy: 49, rx: 4.5, ry: 3.2, fill: '#2b2b2b' }));
        break;
      case 'neko':
        back.push(svg('path', { d: 'M24 26 L22 4 L42 16Z', fill: c.fur }), svg('path', { d: 'M76 26 L78 4 L58 16Z', fill: c.fur }),
          svg('path', { d: 'M27 20 L26 10 L36 16Z', fill: '#ffb3c1' }), svg('path', { d: 'M73 20 L74 10 L64 16Z', fill: '#ffb3c1' }));
        front.push(svg('path', { d: 'M44 15 L46 24 M50 13 L50 23 M56 15 L54 24', stroke: c.dark, 'stroke-width': 3, 'stroke-linecap': 'round', fill: 'none' }),
          svg('path', { d: 'M47 49 L53 49 L50 52Z', fill: '#ff7d93' }),
          svg('path', { d: 'M30 50 L18 47 M30 54 L18 56 M70 50 L82 47 M70 54 L82 56', stroke: '#7a5a3a', 'stroke-width': 1.4, 'stroke-linecap': 'round' }));
        break;
      case 'panda':
        headStroke = '#d9d9de';
        back.push(svg('circle', { cx: 26, cy: 17, r: 10, fill: c.dark }), svg('circle', { cx: 74, cy: 17, r: 10, fill: c.dark }));
        front.push(svg('ellipse', { cx: 39, cy: 42, rx: 8, ry: 10, fill: c.dark, transform: 'rotate(25 39 42)' }),
          svg('ellipse', { cx: 61, cy: 42, rx: 8, ry: 10, fill: c.dark, transform: 'rotate(-25 61 42)' }),
          svg('ellipse', { cx: 50, cy: 51, rx: 4.5, ry: 3, fill: c.dark }));
        break;
      case 'kitsune':
        back.push(svg('path', { d: 'M22 30 L20 2 L44 18Z', fill: c.fur }), svg('path', { d: 'M78 30 L80 2 L56 18Z', fill: c.fur }),
          svg('path', { d: 'M25 22 L24 9 L36 17Z', fill: '#4a2a1a' }), svg('path', { d: 'M75 22 L76 9 L64 17Z', fill: '#4a2a1a' }));
        front.push(svg('path', { d: 'M22 44 Q34 46 50 60 Q66 46 78 44 Q76 66 50 68 Q24 66 22 44Z', fill: '#fff4ea' }),
          svg('ellipse', { cx: 50, cy: 52, rx: 4, ry: 3, fill: '#2b2b2b' }));
        break;
      case 'pen':
        front.push(svg('path', { d: 'M50 26 Q36 18 30 32 Q26 46 34 58 Q42 66 50 66 Q58 66 66 58 Q74 46 70 32 Q64 18 50 26Z', fill: '#ffffff' }),
          svg('path', { d: 'M44 50 L56 50 L50 57Z', fill: '#ff9f1c' }));
        break;
      case 'hiyoko':
        back.push(svg('path', { d: 'M46 14 Q44 4 50 6 Q50 0 54 4 Q58 2 56 12', fill: c.fur, stroke: c.dark, 'stroke-width': 1.5 }));
        front.push(svg('path', { d: 'M45 50 L55 50 L50 56Z', fill: '#ff8c1a' }));
        break;
    }
    return { back, front, headFill, headStroke };
  }

  function build(kind) {
    const c = KINDS[kind];
    const skin = c.skin || c.fur;
    const hand = c.head === 'pen' ? c.fur : skin;
    const foot = c.head === 'pen' || c.head === 'hiyoko' ? '#ff9f1c' : c.head === 'human' ? '#e9edf5' : c.dark;
    const { back, front, headFill, headStroke } = headParts(kind);

    // しっぽ（体の うしろ）
    const tail = [];
    if (kind === 'kitsune') {
      tail.push(svg('path', { d: 'M66 96 Q96 92 94 68 Q90 56 84 66 Q86 84 64 88Z', fill: c.fur }),
        svg('path', { d: 'M94 68 Q90 56 84 66 Q88 70 92 74Z', fill: '#fff4ea' }));
    } else if (kind === 'inu' || kind === 'neko') {
      tail.push(svg('path', { d: 'M66 94 Q84 90 82 74', stroke: c.head === 'inu' ? c.dark : c.fur, 'stroke-width': 6, fill: 'none', 'stroke-linecap': 'round' }));
    } else if (kind === 'panda') {
      tail.push(svg('circle', { cx: 68, cy: 96, r: 5, fill: '#fff', stroke: '#d9d9de' }));
    }

    const leg = (x) => g('chr-leg', [
      svg('rect', { x, y: 96, width: 11, height: 24, rx: 5, fill: c.head === 'human' ? '#ffffff' : skin, stroke: c.head === 'panda' ? '#d9d9de' : 'none' }),
      svg('ellipse', { cx: x + 5.5, cy: 122, rx: 8, ry: 5, fill: foot }),
    ]);
    const arm = (x, side) => g(`chr-arm chr-arm-${side}`, [
      svg('rect', { x, y: 67, width: 10, height: 26, rx: 5, fill: c.smock }),
      svg('circle', { cx: x + 5, cy: 94, r: 5.5, fill: hand, stroke: c.head === 'panda' ? '#d9d9de' : 'none' }),
    ]);

    const eyes = g('chr-eyes', [
      g('chr-eyes-open', [
        svg('circle', { cx: 40, cy: 42, r: 3.8, fill: c.head === 'panda' ? '#fff' : '#2b2b2b' }),
        svg('circle', { cx: 60, cy: 42, r: 3.8, fill: c.head === 'panda' ? '#fff' : '#2b2b2b' }),
        svg('circle', { cx: 41.2, cy: 40.8, r: 1.2, fill: c.head === 'panda' ? '#2b2b2b' : '#fff' }),
        svg('circle', { cx: 61.2, cy: 40.8, r: 1.2, fill: c.head === 'panda' ? '#2b2b2b' : '#fff' }),
      ]),
      g('chr-eyes-happy', [
        svg('path', { d: 'M35 44 Q40 37 45 44 M55 44 Q60 37 65 44', stroke: c.head === 'panda' ? '#fff' : '#2b2b2b', 'stroke-width': 3, fill: 'none', 'stroke-linecap': 'round' }),
      ]),
    ]);
    const mouthY = c.head === 'pen' || c.head === 'hiyoko' ? 60 : 57;
    const mouth = g('chr-mouth', [
      svg('path', { class: 'chr-mouth-smile', d: `M44 ${mouthY} Q50 ${mouthY + 5} 56 ${mouthY}`, stroke: '#7a3b2e', 'stroke-width': 2.5, fill: 'none', 'stroke-linecap': 'round' }),
      svg('path', { class: 'chr-mouth-open', d: `M44 ${mouthY - 1} Q50 ${mouthY + 9} 56 ${mouthY - 1}Z`, fill: '#c2414b' }),
      svg('path', { class: 'chr-mouth-sad', d: `M44 ${mouthY + 4} Q50 ${mouthY - 2} 56 ${mouthY + 4}`, stroke: '#7a3b2e', 'stroke-width': 2.5, fill: 'none', 'stroke-linecap': 'round' }),
    ]);
    const tears = g('chr-tears', [
      svg('path', { d: 'M36 48 Q33 54 36 56 Q39 54 36 48Z', fill: '#6ec6ff' }),
      svg('path', { d: 'M64 48 Q61 54 64 56 Q67 54 64 48Z', fill: '#6ec6ff' }),
    ]);
    const cheeks = c.head === 'pen' ? [] : [
      svg('circle', { cx: 32, cy: 52, r: 4.5, fill: '#ff8fa3', opacity: 0.45 }),
      svg('circle', { cx: 68, cy: 52, r: 4.5, fill: '#ff8fa3', opacity: 0.45 }),
    ];

    const root = svg('svg', { viewBox: '0 0 100 140', class: 'chr-svg', 'aria-hidden': 'true' }, [
      g('chr-shadow', [svg('ellipse', { cx: 50, cy: 132, rx: 26, ry: 5, fill: 'rgba(0,0,0,0.15)' })]),
      g('chr-figure', [
        g('chr-tail', tail),
        g('chr-legs', [leg(37), leg(52)]),
        // スモック（えり と ポケットつき）
        g('chr-body', [
          svg('path', { d: 'M34 64 Q50 60 66 64 L74 100 Q50 106 26 100Z', fill: c.smock }),
          svg('path', { d: 'M42 63 L50 72 L58 63', fill: 'none', stroke: '#ffffff', 'stroke-width': 3.5, 'stroke-linejoin': 'round' }),
          svg('rect', { x: 53, y: 82, width: 11, height: 9, rx: 2.5, fill: 'rgba(255,255,255,0.55)' }),
          svg('circle', { cx: 39, cy: 80, r: 3.6, fill: '#ffe066' }),
        ]),
        arm(23, 'l'), arm(67, 'r'),
        g('chr-head', [
          ...back,
          svg('circle', { cx: 50, cy: 42, r: 28, fill: headFill, stroke: headStroke, 'stroke-width': 1.5 }),
          ...front, ...cheeks, eyes, mouth, tears,
        ]),
      ]),
    ]);
    return root;
  }

  const POSES = ['stand', 'walk', 'sit', 'slide', 'climb', 'wave', 'cheer', 'sad', 'hold'];
  const MOODS = ['normal', 'happy', 'sad', 'wow'];

  function character(kindOrEmoji, opts = {}) {
    const kind = KINDS[kindOrEmoji] ? kindOrEmoji : FROM_EMOJI[kindOrEmoji] || 'kid';
    const wrap = document.createElement('span');
    wrap.className = `chr chr-${kind}`;
    wrap.dataset.kind = kind;
    wrap.append(build(kind));
    wrap.setPose = (p) => {
      POSES.forEach((x) => wrap.classList.remove(`pose-${x}`));
      wrap.classList.add(`pose-${POSES.includes(p) ? p : 'stand'}`);
      return wrap;
    };
    wrap.setMood = (m) => {
      MOODS.forEach((x) => wrap.classList.remove(`mood-${x}`));
      wrap.classList.add(`mood-${MOODS.includes(m) ? m : 'normal'}`);
      return wrap;
    };
    wrap.face = (dir) => { wrap.classList.toggle('face-left', dir === 'left'); return wrap; };
    wrap.setPose(opts.pose || 'stand');
    wrap.setMood(opts.mood || 'normal');
    if (opts.face) wrap.face(opts.face);
    if (opts.size) wrap.style.fontSize = typeof opts.size === 'number' ? opts.size + 'px' : opts.size;
    return wrap;
  }

  Core.character = character;
  Core.characterKind = (kindOrEmoji) => (KINDS[kindOrEmoji] ? kindOrEmoji : FROM_EMOJI[kindOrEmoji] || null);
  Core.CHARACTER_KINDS = Object.keys(KINDS);
  Core.CHARACTER_POSES = POSES;
})();
