/* ============================================================
   The Forge of Hephaestus — Frontend Game Logic
   ============================================================ */

const PLAYER = 1;
const AI = -1;
const BOARD_SIZE = 8;

let state = null;
let animating = false;

// ── DOM references ──────────────────────────────────────────
const boardEl     = document.getElementById('board');
const statusEl    = document.getElementById('status');
const playerScore = document.getElementById('player-score');
const aiScore     = document.getElementById('ai-score');
const turnDot     = document.getElementById('turn-dot');
const turnName    = document.getElementById('turn-name');
const aiStats     = document.getElementById('ai-stats');
const logEl       = document.getElementById('log');
const btnNew      = document.getElementById('btn-new');
const depthInput  = document.getElementById('depth-input');
const modal       = document.getElementById('modal');
const modalIcon   = document.getElementById('modal-icon');
const modalTitle  = document.getElementById('modal-title');
const modalMsg    = document.getElementById('modal-msg');
const modalNew    = document.getElementById('modal-new');

// ── Init ────────────────────────────────────────────────────
function buildLabels() {
  const colLabels = document.getElementById('col-labels');
  const rowLabels = document.getElementById('row-labels');
  for (let c = 0; c < BOARD_SIZE; c++) {
    const el = document.createElement('div');
    el.className = 'col-label';
    el.textContent = String.fromCharCode(65 + c);
    colLabels.appendChild(el);
  }
  for (let r = 0; r < BOARD_SIZE; r++) {
    const el = document.createElement('div');
    el.className = 'row-label';
    el.textContent = r + 1;
    rowLabels.appendChild(el);
  }
}

function buildBoard() {
  boardEl.innerHTML = '';
  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = document.createElement('div');
      cell.className = 'cell';
      cell.dataset.r = r;
      cell.dataset.c = c;
      cell.addEventListener('click', onCellClick);
      boardEl.appendChild(cell);
    }
  }
}

function getCell(r, c) {
  return boardEl.querySelector(`.cell[data-r="${r}"][data-c="${c}"]`);
}

// ── Render ──────────────────────────────────────────────────
function renderState(s, flipCells = [], newMove = null) {
  state = s;
  const legalSet = new Set(s.legal_moves.map(([r, c]) => `${r},${c}`));
  const anvilSet  = new Set(s.anvil_squares.map(([r, c]) => `${r},${c}`));
  const crucSet   = new Set(s.crucible_squares.map(([r, c]) => `${r},${c}`));
  const lastMove  = s.last_move ? `${s.last_move[0]},${s.last_move[1]}` : null;
  const flipSet   = new Set(flipCells.map(([r, c]) => `${r},${c}`));

  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const key  = `${r},${c}`;
      const cell = getCell(r, c);
      const val  = s.board[r][c];

      // Base class
      cell.className = 'cell';
      if (s.game_over || s.current_player === AI) cell.classList.add('no-click');
      if (anvilSet.has(key))  cell.classList.add('anvil');
      if (crucSet.has(key))   cell.classList.add('crucible');
      if (lastMove === key)   cell.classList.add('last-move');
      else if (legalSet.has(key)) cell.classList.add('legal');

      cell.innerHTML = '';

      // Badge
      if (anvilSet.has(key)) {
        const badge = document.createElement('span');
        badge.className = 'cell-badge';
        badge.textContent = '🏛️';
        cell.appendChild(badge);
      } else if (crucSet.has(key)) {
        const badge = document.createElement('span');
        badge.className = 'cell-badge';
        badge.textContent = '💥';
        cell.appendChild(badge);
      }

      // Piece or legal dot
      if (val === PLAYER || val === AI) {
        const piece = document.createElement('div');
        piece.className = 'piece ' + (val === PLAYER ? 'player-piece' : 'ai-piece');
        piece.textContent = val === PLAYER ? '🔥' : '🌊';
        if (flipSet.has(key)) piece.classList.add('flip-anim');
        if (newMove && newMove[0] === r && newMove[1] === c) piece.classList.add('place-anim');
        cell.appendChild(piece);
      } else if (legalSet.has(key)) {
        const dot = document.createElement('div');
        dot.className = 'legal-dot';
        cell.appendChild(dot);
      }
    }
  }

  // Scores
  playerScore.textContent = s.player_score;
  aiScore.textContent     = s.ai_score;

  // Turn
  if (s.game_over) {
    turnDot.style.background = '#888';
    turnName.textContent = 'Game Over';
    turnName.style.color = 'var(--muted)';
  } else if (s.current_player === PLAYER) {
    turnDot.style.background = 'var(--player)';
    turnName.textContent = 'Hephaestus (Player)';
    turnName.style.color = 'var(--player)';
  } else {
    turnDot.style.background = 'var(--ai)';
    turnName.textContent = "Poseidon's Champion (AI)";
    turnName.style.color = 'var(--ai)';
  }

  // AI stats
  const st = s.ai_stats;
  aiStats.innerHTML = `Nodes: ${st.nodes.toLocaleString()} &nbsp;|&nbsp; Pruned: ${st.pruned.toLocaleString()} &nbsp;|&nbsp; Time: ${st.time.toFixed(2)}s`;

  // Status message
  if (!s.game_over) {
    if (s.current_player === PLAYER) {
      statusEl.textContent = 'Your turn — Hephaestus. Select a highlighted cell.';
    } else {
      statusEl.textContent = "🤖 Poseidon's Champion is forging a strategy…";
    }
  }

  // Depth sync
  depthInput.value = s.ai_depth;
}

function appendLog(entry) {
  const div = document.createElement('div');
  div.textContent = entry;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

function buildLogEntry(player, r, c, flips, crucible_squares) {
  const crucSet = new Set(crucible_squares.map(([rr, cc]) => `${rr},${cc}`));
  const symbol = player === PLAYER ? '🔥' : '🌊';
  const name   = player === PLAYER ? 'Hephaestus' : 'AI';
  const coord  = String.fromCharCode(65 + c) + (r + 1);
  const crucible = crucSet.has(`${r},${c}`) ? ' (Crucible!)' : '';
  const flipText = flips.length > 0 ? ` [${flips.length} flipped]` : '';
  return `${symbol} ${name} → ${coord}${crucible}${flipText}`;
}

// ── API helpers ─────────────────────────────────────────────
async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  return res.json();
}

// ── Flow ────────────────────────────────────────────────────
async function loadState() {
  const s = await api('/api/state');
  renderState(s);
  // Rebuild log from history
  logEl.innerHTML = '';
  for (const entry of s.move_history) {
    const flips = [...entry.standard_flips, ...entry.crucible_flips];
    appendLog(buildLogEntry(entry.player, entry.pos[0], entry.pos[1], flips, s.crucible_squares));
  }
  if (s.game_over) showGameOver(s);
}

async function onCellClick(e) {
  if (animating || !state || state.game_over || state.current_player !== PLAYER) return;
  const r = parseInt(e.currentTarget.dataset.r);
  const c = parseInt(e.currentTarget.dataset.c);
  const legalSet = new Set(state.legal_moves.map(([rr, cc]) => `${rr},${cc}`));
  if (!legalSet.has(`${r},${c}`)) {
    statusEl.textContent = '❌ Invalid move! Select a highlighted cell.';
    return;
  }

  animating = true;
  setInteractive(false);

  const data = await api('/api/move', 'POST', { row: r, col: c });
  if (data.error) { statusEl.textContent = '❌ ' + data.error; animating = false; setInteractive(true); return; }

  const flips = data.flips || [];
  appendLog(buildLogEntry(PLAYER, r, c, flips, data.crucible_squares));
  renderState(data, flips, [r, c]);

  if (data.pass === 'ai') {
    statusEl.textContent = "⏭️ Poseidon's Champion has no moves. You go again!";
    animating = false;
    setInteractive(true);
    return;
  }

  if (data.game_over) { animating = false; showGameOver(data); return; }

  // AI turn
  await doAiTurn();
}

async function doAiTurn() {
  statusEl.textContent = "🤖 Poseidon's Champion is forging a strategy…";
  boardEl.classList.add('thinking');

  // Small delay so browser can repaint the status
  await delay(100);

  const data = await api('/api/ai-move', 'POST');
  boardEl.classList.remove('thinking');

  if (data.error) { animating = false; setInteractive(true); return; }

  const flips = data.flips || [];
  const aiMove = data.ai_move || null;
  if (aiMove) {
    appendLog(buildLogEntry(AI, aiMove[0], aiMove[1], flips, data.crucible_squares));
  }
  renderState(data, flips, aiMove);

  if (data.pass === 'player') {
    statusEl.textContent = '⏭️ You have no moves. AI goes again!';
    await delay(800);
    await doAiTurn();
    return;
  }

  if (data.game_over) { animating = false; showGameOver(data); return; }

  animating = false;
  setInteractive(true);
}

function setInteractive(on) {
  boardEl.querySelectorAll('.cell').forEach(c => {
    if (on && state && state.current_player === PLAYER) c.classList.remove('no-click');
    else c.classList.add('no-click');
  });
}

// ── New Game ─────────────────────────────────────────────────
async function startNewGame() {
  const depth = parseInt(depthInput.value) || 5;
  modal.style.display = 'none';
  logEl.innerHTML = '';
  animating = false;
  setInteractive(false);
  const s = await api('/api/new-game', 'POST', { depth });
  renderState(s);
  statusEl.textContent = 'New game started! Select a highlighted cell to place your 🔥 emblem.';
}

// ── Game Over ────────────────────────────────────────────────
function showGameOver(s) {
  const p = s.player_score;
  const a = s.ai_score;
  if (s.winner === 'player') {
    modalIcon.textContent  = '🏆';
    modalTitle.textContent = 'Victory!';
    modalMsg.innerHTML     = `Hephaestus wins!<br><strong>${p} — ${a}</strong>`;
  } else if (s.winner === 'ai') {
    modalIcon.textContent  = '⚒️';
    modalTitle.textContent = "Poseidon's Champion Wins";
    modalMsg.innerHTML     = `The AI claims victory!<br><strong>${a} — ${p}</strong>`;
  } else {
    modalIcon.textContent  = '⚖️';
    modalTitle.textContent = 'The Forge is Balanced';
    modalMsg.innerHTML     = `It's a draw!<br><strong>${p} — ${a}</strong>`;
  }
  statusEl.textContent = `Game over! ${s.winner === 'player' ? '🏆 Hephaestus wins!' : s.winner === 'ai' ? "⚒️ Poseidon's Champion wins!" : '⚖️ Draw!'} Final score: ${p} — ${a}`;
  setTimeout(() => { modal.style.display = 'flex'; }, 600);
}

// ── Depth change ─────────────────────────────────────────────
depthInput.addEventListener('change', async () => {
  const depth = Math.max(1, Math.min(8, parseInt(depthInput.value) || 5));
  depthInput.value = depth;
  await api('/api/set-depth', 'POST', { depth });
});

// ── Helpers ──────────────────────────────────────────────────
function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

// ── Boot ─────────────────────────────────────────────────────
btnNew.addEventListener('click', startNewGame);
modalNew.addEventListener('click', startNewGame);

buildLabels();
buildBoard();
loadState();
