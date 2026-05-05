"""
Entity — base class for everything alive.
"""

import random


class Entity:
    def __init__(self, col: int, row: int, energy: int):
        self.col    = col
        self.row    = row
        self.energy = energy
        self.alive  = True
        self.age    = 0

    def _move_to(self, col: int, row: int, cost: int = 1):
        self.col = col
        self.row = row
        self.energy -= cost

    def _random_move(self, grid):
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        if options:
            nc, nr = random.choice(options)
            return nc, nr
        return self.col, self.row

    def _die(self):
        self.alive = False
