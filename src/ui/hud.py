"""
HUD — draws stats overlay and key hints.
"""

import pygame
import config


class HUD:
    def __init__(self, screen: pygame.Surface, simulation):
        self.screen     = screen
        self.simulation = simulation
        self._font      = pygame.font.SysFont("monospace", 14)
        self._font_lg   = pygame.font.SysFont("monospace", 18, bold=True)

    def draw(self, paused: bool):
        stats = self.simulation.stats
        lines = [
            f"Tick:        {stats['tick']:>6}",
            f"Plants:      {stats['plants']:>6}",
            f"Herbivores:  {stats['herbivores']:>6}",
            f"Predators:   {stats['predators']:>6}",
        ]
        if stats["colonized"]:
            lines.append(f"Colonizers:  {stats['colonizers']:>6}")
        else:
            lines.append("  [C] Unleash colonizers")

        lines += ["", "[SPACE] Pause" if not paused else "[SPACE] Resume", "[Q] Quit"]

        if paused:
            pause_surf = self._font_lg.render("— PAUSED —", True, (255, 220, 80))
            self.screen.blit(pause_surf, (config.SCREEN_WIDTH // 2 - 50, 10))

        x, y = 10, 10
        pad = 6
        line_h = self._font.get_linesize()
        panel_h = len(lines) * line_h + pad * 2
        panel_w = 200

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        self.screen.blit(panel, (x - pad, y - pad))

        for line in lines:
            surf = self._font.render(line, True, config.COL_TEXT)
            self.screen.blit(surf, (x, y))
            y += line_h
