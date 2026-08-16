# ⚒️ The Forge of Hephaestus

> A Mythology-Inspired Othello Variant Featuring a Handcrafted Minimax AI with Alpha-Beta Pruning, Custom Heuristics, and Two Original Gameplay Mechanics — Built as a Full-Stack Web Application

[![Live Demo](https://img.shields.io/badge/demo-online-brightgreen)](https://forgeofhephaestus.jmmn.tech/)
[![Python](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.x-lightgrey)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Hosted on Render](https://img.shields.io/badge/deploy-Render-46E3B7)](https://render.com/)

---

## 🎮 Overview

**The Forge of Hephaestus** is a two-player turn-based strategy game built for an AI Lab final project by **Mohammad Khairul Haque** and **Fahima Mehzabeen**. It reimagines the classic **Othello/Reversi** ruleset within a Greek mythology setting, where you play as **Hephaestus** (🔥) battling **Poseidon's Champion** (🌊) for control of an $8\times 8$ divine forge floor.

The centerpiece of this project is a **handcrafted adversarial search engine** implementing **Minimax with Alpha-Beta Pruning**, augmented with **dynamic root move ordering**, a **six-factor heuristic evaluation function**, and configurable search depth. The AI does not rely on machine learning, neural networks, or pre-trained models — it reasons purely through classical search and domain-specific heuristics.

Two original mechanics — **Anvil Squares** and **Volatile Crucibles** — introduce critical tactical dimensions and material permanence without breaking the perfect-information framework.

🌐 **Live Deployment:** [https://forgeofhephaestus.jmmn.tech/](https://forgeofhephaestus.jmmn.tech/)

---

## ✨ Features

### Special Mechanics

| Mechanic | Description |
|----------|-------------|
| 🏛️ **Anvil Squares** | Corner squares (**A1, H1, A8, H8**). Pieces placed here are **permanently safe** from flips and captures, and count for **double points ($2\times$)** at endgame. |
| 💥 **Volatile Crucibles** | Four designated squares (**C3, F3, C6, F6**). Placing a piece here triggers an **explosion** that flips all 8 adjacent opponent pieces to your color. |

### AI Engine

| Feature | Description |
|---------|-------------|
| 🧠 **Minimax Algorithm** | Classic adversarial search assuming optimal counter-play from both sides. |
| ✂️ **Alpha-Beta Pruning** | Eliminates suboptimal subtrees to dramatically reduce search space. |
| 🔀 **Root Move Ordering** | Prioritizes Anvil corners and outer edges first to establish tight $\alpha$/$\beta$ bounds early. |
| 📊 **6-Factor Heuristic** | Evaluates piece difference, mobility, corner control, positional weights, parity, and frontier vulnerability. |
| ⚙️ **Configurable Depth** | Dynamic difficulty scaling from Depth 1 (beginner) to 8 (expert). |
| 📈 **Live Diagnostics** | Real-time tracking of nodes evaluated, branches pruned, and search execution time. |

### Web Interface & Architecture

- **Full-Stack Architecture:** Thinking Flask REST server with a lightweight, responsive browser client.
- **Session Isolation:** In-memory UUID-keyed session store allowing multiple concurrent games.
- **Mythic Ember Aesthetics:** Custom dark-mode UI with Cinzel typography and CSS-animated disc flips.
- **Live Diagnostics Panel:** Displays real-time search metrics and coordinate-annotated move history logs.

---

## 🚀 Installation & Local Setup

### Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- `pip` or `uv` package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/mkhjmmn/forge-of-hephaestus.git
cd forge-of-hephaestus

# (Optional) Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask development server
python app.py
```

---

## 🎯 How to Play

### Objective
Control the majority of the forge floor by the end of the game. The player with the highest score (accounting for Anvil double-counting) wins.

### Rules

1. **Placement**: On your turn, place your emblem (🔥) on any **highlighted green cell**.
2. **Capture**: When you place a piece, any opponent pieces trapped in a straight line between your new piece and your existing pieces **flip to your color**.
3. **Anvil Squares**: Pieces on corner squares are **permanently safe** — they cannot be flipped, and they count as **2 points** each.
4. **Volatile Crucibles**: Placing a piece on any of the four designated squares (**C3, F3, C6, F6**) triggers an **explosion** that flips all 8 adjacent opponent pieces. The explosion occurs **after** the standard capture resolution. Friendly pieces and Anvil pieces remain unchanged.
5. **Passing**: If you have no legal moves, your turn is skipped.
6. **Game End**: The game ends when neither player can move. The highest score wins.

### Controls

| Action | Input |
|--------|-------|
| Place piece | Click a highlighted cell |
| New Game | Click "New Game" button |
| Adjust AI Difficulty | Change "AI Depth" spinbox (1–8) |

---

## 🧠 AI Architecture

### Algorithm: Minimax with Alpha-Beta Pruning

```
maximize(AI)          minimize(Player)
       │                     │
       ▼                     ▼
    ┌─────┐              ┌─────┐
    │  8  │              │ -8  │
    └──┬──┘              └──┬──┘
   ┌──┴──┐              ┌──┴──┐
   ▼     ▼              ▼     ▼
 ┌───┐ ┌───┐          ┌───┐ ┌───┐
 │ 5 │ │ 8 │          │-3 │ │-8 │
 └───┘ └───┘          └───┘ └───┘
```

The AI explores the game tree to a configurable depth, evaluating non-terminal states with a multi-factor heuristic. Alpha-Beta pruning cuts off branches that cannot possibly influence the final decision, reducing the effective branching factor from **O(bᵈ)** to approximately **O(bᵈᐟ²)** with optimal move ordering.

### Move Ordering

Before searching, candidate moves are sorted by a **priority heuristic** that evaluates corners and edges first:

| Move Type | Priority |
|-----------|----------|
| Anvil (corner) | 1000 |
| Edge square | 100 |
| Positional weight | Dynamic (from weight matrix) |

This ordering maximizes the number of branches pruned by Alpha-Beta, as strong moves are evaluated early and establish tight alpha/beta bounds.

### Evaluation Heuristic

The AI evaluates non-terminal board states using a weighted sum of six strategic factors:

```
Eval(S) =  w₁·(PieceDiff)
         + w₂·(Mobility)
         + w₃·(CornerControl)
         + w₄·(Positional)
         + w₅·(Parity)
         + w₆·(Frontier)
```

| Factor | Weight | Description |
|--------|--------|-------------|
| **Piece Difference** | 1.0 | `(AI_score − Player_score)` with Anvil double-counting |
| **Mobility** | 3.0 | Relative legal move ratio: `(AI_moves − Player_moves) / (total_moves + 1)` |
| **Corner Control** | 25.0 | `(AI_corners − Player_corners) × 25` |
| **Positional** | Dynamic | Sum of `POSITION_WEIGHTS[r][c]` for each owned square |
| **Parity** | 2.0 | `+2` if AI gets last move, `−2` otherwise |
| **Frontier** | −2.0 | Penalty for pieces adjacent to empty squares (vulnerability) |

The positional weight matrix assigns higher values to stable edge and corner positions:

```
[ 100, -20,  10,   5,   5,  10, -20, 100 ]
[ -20, -30,   1,   1,   1,   1, -30, -20 ]
[  10,   1,   5,   2,   2,   5,   1,  10 ]
[   5,   1,   2,   0,   0,   2,   1,   5 ]
[   5,   1,   2,   0,   0,   2,   1,   5 ]
[  10,   1,   5,   2,   2,   5,   1,  10 ]
[ -20, -30,   1,   1,   1,   1, -30, -20 ]
[ 100, -20,  10,   5,   5,  10, -20, 100 ]
```

### Performance

At depth **5**, the AI typically evaluates:
- **~10,000–50,000 nodes** per move
- **Prunes ~40–60%** of branches
- **Responds in <1 second** on modern hardware

---

## 📁 Project Structure

```
forge-of-hephaestus/
├── app.py                   # Flask server (API + session management)
├── engine.py                # Game engine (rules, board state, mechanics)
├── ai.py                    # Minimax AI with Alpha-Beta Pruning
├── static/
│   ├── css/
│   │   └── style.css        # Mythic ember-themed styles
│   └── js/
│       └── game.js          # Browser client logic
├── templates/
│   └── index.html           # Main game page
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
└── assets/                  # Screenshots and media
```

---

## 🛠️ Technical Details

### Problem Domain
**Adversarial game-playing in deterministic, perfect-information, two-player zero-sum environments.**

- **Deterministic**: No randomness — every move outcome is fully predictable.
- **Perfect Information**: Both players see the complete board state.
- **Zero-Sum**: Any gain for one player is an equal loss for the other.
- **Finite State Space**: 8×8 grid with two piece types per player.

### Complexity Analysis

| Metric | Value |
|--------|-------|
| Branching Factor | ~10–15 (early game) → 0 (late game) |
| Estimated State Space | On the order of 10²⁸ board configurations |
| Game Tree Depth | ~60 moves (full game) |
| AI Search Depth | 1–8 (configurable) |

---

## 🎓 Academic Context

This project was developed as a **final project for an AI Laboratory course**. It demonstrates:

- ✅ Implementation of **Minimax** adversarial search
- ✅ **Alpha-Beta Pruning** optimization with measurable performance gains
- ✅ **Move ordering** for enhanced pruning efficiency
- ✅ **Heuristic function design** for non-terminal state evaluation
- ✅ **Game theory** concepts (zero-sum, perfect information, Nash equilibrium approximation)
- ✅ Clean **MVC-style architecture** separating game logic, AI engine, and presentation layer
- ✅ **Full-stack web deployment** with session management and RESTful API design

---

## 🔮 Future Enhancements

- [ ] **Transposition Table** (memoization) for faster repeated-state lookup
- [ ] **Iterative Deepening** with time-controlled search
- [ ] **Undo/Redo** move functionality
- [ ] **Save/Load** game state to file
- [ ] **Sound effects** for piece placement and crucible explosions
- [ ] **Multiplayer mode** (local 2-player or online PvP)
- [ ] **Web deployment** enhancements (WebSocket real-time play)

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with **Python**, **Flask**, and vanilla **JavaScript**
- Inspired by classic **Othello/Reversi** game mechanics
- Mythological theme honoring **Hephaestus**, the Greek god of fire and the forge

---

<div align="center">

**🔥 May the forge favor the clever. ⚒️**

</div>
