# 🌿 Ecosystem Sim

A living, breathing ecosystem — until something smarter arrives.

## Concept

A grid-based world where plants grow, herbivores graze, and predators hunt.
Watch population cycles emerge naturally. Then press **C** to unleash the
Colonizers — an intelligent species that builds, harvests, and expands,
reshaping (or destroying) everything in their path.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key     | Action                        |
|---------|-------------------------------|
| `SPACE` | Pause / Resume                |
| `C`     | Spawn colonizer species       |
| `Q`     | Quit                          |

## Project Structure

```
ecosystem-sim/
├── main.py              # Entry point
├── config.py            # All tunable constants
├── src/
│   ├── simulation.py    # Tick loop & entity management
│   ├── entities/
│   │   ├── entity.py    # Base class
│   │   ├── plant.py
│   │   ├── herbivore.py
│   │   ├── predator.py
│   │   └── colonizer.py
│   ├── world/
│   │   └── grid.py      # Terrain & tile types
│   └── ui/
│       ├── renderer.py  # Pygame drawing
│       └── hud.py       # Stats overlay
└── tests/               # Unit tests (coming soon)
```

## Roadmap

- [ ] Phase 1 — Stable ecosystem (plants / herbivores / predators)
- [ ] Phase 2 — Colonizer AI (build, harvest, expand)
- [ ] Phase 3 — Population graphs over time
- [ ] Phase 4 — Player interventions (weather, plague, migration)
- [ ] Phase 5 — Colonizer collapse / equilibrium endings
