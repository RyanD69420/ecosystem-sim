"""
HUD — stylish stats overlay with colour-coded entity counts.
"""

import pygame
import math
import config


class HUD:
    def __init__(self, screen: pygame.Surface, simulation):
        self.screen     = screen
        self.simulation = simulation
        self._font      = pygame.font.SysFont("monospace", 13)
        self._font_bold = pygame.font.SysFont("monospace", 13, bold=True)
        self._font_lg   = pygame.font.SysFont("monospace", 20, bold=True)
        self._tick      = 0

    def draw(self, paused: bool):
        self._tick += 1
        stats = self.simulation.stats

        # ── Panel ────────────────────────────────────────────────────────────
        pad    = 10
        line_h = 20
        panel_w = 220

        entries = [
            ("ECOSYSTEM SIM",   None,            True),
            (None,              None,            False),   # divider
            (f"Tick   {stats['tick']:>6}", (200, 200, 200), False),
            (None,              None,            False),
            ("🌿 Plants",       (60, 210, 90),   False),
            (f"  {stats['plants']:>5}",  (60, 210, 90),   False),
            ("🟡 Herbivores",   (255, 210, 50),  False),
            (f"  {stats['herbivores']:>5}", (255, 210, 50), False),
            ("🔴 Predators",    (255, 80,  80),  False),
            (f"  {stats['predators']:>5}", (255, 80, 80),  False),
        ]

        if stats["colonized"]:
            entries += [
                ("🔵 Colonizers",  (80, 200, 255),  False),
                (f"  {stats['colonizers']:>5}", (80, 200, 255), False),
            ]
        else:
            entries += [
                (None,            None,            False),
                ("[C] Colonizers", (120, 120, 140), False),
                ("    arrive!",   (120, 120, 140), False),
            ]

        entries += [
            (None,             None,           False),
            ("[SPC] Pause" if not paused else "[SPC] Resume", (160, 160, 160), False),
            ("[R]   Restart",   (160, 160, 160), False),
            ("[Q]   Quit",     (160, 160, 160), False),
        ]

        panel_h = len(entries) * line_h + pad * 2

        # Translucent dark panel
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((8, 12, 20, 200))
        # Subtle border
        pygame.draw.rect(panel, (60, 80, 100, 180),
                         (0, 0, panel_w, panel_h), 1)
        self.screen.blit(panel, (8, 8))

        # Left accent bar
        accent = pygame.Surface((3, panel_h), pygame.SRCALPHA)
        accent.fill((80, 200, 255, 200))
        self.screen.blit(accent, (8, 8))

        # Draw text
        x = 18
        y = 8 + pad
        for text, colour, bold in entries:
            if text is None:
                # Divider line
                pygame.draw.line(self.screen, (40, 55, 70),
                                 (x, y + line_h // 2),
                                 (x + panel_w - 20, y + line_h // 2), 1)
            else:
                font = self._font_bold if bold else self._font
                col  = colour or (230, 230, 230)
                surf = font.render(text, True, col)
                self.screen.blit(surf, (x, y))
            y += line_h

        # ── Paused banner ────────────────────────────────────────────────────
        if paused:
            pulse = abs(math.sin(self._tick * 0.05))
            alpha = int(180 + 75 * pulse)
            banner = self._font_lg.render("⏸  PAUSED", True, (255, 220, 60))
            bx = config.SCREEN_WIDTH  // 2 - banner.get_width()  // 2
            by = config.SCREEN_HEIGHT // 2 - banner.get_height() // 2
            bg = pygame.Surface((banner.get_width() + 24, banner.get_height() + 12), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            self.screen.blit(bg, (bx - 12, by - 6))
            self.screen.blit(banner, (bx, by))

        # ── Colonizer arrival flash ──────────────────────────────────────────
        if stats["colonized"] and stats["tick"] < 60:
            flash_alpha = int(200 * (1 - stats["tick"] / 60))
            flash = pygame.Surface((config.SCREEN_WIDTH, 40), pygame.SRCALPHA)
            flash.fill((80, 200, 255, flash_alpha))
            msg = self._font_lg.render("⚠  COLONIZERS HAVE ARRIVED", True, (255, 255, 255))
            flash.blit(msg, (config.SCREEN_WIDTH // 2 - msg.get_width() // 2, 8))
            self.screen.blit(flash, (0, config.SCREEN_HEIGHT // 2 - 20))
