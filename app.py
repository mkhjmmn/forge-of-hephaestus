#!/usr/bin/env python3
"""
The Forge of Hephaestus — Web Edition
Flask backend serving game state via REST API.
"""

from flask import Flask, request, jsonify, session, render_template
import uuid
from forge_of_hephaestus import (
    ForgeEngine,
    HephaestusAI,
    PLAYER,
    AI,
    ANVIL_SQUARES,
    CRUCIBLE_SQUARES
)

app = Flask(__name__)
app.secret_key = "forge_of_hephaestus_secret"

# =============================================================================
# IN-MEMORY GAME STORE (keyed by session id)
# =============================================================================

games = {}


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

    if engine.is_game_over():
        g["game_over"] = True
        return jsonify({**game_to_response(g), "flips": [list(f) for f in flips]})

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
        g["current_player"] = PLAYER
        return jsonify({**game_to_response(g), "pass": "ai", "flips": []})

    flips = engine.make_move(move[0], move[1], AI)

    if engine.is_game_over():
        g["game_over"] = True
        return jsonify({**game_to_response(g), "ai_move": list(move), "flips": [list(f) for f in flips]})

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