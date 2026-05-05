"""
Plant — grows in place, spreads slowly, can be eaten.
"""

import random
from src.entities.entity import Entity
import config


class Plant(Entity):
    def __init__(self, col: int, row: int):
        super().__init__(col, row, config.PLANT_ENERGY)
        self._spread_ready = False

    def tick(self, grid):
        self.age += 1
        self._spread_ready = random.random() < config.PLANT_SPREAD_CHANCE

    def wants_to_spread(self) -> bool:
        return self._spread_ready

    def spread_target(self, grid):
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        random.shuffle(options)
        for c, r in options:
            return c, r
        return None, None

    def be_eaten(self) -> int:
        """Called by herbivore. Returns energy gained."""
        self._die()
        return config.HERBIVORE_EAT_GAIN

    def be_harvested(self) -> int:
        """Called by colonizer."""
        self._die()
        return config.COLONIZER_HARVEST_GAIN
