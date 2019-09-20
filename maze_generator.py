"""
author: edacjos
created: 9/7/19
"""

import tkinter as tk
import random


DELAY = 200
WIDTH = HEIGHT = 600
ROWS = COLUMNS = 15


class Cell(object):
    @staticmethod
    def get_index(i: int, j: int):
        return j + i * COLUMNS

    def __init__(self, i: int, j: int, x: int, y: int, w: int, h: int, canvas: tk.Canvas):
        self.i, self.j = i, j
        self.x, self.y = x, y
        self.width, self.height = w, h
        self.padx = self.pady = 3
        self.canvas = canvas

        self.visited = False
        self.highlighted = False
        self.finished = False

        self.walls = [
            True,  # top
            True,  # right
            True,  # bottom
            True   # left
        ]

        self.neighbours = []

    def draw(self):
        if self.walls[0]:
            self.canvas.create_line((self.x, self.y, self.x + self.width, self.y), width=5)
        if self.walls[1]:
            self.canvas.create_line((self.x + self.width, self.y, self.x + self.width, self.y + self.height), width=5)
        if self.walls[2]:
            self.canvas.create_line((self.x, self.y + self.height, self.x + self.width, self.y + self.height), width=5)
        if self.walls[3]:
            self.canvas.create_line((self.x, self.y, self.x, self.y + self.height), width=5)

        if not self.finished:
            if self.visited:
                self.canvas.create_rectangle((self.x + self.padx, self.y + self.pady,
                                              self.x + self.width - self.padx, self.y + self.height - self.pady),
                                             fill='#a000ef', width=0)
            if self.highlighted:
                self.canvas.create_rectangle((self.x + self.padx, self.y + self.pady,
                                              self.x + self.width - self.padx, self.y + self.height - self.pady),
                                             fill='#00ffff', width=0)

    def break_the_walls(self, other):
        x = self.i - other.i
        if x == 1:
            self.walls[3] = False
            other.walls[1] = False
        elif x == -1:
            self.walls[1] = False
            other.walls[3] = False
        y = self.j - other.j
        if y == 1:
            self.walls[0] = False
            other.walls[2] = False
        elif y == -1:
            self.walls[2] = False
            other.walls[0] = False

    def check_neighbours(self, grid: list):
        neighbours = []

        if self.i > 0 and not grid[self.get_index(self.i - 1, self.j)].visited:
            neighbours.append(grid[self.get_index(self.i - 1, self.j)])
        if self.i < COLUMNS - 1 and not grid[self.get_index(self.i + 1, self.j)].visited:
            neighbours.append(grid[self.get_index(self.i + 1, self.j)])
        if self.j > 0 and not grid[self.get_index(self.i, self.j - 1)].visited:
            neighbours.append(grid[self.get_index(self.i, self.j - 1)])
        if self.j < COLUMNS - 1 and not grid[self.get_index(self.i, self.j + 1)].visited:
            neighbours.append(grid[self.get_index(self.i, self.j + 1)])

        if len(neighbours) > 0:
            return random.choice(neighbours)
        else:
            return None


class MazeGenerator:
    def __init__(self, cells: list):
        self.cells = cells
        self.current = self.cells[0]
        self.current.visited = True
        self.current.highlighted = True
        self.stack = []

    def generate(self):
        next_cell = self.current.check_neighbours(self.cells)

        if next_cell:
            self.stack.append(self.current)

            self.current.break_the_walls(next_cell)

            self.current.highlighted = False
            self.current = next_cell
            self.current.visited = True
            self.current.highlighted = True
        elif len(self.stack) > 0:
            self.current.highlighted = False
            self.current.finished = True
            self.current = self.stack.pop()
            self.current.highlighted = True
        else:
            self.current.highlighted = False
            self.current.finished = True


class Canvas(tk.Canvas):
    class ControlKeys:
        GENERATE_KEY = 'g'

    def __init__(self, **kw):
        super().__init__(**kw)

        self.cells = []
        for i in range(ROWS):
            for j in range(COLUMNS):
                self.cells.append(Cell(
                    i, j,
                    i * WIDTH // ROWS,
                    j * HEIGHT // COLUMNS,
                    WIDTH // ROWS,
                    HEIGHT // COLUMNS,
                    self
                ))

        self.maze_generator = MazeGenerator(self.cells)

        self.after_id = self.after(DELAY, self.on_timer)

        self.bind_all('<Key>', self.on_key_pressed)

    def on_key_pressed(self, key):
        key = key.keysym

        if key == self.ControlKeys.GENERATE_KEY:
            self.recreate_cells()

    def on_timer(self):
        self.delete(tk.ALL)
        self.maze_generator.generate()
        self.draw()
        self.after_id = self.after(DELAY, self.on_timer)

    def draw(self):
        for cell in self.cells:
            cell.draw()

    def recreate_cells(self):
        self.cells = []
        for i in range(ROWS):
            for j in range(COLUMNS):
                self.cells.append(Cell(
                    i, j,
                    i * WIDTH // ROWS,
                    j * HEIGHT // COLUMNS,
                    WIDTH // ROWS,
                    HEIGHT // COLUMNS,
                    self
                ))
        self.maze_generator = MazeGenerator(self.cells)


class Window(tk.Frame):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.canvas = Canvas(bg='#ffffff', width=WIDTH, height=HEIGHT,)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)


if __name__ == '__main__':
    root = tk.Tk()
    window = Window()
    root.mainloop()
