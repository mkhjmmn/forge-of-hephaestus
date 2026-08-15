#!/usr/bin/env python3
"""
The Forge of Hephaestus
A Mythological Othello Variant with Alpha-Beta Pruning AI
============================================================
A turn-based strategy game where Hephaestus (Player) battles
Poseidon's Champion (AI) on the divine forge floor.

Special Mechanics:
  - Anvil Squares: Corner squares (A1, H1, A8, H8). Pieces here
    are permanently safe and count for double points.
  - Volatile Crucibles: Center 4 squares (C3, F3, C6, F6).
    Placing a piece here triggers an explosion that flips all
    8 adjacent pieces.

AI Engine:
  - Minimax with Alpha-Beta Pruning
  - Configurable search depth
  - Heuristic evaluation: mobility, corner control, stability,
    parity, and piece difference.
"""

import copy
import time

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

BOARD_SIZE = 8
EMPTY = 0
PLAYER = 1      # Hephaestus (Human)
AI = -1         # Poseidon's Champion (Computer)

# Special squares
ANVIL_SQUARES = {(0, 0), (0, 7), (7, 0), (7, 7)}
CRUCIBLE_SQUARES = {(2, 2), (2, 5), (5, 2), (5, 5)}

# 8 directions for line capture
DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1)
]

# Color palette
COLORS = {
    "bg": "#1a0f0a",
    "panel": "#2d1b0e",
    "board_bg": "#1a0f08",
    "cell": "#4a3728",
    "cell_hover": "#5a4535",
    "anvil": "#2a2a2a",
    "crucible": "#4a1a1a",
    "legal": "#4a5a35",
    "last_move": "#ff9d00",
    "text": "#f4e4c1",
    "accent": "#ff9d00",
    "player": "#ffaa33",
    "ai": "#6699cc",
    "btn": "#cc6600",
    "btn_hover": "#dd7700",
}

# Evaluation weights (tunable)
WEIGHTS = {
    "piece_diff": 1.0,
    "mobility": 3.0,
    "corner": 25.0,
    "stability": 5.0,
    "parity": 2.0,
    "frontier": -2.0,
}

# Positional weight matrix (center is valuable, edges more so)
POSITION_WEIGHTS = [
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -30,   1,   1,   1,   1, -30, -20],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [  5,   1,   2,   0,   0,   2,   1,   5],
    [  5,   1,   2,   0,   0,   2,   1,   5],
    [ 10,   1,   5,   2,   2,   5,   1,  10],
    [-20, -30,   1,   1,   1,   1, -30, -20],
    [100, -20,  10,   5,   5,  10, -20, 100],
]


# =============================================================================
# GAME LOGIC ENGINE
# =============================================================================

class ForgeEngine:
    """Core game logic for The Forge of Hephaestus."""

    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.last_move = None
        self.move_history = []
        self._init_board()

    def _init_board(self):
        """Set up the classic Othello starting position."""
        self.board[3][3] = PLAYER
        self.board[3][4] = AI
        self.board[4][3] = AI
        self.board[4][4] = PLAYER

    def clone(self):
        """Return a deep copy of the engine state."""
        new_engine = ForgeEngine.__new__(ForgeEngine)
        new_engine.board = [row[:] for row in self.board]
        new_engine.last_move = self.last_move
        new_engine.move_history = self.move_history[:]
        return new_engine

    def in_bounds(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def get_opponent(self, player):
        return AI if player == PLAYER else PLAYER

    def is_anvil(self, r, c):
        return (r, c) in ANVIL_SQUARES

    def is_crucible(self, r, c):
        return (r, c) in CRUCIBLE_SQUARES

    def get_legal_moves(self, player):
        """Return list of (row, col) tuples where player can legally place."""
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.is_valid_move(r, c, player):
                    moves.append((r, c))
        return moves

    def is_valid_move(self, r, c, player):
        """Check if placing at (r,c) is legal for player."""
        if not self.in_bounds(r, c) or self.board[r][c] != EMPTY:
            return False
        opponent = self.get_opponent(player)
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            found_opponent = False
            while self.in_bounds(nr, nc) and self.board[nr][nc] == opponent:
                found_opponent = True
                nr += dr
                nc += dc
            if found_opponent and self.in_bounds(nr, nc) and self.board[nr][nc] == player:
                return True
        return False

    def get_flips(self, r, c, player):
        """Return list of (row, col) that would flip if player places at (r,c)."""
        flips = []
        opponent = self.get_opponent(player)
        for dr, dc in DIRECTIONS:
            line = []
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc) and self.board[nr][nc] == opponent:
                line.append((nr, nc))
                nr += dr
                nc += dc
            if line and self.in_bounds(nr, nc) and self.board[nr][nc] == player:
                flips.extend(line)
        return flips

    def make_move(self, r, c, player):
        """
        Execute a move for player at (r,c).
        Returns list of flipped positions for animation/logging.
        """
        if not self.is_valid_move(r, c, player):
            return []

        self.board[r][c] = player
        flips = self.get_flips(r, c, player)

        # Standard Othello flips (respecting Anvil immunity)
        standard_flips = []
        for fr, fc in flips:
            if not self.is_anvil(fr, fc):
                self.board[fr][fc] = player
                standard_flips.append((fr, fc))

        # Volatile Crucible explosion
        crucible_flips = []
        if self.is_crucible(r, c):
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if self.in_bounds(nr, nc) and self.board[nr][nc] == self.get_opponent(player):
                        if not self.is_anvil(nr, nc):
                            self.board[nr][nc] = player
                            crucible_flips.append((nr, nc))

        self.last_move = (r, c)
        self.move_history.append({
            "player": player,
            "pos": (r, c),
            "standard_flips": standard_flips,
            "crucible_flips": crucible_flips,
        })
        return standard_flips + crucible_flips

    def count_pieces(self):
        """Return (player_count, ai_count)."""
        p = sum(row.count(PLAYER) for row in self.board)
        a = sum(row.count(AI) for row in self.board)
        return p, a

    def get_score(self, player):
        """
        Calculate score with Anvil double-counting.
        Anvil pieces count as 2 points each.
        """
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    score += 2 if self.is_anvil(r, c) else 1
        return score

    def is_game_over(self):
        """Game ends when neither player has legal moves."""
        return (not self.get_legal_moves(PLAYER)) and (not self.get_legal_moves(AI))

    def get_winner(self):
        """Return PLAYER, AI, or 0 (draw)."""
        p_score = self.get_score(PLAYER)
        a_score = self.get_score(AI)
        if p_score > a_score:
            return PLAYER
        elif a_score > p_score:
            return AI
        return 0


# =============================================================================
# AI ENGINE: MINIMAX + ALPHA-BETA PRUNING
# =============================================================================

class HephaestusAI:
    """Adversarial search engine with Alpha-Beta pruning."""

    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        self.search_time = 0.0

    def get_best_move(self, engine):
        """Find the optimal move for the AI using Alpha-Beta Minimax."""
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        start = time.time()

        legal_moves = engine.get_legal_moves(AI)
        if not legal_moves:
            return None

        best_move = None
        best_value = -float("inf")
        alpha = -float("inf")
        beta = float("inf")

        # Move ordering: evaluate corners and edges first for better pruning
        legal_moves.sort(key=lambda m: self._move_priority(engine, m), reverse=True)

        for move in legal_moves:
            child = engine.clone()
            child.make_move(move[0], move[1], AI)
            value = self._minimax(child, self.max_depth - 1, alpha, beta, False)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)

        self.search_time = time.time() - start
        return best_move

    def _move_priority(self, engine, move):
        """Heuristic for move ordering — corners and edges first."""
        r, c = move
        if (r, c) in ANVIL_SQUARES:
            return 1000
        if r == 0 or r == 7 or c == 0 or c == 7:
            return 100
        return POSITION_WEIGHTS[r][c]

    def _minimax(self, engine, depth, alpha, beta, is_maximizing):
        """Recursive Minimax with Alpha-Beta pruning."""
        self.nodes_evaluated += 1

        if depth == 0 or engine.is_game_over():
            return self._evaluate(engine)

        player = AI if is_maximizing else PLAYER
        legal_moves = engine.get_legal_moves(player)

        # If no legal moves, pass turn to opponent
        if not legal_moves:
            return self._minimax(engine, depth - 1, alpha, beta, not is_maximizing)

        if is_maximizing:
            max_eval = -float("inf")
            for move in legal_moves:
                child = engine.clone()
                child.make_move(move[0], move[1], player)
                eval_val = self._minimax(child, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in legal_moves:
                child = engine.clone()
                child.make_move(move[0], move[1], player)
                eval_val = self._minimax(child, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval_val)
                beta = min(beta, eval_val)
                if beta <= alpha:
                    self.pruned_branches += 1
                    break
            return min_eval

    def _evaluate(self, engine):
        """
        Heuristic evaluation function.
        Combines multiple strategic factors into a single scalar.
        """
        if engine.is_game_over():
            winner = engine.get_winner()
            if winner == AI:
                return 10000
            elif winner == PLAYER:
                return -10000
            return 0

        score = 0.0

        # 1. Piece difference (with Anvil weighting)
        p_score = engine.get_score(PLAYER)
        a_score = engine.get_score(AI)
        score += WEIGHTS["piece_diff"] * (a_score - p_score)

        # 2. Mobility (number of legal moves)
        p_mobility = len(engine.get_legal_moves(PLAYER))
        a_mobility = len(engine.get_legal_moves(AI))
        if p_mobility + a_mobility != 0:
            score += WEIGHTS["mobility"] * (a_mobility - p_mobility) / (p_mobility + a_mobility + 1)

        # 3. Corner control (Anvil squares)
        p_corners = sum(1 for sq in ANVIL_SQUARES if engine.board[sq[0]][sq[1]] == PLAYER)
        a_corners = sum(1 for sq in ANVIL_SQUARES if engine.board[sq[0]][sq[1]] == AI)
        score += WEIGHTS["corner"] * (a_corners - p_corners)

        # 4. Positional weights
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                val = engine.board[r][c]
                if val == AI:
                    score += POSITION_WEIGHTS[r][c]
                elif val == PLAYER:
                    score -= POSITION_WEIGHTS[r][c]

        # 5. Parity (who gets the last move is advantageous)
        empty_count = sum(row.count(EMPTY) for row in engine.board)
        if empty_count % 2 == 0:
            score += WEIGHTS["parity"]  # AI gets last move
        else:
            score -= WEIGHTS["parity"]

        # 6. Frontier pieces (pieces adjacent to empty squares are vulnerable)
        p_frontier = self._count_frontier(engine, PLAYER)
        a_frontier = self._count_frontier(engine, AI)
        score += WEIGHTS["frontier"] * (a_frontier - p_frontier)

        return score

    def _count_frontier(self, engine, player):
        """Count how many of player's pieces are adjacent to empty squares."""
        count = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if engine.board[r][c] == player:
                    for dr, dc in DIRECTIONS:
                        nr, nc = r + dr, c + dc
                        if engine.in_bounds(nr, nc) and engine.board[nr][nc] == EMPTY:
                            count += 1
                            break
        return count