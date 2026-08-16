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
- **Session Isolation:** In-memory UUID-keyed session store allowing multiple concurrent games[cite: 2].
- **Mythic Ember Aesthetics:** Custom dark-mode UI with Cinzel typography and CSS-animated disc flips[cite: 1, 3].
- **Live Diagnostics Panel:** Displays real-time search metrics and coordinate-annotated move history logs[cite: 1, 2].

---

## 🚀 Installation & Local Setup

### Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- `pip` or `uv` package manager

### Quick Start

```bash
# Clone the repository
git clone [https://github.com/mkhjmmn/forge-of-hephaestus.git](https://github.com/mkhjmmn/forge-of-hephaestus.git)
cd forge-of-hephaestus

# (Optional) Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask development server
python app.py
