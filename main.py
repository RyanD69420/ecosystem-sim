"""
Ecosystem Simulation
====================
A living world of plants, herbivores, and predators —
until something smarter arrives.

Run: python main.py
"""

import pygame
from src.world.grid import Grid
from src.ui.renderer import Renderer
from src.ui.hud import HUD
from src.simulation import Simulation
import config

def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    pygame.display.set_caption("Ecosystem Sim")
    clock = pygame.time.Clock()

    grid = Grid(config.GRID_COLS, config.GRID_ROWS)
    simulation = Simulation(grid)
    renderer = Renderer(screen, grid)
    hud = HUD(screen, simulation)

    simulation.seed_world()

    running = True
    paused = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r:
                    grid = Grid(config.GRID_COLS, config.GRID_ROWS)
                    simulation = Simulation(grid)
                    renderer = Renderer(screen, grid)
                    hud = HUD(screen, simulation)
                    simulation.seed_world()
                    paused = False
                # Phase 2: spawn colonizers with 'C'
                if event.key == pygame.K_c:
                    simulation.spawn_colonizers()

        if not paused:
            simulation.step()

        renderer.draw()
        renderer.draw_entities(simulation)
        hud.draw(paused)
        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
