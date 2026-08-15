# ⚒️ The Forge of Hephaestus

> A Mythology-Inspired Othello Variant Featuring a Handcrafted Minimax AI with Alpha-Beta Pruning, Custom Heuristics, and Two Original Gameplay Mechanics

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Game](https://img.shields.io/badge/genre-turn--based--strategy-orange)]()

---

## 🎮 Overview

**The Forge of Hephaestus** is a two-player turn-based strategy game built for an AI Lab final project. It reimagines the classic **Othello/Reversi** mechanic within a Greek mythology setting, where you play as **Hephaestus** (🔥) battling **Poseidon's Champion** (⚒️) for control of the divine forge floor.

The centerpiece of this project is a **handcrafted adversarial search engine** implementing **Minimax with Alpha-Beta Pruning**, augmented with **dynamic move ordering**, a **six-factor heuristic evaluation function**, and configurable search depth. The AI does not rely on machine learning, neural networks, or pre-trained models — it reasons purely through classical search and domain-specific strategy.

Two original mechanics — **Anvil Squares** and **Volatile Crucibles** — add strategic depth without breaking the perfect-information framework, giving the AI new axes to evaluate beyond standard Othello.

---

## ✨ Features

### Special Mechanics

| Mechanic | Description |
|----------|-------------|
| 🏛️ **Anvil Squares** | Corner squares (A1, H1, A8, H8). Pieces placed here are **permanently safe** and count for **double points** at endgame. |
| 💥 **Volatile Crucibles** | Center 4 squares (D4, D5, E4, E5). Placing a piece here triggers an **explosion** that flips all 8 adjacent opponent pieces. |

### AI Engine

| Feature | Description |
|---------|-------------|
| 🧠 **Minimax Algorithm** | Classic adversarial search assuming optimal opponent play. |
| ✂️ **Alpha-Beta Pruning** | Dramatically reduces search space by eliminating irrelevant branches. |
| 🔀 **Move Ordering** | Corners and high-value edges are searched first to maximize pruning efficiency. |
| 📊 **6-Factor Heuristic** | Evaluates piece difference, mobility, corner control, positional weights, parity, and frontier vulnerability. |
| ⚙️ **Configurable Depth** | Adjust AI difficulty from 1 (beginner) to 8 (expert) via the in-game sidebar. |
| 📈 **Live Stats** | Real-time display of nodes evaluated, branches pruned, and search time per move. |

### Interface

- Dark forge-themed **tkinter GUI** with ember/orange and steel-blue aesthetics
- Interactive hover effects and legal move highlighting
- Turn indicator with pulsing animation
- Move history log with coordinate notation
- Scoreboard with Anvil double-counting

---

## 🖼️ Screenshot

```

```

---

## 🚀 Installation & Running

### Requirements

- **Python 3.7+**
- **tkinter** (bundled with standard Python — no additional install needed)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/mkhjmmn/forge-of-hephaestus.git
cd forge-of-hephaestus

# Run the game
python forge_of_hephaestus.py
```

No external dependencies — Python and tkinter are all you need.

---

## 🎯 How to Play

### Objective
Control the majority of the forge floor by the end of the game. The player with the highest score (accounting for Anvil double-counting) wins.

### Rules

1. **Placement**: On your turn, place your emblem (🔥) on any **highlighted green cell**.
2. **Capture**: When you place a piece, any opponent pieces trapped in a straight line between your new piece and your existing pieces **flip to your color**.
3. **Anvil Squares**: Pieces on corner squares are **permanently safe** — they cannot be flipped, and they count as **2 points** each.
4. **Volatile Crucibles**: Placing a piece on any of the 4 center squares triggers an **explosion** that flips all 8 adjacent opponent pieces. The explosion occurs **after** the standard capture resolution. Friendly pieces and Anvil pieces remain unchanged.
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
├── forge_of_hephaestus.py   # Main game file (engine + AI + GUI)
├── README.md                # This file
├── LICENSE                  # MIT License
└── assets/                  # (Optional) Screenshots and media
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

---

## 🔮 Future Enhancements

- [ ] **Transposition Table** (memoization) for faster repeated-state lookup
- [ ] **Iterative Deepening** with time-controlled search
- [ ] **Undo/Redo** move functionality
- [ ] **Save/Load** game state to file
- [ ] **Sound effects** for piece placement and crucible explosions
- [ ] **Multiplayer mode** (local 2-player)
- [ ] **Web deployment** via PyScript/Brython

---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with Python's standard **tkinter** library
- Inspired by classic **Othello/Reversi** game mechanics
- Mythological theme honoring **Hephaestus**, the Greek god of fire and the forge

---

<div align="center">

**🔥 May the forge favor the clever. ⚒️**

</div>
