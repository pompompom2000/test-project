/** 画面の組み立てと入出力。判定ロジックは engine.js 側。 */

const STORAGE_KEY = 'domeru-yoso:v2';

const state = { surfaceKey: 'turf', stateKey: 'yielding', courseKey: '' };

const $ = (sel) => document.querySelector(sel);
const rowsEl = () => $('#horse-rows');

const esc = (v) =>
  v === undefined || v === null
    ? ''
    : String(v).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

/* ---------- レース条件 ---------- */

function buildSegmented(container, items, selectedKey, onSelect) {
  container.innerHTML = '';
  items.forEach((item) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'seg';
    btn.textContent = item.label;
    btn.setAttribute('aria-pressed', String(item.key === selectedKey));
    btn.addEventListener('click', () => onSelect(item.key));
    container.appendChild(btn);
  });
}

function renderConditions() {
  buildSegmented($('#surface-group'), SURFACES, state.surfaceKey, (key) => {
    state.surfaceKey = key;
    renderConditions();
    save();
  });
  buildSegmented($('#state-group'), TRACK_STATES, state.stateKey, (key) => {
    state.stateKey = key;
    renderConditions();
    save();
  });
  $('#surface-insight').textContent = surfaceInsight(state);
  const course = COURSE_DB[state.courseKey];
  $('#course-note').textContent = course ? course.note : '';
  document.body.dataset.mud = stateByKey(state.stateKey).mud >= 0.8 ? 'heavy' : 'light';
}

/* ---------- 出走馬 ---------- */

const FIELDS = [
  { key: 'name', label: '馬名', type: 'text', placeholder: '馬名' },
  { key: 'sire', label: '種牡馬（父）', type: 'text', placeholder: '例：キズナ', list: 'sire-list' },
  { key: 'jockey', label: '騎手', type: 'text', placeholder: '例：ルメール' },
  { key: 'trainer', label: '調教師', type: 'text', placeholder: '例：木村' },
  { key: 'post', label: '枠番', type: 'number', min: 1, max: 8 },
  { key: 'weight', label: '馬体重(kg)', type: 'number', min: 300, max: 700, step: 2 },
  { key: 'odds', label: '単勝オッズ', type: 'number', min: 1, step: 0.1 },
  { key: 'gaikyu', label: '外厩先', type: 'text', placeholder: '例：ノーザンＦ天栄', list: 'gaikyu-list' },
];

function addRow(data = {}) {
  const card = document.createElement('div');
  card.className = 'horse-input';
  const inputs = FIELDS.map(
    (f) => `
      <label class="field">
        <span class="field-label">${f.label}</span>
        <input type="${f.type}" class="f-${f.key}" ${f.list ? `list="${f.list}"` : ''}
          ${f.min !== undefined ? `min="${f.min}"` : ''} ${f.max !== undefined ? `max="${f.max}"` : ''}
          ${f.step ? `step="${f.step}"` : ''}
          placeholder="${f.placeholder || '—'}" value="${esc(data[f.key])}">
      </label>`
  ).join('');

  card.innerHTML = `
    <div class="horse-input-head">
      <span class="num-badge"></span>
      <button type="button" class="btn-del" aria-label="この馬を削除">×</button>
    </div>
    <div class="field-grid">
      ${inputs}
      <label class="field">
        <span class="field-label">性別</span>
        <select class="f-sex">
          <option value="">—</option>
          ${SEXES.map((s) => `<option value="${s}"${data.sex === s ? ' selected' : ''}>${s}</option>`).join('')}
        </select>
      </label>
      <label class="field">
        <span class="field-label">厩舎コメント（道悪）</span>
        <select class="f-commentWet">
          <option value="">—</option>
          <option value="welcome"${data.commentWet === 'welcome' ? ' selected' : ''}>道悪歓迎</option>
          <option value="avoid"${data.commentWet === 'avoid' ? ' selected' : ''}>良馬場希望</option>
        </select>
      </label>
      <label class="field">
        <span class="field-label">厩舎コメント（仕上がり）</span>
        <select class="f-commentCondition">
          <option value="">—</option>
          <option value="sharp"${data.commentCondition === 'sharp' ? ' selected' : ''}>良好</option>
          <option value="doubt"${data.commentCondition === 'doubt' ? ' selected' : ''}>不安</option>
        </select>
      </label>
      <label class="field field-check">
        <input type="checkbox" class="f-layoff"${data.layoff ? ' checked' : ''}>
        <span>休み明け</span>
      </label>
      <label class="field">
        <span class="field-label">脚質</span>
        <select class="f-style">
          <option value="">—</option>
          ${RUN_STYLES.map((s) => `<option value="${s}"${data.style === s ? ' selected' : ''}>${s}</option>`).join('')}
        </select>
      </label>
      <label class="field field-pair">
        <span class="field-label">良馬場 出走 / 3着内</span>
        <span class="pair">
          <input type="number" class="f-firmStarts" min="0" max="99" placeholder="0" value="${esc(data.firmStarts)}">
          <span>/</span>
          <input type="number" class="f-firmPlaces" min="0" max="99" placeholder="0" value="${esc(data.firmPlaces)}">
        </span>
      </label>
      <label class="field field-pair">
        <span class="field-label">道悪 出走 / 3着内</span>
        <span class="pair">
          <input type="number" class="f-mudStarts" min="0" max="99" placeholder="0" value="${esc(data.mudStarts)}">
          <span>/</span>
          <input type="number" class="f-mudPlaces" min="0" max="99" placeholder="0" value="${esc(data.mudPlaces)}">
        </span>
      </label>
    </div>
  `;
  card.querySelector('.btn-del').addEventListener('click', () => {
    card.remove();
    renumber();
    save();
  });
  card.addEventListener('input', save);
  card.addEventListener('change', save);
  rowsEl().appendChild(card);
  renumber();
  return card;
}

function renumber() {
  [...rowsEl().children].forEach((card, i) => {
    card.querySelector('.num-badge').textContent = i + 1;
  });
}

const numOf = (el) => {
  const n = Number(el.value);
  return el.value !== '' && Number.isFinite(n) ? n : 0;
};

function readHorses() {
  return [...rowsEl().children]
    .map((card, i) => {
      const val = (cls) => card.querySelector(`.f-${cls}`).value.trim();
      const num = (cls) => numOf(card.querySelector(`.f-${cls}`));
      return {
        no: i + 1,
        name: val('name'),
        sire: val('sire'),
        jockey: val('jockey'),
        trainer: val('trainer'),
        sex: val('sex') || null,
        style: val('style') || null,
        post: num('post') || null,
        weight: num('weight'),
        odds: num('odds'),
        gaikyu: val('gaikyu'),
        layoff: card.querySelector('.f-layoff').checked,
        commentWet: val('commentWet') || null,
        commentCondition: val('commentCondition') || null,
        firmStarts: num('firmStarts'),
        firmPlaces: num('firmPlaces'),
        mudStarts: num('mudStarts'),
        mudPlaces: num('mudPlaces'),
      };
    })
    .filter((h) => h.name || h.sire)
    .map((h) => ({
      ...h,
      firmPlaces: Math.min(h.firmPlaces, h.firmStarts),
      mudPlaces: Math.min(h.mudPlaces, h.mudStarts),
      comment:
        h.commentWet || h.commentCondition
          ? { wet: h.commentWet, condition: h.commentCondition }
          : null,
    }));
}

/* ---------- 本日の傾向 ---------- */

const TREND_FIELDS = ['sires', 'jockeys', 'trainers', 'posts', 'styles', 'popularity'];

function readTrendInput() {
  const obj = { meeting: $('#trend-meeting').value.trim() };
  TREND_FIELDS.forEach((k) => {
    obj[k] = $(`#trend-${k}`).value;
  });
  return obj;
}

function renderTrendReadout() {
  const input = readTrendInput();
  const trend = parseTrend(input);
  const lines = trendSummary(trend) || [];
  const bias = popularityBias(trend.popularity);
  const el = $('#trend-readout');

  if (!lines.length && !bias) {
    el.innerHTML = '';
    return;
  }
  el.innerHTML = `
    <div class="trend-summary">
      ${input.meeting ? `<p class="trend-meeting">${esc(input.meeting)}</p>` : ''}
      ${lines.map((l) => `<p>${esc(l)}</p>`).join('')}
      ${bias ? `<p class="bias bias-${bias.level}">${esc(bias.note)}</p>` : ''}
    </div>
  `;
}

const TREND_SAMPLE = {
  meeting: '4回中山6日目 2026/9/20（競馬ラボ「本日の傾向」より）',
  sires: 'サリオス\nアルアイン\nStarspan\nアドマイヤマーズ\nサリオス\nファインニードル\nエフフォーリア\nルーラーシップ\nグローリーヴェイズ\nシルバーステート\nレイデオロ\nシルバーステート',
  jockeys: '三浦皇成 2.0.0.3\n津村明秀 1.2.1.3\nC.ルメール 3.0.0.3',
  trainers: '',
  posts: '7,2,5\n8,8,2\n3,6,3\n1,7,1',
  styles: '',
  popularity: '1,5,8\n1,7,6\n2,3,7\n7,9,6',
};

/* ---------- 判定結果 ---------- */

function renderResult() {
  const horses = readHorses();
  const el = $('#result');

  if (!horses.length) {
    el.innerHTML = '<p class="empty">出走馬を1頭以上入力してください（馬名か種牡馬のどちらかがあればOK）。</p>';
    return;
  }

  const trendInput = readTrendInput();
  const trend = parseTrend(trendInput);
  const race = {
    surfaceKey: state.surfaceKey,
    stateKey: state.stateKey,
    course: COURSE_DB[state.courseKey] || null,
    trend,
    popularity: trend.popularity,
  };

  const { horses: ranked, shakeUp, state: trackState, popBias } = evaluateRace(horses, race);
  const stance = raceStance(race, shakeUp);
  const surfaceLabel = SURFACES.find((s) => s.key === state.surfaceKey).label;
  const risers = ranked.filter((h) => h.rankShift > 0);
  const fallers = ranked.filter((h) => h.rankShift < 0);
  const labelOf = (h) => `${h.no}. ${h.name || h.sire}`;

  el.innerHTML = `
    <div class="race-summary stance-${stance.level}">
      <div class="race-summary-head">
        <span class="race-chip">${surfaceLabel}・${trackState.label}</span>
        <div class="shake">
          <span class="shake-label">波乱度</span>
          <span class="shake-bar"><span style="width:${shakeUp}%"></span></span>
          <span class="shake-value">${shakeUp}</span>
        </div>
      </div>
      <h3>${stance.title}</h3>
      <p>${stance.body}</p>
      <p class="race-insight">${surfaceInsight(race)}</p>
      ${popBias ? `<p class="bias bias-${popBias.level}">${esc(popBias.note)}</p>` : ''}
      ${
        risers.length || fallers.length
          ? `<p class="shift-summary">
              ${risers.length ? `<strong class="up">道悪で評価を上げた馬</strong>：${risers.map(labelOf).map(esc).join('、')}` : ''}
              ${risers.length && fallers.length ? '<br>' : ''}
              ${fallers.length ? `<strong class="down">評価を下げた馬</strong>：${fallers.map(labelOf).map(esc).join('、')}` : ''}
            </p>`
          : ''
      }
    </div>
    <ol class="horse-results">${ranked.map(renderHorse).join('')}</ol>
  `;
}

function renderHorse(h) {
  const mud = stateByKey(state.stateKey).mud;
  const shift =
    h.rankShift > 0
      ? `<span class="shift up">▲${h.rankShift}</span>`
      : h.rankShift < 0
      ? `<span class="shift down">▼${Math.abs(h.rankShift)}</span>`
      : '<span class="shift flat">→</span>';

  const tags = [
    ...h.sireInfo.tags,
    ...h.courseInfo.tags,
    ...h.gaikyuInfo.tags,
    ...h.commentInfo.tags,
    ...h.trendInfo.tags,
  ]
    .map((t) => `<span class="tag ${t.tone}">${esc(t.label)}</span>`)
    .join('');

  const factors = [
    { label: '血統', value: h.sireInfo.value, note: h.sireInfo.summary },
    { label: '馬体重', value: h.weightInfo.value * mud, note: h.weightInfo.note },
    { label: '道悪実績', value: h.recordInfo.value * mud, note: h.recordInfo.note },
    { label: 'コース傾向', value: h.courseInfo.value, note: h.courseInfo.note },
    { label: '外厩', value: h.gaikyuInfo.value, note: h.gaikyuInfo.note },
    { label: '厩舎コメント', value: h.commentInfo.value, note: h.commentInfo.note },
    { label: '当日の傾向', value: h.trendInfo.value, note: h.trendInfo.note },
  ];

  return `
    <li class="horse-card">
      <div class="horse-head">
        <span class="mark mark-${markClass(h.mark.mark)}">${h.mark.mark}</span>
        <div class="horse-title">
          <span class="horse-name">${esc(h.no)}. ${esc(h.name || '（馬名未入力）')}</span>
          <span class="horse-meta">${[
            h.sire ? `父${esc(h.sire)}` : '種牡馬未入力',
            h.sex ? esc(h.sex) : '',
            h.jockey ? esc(h.jockey) : '',
            h.post ? `${esc(h.post)}枠` : '',
            h.style ? esc(h.style) : '',
            h.weight ? `${esc(h.weight)}kg` : '',
          h.marketRank ? `市場${esc(h.marketRank)}番人気` : '',
          ]
            .filter(Boolean)
            .join('・')}</span>
        </div>
        <div class="horse-score">
          <span class="score-value">${Math.round(h.score)}</span>
          <span class="score-label">${h.mark.label}</span>
        </div>
      </div>
      <div class="score-bar"><span style="width:${h.score}%"></span></div>
      <div class="horse-shift">良馬場評価 ${h.firmRank}位 → この馬場 ${h.rank}位 ${shift}${
        h.valueGap > 2
          ? ` <span class="value up">妙味あり（市場より${h.valueGap}枚上の評価）</span>`
          : h.valueGap < -2
          ? ` <span class="value down">人気先行（市場より${Math.abs(h.valueGap)}枚下の評価）</span>`
          : ''
      }</div>
      ${tags ? `<div class="tags">${tags}</div>` : ''}
      <ul class="factors">${factors.map(renderFactor).join('')}</ul>
      ${h.sireInfo.note ? `<p class="sire-note"><strong>${esc(h.sire)}</strong>：${esc(h.sireInfo.note)}</p>` : ''}
    </li>
  `;
}

function renderFactor(f) {
  const v = Math.round(f.value * 10) / 10;
  const tone = v > 0.5 ? 'plus' : v < -0.5 ? 'minus' : 'flat';
  return `<li>
    <span class="factor-label">${esc(f.label)}</span>
    <span class="factor-value ${tone}">${v > 0 ? `+${v}` : v}</span>
    <span class="factor-note">${esc(f.note)}</span>
  </li>`;
}

const markClass = (mark) => ({ '◎': 'honmei', '○': 'taiko', '▲': 'tanana', '△': 'osae', '×': 'kiru' }[mark] || 'osae');

/* ---------- 保存 / サンプル ---------- */

function save() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ ...state, horses: readHorses(), trend: readTrendInput() })
    );
  } catch (e) {
    /* プライベートウィンドウなどでは保存できない。動作は継続する。 */
  }
  renderTrendReadout();
}

function restore() {
  let saved = null;
  try {
    saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
  } catch (e) {
    saved = null;
  }
  if (saved && SURFACES.some((s) => s.key === saved.surfaceKey)) state.surfaceKey = saved.surfaceKey;
  if (saved && TRACK_STATES.some((s) => s.key === saved.stateKey)) state.stateKey = saved.stateKey;
  if (saved && saved.courseKey && COURSE_DB[saved.courseKey]) state.courseKey = saved.courseKey;

  if (saved && saved.trend) {
    $('#trend-meeting').value = saved.trend.meeting || '';
    TREND_FIELDS.forEach((k) => {
      $(`#trend-${k}`).value = saved.trend[k] || '';
    });
  }

  const horses = saved && Array.isArray(saved.horses) && saved.horses.length ? saved.horses : null;
  if (horses) horses.forEach(addRow);
  else for (let i = 0; i < 3; i += 1) addRow();
}

const SAMPLE = [
  { name: 'サンプルA', sex: '牡', sire: 'キズナ', jockey: '', post: 2, style: '先行', weight: 486, firmStarts: 10, firmPlaces: 3, mudStarts: 4, mudPlaces: 3 },
  { name: 'サンプルB', sex: '牝', sire: 'ディープインパクト', jockey: '', post: 4, style: '差し', weight: 442, firmStarts: 12, firmPlaces: 7, mudStarts: 2, mudPlaces: 0 },
  { name: 'サンプルC', sex: '牡', sire: 'ハービンジャー', jockey: '', post: 5, style: '追込', weight: 508, firmStarts: 8, firmPlaces: 2, mudStarts: 3, mudPlaces: 2 },
  { name: 'サンプルD', sex: '牡', sire: 'ジャスタウェイ', jockey: '', post: 7, style: '先行', weight: 470, firmStarts: 15, firmPlaces: 8, mudStarts: 5, mudPlaces: 1 },
  { name: 'サンプルE', sex: '牝', sire: 'モズアスコット', jockey: '', post: 8, style: '逃げ', weight: 460, firmStarts: 6, firmPlaces: 1, mudStarts: 3, mudPlaces: 2 },
];

/* ---------- 初期化 ---------- */

function init() {
  $('#sire-list').innerHTML = allSireNames().map((n) => `<option value="${esc(n)}"></option>`).join('');
  $('#gaikyu-list').innerHTML = allGaikyuNames().map((n) => `<option value="${esc(n)}"></option>`).join('');

  const courseSelect = $('#course-select');
  courseSelect.innerHTML =
    '<option value="">指定しない</option>' +
    courseOptions().map((c) => `<option value="${esc(c.key)}">${esc(c.label)}</option>`).join('');

  restore();
  courseSelect.value = state.courseKey;
  courseSelect.addEventListener('change', () => {
    state.courseKey = courseSelect.value;
    renderConditions();
    save();
  });
  renderConditions();
  renderTrendReadout();

  TREND_FIELDS.concat(['meeting']).forEach((k) => {
    $(`#trend-${k}`).addEventListener('input', save);
  });

  $('#add-row').addEventListener('click', () => {
    addRow();
    save();
  });
  $('#clear-rows').addEventListener('click', () => {
    rowsEl().innerHTML = '';
    for (let i = 0; i < 3; i += 1) addRow();
    $('#result').innerHTML = '';
    save();
  });
  $('#load-sample').addEventListener('click', () => {
    rowsEl().innerHTML = '';
    SAMPLE.forEach(addRow);
    save();
    renderResult();
  });
  $('#load-trend-sample').addEventListener('click', () => {
    $('#trend-meeting').value = TREND_SAMPLE.meeting;
    TREND_FIELDS.forEach((k) => {
      $(`#trend-${k}`).value = TREND_SAMPLE[k];
    });
    save();
  });
  $('#clear-trend').addEventListener('click', () => {
    $('#trend-meeting').value = '';
    TREND_FIELDS.forEach((k) => {
      $(`#trend-${k}`).value = '';
    });
    save();
  });
  $('#evaluate').addEventListener('click', renderResult);
}

document.addEventListener('DOMContentLoaded', init);
