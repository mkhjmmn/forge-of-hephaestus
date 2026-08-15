#!/usr/bin/env python3
"""
The Forge of Hephaestus — Web Edition
Flask backend serving game state via REST API.
"""

from flask import Flask, request, jsonify, session, render_template
import copy
import time
import uuid

app = Flask(__name__)
app.secret_key = "forge_of_hephaestus_secret"

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

BOARD_SIZE = 8
EMPTY = 0
PLAYER = 1      # Hephaestus (Human)
AI = -1         # Poseidon's Champion (Computer)

ANVIL_SQUARES = {(0, 0), (0, 7), (7, 0), (7, 7)}
CRUCIBLE_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1)
]

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

WEIGHTS = {
    "piece_diff": 1.0,
    "mobility": 3.0,
    "corner": 25.0,
    "stability": 5.0,
    "parity": 2.0,
    "frontier": -2.0,
}


# =============================================================================
# GAME LOGIC ENGINE
# =============================================================================

class ForgeEngine:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.last_move = None
        self.move_history = []
        self._init_board()

    def _init_board(self):
        self.board[3][3] = PLAYER
        self.board[3][4] = AI
        self.board[4][3] = AI
        self.board[4][4] = PLAYER

    def clone(self):
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
        return [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
                if self.is_valid_move(r, c, player)]

    def is_valid_move(self, r, c, player):
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
        if not self.is_valid_move(r, c, player):
            return []

        self.board[r][c] = player
        flips = self.get_flips(r, c, player)

        standard_flips = []
        for fr, fc in flips:
            if not self.is_anvil(fr, fc):
                self.board[fr][fc] = player
                standard_flips.append((fr, fc))

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
            "pos": [r, c],
            "standard_flips": standard_flips,
            "crucible_flips": crucible_flips,
        })
        return standard_flips + crucible_flips

    def count_pieces(self):
        p = sum(row.count(PLAYER) for row in self.board)
        a = sum(row.count(AI) for row in self.board)
        return p, a

    def get_score(self, player):
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    score += 2 if self.is_anvil(r, c) else 1
        return score

    def is_game_over(self):
        return (not self.get_legal_moves(PLAYER)) and (not self.get_legal_moves(AI))

    def get_winner(self):
        p_score = self.get_score(PLAYER)
        a_score = self.get_score(AI)
        if p_score > a_score:
            return PLAYER
        elif a_score > p_score:
            return AI
        return 0

    def to_dict(self):
        return {
            "board": self.board,
            "last_move": list(self.last_move) if self.last_move else None,
            "move_history": self.move_history,
        }

    @classmethod
    def from_dict(cls, d):
        engine = cls.__new__(cls)
        engine.board = d["board"]
        engine.last_move = tuple(d["last_move"]) if d["last_move"] else None
        engine.move_history = d["move_history"]
        return engine


# =============================================================================
# AI ENGINE
# =============================================================================

class HephaestusAI:
    def __init__(self, max_depth=5):
        self.max_depth = max_depth
        self.nodes_evaluated = 0
        self.pruned_branches = 0
        self.search_time = 0.0

    def get_best_move(self, engine):
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
        r, c = move
        if (r, c) in ANVIL_SQUARES:
            return 1000
        if r == 0 or r == 7 or c == 0 or c == 7:
            return 100
        return POSITION_WEIGHTS[r][c]

    def _minimax(self, engine, depth, alpha, beta, is_maximizing):
        self.nodes_evaluated += 1
        if depth == 0 or engine.is_game_over():
            return self._evaluate(engine)

        player = AI if is_maximizing else PLAYER
        legal_moves = engine.get_legal_moves(player)

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
        if engine.is_game_over():
            winner = engine.get_winner()
            if winner == AI:
                return 10000
            elif winner == PLAYER:
                return -10000
            return 0

        score = 0.0
        p_score = engine.get_score(PLAYER)
        a_score = engine.get_score(AI)
        score += WEIGHTS["piece_diff"] * (a_score - p_score)

        p_mobility = len(engine.get_legal_moves(PLAYER))
        a_mobility = len(engine.get_legal_moves(AI))
        if p_mobility + a_mobility != 0:
            score += WEIGHTS["mobility"] * (a_mobility - p_mobility) / (p_mobility + a_mobility + 1)

        p_corners = sum(1 for sq in ANVIL_SQUARES if engine.board[sq[0]][sq[1]] == PLAYER)
        a_corners = sum(1 for sq in ANVIL_SQUARES if engine.board[sq[0]][sq[1]] == AI)
        score += WEIGHTS["corner"] * (a_corners - p_corners)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                val = engine.board[r][c]
                if val == AI:
                    score += POSITION_WEIGHTS[r][c]
                elif val == PLAYER:
                    score -= POSITION_WEIGHTS[r][c]

        empty_count = sum(row.count(EMPTY) for row in engine.board)
        if empty_count % 2 == 0:
            score += WEIGHTS["parity"]
        else:
            score -= WEIGHTS["parity"]

        p_frontier = self._count_frontier(engine, PLAYER)
        a_frontier = self._count_frontier(engine, AI)
        score += WEIGHTS["frontier"] * (a_frontier - p_frontier)

        return score

    def _count_frontier(self, engine, player):
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


# =============================================================================
# IN-MEMORY GAME STORE (keyed by session id)
# =============================================================================

games = {}  # session_id -> {"engine": ForgeEngine, "ai": HephaestusAI, "current_player": int, "game_over": bool}


def get_game():
    sid = session.get("sid")
    if not sid or sid not in games:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        games[sid] = new_game_state()
    return games[sid]


def new_game_state(depth=5):
    return {
        "engine": ForgeEngine(),
        "ai": HephaestusAI(max_depth=depth),
        "current_player": PLAYER,
        "game_over": False,
    }


def game_to_response(g):
    engine = g["engine"]
    current_player = g["current_player"]
    game_over = g["game_over"]

    legal_moves = engine.get_legal_moves(current_player) if not game_over else []
    p_score = engine.get_score(PLAYER)
    a_score = engine.get_score(AI)
    p_count, a_count = engine.count_pieces()

    anvil_list = [[r, c] for r, c in ANVIL_SQUARES]
    crucible_list = [[r, c] for r, c in CRUCIBLE_SQUARES]

    winner = None
    if game_over:
        w = engine.get_winner()
        if w == PLAYER:
            winner = "player"
        elif w == AI:
            winner = "ai"
        else:
            winner = "draw"

    return {
        "board": engine.board,
        "current_player": current_player,
        "legal_moves": [list(m) for m in legal_moves],
        "last_move": list(engine.last_move) if engine.last_move else None,
        "player_score": p_score,
        "ai_score": a_score,
        "player_count": p_count,
        "ai_count": a_count,
        "game_over": game_over,
        "winner": winner,
        "move_history": engine.move_history,
        "anvil_squares": anvil_list,
        "crucible_squares": crucible_list,
        "ai_depth": g["ai"].max_depth,
        "ai_stats": {
            "nodes": g["ai"].nodes_evaluated,
            "pruned": g["ai"].pruned_branches,
            "time": round(g["ai"].search_time, 2),
        },
    }


# =============================================================================
# ROUTES
# =============================================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    g = get_game()
    return jsonify(game_to_response(g))


@app.route("/api/new-game", methods=["POST"])
def api_new_game():
    data = request.get_json(silent=True) or {}
    depth = int(data.get("depth", 5))
    sid = session.get("sid", str(uuid.uuid4()))
    session["sid"] = sid
    games[sid] = new_game_state(depth=depth)
    return jsonify(game_to_response(games[sid]))


@app.route("/api/move", methods=["POST"])
def api_move():
    g = get_game()
    if g["game_over"]:
        return jsonify({"error": "Game is over"}), 400
    if g["current_player"] != PLAYER:
        return jsonify({"error": "Not your turn"}), 400

    data = request.get_json()
    r, c = int(data["row"]), int(data["col"])
    engine = g["engine"]

    if not engine.is_valid_move(r, c, PLAYER):
        return jsonify({"error": "Invalid move"}), 400

    flips = engine.make_move(r, c, PLAYER)

    # Check game over
    if engine.is_game_over():
        g["game_over"] = True
        return jsonify({**game_to_response(g), "flips": [list(f) for f in flips]})

    # Check if AI has moves; if not, player goes again
    if not engine.get_legal_moves(AI):
        g["current_player"] = PLAYER
        return jsonify({**game_to_response(g), "flips": [list(f) for f in flips], "pass": "ai"})

    g["current_player"] = AI
    return jsonify({**game_to_response(g), "flips": [list(f) for f in flips]})


@app.route("/api/ai-move", methods=["POST"])
def api_ai_move():
    g = get_game()
    if g["game_over"]:
        return jsonify({"error": "Game is over"}), 400
    if g["current_player"] != AI:
        return jsonify({"error": "Not AI's turn"}), 400

    engine = g["engine"]
    ai = g["ai"]
    move = ai.get_best_move(engine)

    if move is None:
        # AI has no moves — pass back to player
        g["current_player"] = PLAYER
        return jsonify({**game_to_response(g), "pass": "ai", "flips": []})

    flips = engine.make_move(move[0], move[1], AI)

    if engine.is_game_over():
        g["game_over"] = True
        return jsonify({**game_to_response(g), "ai_move": list(move), "flips": [list(f) for f in flips]})

    # Check if player has moves; if not, AI goes again
    if not engine.get_legal_moves(PLAYER):
        g["current_player"] = AI
        return jsonify({**game_to_response(g), "ai_move": list(move), "flips": [list(f) for f in flips], "pass": "player"})

    g["current_player"] = PLAYER
    return jsonify({**game_to_response(g), "ai_move": list(move), "flips": [list(f) for f in flips]})


@app.route("/api/set-depth", methods=["POST"])
def api_set_depth():
    g = get_game()
    data = request.get_json()
    depth = max(1, min(8, int(data.get("depth", 5))))
    g["ai"].max_depth = depth
    return jsonify({"depth": depth})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
