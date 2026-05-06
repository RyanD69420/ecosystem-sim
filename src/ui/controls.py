"""
Controls — bottom bar with draggable sliders for live ecosystem tuning.

Each slider writes directly into the config module so every entity
picks up the new value on its very next tick — no restart needed.
"""

import pygame
import config


# ── Slider definition ────────────────────────────────────────────────────────

class Slider:
    """A single horizontal drag slider bound to a config attribute."""

    def __init__(self, label: str, attr: str, min_val: float, max_val: float,
                 fmt: str = ".2f", step: float = None):
        self.label   = label
        self.attr    = attr          # name of the attribute in the config module
        self.min_val = min_val
        self.max_val = max_val
        self.fmt     = fmt           # format string for display value
        self.step    = step          # snap to step if provided (e.g. 1 for ints)

        # Layout — filled in by ControlBar.layout()
        self.x = self.y = self.w = self.h = 0
        self.track_x = self.track_w = 0
        self.dragging = False

    # ── Value helpers ────────────────────────────────────────────────────────

    @property
    def value(self):
        return getattr(config, self.attr)

    @value.setter
    def value(self, v):
        if self.step:
            v = round(v / self.step) * self.step
        v = max(self.min_val, min(self.max_val, v))
        if self.fmt.endswith('f'):
            v = float(v)
        else:
            v = int(round(v))
        setattr(config, self.attr, v)

    @property
    def _ratio(self):
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    @property
    def _handle_x(self):
        return int(self.track_x + self._ratio * self.track_w)

    # ── Input ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hx = self._handle_x
            hy = self.y + self.h // 2
            if abs(event.pos[0] - hx) <= 10 and abs(event.pos[1] - hy) <= 10:
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            ratio = (event.pos[0] - self.track_x) / self.track_w
            self.value = self.min_val + ratio * (self.max_val - self.min_val)

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface, font, font_bold):
        cx = self.x + self.w // 2

        # Label
        lbl = font.render(self.label, True, (180, 180, 190))
        screen.blit(lbl, (cx - lbl.get_width() // 2, self.y + 4))

        # Value
        val_str = format(self.value, self.fmt)
        val_surf = font_bold.render(val_str, True, (230, 230, 255))
        screen.blit(val_surf, (cx - val_surf.get_width() // 2, self.y + 18))

        # Track
        track_y = self.y + 52
        pygame.draw.rect(screen, (50, 55, 70),
                         (self.track_x, track_y - 2, self.track_w, 4), border_radius=2)
        # Filled portion
        filled_w = int(self._ratio * self.track_w)
        if filled_w > 0:
            pygame.draw.rect(screen, (80, 160, 220),
                             (self.track_x, track_y - 2, filled_w, 4), border_radius=2)

        # Handle
        hx = self._handle_x
        pygame.draw.circle(screen, (200, 220, 255), (hx, track_y), 7)
        pygame.draw.circle(screen, (80, 160, 220),  (hx, track_y), 7, 2)


# ── Control bar ─────────────────────────────────────────────────────────────

class ControlBar:
    """Renders the full bottom panel with grouped sliders."""

    # Define all sliders: (label, config_attr, min, max, fmt, step)
    SLIDERS = [
        # Herbivore group
        Slider("🟡 Repro chance",  "HERBIVORE_REPRODUCE_CHANCE", 0.05, 1.0,  ".2f"),
        Slider("🟡 Eat gain",      "HERBIVORE_EAT_GAIN",         5,    50,   ".0f", 1),
        Slider("🟡 Crowd limit",   "HERBIVORE_CROWD_THRESHOLD",  1,    12,   ".0f", 1),
        Slider("🟡 Food radius",   "HERBIVORE_MAX_POP",          50,   500,  ".0f", 10),
        # Predator group
        Slider("🔴 Repro chance",  "PREDATOR_REPRODUCE_CHANCE",  0.05, 1.0,  ".2f"),
        Slider("🔴 Eat gain",      "PREDATOR_EAT_GAIN",          20,   120,  ".0f", 1),
        Slider("🔴 Vision",        "PREDATOR_MIN_HUNT_POP",      0,    20,   ".0f", 1),
        Slider("🔴 Move cost",     "PREDATOR_MOVE_COST",         1,    5,    ".0f", 1),
        # Plants
        Slider("🌿 Spread",        "PLANT_SPREAD_CHANCE",        0.01, 0.15, ".2f"),
    ]

    def __init__(self, screen: pygame.Surface):
        self.screen  = screen
        self.font    = pygame.font.SysFont("monospace", 11)
        self.font_b  = pygame.font.SysFont("monospace", 11, bold=True)
        self.font_hd = pygame.font.SysFont("monospace", 12, bold=True)
        self._layout()

    def _layout(self):
        """Distribute sliders evenly across the bottom bar."""
        bar_y  = config.SIM_HEIGHT
        bar_h  = config.CONTROL_BAR_H
        pad    = 8
        n      = len(self.SLIDERS)
        sw     = (config.SCREEN_WIDTH - pad * 2) // n
        track_pad = 10

        for i, sl in enumerate(self.SLIDERS):
            sl.x       = pad + i * sw
            sl.y       = bar_y + 4
            sl.w       = sw
            sl.h       = bar_h - 8
            sl.track_x = sl.x + track_pad
            sl.track_w = sw - track_pad * 2

    def handle_event(self, event):
        for sl in self.SLIDERS:
            sl.handle_event(event)

    def draw(self):
        bar_rect = pygame.Rect(0, config.SIM_HEIGHT, config.SCREEN_WIDTH, config.CONTROL_BAR_H)

        # Background
        pygame.draw.rect(self.screen, (12, 16, 26), bar_rect)
        # Top border
        pygame.draw.line(self.screen, (60, 80, 110),
                         (0, config.SIM_HEIGHT), (config.SCREEN_WIDTH, config.SIM_HEIGHT), 2)

        # Section labels
        herb_x = self.SLIDERS[0].x
        pred_x = self.SLIDERS[4].x
        plant_x = self.SLIDERS[8].x
        label_y = config.SIM_HEIGHT + 72

        for text, x, col in [
            ("── HERBIVORES ──", herb_x,  (200, 180,  60)),
            ("── PREDATORS ──",  pred_x,  (220,  80,  80)),
            ("── PLANTS ──",     plant_x, ( 80, 200, 100)),
        ]:
            surf = self.font_hd.render(text, True, col)
            self.screen.blit(surf, (x, label_y))

        # Dividers between groups
        for div_x in [self.SLIDERS[4].x - 4, self.SLIDERS[8].x - 4]:
            pygame.draw.line(self.screen, (40, 50, 70),
                             (div_x, config.SIM_HEIGHT + 6),
                             (div_x, config.SIM_HEIGHT + config.CONTROL_BAR_H - 6), 1)

        # Draw each slider
        for sl in self.SLIDERS:
            sl.draw(self.screen, self.font, self.font_b)
