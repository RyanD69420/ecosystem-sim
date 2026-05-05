"""
Colonizer — the intelligent invader.

Behaviour priorities (in order):
  1. Build a structure on current cell if energy allows and cell is bare
  2. Harvest nearest plant
  3. Hunt herbivores for food if starving
  4. Expand toward unexplored territory
  5. Reproduce when very well-fed
"""

import random
from src.entities.entity import Entity
from src.world.grid import TileType
import config


class Colonizer(Entity):
    def __init__(self, col: int, row: int, energy: int = None):
        super().__init__(col, row, energy or config.COLONIZER_START_ENERGY)
        self._reproduce_flag = False
        self.structures_built = 0

    def tick(self, grid, plant_map: dict, herbivores: list, predators: list, colonizers: list):
        self.age += 1
        self.energy -= config.HERBIVORE_MOVE_COST  # base upkeep

        if self.energy <= 0:
            self._die()
            return

        # 1. Build structure
        if (self.energy > config.COLONIZER_BUILD_COST * 2 and
                grid.tile_at(self.col, self.row) == TileType.GRASS):
            grid.set_tile(self.col, self.row, TileType.STRUCTURE)
            self.energy -= config.COLONIZER_BUILD_COST
            self.structures_built += 1
            return

        # 2. Harvest adjacent / current plant
        for key in list(plant_map.keys()):
            c, r = key
            if abs(c - self.col) <= 1 and abs(r - self.row) <= 1:
                plant = plant_map[key]
                if plant.alive:
                    gained = plant.be_harvested()
                    self.energy = min(self.energy + gained, config.COLONIZER_START_ENERGY * 2)
                    del plant_map[key]
                    self._reproduce_flag = self.energy > config.COLONIZER_START_ENERGY * 1.5
                    return

        # 3. Hunt herbivore if hungry
        if self.energy < config.COLONIZER_START_ENERGY // 2:
            target = self._nearest(herbivores, radius=config.COLONIZER_VISION_RADIUS)
            if target:
                if target.col == self.col and target.row == self.row:
                    target._die()
                    self.energy += config.PREDATOR_EAT_GAIN
                    return
                nc, nr = self._step_toward(grid, target.col, target.row)
                self._move_to(nc, nr)
                return

        # 4. Expand — move away from other colonizers
        nc, nr = self._expand(grid, colonizers)
        self._move_to(nc, nr)
        self._reproduce_flag = self.energy > config.COLONIZER_START_ENERGY * 1.5

    def wants_to_reproduce(self) -> bool:
        return self._reproduce_flag and self.alive

    def reproduce(self):
        self.energy = int(self.energy * 0.6)
        self._reproduce_flag = False
        return Colonizer(self.col, self.row, self.energy // 2)

    # ── Navigation ───────────────────────────────────────────────────────────

    def _expand(self, grid, colonizers):
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        if not options:
            return self.col, self.row
        # Prefer cells far from other colonizers
        def score(p):
            min_d = min(
                ((c2.col - p[0])**2 + (c2.row - p[1])**2 for c2 in colonizers),
                default=9999
            )
            return min_d
        return max(options, key=score)

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
