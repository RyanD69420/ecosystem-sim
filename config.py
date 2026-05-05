# ─── Display ────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 768
FPS           = 30

# ─── Grid ───────────────────────────────────────────────────────────────────
GRID_COLS = 80
GRID_ROWS = 60
CELL_SIZE  = SCREEN_WIDTH // GRID_COLS   # ~12px per cell

# ─── World Generation ───────────────────────────────────────────────────────
WATER_RATIO      = 0.12   # fraction of tiles that start as water
ROCK_RATIO       = 0.08
INITIAL_PLANTS   = 400
INITIAL_HERBIVORES = 80
INITIAL_PREDATORS  = 6

# ─── Energy ─────────────────────────────────────────────────────────────────
PLANT_ENERGY          = 30
PLANT_SPREAD_CHANCE   = 0.04   # per tick, per plant
PLANT_REGROW_TICKS    = 15

HERBIVORE_START_ENERGY  = 60
HERBIVORE_MAX_ENERGY    = 100
HERBIVORE_MOVE_COST     = 1
HERBIVORE_EAT_GAIN      = 25
HERBIVORE_REPRODUCE_AT  = 65
HERBIVORE_STARVE_AT     = 0

PREDATOR_START_ENERGY   = 60
PREDATOR_MAX_ENERGY     = 120
PREDATOR_MOVE_COST      = 3
PREDATOR_EAT_GAIN       = 40
PREDATOR_REPRODUCE_AT   = 100
PREDATOR_STARVE_AT      = 0

# ─── Colonizers (Phase 2) ───────────────────────────────────────────────────
COLONIZER_START_COUNT   = 5
COLONIZER_START_ENERGY  = 200
COLONIZER_BUILD_COST    = 30
COLONIZER_HARVEST_GAIN  = 40
COLONIZER_VISION_RADIUS = 5

# ─── Colours ────────────────────────────────────────────────────────────────
COL_GRASS     = (106, 153,  85)
COL_DIRT      = (180, 140,  90)
COL_WATER     = ( 64, 120, 200)
COL_ROCK      = (120, 120, 120)
COL_PLANT     = ( 34, 200,  80)
COL_HERBIVORE = (240, 220,  60)
COL_PREDATOR  = (220,  60,  60)
COL_COLONIZER = ( 80, 180, 240)
COL_STRUCTURE = (160, 160, 180)
COL_HUD_BG    = (  0,   0,   0, 180)
COL_TEXT      = (230, 230, 230)
