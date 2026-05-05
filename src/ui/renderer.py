"""
Renderer — draws the grid and all entities each frame.
"""

import pygame
from src.world.grid import TileType
import config


TILE_COLOURS = {
    TileType.GRASS:     config.COL_GRASS,
    TileType.DIRT:      config.COL_DIRT,
    TileType.WATER:     config.COL_WATER,
    TileType.ROCK:      config.COL_ROCK,
    TileType.STRUCTURE: config.COL_STRUCTURE,
}


class Renderer:
    def __init__(self, screen: pygame.Surface, grid):
        self.screen = screen
        self.grid   = grid
        self.cs     = config.CELL_SIZE
        self._build_terrain_surface()

    def _build_terrain_surface(self):
        """Pre-render the static terrain into a surface for speed."""
        self._terrain = pygame.Surface(
            (self.grid.cols * self.cs, self.grid.rows * self.cs)
        )
        self._redraw_terrain()

    def _redraw_terrain(self):
        for c in range(self.grid.cols):
            for r in range(self.grid.rows):
                tile = self.grid.tiles[c][r]
                col  = TILE_COLOURS.get(tile, config.COL_GRASS)
                rect = pygame.Rect(c * self.cs, r * self.cs, self.cs, self.cs)
                pygame.draw.rect(self._terrain, col, rect)

    def draw(self):
        # Terrain changes (structures) require a redraw — cheap enough at 80×60
        self._redraw_terrain()
        self.screen.blit(self._terrain, (0, 0))

    def draw_entities(self, simulation):
        cs = self.cs
        # Plants — small green dot
        for p in simulation.plants:
            if p.alive:
                cx = p.col * cs + cs // 2
                cy = p.row * cs + cs // 2
                pygame.draw.circle(self.screen, config.COL_PLANT, (cx, cy), max(2, cs // 4))

        # Herbivores — yellow square
        for h in simulation.herbivores:
            if h.alive:
                r = pygame.Rect(h.col * cs + 1, h.row * cs + 1, cs - 2, cs - 2)
                pygame.draw.rect(self.screen, config.COL_HERBIVORE, r)

        # Predators — red diamond
        for p in simulation.predators:
            if p.alive:
                cx = p.col * cs + cs // 2
                cy = p.row * cs + cs // 2
                half = max(3, cs // 2)
                points = [(cx, cy-half), (cx+half, cy), (cx, cy+half), (cx-half, cy)]
                pygame.draw.polygon(self.screen, config.COL_PREDATOR, points)

        # Colonizers — cyan circle with outline
        for c in simulation.colonizers:
            if c.alive:
                cx = c.col * cs + cs // 2
                cy = c.row * cs + cs // 2
                pygame.draw.circle(self.screen, config.COL_COLONIZER, (cx, cy), max(3, cs // 2))
                pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), max(3, cs // 2), 1)
