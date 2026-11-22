import pygame

from board import SIZE, LADDERS, SNAKES

CELL = 60
COLS = 10
BOARD_PX = CELL * COLS
PANEL_W = 260
WINDOW_W = BOARD_PX + PANEL_W
WINDOW_H = BOARD_PX

CELL_LIGHT = (245, 236, 210)
CELL_DARK = (222, 205, 160)
GRID_LINE = (150, 130, 90)
TEXT_DARK = (60, 50, 30)
LADDER_COLOR = (139, 90, 43)
SNAKE_BODY = (40, 140, 70)
SNAKE_HEAD = (200, 40, 40)
PATH_COLOR = (230, 60, 200)
PANEL_BG = (35, 40, 55)
PANEL_TEXT = (235, 235, 235)
HINT_TEXT = (180, 190, 210)
PLAYER_COLORS = [(40, 90, 220), (240, 140, 20)]
PLAYER_NAMES = ["Pemain 1", "Pemain 2"]

_fonts = {}


def _font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("arial", size, bold=bold)
    return _fonts[key]


def cell_center(n):
    row = (n - 1) // COLS
    col = (n - 1) % COLS
    # papan zig-zag: baris ganjil (dari bawah) dibaca kanan ke kiri
    if row % 2 == 1:
        col = COLS - 1 - col
    x = col * CELL + CELL // 2
    y = BOARD_PX - (row * CELL + CELL // 2)
    return x, y


def _draw_ladder(screen, foot, top):
    x1, y1 = cell_center(foot)
    x2, y2 = cell_center(top)
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** 0.5 or 1
    ox, oy = -dy / length * 7, dx / length * 7

    for sign in (1, -1):
        pygame.draw.line(screen, LADDER_COLOR,
                         (x1 + sign * ox, y1 + sign * oy),
                         (x2 + sign * ox, y2 + sign * oy), 4)

    rungs = max(2, int(length // 22))
    for i in range(1, rungs):
        t = i / rungs
        cx, cy = x1 + dx * t, y1 + dy * t
        pygame.draw.line(screen, LADDER_COLOR, (cx - ox, cy - oy), (cx + ox, cy + oy), 3)


def _draw_snake(screen, head, tail):
    hx, hy = cell_center(head)
    tx, ty = cell_center(tail)
    pygame.draw.line(screen, SNAKE_BODY, (hx, hy), (tx, ty), 7)
    pygame.draw.circle(screen, SNAKE_BODY, (tx, ty), 5)
    pygame.draw.circle(screen, SNAKE_HEAD, (hx, hy), 9)


def draw_board(screen):
    for n in range(1, SIZE + 1):
        cx, cy = cell_center(n)
        rect = pygame.Rect(cx - CELL // 2, cy - CELL // 2, CELL, CELL)
        color = CELL_LIGHT if n % 2 == 0 else CELL_DARK
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, GRID_LINE, rect, 1)
        label = _font(15).render(str(n), True, TEXT_DARK)
        screen.blit(label, (rect.x + 4, rect.y + 3))

    for foot, top in LADDERS.items():
        _draw_ladder(screen, foot, top)
    for head, tail in SNAKES.items():
        _draw_snake(screen, head, tail)


def draw_players(screen, game):
    same_cell = game.positions[0] == game.positions[1]
    for player, pos in enumerate(game.positions):
        cx, cy = cell_center(pos)
        shift = (-9 if player == 0 else 9) if same_cell else 0
        center = (cx + shift, cy + 8)
        pygame.draw.circle(screen, (255, 255, 255), center, 13)
        pygame.draw.circle(screen, PLAYER_COLORS[player], center, 11)


def draw_info(screen, game, min_throws=None):
    pygame.draw.rect(screen, PANEL_BG, pygame.Rect(BOARD_PX, 0, PANEL_W, WINDOW_H))

    x = BOARD_PX + 18
    y = 18

    def put(text, size=18, color=PANEL_TEXT, bold=False, gap=8):
        nonlocal y
        surf = _font(size, bold).render(text, True, color)
        screen.blit(surf, (x, y))
        y += surf.get_height() + gap

    put("ULAR TANGGA", 26, bold=True, gap=14)

    if game.winner is None:
        put("Giliran:")
        put(PLAYER_NAMES[game.turn], 24, PLAYER_COLORS[game.turn], True, 14)
    else:
        put("PEMENANG:")
        put(PLAYER_NAMES[game.winner], 24, PLAYER_COLORS[game.winner], True, 14)

    dice = "-" if game.last_dice is None else str(game.last_dice)
    put("Dadu terakhir: " + dice, gap=14)

    for p in range(2):
        text = "%s: kotak %d (%d lemparan)" % (PLAYER_NAMES[p], game.positions[p], game.throws_of(p))
        put(text, 16, PLAYER_COLORS[p], gap=6)

    y += 10
    if game.winner is not None and min_throws is not None:
        put("Pemenang butuh %d lemparan." % game.throws_of(game.winner), 16, gap=4)
        put("BFS minimal %d lemparan." % min_throws, 16, gap=10)
        put("Tekan R untuk main lagi", 15, (255, 220, 120), gap=14)

    y = WINDOW_H - 110
    put("SPASI : lempar dadu", 15, HINT_TEXT, gap=4)
    put("B     : jalur BFS", 15, HINT_TEXT, gap=4)
    put("R     : ulang permainan", 15, HINT_TEXT, gap=4)
    put("ESC   : keluar", 15, HINT_TEXT, gap=4)


def draw_path(screen, path):
    if len(path) < 2:
        return
    points = [cell_center(n) for n in path]
    pygame.draw.lines(screen, PATH_COLOR, False, points, 4)
    for p in points:
        pygame.draw.circle(screen, PATH_COLOR, p, 6)
    pygame.draw.circle(screen, (255, 255, 255), points[0], 4)
    pygame.draw.circle(screen, (255, 255, 255), points[-1], 4)