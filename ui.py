import math

import pygame
import pygame.gfxdraw

from board import SIZE, LADDERS, SNAKES, move

CELL = 60
COLS = 10
BOARD_X = 20
BOARD_Y = 20
BOARD_PX = CELL * COLS
PANEL_X = BOARD_X + BOARD_PX + 20
PANEL_W = 320
WINDOW_W = PANEL_X + PANEL_W + 20
WINDOW_H = BOARD_PX + 40

BG = (18, 20, 28)
PANEL = (27, 30, 43)
CARD = (37, 42, 59)
CARD_LINE = (52, 58, 80)
TEXT = (255, 255, 255)
MUTED = (169, 175, 199)
NUM = (122, 90, 46)

CELL_A = (255, 247, 230)
CELL_B = (255, 233, 194)
CELL_LADDER = (215, 245, 225)
CELL_SNAKE = (255, 220, 221)
CELL_GOAL = (255, 210, 77)
GRID_LINE = (196, 160, 104)

RAIL = (138, 90, 34)
RUNG = (201, 138, 60)
SNAKE_OUTLINE = (30, 42, 34)
SNAKE_COLORS = [(34, 165, 91), (229, 72, 77), (142, 78, 198), (18, 165, 148),
                (214, 64, 159), (62, 99, 221), (247, 107, 21), (70, 167, 88)]

PATH = (124, 58, 237)
PATH_SOFT = (58, 44, 102)
PATH_TEXT = (217, 204, 255)
LADDER_TEXT = (126, 226, 168)
GOLD = (255, 210, 77)

PLAYER_COLORS = [(47, 107, 255), (255, 138, 31)]
PLAYER_SHADE = [(28, 71, 194), (204, 102, 10)]
PLAYER_NAMES = ["Player 1", "Player 2"]

_fonts = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = pygame.font.SysFont("segoeui,helveticaneue,arial", size, bold=bold)
    return _fonts[key]


def text(screen, s, size, color, pos, bold=False, anchor="topleft"):
    surf = font(size, bold).render(str(s), True, color)
    rect = surf.get_rect(**{anchor: pos})
    screen.blit(surf, rect)
    return rect


def circle(screen, color, center, r):
    x, y = int(center[0]), int(center[1])
    pygame.gfxdraw.filled_circle(screen, x, y, r, color)
    pygame.gfxdraw.aacircle(screen, x, y, r, color)


def cell_center(n):
    row = (n - 1) // COLS
    col = (n - 1) % COLS
    # zig-zag board: odd rows (counted from the bottom) run right to left
    if row % 2 == 1:
        col = COLS - 1 - col
    x = BOARD_X + col * CELL + CELL // 2
    y = BOARD_Y + BOARD_PX - (row * CELL + CELL // 2)
    return x, y


def throws_text(n):
    return "%d throw%s" % (n, "" if n == 1 else "s")


def dice_for_path(path):
    steps = []
    for a, b in zip(path, path[1:]):
        d = next(d for d in range(1, 7) if move(a, d) == b)
        steps.append((d, b, a + d in LADDERS))
    return steps


def _thick_polyline(screen, color, points, width):
    r = width // 2
    for a, b in zip(points, points[1:]):
        pygame.draw.line(screen, color, a, b, width)
    for p in points:
        circle(screen, color, p, r)


def _snake_points(head, tail):
    x1, y1 = cell_center(head)
    x2, y2 = cell_center(tail)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    nx, ny = -dy / length, dx / length
    waves = max(1.5, length / 90)
    amp = min(16, length / 8)
    pts = []
    for i in range(41):
        t = i / 40
        off = amp * math.sin(math.pi * t) ** 0.6 * math.sin(t * waves * 2 * math.pi)
        pts.append((x1 + dx * t + nx * off, y1 + dy * t + ny * off))
    return pts


def _draw_snake(screen, head, tail, color):
    pts = _snake_points(head, tail)
    _thick_polyline(screen, SNAKE_OUTLINE, pts, 15)
    _thick_polyline(screen, color, pts, 11)
    for p in pts[3:-2:4]:
        circle(screen, (255, 255, 255), p, 1)

    hx, hy = pts[0]
    fx, fy = hx - pts[2][0], hy - pts[2][1]
    f = math.hypot(fx, fy) or 1
    fx, fy = fx / f, fy / f
    sx, sy = -fy, fx
    tongue = (hx + fx * 13, hy + fy * 13)
    for side in (1, -1):
        tip = (tongue[0] + fx * 6 + sx * 3 * side, tongue[1] + fy * 6 + sy * 3 * side)
        pygame.draw.line(screen, (229, 72, 77), tongue, tip, 2)
    circle(screen, SNAKE_OUTLINE, (hx, hy), 12)
    circle(screen, color, (hx, hy), 10)
    for side in (1, -1):
        ex, ey = hx + fx * 4 + sx * 4.5 * side, hy + fy * 4 + sy * 4.5 * side
        circle(screen, (255, 255, 255), (ex, ey), 3)
        circle(screen, (17, 17, 17), (ex + fx, ey + fy), 1)


def _draw_ladder(screen, foot, top):
    x1, y1 = cell_center(foot)
    x2, y2 = cell_center(top)
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ox, oy = -dy / length * 9, dx / length * 9
    rungs = max(2, int(length // 20))
    for i in range(1, rungs):
        t = i / rungs
        cx, cy = x1 + dx * t, y1 + dy * t
        pygame.draw.line(screen, RUNG, (cx - ox, cy - oy), (cx + ox, cy + oy), 4)
    for s in (1, -1):
        pygame.draw.line(screen, RAIL, (x1 + s * ox, y1 + s * oy), (x2 + s * ox, y2 + s * oy), 5)


_board_cache = None


def draw_board(screen):
    # the board is static, so draw it once and reuse it every frame
    global _board_cache
    if _board_cache is None:
        _board_cache = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
        _render_board(_board_cache)
    screen.blit(_board_cache, (0, 0))


def _render_board(screen):
    frame = pygame.Rect(BOARD_X - 4, BOARD_Y - 4, BOARD_PX + 8, BOARD_PX + 8)
    pygame.draw.rect(screen, (44, 50, 71), frame, border_radius=18)

    for n in range(1, SIZE + 1):
        cx, cy = cell_center(n)
        rect = pygame.Rect(cx - CELL // 2, cy - CELL // 2, CELL, CELL)
        row = (n - 1) // COLS
        color = CELL_A if (n + row) % 2 else CELL_B
        if n in LADDERS:
            color = CELL_LADDER
        elif n in SNAKES:
            color = CELL_SNAKE
        elif n == SIZE:
            color = CELL_GOAL
        pygame.draw.rect(screen, color, rect)
        text(screen, n, 13, NUM, (rect.x + 5, rect.y + 3), bold=True)

    for i in range(COLS + 1):
        x = BOARD_X + i * CELL
        y = BOARD_Y + i * CELL
        pygame.draw.line(screen, GRID_LINE, (x, BOARD_Y), (x, BOARD_Y + BOARD_PX), 2)
        pygame.draw.line(screen, GRID_LINE, (BOARD_X, y), (BOARD_X + BOARD_PX, y), 2)

    for foot, top in LADDERS.items():
        _draw_ladder(screen, foot, top)
    for i, (head, tail) in enumerate(SNAKES.items()):
        _draw_snake(screen, head, tail, SNAKE_COLORS[i % len(SNAKE_COLORS)])


def _dashed(screen, color, a, b, width, dash=10, gap=7):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    d = 0
    while d < length:
        e = min(d + dash, length)
        pygame.draw.line(screen, color, (a[0] + ux * d, a[1] + uy * d), (a[0] + ux * e, a[1] + uy * e), width)
        d += dash + gap


def draw_path(screen, path):
    if len(path) < 2:
        return
    pts = [cell_center(n) for n in path]
    _thick_polyline(screen, (255, 255, 255), pts, 9)
    for a, b in zip(pts, pts[1:]):
        _dashed(screen, PATH, a, b, 4)
    for i, p in enumerate(pts[1:], 1):
        circle(screen, (255, 255, 255), p, 13)
        circle(screen, PATH, p, 11)
        text(screen, i, 13, TEXT, p, bold=True, anchor="center")


def draw_token(screen, pos, player, offset=0.0, lift=0.0):
    x, y = pos
    x += offset
    y += 10 - lift
    shadow = pygame.Surface((28, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
    screen.blit(shadow, (x - 14, y + 7 + lift))
    circle(screen, (255, 255, 255), (x, y), 14)
    circle(screen, PLAYER_COLORS[player], (x, y), 11)
    text(screen, player + 1, 13, TEXT, (x, y), bold=True, anchor="center")


def draw_dice(screen, value, rect):
    pygame.draw.rect(screen, (255, 255, 255), rect, border_radius=16)
    pygame.draw.rect(screen, (226, 228, 238), rect, 3, border_radius=16)
    if value is None:
        text(screen, "?", 30, (27, 30, 43), rect.center, bold=True, anchor="center")
        return
    layout = {1: [(1, 1)], 2: [(0, 0), (2, 2)], 3: [(0, 0), (1, 1), (2, 2)],
              4: [(0, 0), (2, 0), (0, 2), (2, 2)], 5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
              6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)]}[value]
    g = rect.w / 4
    for c, r in layout:
        circle(screen, (27, 30, 43), (rect.x + g * (c + 1), rect.y + g * (r + 1)), int(rect.w / 11))


class Button:
    def __init__(self, rect, label, key_hint, primary=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.key_hint = key_hint
        self.primary = primary

    def hovered(self, mouse):
        return self.rect.collidepoint(mouse)

    def draw(self, screen, mouse, enabled=True, active=False):
        hover = enabled and self.hovered(mouse)
        if self.primary:
            base = PLAYER_COLORS[0] if enabled else (70, 78, 104)
            shade = PLAYER_SHADE[0] if enabled else (50, 56, 76)
            if hover:
                base = (78, 130, 255)
            pygame.draw.rect(screen, shade, self.rect.move(0, 4), border_radius=14)
            pygame.draw.rect(screen, base, self.rect, border_radius=14)
            size = 18
        else:
            base = PATH_SOFT if active else CARD
            if hover:
                base = tuple(min(c + 14, 255) for c in base)
            pygame.draw.rect(screen, base, self.rect, border_radius=12)
            pygame.draw.rect(screen, PATH if active else CARD_LINE, self.rect, 1, border_radius=12)
            size = 14

        label = font(size, True).render(self.label, True, TEXT if enabled else MUTED)
        hint = font(11, True).render(self.key_hint, True, TEXT)
        hint_box = pygame.Rect(0, 0, hint.get_width() + 12, hint.get_height() + 2)
        total = label.get_width() + 10 + hint_box.w
        x = self.rect.centerx - total // 2
        screen.blit(label, label.get_rect(midleft=(x, self.rect.centery)))
        hint_box.midleft = (x + label.get_width() + 10, self.rect.centery)
        pygame.draw.rect(screen, tuple(min(c + 40, 255) for c in base), hint_box, border_radius=6)
        screen.blit(hint, hint.get_rect(center=hint_box.center))


def make_buttons():
    return {
        "roll": Button((PANEL_X, 156, PANEL_W, 52), "Roll Dice", "SPACE", primary=True),
        "path": Button((PANEL_X, 222, (PANEL_W - 10) // 2, 40), "BFS Path", "B"),
        "reset": Button((PANEL_X + (PANEL_W + 10) // 2, 222, (PANEL_W - 10) // 2, 40), "Restart", "R"),
        "again": Button((BOARD_X + 150, BOARD_Y + 400, 300, 48), "Play Again", "R", primary=True),
    }


def _card(screen, rect, border=None):
    pygame.draw.rect(screen, CARD, rect, border_radius=14)
    if border:
        pygame.draw.rect(screen, border, rect, 2, border_radius=14)


def draw_panel(screen, game, view, buttons, mouse):
    pygame.draw.rect(screen, BG, (PANEL_X - 10, 0, PANEL_W + 30, WINDOW_H))

    text(screen, "Snakes & Ladders", 24, TEXT, (PANEL_X, 14), bold=True)
    badge = font(12, True).render("BFS Solver", True, PATH_TEXT)
    brect = pygame.Rect(0, 0, badge.get_width() + 20, 24)
    brect.topright = (PANEL_X + PANEL_W, 24)
    pygame.draw.rect(screen, PATH_SOFT, brect, border_radius=12)
    screen.blit(badge, badge.get_rect(center=brect.center))

    turn_card = pygame.Rect(PANEL_X, 62, PANEL_W, 82)
    _card(screen, turn_card)
    dice_rect = pygame.Rect(turn_card.x + 12, turn_card.y + 9, 64, 64)
    draw_dice(screen, view["dice_face"], dice_rect)
    tx = dice_rect.right + 16
    if view["winner"] is None:
        text(screen, "Turn", 13, MUTED, (tx, turn_card.y + 10), bold=True)
        text(screen, PLAYER_NAMES[view["turn"]], 26, PLAYER_COLORS[view["turn"]], (tx, turn_card.y + 26), bold=True)
        last = "-" if game.last_dice is None else game.last_dice
        text(screen, "Last roll: %s" % last, 13, MUTED, (tx, turn_card.y + 58))
    else:
        text(screen, "Game over", 13, MUTED, (tx, turn_card.y + 14), bold=True)
        text(screen, "We have a winner!", 22, GOLD, (tx, turn_card.y + 32), bold=True)

    busy = view["busy"]
    buttons["roll"].draw(screen, mouse, enabled=not busy and view["winner"] is None)
    buttons["path"].draw(screen, mouse, active=view["show_path"])
    buttons["reset"].draw(screen, mouse)

    y = 276
    for p in range(2):
        active = view["winner"] is None and view["turn"] == p
        card = pygame.Rect(PANEL_X, y, PANEL_W, 62)
        _card(screen, card, PLAYER_COLORS[p] if active else None)
        circle(screen, PLAYER_COLORS[p], (card.x + 20, card.y + 19), 7)
        text(screen, PLAYER_NAMES[p], 15, TEXT, (card.x + 34, card.y + 9), bold=True)
        text(screen, throws_text(game.throws_of(p)), 13, MUTED, (card.right - 14, card.y + 11), anchor="topright")
        pos = view["shown_pos"][p]
        bar = pygame.Rect(card.x + 14, card.y + 40, PANEL_W - 110, 8)
        pygame.draw.rect(screen, CARD_LINE, bar, border_radius=4)
        fill = bar.copy()
        fill.w = max(8, int(bar.w * pos / SIZE))
        pygame.draw.rect(screen, PLAYER_COLORS[p], fill, border_radius=4)
        text(screen, "Square %d" % pos, 13, TEXT, (card.right - 14, card.y + 35), bold=True, anchor="topright")
        y += 72

    _draw_bfs_card(screen, game, view, pygame.Rect(PANEL_X, y, PANEL_W, WINDOW_H - 20 - y))


def _draw_bfs_card(screen, game, view, rect):
    _card(screen, rect, PATH_SOFT)
    x, y = rect.x + 14, rect.y + 12
    text(screen, "Shortest route (BFS)", 14, PATH_TEXT, (x, y), bold=True)

    if view["winner"] is not None:
        text(screen, "Winner needed %s." % throws_text(game.throws_of(view["winner"])), 14, TEXT, (x, y + 30), bold=True)
        text(screen, "BFS minimum: %s." % throws_text(view["min_throws"]), 14, MUTED, (x, y + 54))
        return

    text(screen, "from square %d" % view["path_start"], 12, MUTED, (rect.right - 14, y + 2), anchor="topright")
    steps = view["steps"]
    count = throws_text(len(steps))
    text(screen, count, 15, TEXT, (x, y + 26), bold=True)
    text(screen, "left to reach square 100", 13, MUTED, (x + font(15, True).size(count)[0] + 6, y + 28))

    gap = 5
    w = (rect.w - 28 - gap * 6) // 7
    cy = y + 56
    for i, (d, dest, ladder) in enumerate(steps):
        chip = pygame.Rect(x + i * (w + gap), cy, w, 58)
        pygame.draw.rect(screen, CARD_LINE, chip, border_radius=10)
        text(screen, "#%d" % (i + 1), 10, MUTED, (chip.centerx, chip.y + 4), bold=True, anchor="midtop")
        text(screen, d, 22, TEXT, (chip.centerx, chip.y + 16), bold=True, anchor="midtop")
        mark = ("^%d" if ladder else "%d") % dest
        text(screen, mark, 11, LADDER_TEXT if ladder else PATH_TEXT, (chip.centerx, chip.bottom - 4), bold=True, anchor="midbottom")

    text(screen, "Big number = dice needed, ^ = ladder climb", 11, MUTED, (x, cy + 66))


def draw_winner(screen, game, min_throws, buttons, mouse):
    shade = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
    shade.fill((15, 17, 26, 185))
    screen.blit(shade, (BOARD_X, BOARD_Y))

    card = pygame.Rect(0, 0, 360, 300)
    card.center = (BOARD_X + BOARD_PX // 2, BOARD_Y + BOARD_PX // 2)
    pygame.draw.rect(screen, (255, 255, 255), card, border_radius=22)

    w = game.winner
    circle(screen, GOLD, (card.centerx, card.y + 46), 32)
    circle(screen, PLAYER_COLORS[w], (card.centerx, card.y + 46), 26)
    text(screen, w + 1, 28, TEXT, (card.centerx, card.y + 46), bold=True, anchor="center")
    text(screen, "%s Wins!" % PLAYER_NAMES[w], 32, PLAYER_COLORS[w], (card.centerx, card.y + 88), bold=True, anchor="midtop")

    throws = game.throws_of(w)
    for i, (label, value, bg, fg) in enumerate([
            ("Winner's throws", throws, (242, 244, 250), (27, 30, 43)),
            ("Minimum BFS", min_throws, (238, 232, 255), PATH)]):
        box = pygame.Rect(card.x + 24 + i * 162, card.y + 140, 150, 66)
        pygame.draw.rect(screen, bg, box, border_radius=12)
        text(screen, label, 12, (91, 97, 120), (box.centerx, box.y + 8), bold=True, anchor="midtop")
        text(screen, value, 28, fg, (box.centerx, box.y + 26), bold=True, anchor="midtop")

    extra = throws - min_throws
    msg = "Matched the shortest route!" if extra <= 0 else "%s more than the shortest route." % throws_text(extra)
    text(screen, msg, 13, (91, 97, 120), (card.centerx, card.y + 216), anchor="midtop")

    buttons["again"].rect.midbottom = (card.centerx, card.bottom - 18)
    buttons["again"].rect.w = card.w - 48
    buttons["again"].rect.centerx = card.centerx
    buttons["again"].draw(screen, mouse)