"""
Renderer — visually rich drawing of the grid and all entities.

Design direction: organic/natural with a painterly feel.
- Terrain has texture variation and subtle shading
- Entities glow, pulse, and have distinct silhouettes
- Water shimmers, grass has depth, structures feel imposing
"""

import pygame
import math
import random
from src.world.grid import TileType
import config

# ── Terrain base colours ────────────────────────────────────────────────────
TILE_BASE = {
    TileType.GRASS:     (72,  120,  56),
    TileType.DIRT:      (160, 118,  72),
    TileType.WATER:     (38,   90, 180),
    TileType.ROCK:      (100, 100, 108),
    TileType.STRUCTURE: (140, 130, 160),
}

TILE_HIGHLIGHT = {
    TileType.GRASS:     (95,  155,  72),
    TileType.DIRT:      (190, 148,  95),
    TileType.WATER:     (55,  120, 210),
    TileType.ROCK:      (130, 130, 138),
    TileType.STRUCTURE: (180, 170, 200),
}


class Renderer:
    def __init__(self, screen: pygame.Surface, grid):
        self.screen = screen
        self.grid   = grid
        self.cs     = config.CELL_SIZE
        self._tick  = 0

        # Per-cell random seed for texture variation
        self._cell_noise = [
            [random.random() for _ in range(grid.rows)]
            for _ in range(grid.cols)
        ]

        self._terrain_surf = pygame.Surface(
            (grid.cols * self.cs, grid.rows * self.cs)
        )
        self._build_terrain()

    # ── Terrain ─────────────────────────────────────────────────────────────

    def _build_terrain(self):
        cs = self.cs
        surf = self._terrain_surf
        for c in range(self.grid.cols):
            for r in range(self.grid.rows):
                tile  = self.grid.tiles[c][r]
                noise = self._cell_noise[c][r]
                base  = TILE_BASE[tile]
                hi    = TILE_HIGHLIGHT[tile]

                # Blend base + highlight by noise
                t = noise * 0.45
                col = tuple(int(base[i] + (hi[i] - base[i]) * t) for i in range(3))

                rect = pygame.Rect(c * cs, r * cs, cs, cs)
                pygame.draw.rect(surf, col, rect)

                # Edge darkening for depth
                if noise < 0.15:
                    dark = pygame.Surface((cs, cs), pygame.SRCALPHA)
                    dark.fill((0, 0, 0, 40))
                    surf.blit(dark, rect.topleft)

                # Grass detail — tiny darker flecks
                if tile == TileType.GRASS and cs >= 8 and noise > 0.7:
                    for _ in range(2):
                        fx = c * cs + random.randint(1, cs - 2)
                        fy = r * cs + random.randint(1, cs - 2)
                        pygame.draw.circle(surf, (45, 90, 35), (fx, fy), 1)

                # Rock cracks
                if tile == TileType.ROCK and cs >= 8 and noise > 0.6:
                    x1 = c * cs + int(noise * cs * 0.3)
                    y1 = r * cs + int(noise * cs * 0.4)
                    x2 = x1 + int(noise * 4)
                    y2 = y1 + int(noise * 3)
                    pygame.draw.line(surf, (70, 70, 76), (x1, y1), (x2, y2), 1)

    def _draw_water_shimmer(self, c: int, r: int):
        """Animated shimmer on water tiles."""
        cs   = self.cs
        t    = self._tick * 0.05
        n    = self._cell_noise[c][r]
        wave = math.sin(t + n * 6.28) * 0.5 + 0.5
        alpha = int(wave * 35 + 10)
        shimmer = pygame.Surface((cs, cs), pygame.SRCALPHA)
        shimmer.fill((180, 220, 255, alpha))
        self.screen.blit(shimmer, (c * cs, r * cs))

    def _draw_structure_glow(self, c: int, r: int):
        cs = self.cs
        glow = pygame.Surface((cs, cs), pygame.SRCALPHA)
        glow.fill((200, 190, 255, 30))
        self.screen.blit(glow, (c * cs, r * cs))
        x, y = c * cs, r * cs
        pygame.draw.line(self.screen, (100, 90, 130), (x, y), (x + cs, y), 1)
        pygame.draw.line(self.screen, (100, 90, 130), (x, y), (x, y + cs), 1)

    # ── Entity drawing ───────────────────────────────────────────────────────

    def _draw_plant(self, p):
        cs  = self.cs
        cx  = p.col * cs + cs // 2
        cy  = p.row * cs + cs // 2
        r   = max(2, cs // 3)
        age_scale = min(1.0, p.age / 20.0)
        green = (
            int(30  + 40  * age_scale),
            int(160 + 50  * age_scale),
            int(40  + 20  * age_scale),
        )
        # Soft glow
        glow = pygame.Surface((cs * 2, cs * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*green, 40), (cs, cs), r + 3)
        self.screen.blit(glow, (cx - cs, cy - cs))
        # Stem
        pygame.draw.line(self.screen, (30, 100, 30),
                         (cx, cy + r), (cx, cy), max(1, cs // 8))
        # Leaf body
        pygame.draw.circle(self.screen, green, (cx, cy), r)
        # Highlight
        pygame.draw.circle(self.screen, (
            min(255, green[0] + 60),
            min(255, green[1] + 60),
            min(255, green[2] + 40),
        ), (cx - r // 3, cy - r // 3), max(1, r // 3))

    def _draw_herbivore(self, h):
        cs   = self.cs
        cx   = h.col * cs + cs // 2
        cy   = h.row * cs + cs // 2
        r    = max(3, cs // 2 - 1)
        pulse = math.sin(self._tick * 0.1 + h.col * 0.3) * 0.15 + 0.85
        body_r = int(r * pulse)

        energy_ratio = h.energy / config.HERBIVORE_MAX_ENERGY
        col = (
            255,
            int(180 + 60 * energy_ratio),
            int(20  + 40 * energy_ratio),
        )

        # Shadow
        shadow = pygame.Surface((cs * 2, cs * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50),
                            (cs - body_r, cs + body_r - 2, body_r * 2, body_r))
        self.screen.blit(shadow, (cx - cs, cy - cs))

        # Glow
        glow = pygame.Surface((cs * 3, cs * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*col, 35), (cs + cs // 2, cs + cs // 2), body_r + 4)
        self.screen.blit(glow, (cx - cs - cs // 2, cy - cs - cs // 2))

        # Body
        body_rect = pygame.Rect(cx - body_r, cy - body_r, body_r * 2, body_r * 2)
        pygame.draw.rect(self.screen, col, body_rect, border_radius=max(2, body_r // 2))

        # Eyes
        eye_r = max(1, body_r // 4)
        pygame.draw.circle(self.screen, (20, 20, 20),
                           (cx - body_r // 3, cy - body_r // 4), eye_r)
        pygame.draw.circle(self.screen, (20, 20, 20),
                           (cx + body_r // 3, cy - body_r // 4), eye_r)
        pygame.draw.circle(self.screen, (255, 255, 255),
                           (cx - body_r // 3 + 1, cy - body_r // 4 - 1), max(1, eye_r // 2))

    def _draw_predator(self, p):
        cs  = self.cs
        cx  = p.col * cs + cs // 2
        cy  = p.row * cs + cs // 2
        r   = max(3, cs // 2)

        energy_ratio = p.energy / config.PREDATOR_MAX_ENERGY
        col = (
            int(200 + 55 * energy_ratio),
            int(30  * energy_ratio),
            int(30  * energy_ratio),
        )

        # Menacing glow
        glow = pygame.Surface((cs * 4, cs * 4), pygame.SRCALPHA)
        glow_alpha = int(30 + 25 * math.sin(self._tick * 0.08))
        pygame.draw.circle(glow, (*col, glow_alpha), (cs * 2, cs * 2), r + 5)
        self.screen.blit(glow, (cx - cs * 2, cy - cs * 2))

        # Shadow
        shadow = pygame.Surface((cs * 2, cs * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60),
                            (cs - r, cs + r - 2, r * 2, r))
        self.screen.blit(shadow, (cx - cs, cy - cs))

        # Diamond body
        points = [
            (cx,     cy - r),
            (cx + r, cy),
            (cx,     cy + r),
            (cx - r, cy),
        ]
        pygame.draw.polygon(self.screen, col, points)
        inner = [
            (cx,          cy - r // 2),
            (cx + r // 2, cy),
            (cx,          cy + r // 2),
            (cx - r // 2, cy),
        ]
        lighter = tuple(min(255, c + 60) for c in col)
        pygame.draw.polygon(self.screen, lighter, inner)
        pygame.draw.polygon(self.screen, (255, 80, 80), points, 1)

        # Slit eyes
        eye_col = (255, 220, 0)
        pygame.draw.circle(self.screen, eye_col,
                           (cx - r // 3, cy - r // 5), max(1, r // 4))
        pygame.draw.circle(self.screen, eye_col,
                           (cx + r // 3, cy - r // 5), max(1, r // 4))
        pygame.draw.line(self.screen, (0, 0, 0),
                         (cx - r // 3, cy - r // 5 - 1),
                         (cx - r // 3, cy - r // 5 + 1), 1)
        pygame.draw.line(self.screen, (0, 0, 0),
                         (cx + r // 3, cy - r // 5 - 1),
                         (cx + r // 3, cy - r // 5 + 1), 1)

    def _draw_colonizer(self, c):
        cs  = self.cs
        cx  = c.col * cs + cs // 2
        cy  = c.row * cs + cs // 2
        r   = max(3, cs // 2)
        t   = self._tick * 0.07

        # Rotating tech ring
        ring_col = (80, 200, 255)
        for i in range(6):
            angle = t + i * math.pi / 3
            rx = cx + int(r * math.cos(angle))
            ry = cy + int(r * math.sin(angle))
            pygame.draw.circle(self.screen, ring_col, (rx, ry), max(1, r // 5))

        # Pulsing core glow
        glow = pygame.Surface((cs * 4, cs * 4), pygame.SRCALPHA)
        glow_r = int(r + 3 + 2 * math.sin(t * 2))
        pygame.draw.circle(glow, (80, 200, 255, 45), (cs * 2, cs * 2), glow_r)
        self.screen.blit(glow, (cx - cs * 2, cy - cs * 2))

        # Core body
        pygame.draw.circle(self.screen, (20, 40, 80), (cx, cy), r - 1)
        pygame.draw.circle(self.screen, (80, 200, 255), (cx, cy), r - 1, 2)

        # Tech crosshair
        pygame.draw.line(self.screen, (80, 200, 255),
                         (cx - r // 2, cy), (cx + r // 2, cy), 1)
        pygame.draw.line(self.screen, (80, 200, 255),
                         (cx, cy - r // 2), (cx, cy + r // 2), 1)

        # Bright centre
        pygame.draw.circle(self.screen, (200, 240, 255), (cx, cy), max(1, r // 4))

    # ── Main draw ────────────────────────────────────────────────────────────

    def draw(self):
        self._tick += 1
        self.screen.blit(self._terrain_surf, (0, 0))

        for c in range(self.grid.cols):
            for r in range(self.grid.rows):
                tile = self.grid.tiles[c][r]
                if tile == TileType.WATER:
                    self._draw_water_shimmer(c, r)
                elif tile == TileType.STRUCTURE:
                    self._draw_structure_glow(c, r)

        # Rebuild terrain every 30 ticks to catch new structures
        if self._tick % 30 == 0:
            self._build_terrain()

    def draw_entities(self, simulation):
        for p in simulation.plants:
            if p.alive:
                self._draw_plant(p)

        for h in simulation.herbivores:
            if h.alive:
                self._draw_herbivore(h)

        for p in simulation.predators:
            if p.alive:
                self._draw_predator(p)

        for c in simulation.colonizers:
            if c.alive:
                self._draw_colonizer(c)
