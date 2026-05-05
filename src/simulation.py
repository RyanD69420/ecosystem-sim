"""
Simulation — owns the tick loop and entity lists.
"""

import random
from src.world.grid import Grid
from src.entities.plant import Plant
from src.entities.herbivore import Herbivore
from src.entities.predator import Predator
from src.entities.colonizer import Colonizer
import config


class Simulation:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.tick = 0
        self.plants:     list[Plant]     = []
        self.herbivores: list[Herbivore] = []
        self.predators:  list[Predator]  = []
        self.colonizers: list[Colonizer] = []
        self.colonizers_arrived = False

    # ── Setup ────────────────────────────────────────────────────────────────

    def seed_world(self):
        land_cells = [
            (c, r) for c in range(self.grid.cols)
                   for r in range(self.grid.rows)
                   if self.grid.is_land(c, r)
        ]
        random.shuffle(land_cells)

        for i in range(config.INITIAL_PLANTS):
            c, r = land_cells[i]
            self.plants.append(Plant(c, r))

        # Pre-warm plants — let them spread for 80 ticks before animals arrive
        # so there's a thick carpet of vegetation ready to sustain herbivores
        for _ in range(80):
            self._step_plants()

        for i in range(config.INITIAL_HERBIVORES):
            c, r = land_cells[config.INITIAL_PLANTS + i]
            self.herbivores.append(Herbivore(c, r))

        for i in range(config.INITIAL_PREDATORS):
            c, r = land_cells[config.INITIAL_PLANTS + config.INITIAL_HERBIVORES + i]
            self.predators.append(Predator(c, r))

    def spawn_colonizers(self):
        if self.colonizers_arrived:
            return
        self.colonizers_arrived = True
        edge_cells = self._edge_land_cells()
        for i in range(min(config.COLONIZER_START_COUNT, len(edge_cells))):
            c, r = edge_cells[i]
            self.colonizers.append(Colonizer(c, r))
        print(f"[tick {self.tick}] Colonizers have arrived!")

    # ── Main tick ────────────────────────────────────────────────────────────

    def step(self):
        self.tick += 1
        self._step_plants()
        self._step_herbivores()
        self._step_predators()
        self._step_colonizers()

    # ── Private step helpers ─────────────────────────────────────────────────

    def _step_plants(self):
        new_plants = []
        for p in self.plants:
            p.tick(self.grid)
            if p.wants_to_spread():
                nx, ny = p.spread_target(self.grid)
                if nx is not None and not self._plant_at(nx, ny):
                    new_plants.append(Plant(nx, ny))
        self.plants = [p for p in self.plants if p.alive]
        self.plants.extend(new_plants)

    def _step_herbivores(self):
        plant_map = {(p.col, p.row): p for p in self.plants if p.alive}
        new_herbs = []
        for h in self.herbivores:
            h.tick(self.grid, plant_map, self.predators, self.herbivores)
            if h.wants_to_reproduce():
                if len(self.herbivores) + len(new_herbs) < config.HERBIVORE_MAX_POP:
                    baby = h.reproduce()
                    if baby:
                        new_herbs.append(baby)
        self.herbivores = [h for h in self.herbivores if h.alive]
        self.herbivores.extend(new_herbs)

    def _step_predators(self):
        new_preds = []
        for p in self.predators:
            p.tick(self.grid, self.herbivores)
            if p.wants_to_reproduce():
                baby = p.reproduce()
                if baby:
                    new_preds.append(baby)
        self.predators = [p for p in self.predators if p.alive]
        self.predators.extend(new_preds)

    def _step_colonizers(self):
        plant_map = {(p.col, p.row): p for p in self.plants if p.alive}
        new_cols = []
        for c in self.colonizers:
            c.tick(self.grid, plant_map, self.herbivores, self.predators, self.colonizers)
            if c.wants_to_reproduce():
                baby = c.reproduce()
                if baby:
                    new_cols.append(baby)
        self.colonizers = [c for c in self.colonizers if c.alive]
        self.colonizers.extend(new_cols)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _plant_at(self, col, row):
        return any(p.col == col and p.row == row for p in self.plants if p.alive)

    def _edge_land_cells(self):
        cells = []
        for c in range(self.grid.cols):
            for r in [0, self.grid.rows - 1]:
                if self.grid.is_land(c, r):
                    cells.append((c, r))
        for r in range(self.grid.rows):
            for c in [0, self.grid.cols - 1]:
                if self.grid.is_land(c, r):
                    cells.append((c, r))
        random.shuffle(cells)
        return cells

    # ── Stats (for HUD) ──────────────────────────────────────────────────────

    @property
    def stats(self):
        return {
            "tick":        self.tick,
            "plants":      len(self.plants),
            "herbivores":  len(self.herbivores),
            "predators":   len(self.predators),
            "colonizers":  len(self.colonizers),
            "colonized":   self.colonizers_arrived,
        }
