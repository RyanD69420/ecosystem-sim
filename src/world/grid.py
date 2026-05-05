"""
Grid — the terrain layer. Each cell has a TileType.
Uses simple noise-like generation for natural-looking terrain.
"""

import random
import math
from enum import IntEnum


class TileType(IntEnum):
    GRASS = 0
    DIRT  = 1
    WATER = 2
    ROCK  = 3
    STRUCTURE = 4   # built by colonizers


class Grid:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.tiles = [[TileType.GRASS] * rows for _ in range(cols)]
        self._generate()

    # ── Generation ───────────────────────────────────────────────────────────

    def _generate(self):
        import config
        # Simple blob generation using random walk seeds
        self._scatter_blobs(TileType.WATER, config.WATER_RATIO, radius=4)
        self._scatter_blobs(TileType.ROCK,  config.ROCK_RATIO,  radius=2)
        self._scatter_blobs(TileType.DIRT,  0.10, radius=3)

    def _scatter_blobs(self, tile: TileType, ratio: float, radius: int):
        total = self.cols * self.rows
        target = int(total * ratio)
        placed = 0
        attempts = 0
        while placed < target and attempts < target * 10:
            attempts += 1
            cx = random.randint(0, self.cols - 1)
            cy = random.randint(0, self.rows - 1)
            for dc in range(-radius, radius + 1):
                for dr in range(-radius, radius + 1):
                    if dc*dc + dr*dr <= radius*radius:
                        nc, nr = cx + dc, cy + dr
                        if self.in_bounds(nc, nr) and self.tiles[nc][nr] == TileType.GRASS:
                            if random.random() < 0.7:
                                self.tiles[nc][nr] = tile
                                placed += 1

    # ── Queries ──────────────────────────────────────────────────────────────

    def in_bounds(self, col: int, row: int) -> bool:
        return 0 <= col < self.cols and 0 <= row < self.rows

    def is_land(self, col: int, row: int) -> bool:
        return self.in_bounds(col, row) and self.tiles[col][row] not in (TileType.WATER, TileType.ROCK)

    def tile_at(self, col: int, row: int) -> TileType:
        if self.in_bounds(col, row):
            return self.tiles[col][row]
        return TileType.ROCK

    def set_tile(self, col: int, row: int, tile: TileType):
        if self.in_bounds(col, row):
            self.tiles[col][row] = tile

    def neighbours(self, col: int, row: int, include_diag=False):
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        if include_diag:
            dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
        return [(col+dc, row+dr) for dc,dr in dirs if self.in_bounds(col+dc, row+dr)]

    def land_neighbours(self, col: int, row: int, include_diag=False):
        return [(c, r) for c, r in self.neighbours(col, row, include_diag) if self.is_land(c, r)]
