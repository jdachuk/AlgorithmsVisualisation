"""
author: edacjos
created: 9/7/19
"""

import tkinter as tk
import random

DELAY = 20
WIDTH = HEIGHT = 603
COLUMNS = ROWS = 50
WALL_RATIO = .3
ALLOW_DIAGONALS = False


class Spot(object):

    def __init__(self, i, j, x, y, width, height, is_wall=False):
        self.i, self.j = i, j
        self.x, self.y = x, y
        self.width, self.height = width, height

        self.f = 0
        self.g = 0
        self.h = 0

        self.is_wall = is_wall
        self.color = '#ffffff'

        self.neighbours = []
        self.previous = None

    def add_neighbours(self, grid, allow_diags=False):
        if self.i < len(grid) - 1:
            self.neighbours.append(grid[self.i + 1][self.j])
        if self.i > 0:
            self.neighbours.append(grid[self.i - 1][self.j])
        if self.j < len(grid[self.i]) - 1:
            self.neighbours.append(grid[self.i][self.j + 1])
        if self.j > 0:
            self.neighbours.append(grid[self.i][self.j - 1])
        if allow_diags:
            if self.i > 0 and self.j > 0:
                self.neighbours.append(grid[self.i - 1][self.j - 1])
            if self.i > 0 and self.j < len(grid) - 1:
                self.neighbours.append(grid[self.i - 1][self.j + 1])
            if self.i < len(grid) - 1 and self.j > 0:
                self.neighbours.append(grid[self.i + 1][self.j - 1])
            if self.i < len(grid) - 1 and self.j < len(grid) - 1:
                self.neighbours.append(grid[self.i + 1][self.j + 1])

    def get_color(self):
        if self.is_wall:
            return '#000000'
        else:
            return self.color

    def __eq__(self, other):
        return self.i == other.i and self.j == other.j

    def __gt__(self, other):
        return self.f > other.f

    def __lt__(self, other):
        return self.f < other.f

    def __ge__(self, other):
        return self.f >= other.f

    def __le__(self, other):
        return self.f <= other.f

    def __repr__(self):
        return f'({self.i} {self.j} {self.f}) :{self.previous}'


class Map(object):
    def __init__(self, cols, rows, x, y, w, h, wall_ratio=.3):
        self.cols = cols
        self.rows = rows

        self.grid = []
        self.path = []

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.wall_ratio = wall_ratio

        for i in range(cols):
            self.grid.append([])

        for i in range(cols):
            for j in range(rows):
                is_wall = random.random() < self.wall_ratio
                self.grid[i].append(
                    Spot(i, j, x + i * w // cols, y + j * h // rows, w // cols, h // rows, is_wall)
                )

        self.grid[0][0].is_wall = False
        self.grid[-1][-1].is_wall = False

        for i in range(cols):
            for j in range(rows):
                self.grid[i][j].add_neighbours(self.grid, ALLOW_DIAGONALS)


def distance(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return (dx * dx + dy * dy)**1/2


def heuristic(a, b):
    if ALLOW_DIAGONALS:
        return distance(a.i, a.j, b.i, b.j)
    return abs(a.i - b.i) + abs(a.j - b.j)


class AStar:
    def __init__(self, start, end, grid):
        self.start = start
        self.end = end
        self.grid = grid

        self.open_set = [self.start]
        self.closed_set = []
        self.path = []

        self.finished = False

    def solve(self):
        if len(self.open_set) > 0:
            current = min(self.open_set)
            current_spots = []

            for spot in self.open_set:
                if spot.f == current.f:
                    current_spots.append(spot)

            if current == self.end:
                self.finished = True

            for current in current_spots:
                self.open_set.remove(current)
                self.closed_set.append(current)

                for neighbour in current.neighbours:
                    if neighbour not in self.closed_set and not neighbour.is_wall:
                        tentative_score = current.g + distance(current.i, current.j, neighbour.i, neighbour.j)

                        new_path = False
                        if neighbour not in self.open_set:
                            self.open_set.append(neighbour)
                            new_path = True
                        else:
                            if tentative_score <= current.g:
                                new_path = True

                        if new_path:
                            neighbour.g = tentative_score
                            neighbour.f = neighbour.g + heuristic(neighbour, self.end)
                            neighbour.previous = current
        else:
            self.finished = True
            return

        for node in self.open_set:
            node.color = '#ff0000'
        for node in self.closed_set:
            node.color = '#00ff00'

        self.fill_path(current)

    def fill_path(self, current):
        self.path = []
        temp = current
        while temp.previous:
            self.path.append(temp)
            temp = temp.previous
        self.path.append(self.start)

        for node in self.path:
            node.color = '#0000ff'


class Canvas(tk.Canvas):
    class ControlKeys:
        GENERATE_KEY = 'g'
        FIND_PATH_KEY = 'p'

    def __init__(self, **kw):
        super().__init__(width=WIDTH, height=HEIGHT, **kw)
        self.padx = 2
        self.pady = 2

        self.cols = COLUMNS
        self.rows = ROWS

        self.running = False

        self.map = Map(self.cols, self.rows,
                       self.padx, self.pady,
                       WIDTH - self.padx, HEIGHT - self.pady,
                       WALL_RATIO)
        self.algorithm = None

        self.bind_all('<Key>', self.on_key_pressed)

        self.after_id = self.after(DELAY, self.on_timer)

    def on_key_pressed(self, key):
        key = key.keysym

        if key == self.ControlKeys.GENERATE_KEY:
            self.generate_map()
        elif key == self.ControlKeys.FIND_PATH_KEY:
            self.algorithm = AStar(self.map.grid[0][0], self.map.grid[-1][-1], self.map.grid)

    def on_timer(self):
        self.draw()

        if self.algorithm and not self.algorithm.finished:
            self.algorithm.solve()

        self.after_id = self.after(DELAY, self.on_timer)

    def generate_map(self):
        self.map = Map(self.map.cols, self.map.rows,
                       self.map.x, self.map.y,
                       self.map.w, self.map.h,
                       self.map.wall_ratio)

    def draw(self):
        self.delete(tk.ALL)

        for i in range(self.map.cols):
            for j in range(self.map.rows):
                self.draw_spot(self.map.grid[i][j])

    def draw_spot(self, spot):
        color = spot.get_color()

        if color != '#ffffff':
            if ALLOW_DIAGONALS:
                self.create_oval((spot.x, spot.y, spot.x + spot.width, spot.y + spot.height), fill=color, width=0)
            else:
                self.create_rectangle((spot.x, spot.y, spot.x + spot.width, spot.y + spot.height), fill=color, width=0)


class Window(tk.Frame):
    def __init__(self, **kw):
        super().__init__(width=WIDTH, height=HEIGHT, **kw)
        self.canvas = Canvas(bg='#ffffff')
        self.canvas.grid(row=0, column=0, padx=10, pady=10)


if __name__ == '__main__':
    root = tk.Tk()
    window = Window()
    root.mainloop()
