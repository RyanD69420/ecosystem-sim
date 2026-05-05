"""
Herbivore — wanders, eats plants, flees predators, reproduces.

Crowding mechanic: herbivores lose extra energy when too many others
are nearby, naturally self-regulating density without a hard cap.
"""

import random
from src.entities.entity import Entity
import config


class Herbivore(Entity):
    def __init__(self, col: int, row: int, energy: int = None):
        super().__init__(col, row, energy or config.HERBIVORE_START_ENERGY)
        self._reproduce_flag = False

    def tick(self, grid, plant_map: dict, predators: list, herbivores: list):
        self.age += 1
        self.energy -= config.HERBIVORE_MOVE_COST

        # Crowding stress — too many neighbours costs extra energy.
        # This naturally limits density without a hard cap.
        crowd = sum(
            1 for h in herbivores
            if h is not self and h.alive
            and abs(h.col - self.col) <= 2
            and abs(h.row - self.row) <= 2
        )
        if crowd > config.HERBIVORE_CROWD_THRESHOLD:
            self.energy -= (crowd - config.HERBIVORE_CROWD_THRESHOLD)

        if self.energy <= config.HERBIVORE_STARVE_AT:
            self._die()
            return

        # Try to eat at current position first
        if (self.col, self.row) in plant_map:
            plant = plant_map[(self.col, self.row)]
            if plant.alive:
                gained = plant.be_eaten()
                self.energy = min(self.energy + gained, config.HERBIVORE_MAX_ENERGY)
                del plant_map[(self.col, self.row)]
                self._reproduce_flag = (
                    self.energy >= config.HERBIVORE_REPRODUCE_AT and
                    random.random() < config.HERBIVORE_REPRODUCE_CHANCE
                )
                return

        # Flee if predator nearby
        threat = self._nearest(predators, radius=4)
        if threat:
            nc, nr = self._flee(grid, threat)
        else:
            # Only seek food when hungry — well-fed herbivores wander freely,
            # giving plant patches a chance to recover behind them.
            hungry = self.energy < config.HERBIVORE_MAX_ENERGY * 0.6
            if hungry:
                food = self._nearest_key(plant_map, radius=4)
                nc, nr = self._step_toward(grid, *food) if food else self._random_move(grid)
            else:
                # Crowded? Move away from the pack.
                if crowd > config.HERBIVORE_CROWD_THRESHOLD:
                    nc, nr = self._disperse(grid, herbivores)
                else:
                    nc, nr = self._random_move(grid)

        self._move_to(nc, nr, cost=config.HERBIVORE_MOVE_COST)
        self._reproduce_flag = (
            self.energy >= config.HERBIVORE_REPRODUCE_AT and
            random.random() < config.HERBIVORE_REPRODUCE_CHANCE
        )

    def wants_to_reproduce(self) -> bool:
        return self._reproduce_flag and self.alive

    def reproduce(self):
        self.energy //= 2
        self._reproduce_flag = False
        return Herbivore(self.col, self.row, self.energy)

    # ── Navigation helpers ───────────────────────────────────────────────────

    def _nearest(self, entities, radius: int):
        best, best_d = None, radius * radius
        for e in entities:
            if not e.alive:
                continue
            d = (e.col - self.col)**2 + (e.row - self.row)**2
            if d < best_d:
                best, best_d = e, d
        return best

    def _nearest_key(self, mapping: dict, radius: int):
        best, best_d = None, radius * radius
        for (c, r) in mapping:
            d = (c - self.col)**2 + (r - self.row)**2
            if d < best_d:
                best, best_d = (c, r), d
        return best

    def _step_toward(self, grid, tc: int, tr: int):
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        if not options:
            return self.col, self.row
        return min(options, key=lambda p: (p[0]-tc)**2 + (p[1]-tr)**2)

    def _flee(self, grid, threat):
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        if not options:
            return self.col, self.row
        return max(options, key=lambda p: (p[0]-threat.col)**2 + (p[1]-threat.row)**2)

    def _disperse(self, grid, herbivores):
        """Move toward least-crowded adjacent cell."""
        options = grid.land_neighbours(self.col, self.row, include_diag=True)
        if not options:
            return self.col, self.row
        def crowding_at(pos):
            return sum(
                1 for h in herbivores
                if h.alive and abs(h.col - pos[0]) <= 2 and abs(h.row - pos[1]) <= 2
            )
        return min(options, key=crowding_at)
