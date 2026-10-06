import math
import random
from game.state import P1, P2

def evaluate_state(state, ml_model):
    ml_score = ml_model.predict(state.get_features())[0]
    bonus_score = (state.s1 - state.s2) * 200
    territory_score = (state.get_bfs_area(P1) - state.get_bfs_area(P2)) * 40
    noise = random.uniform(-15, 15)
    return ml_score + bonus_score + territory_score + noise

def minimax(state, depth, alpha, beta, is_max, ml_model):
    m1, m2 = (state.get_moves(P1), state.get_moves(P2))
    term = not m1 or not m2
    if depth == 0 or term:
        if term:
            if not m1 and (not m2):
                return 0
            return 10000 if not m2 else -10000
        return evaluate_state(state, ml_model)
    moves = m1 if is_max else m2
    random.shuffle(moves)
    best_val = -math.inf if is_max else math.inf
    for m in moves:
        ev = minimax(state.apply_move(m), depth - 1, alpha, beta, not is_max, ml_model)
        if is_max:
            best_val = max(best_val, ev)
            alpha = max(alpha, ev)
        else:
            best_val = min(best_val, ev)
            beta = min(beta, ev)
        if beta <= alpha:
            break
    return best_val

def get_best_move(state, ml_model, depth=4):
    moves = state.get_moves(state.turn)
    if not moves:
        return (None, 0)
    is_max = state.turn == P1
    best_m = moves[0]
    best_v = -math.inf if is_max else math.inf
    for m in moves:
        v = minimax(state.apply_move(m), depth, -math.inf, math.inf, not is_max, ml_model)
        if is_max and v > best_v or (not is_max and v < best_v):
            best_m, best_v = (m, v)
    return (best_m, best_v)
