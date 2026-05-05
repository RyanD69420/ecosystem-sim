"""
Predator — hunts herbivores, reproduces when well-fed.
"""

import random
from src.entities.entity import Entity
import config


class Predator(Entity):
    def __init__(self, col: int, row: int, energy: int = None):
        super().__init__(col, row, energy or config.PREDATOR_START_ENERGY)
        self._reproduce_flag = False

    def tick(self, grid, herbivores: list):
        self.age += 1
        self.energy -= config.PREDATOR_MOVE_COST

        if self.energy <= config.PREDATOR_STARVE_AT:
            self._die()
            return

        # Try to eat adjacent herbivore
        for h in herbivores:
            if h.alive and h.col == self.col and h.row == self.row:
                h._die()
                self.energy = min(self.energy + config.PREDATOR_EAT_GAIN, config.PREDATOR_MAX_ENERGY)
                self._reproduce_flag = self.energy >= config.PREDATOR_REPRODUCE_AT
                return

        # Hunt nearest herbivore
        target = self._nearest(herbivores, radius=8)
        if target:
            nc, nr = self._step_toward(grid, target.col, target.row)
        else:
            nc, nr = self._random_move(grid)

        self._move_to(nc, nr, cost=config.PREDATOR_MOVE_COST)
        self._reproduce_flag = self.energy >= config.PREDATOR_REPRODUCE_AT

    def wants_to_reproduce(self) -> bool:
        return self._reproduce_flag and self.alive

    def reproduce(self):
        self.energy //= 2
        self._reproduce_flag = False
        return Predator(self.col, self.row, self.energy)

    def _nearest(self, entities, radius: int):
        best, best_d = None, radius * radius
        for e in entities:
            if not e.alive:
                continue
            d = (e.col - self.col)**2 + (e.row - self.row)**2
            if d < best_d:
                best, best_d = e, d
        return best

    def _step_toward(self, grid, tc: int, tr: int):
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        if not options:
            return self.col, self.row
        return min(options, key=lambda p: (p[0]-tc)**2 + (p[1]-tr)**2)
