import pygame
import os
import warnings
warnings.filterwarnings('ignore', message='X does not have valid feature names')
from game.state import TronState, P1, P2, LEVELS
from ai.ml_model import load_or_train_model
from ai.minimax import get_best_move
from ui.renderer import init_display, draw_hud, draw_game_over, draw_state

def main():
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tron_model.pkl')
    ml_model = load_or_train_model(model_path)
    screen, font, small_font = init_display()
    clock = pygame.time.Clock()
    state = TronState(0)
    t1, t2 = ([[state.p1]], [[state.p2]])
    history_scores = [0.0]
    running, over, auto, score, lvl = (True, False, False, 0.0, 0)
    fps = 15
    ai_depth = 4
    while running:
        clock.tick(fps)
        moved = False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_a:
                    auto = not auto
                if e.key == pygame.K_EQUALS or e.key == pygame.K_PLUS:
                    fps = min(60, fps + 5)
                if e.key == pygame.K_MINUS:
                    fps = max(5, fps - 5)
                if pygame.K_1 <= e.key <= pygame.K_5:
                    ai_depth = e.key - pygame.K_0
                if e.key == pygame.K_SPACE:
                    lvl = (lvl + 1) % len(LEVELS)
                    state = TronState(lvl)
                    over, score = (False, 0)
                    t1, t2 = ([[state.p1]], [[state.p2]])
                    history_scores = [0.0]
        if not over:
            if state.turn == P1 and (not auto):
                k = pygame.key.get_pressed()
                d = (0, -1) if k[pygame.K_LEFT] else (0, 1) if k[pygame.K_RIGHT] else (-1, 0) if k[pygame.K_UP] else (1, 0) if k[pygame.K_DOWN] else (0, 0)
                if d in state.get_moves(P1):
                    pp = state.p1
                    state = state.apply_move(d)
                    moved = True
                    history_scores.append(score)
                    if abs(state.p1[0] - pp[0]) > 1 or abs(state.p1[1] - pp[1]) > 1:
                        t1.append([state.p1])
                    else:
                        t1[-1].append(state.p1)
            if state.turn == P1 and auto or state.turn == P2:
                m, v = get_best_move(state, ml_model, depth=ai_depth)
                if m:
                    score, p = (v, state.turn)
                    history_scores.append(score)
                    pp = state.p1 if p == P1 else state.p2
                    state = state.apply_move(m)
                    if p == P1:
                        if abs(state.p1[0] - pp[0]) > 1 or abs(state.p1[1] - pp[1]) > 1:
                            t1.append([state.p1])
                        else:
                            t1[-1].append(state.p1)
                    elif abs(state.p2[0] - pp[0]) > 1 or abs(state.p2[1] - pp[1]) > 1:
                        t2.append([state.p2])
                    else:
                        t2[-1].append(state.p2)
                    moved = True
                else:
                    over = True
            if moved and (not state.get_moves(P1) and (not state.get_moves(P2))):
                over = True
        draw_state(screen, state, t1, t2)
        draw_hud(screen, font, small_font, state, score, auto, history_scores, fps, ai_depth)
        if over:
            draw_game_over(screen, font, small_font, state)
        pygame.display.flip()
if __name__ == '__main__':
    main()
