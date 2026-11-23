import math
import random
import sys

import pygame

import ui
from board import SIZE, LADDERS, SNAKES
from game import Game
from solver import bfs

FPS = 60
ROLL_TIME = 0.5
STEP_TIME = 0.14
SLIDE_TIME = 0.45


def waypoints(old, dice):
    landing = old + dice
    if landing > SIZE:
        return []
    route = [(n, "step") for n in range(old + 1, landing + 1)]
    if landing in LADDERS or landing in SNAKES:
        route.append((LADDERS.get(landing, SNAKES.get(landing)), "slide"))
    return route


class App:
    def __init__(self):
        self.min_throws, _ = bfs()
        self.buttons = ui.make_buttons()
        self.reset()

    def reset(self):
        self.game = Game()
        self.show_path = False
        self.shown = list(self.game.positions)
        self.state = "idle"
        self.timer = 0.0
        self.face = None
        self.mover = 0
        self.route = []
        self.leg_from = 1
        self.refresh_path()

    def refresh_path(self):
        start = self.game.positions[self.game.turn]
        _, self.path = bfs(start)
        self.steps = ui.dice_for_path(self.path)

    @property
    def busy(self):
        return self.state != "idle"

    def roll(self):
        if self.busy or self.game.winner is not None:
            return
        self.state = "rolling"
        self.timer = 0.0

    def finish_roll(self):
        self.mover = self.game.turn
        old = self.game.positions[self.mover]
        self.game.roll()
        self.face = self.game.last_dice
        self.route = waypoints(old, self.game.last_dice)
        self.leg_from = old
        self.timer = 0.0
        self.state = "moving" if self.route else "idle"
        if not self.route:
            self.refresh_path()

    def update(self, dt):
        if self.state == "rolling":
            self.timer += dt
            if int(self.timer / 0.07) != int((self.timer - dt) / 0.07):
                self.face = random.randint(1, 6)
            if self.timer >= ROLL_TIME:
                self.finish_roll()
        elif self.state == "moving":
            self.timer += dt
            target, kind = self.route[0]
            if self.timer >= (STEP_TIME if kind == "step" else SLIDE_TIME):
                self.shown[self.mover] = target
                self.leg_from = target
                self.route.pop(0)
                self.timer = 0.0
                if not self.route:
                    self.state = "idle"
                    self.shown = list(self.game.positions)
                    if self.game.winner is None:
                        self.refresh_path()

    def token_pixel(self, player):
        if self.state != "moving" or player != self.mover:
            return ui.cell_center(self.shown[player]), 0.0
        target, kind = self.route[0]
        t = min(1.0, self.timer / (STEP_TIME if kind == "step" else SLIDE_TIME))
        if kind == "slide":
            t = t * t * (3 - 2 * t)
        x1, y1 = ui.cell_center(self.leg_from)
        x2, y2 = ui.cell_center(target)
        lift = math.sin(math.pi * t) * 10 if kind == "step" else 0.0
        return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t), lift

    def view(self):
        turn = self.mover if self.busy else self.game.turn
        winner = None if self.busy else self.game.winner
        return {
            "busy": self.busy,
            "turn": turn,
            "winner": winner,
            "dice_face": self.face,
            "shown_pos": self.shown,
            "show_path": self.show_path,
            "path_start": self.path[0] if self.path else self.game.positions[turn],
            "steps": self.steps,
            "min_throws": self.min_throws,
        }

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.roll()
            elif event.key == pygame.K_b:
                self.show_path = not self.show_path
            elif event.key == pygame.K_r:
                self.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game.winner is not None and not self.busy:
                if self.buttons["again"].hovered(event.pos):
                    self.reset()
                return
            if self.buttons["roll"].hovered(event.pos):
                self.roll()
            elif self.buttons["path"].hovered(event.pos):
                self.show_path = not self.show_path
            elif self.buttons["reset"].hovered(event.pos):
                self.reset()

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        view = self.view()
        screen.fill(ui.BG)
        ui.draw_board(screen)
        if self.show_path and view["winner"] is None and not self.busy:
            ui.draw_path(screen, self.path)

        pixels = [self.token_pixel(p) for p in range(2)]
        same = self.shown[0] == self.shown[1] and not self.busy
        order = [1 - self.mover, self.mover] if self.busy else [0, 1]
        for p in order:
            pos, lift = pixels[p]
            offset = (-10 if p == 0 else 10) if same else 0
            ui.draw_token(screen, pos, p, offset, lift)

        ui.draw_panel(screen, self.game, view, self.buttons, mouse)
        if view["winner"] is not None:
            ui.draw_winner(screen, self.game, self.min_throws, self.buttons, mouse)


def main():
    pygame.init()
    screen = pygame.display.set_mode((ui.WINDOW_W, ui.WINDOW_H))
    pygame.display.set_caption("Ular Tangga BFS")
    clock = pygame.time.Clock()
    app = App()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            else:
                app.handle(event)

        app.update(dt)
        app.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()