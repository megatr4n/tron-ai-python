import pygame
import math
from game.state import P1, P2, ROWS, COLS
TILE = 45
UI_WIDTH = 350
WIDTH = COLS * TILE + UI_WIDTH
HEIGHT = ROWS * TILE
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 150)
BG_COLOR = (10, 10, 15)

def init_display():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Проєкт: Tron AI')
    font = pygame.font.SysFont('Helvetica', 22, bold=True)
    small_font = pygame.font.SysFont('Helvetica', 14, bold=True)
    return (screen, font, small_font)

def draw_glow(surface, color, pos, radius):
    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        alpha = max(0, 150 - r / radius * 150)
        pygame.draw.circle(glow_surf, (*color, int(alpha)), (radius, radius), r)
    surface.blit(glow_surf, (pos[0] - radius, pos[1] - radius))

def draw_hud(screen, f, sf, state, score, auto, history_scores, fps, ai_depth):
    pygame.draw.rect(screen, (20, 20, 25), (COLS * TILE, 0, UI_WIDTH, HEIGHT))
    pygame.draw.line(screen, (60, 60, 80), (COLS * TILE, 0), (COLS * TILE, HEIGHT), 2)
    y = 30
    screen.blit(f.render('NEON TRON: AI DEBUG', True, (255, 255, 255)), (COLS * TILE + 20, y))
    y += 40
    mode_color = CYAN if auto else (255, 200, 0)
    screen.blit(sf.render(f"Режим гри: {('AI vs AI (Автопілот)' if auto else 'Гравець vs AI')}", True, mode_color), (COLS * TILE + 20, y))
    y += 25
    screen.blit(sf.render(f'Глибина Minimax: {ai_depth} кроків вперед', True, (150, 255, 150)), (COLS * TILE + 20, y))
    y += 25
    screen.blit(sf.render(f'Швидкість: {fps} FPS', True, (150, 150, 150)), (COLS * TILE + 20, y))
    y += 40
    screen.blit(sf.render(f'Зібрано ядер (СИНІЙ): {state.s1}', True, CYAN), (COLS * TILE + 20, y))
    y += 25
    screen.blit(sf.render(f'Зібрано ядер (ЧЕРВ): {state.s2}', True, MAGENTA), (COLS * TILE + 20, y))
    y += 40
    screen.blit(sf.render('АНАЛІЗ ТЕРИТОРІЇ (FLOOD FILL):', True, (150, 150, 150)), (COLS * TILE + 20, y))
    y += 25
    screen.blit(sf.render(f'СИНІЙ Контроль: {state.get_bfs_area(P1)} крок.', True, CYAN), (COLS * TILE + 20, y))
    y += 25
    screen.blit(sf.render(f'ЧЕРВОНИЙ Контроль: {state.get_bfs_area(P2)} крок.', True, MAGENTA), (COLS * TILE + 20, y))
    y += 40
    screen.blit(sf.render('ШТУЧНА НЕЙРОМЕРЕЖА (ПРОГНОЗ):', True, (150, 150, 150)), (COLS * TILE + 20, y))
    y += 30
    prob_cyan = max(0, min(100, 50 + score / 40))
    screen.blit(sf.render(f'СИНІЙ: {prob_cyan:.1f}%  |  ЧЕРВ: {100 - prob_cyan:.1f}%', True, (255, 255, 255)), (COLS * TILE + 20, y))
    y += 30
    pygame.draw.rect(screen, MAGENTA, (COLS * TILE + 20, y, 300, 20), border_radius=10)
    bar_pos = max(0, min(300, prob_cyan / 100 * 300))
    if bar_pos > 0:
        pygame.draw.rect(screen, CYAN, (COLS * TILE + 20, y, bar_pos, 20), border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), (COLS * TILE + 20 + bar_pos - 3, y - 5, 6, 30), border_radius=3)
    y = HEIGHT - 130
    screen.blit(sf.render('КЕРУВАННЯ:', True, (150, 150, 150)), (COLS * TILE + 20, y))
    y += 25
    screen.blit(sf.render('[СТРІЛОЧКИ] - Рух  |  [ESC] - Вихід', True, (200, 200, 200)), (COLS * TILE + 20, y))
    y += 20
    screen.blit(sf.render('[A] - Автопілот  |  [+]/[-] - Швидкість', True, (200, 200, 200)), (COLS * TILE + 20, y))
    y += 20
    screen.blit(sf.render('[1]-[5] - Глибина пошуку ШІ', True, (200, 200, 200)), (COLS * TILE + 20, y))
    y += 20
    screen.blit(sf.render('[ПРОБІЛ] - Перемикання рівнів', True, (200, 200, 200)), (COLS * TILE + 20, y))

def draw_game_over(screen, font, small_font, state):
    m1, m2 = (state.get_moves(P1), state.get_moves(P2))
    if not m1 and (not m2):
        txt, col = ('НІЧИЯ!', (255, 255, 255))
    elif not m2:
        txt, col = ('ПЕРЕМОГА СИНІХ!', CYAN)
    else:
        txt, col = ('ПЕРЕМОГА ЧЕРВОНИХ!', MAGENTA)
    overlay = pygame.Surface((COLS * TILE, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    text_surf = font.render(txt, True, col)
    draw_glow(screen, col, (COLS * TILE // 2, HEIGHT // 2 - 20), 100)
    screen.blit(text_surf, (COLS * TILE // 2 - text_surf.get_width() // 2, HEIGHT // 2 - 20 - text_surf.get_height() // 2))
    space_surf = small_font.render('Натисніть ПРОБІЛ для нового рівня', True, (200, 200, 200))
    screen.blit(space_surf, (COLS * TILE // 2 - space_surf.get_width() // 2, HEIGHT // 2 + 40))

def draw_state(screen, state, t1, t2):
    screen.fill(BG_COLOR)
    t = pygame.time.get_ticks()
    offset_y = t // 50 % TILE
    offset_x = t // 50 % TILE
    for r in range(-1, ROWS + 1):
        y = r * TILE + offset_y
        if 0 <= y <= HEIGHT:
            pygame.draw.line(screen, (20, 20, 35), (0, y), (COLS * TILE, y), 1)
    for c in range(-1, COLS + 1):
        x = c * TILE + offset_x
        if 0 <= x <= COLS * TILE:
            pygame.draw.line(screen, (20, 20, 35), (x, 0), (x, HEIGHT), 1)
    for r, c in getattr(state, 'static_walls', []):
        if 0 <= r < ROWS and 0 <= c < COLS:
            rect = (c * TILE + 2, r * TILE + 2, TILE - 4, TILE - 4)
            pygame.draw.rect(screen, (20, 20, 30), rect, border_radius=4)
            pygame.draw.rect(screen, (255, 80, 0), rect, width=2, border_radius=4)
            draw_glow(screen, (255, 80, 0), (c * TILE + TILE // 2, r * TILE + TILE // 2), 20)
            pygame.draw.line(screen, (255, 80, 0), (c * TILE + TILE // 3, r * TILE + TILE // 3), (c * TILE + 2 * TILE // 3, r * TILE + 2 * TILE // 3), 2)
            pygame.draw.line(screen, (255, 80, 0), (c * TILE + 2 * TILE // 3, r * TILE + TILE // 3), (c * TILE + TILE // 3, r * TILE + 2 * TILE // 3), 2)
    pulse = 4 * math.sin(t / 200)
    for r, c in state.portals:
        center = (c * TILE + TILE // 2, r * TILE + TILE // 2)
        draw_glow(screen, (0, 255, 100), center, int(30 + pulse))
        pygame.draw.circle(screen, (255, 255, 255), center, int(TILE // 3 + pulse // 2), 2)
        pygame.draw.circle(screen, (0, 255, 100), center, 5)
    angle = t / 500
    for r, c in state.cores:
        center = (c * TILE + TILE // 2, r * TILE + TILE // 2)
        draw_glow(screen, (255, 200, 0), center, 25)
        s = TILE // 3
        pts = [(center[0] + s * math.cos(angle), center[1] + s * math.sin(angle)), (center[0] + s * math.cos(angle + math.pi / 2), center[1] + s * math.sin(angle + math.pi / 2)), (center[0] + s * math.cos(angle + math.pi), center[1] + s * math.sin(angle + math.pi)), (center[0] + s * math.cos(angle + 3 * math.pi / 2), center[1] + s * math.sin(angle + 3 * math.pi / 2))]
        pygame.draw.polygon(screen, (255, 255, 255), pts, 2)

    def draw_trail(trails, base_color, glow_color):
        for tr in trails:
            if len(tr) > 1:
                pts = [(c * TILE + TILE // 2, r * TILE + TILE // 2) for r, c in tr]
                pygame.draw.lines(screen, glow_color, False, pts, 18)
                pygame.draw.lines(screen, base_color, False, pts, 6)
                pygame.draw.lines(screen, (255, 255, 255), False, pts, 2)
                for i in range(len(tr)):
                    px, py = pts[i]
                    pygame.draw.circle(screen, (255, 255, 255), (px, py), 4)
                    pygame.draw.circle(screen, base_color, (px, py), 6, 1)
    draw_trail(t1, CYAN, (0, 80, 120))
    draw_trail(t2, MAGENTA, (120, 0, 40))
    c1, c2 = ((state.p1[1] * TILE + TILE // 2, state.p1[0] * TILE + TILE // 2), (state.p2[1] * TILE + TILE // 2, state.p2[0] * TILE + TILE // 2))
    draw_glow(screen, CYAN, c1, int(50 + pulse * 2))
    draw_glow(screen, MAGENTA, c2, int(50 + pulse * 2))
    pygame.draw.circle(screen, (255, 255, 255), c1, 12)
    pygame.draw.circle(screen, CYAN, c1, 6)
    pygame.draw.circle(screen, (255, 255, 255), c2, 12)
    pygame.draw.circle(screen, MAGENTA, c2, 6)
    scanlines = pygame.Surface((COLS * TILE, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(scanlines, (0, 0, 0, 90), (0, y), (COLS * TILE, y), 1)
    for y in range(2, HEIGHT, 4):
        pygame.draw.line(scanlines, (255, 255, 255, 8), (0, y), (COLS * TILE, y), 1)
    screen.blit(scanlines, (0, 0))
