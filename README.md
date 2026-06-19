*This project has been created as part of the 42 curriculum by \<iazzouzi>.*

# Fly-in 🚁

## Description

Fly-in is a drone fleet routing simulation written in **Python 3.10+**.
Given a map file describing a network of connected zones, the program
routes every drone from a single start hub to a single end hub in the
fewest possible simulation turns, then replays the result in an
interactive graphical window.

The simulation respects a strict set of rules: zones have capacity limits
and movement costs, connections have throughput limits, and blocked zones
are completely inaccessible. Restricted zones require two turns to enter.
All of this is enforced turn-by-turn while multiple drones fly in parallel.

---

## Instructions

### Requirements

- Python 3.10 or later
- Dependencies: `arcade==3.3.3`, `webcolors==25.10.0`

### Installation

```bash
make install
```

This runs `pip install -r requirements.txt` and installs all dependencies.

### Running the simulation

```bash
make run                   # prompts for a map file path if none given
python3 main.py map.txt    # or pass the path directly
```

### Other Makefile targets

| Target | Action |
|---|---|
| `make install` | Install Python dependencies |
| `make run` | Launch the simulation |
| `make debug` | Run under `pdb` |
| `make clean` | Remove `__pycache__`, `.mypy_cache`, `.pyc` files |
| `make lint` | Run `flake8` and `mypy` with standard flags |
| `make lint-strict` | Run `flake8` and `mypy --strict` |

### Map file format

Map files are plain `.txt` files. Example:

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: obstacleX 5 5 [zone=blocked color=gray]

connection: hub-roof1
connection: hub-corridorA
connection: corridorA-roof1 [max_link_capacity=2]
connection: roof1-goal
```

**Zone types:** `normal` (1 turn), `restricted` (2 turns), `priority`
(1 turn, preferred by pathfinder), `blocked` (impassable).

**Zone names** must not contain `-` or spaces.

**Comments** start with `#`.

---

## Algorithm

### Pathfinding — Dijkstra with cost weighting

`Engine.next()` runs Dijkstra's algorithm from the drone's current zone to
the end hub. Edge weights are the destination zone's `cost` attribute:

| Zone type | Cost |
|---|---|
| `normal` | 1.0 |
| `restricted` | 2.0 |
| `priority` | 0.2 |
| `blocked` | skipped |

Priority zones are given a very low cost (0.2) so Dijkstra naturally
explores them first and routes drones through them whenever a path exists,
matching the subject's "should be prioritised in pathfinding" requirement.

### Base-cost constraint

When the first drone reaches the end hub, its total cumulative path cost is
recorded as the **base cost**. All subsequent calls to `Engine.next()` that
would produce a total cost different from the base are rejected (`None` is
returned). This distributes drones across multiple equally weighted paths
instead of funnelling every drone down a single shortest route.

### Path caching

Once a `[current_zone, next_zone]` pair is resolved by Dijkstra, it is
stored in a shared cache list. Subsequent calls for the same current zone
return the cached next hop in O(cache_size) time, avoiding redundant heap
operations. Cache entries are skipped when the target zone is `reserved`.

### Turn-by-turn simulation — `Engine.simulator()`

The simulator loops until all drones are delivered:

1. **`stmp`** — a per-turn set prevents any drone from moving twice in the
   same turn.
2. **Restricted-zone transit** — when a drone moves toward a `restricted`
   zone, it is placed in the `tmp` set. On the next turn it is processed
   first and completes the journey. It cannot wait: once committed to the
   restricted entry it must arrive on turn 2.
3. **Zone capacity** — a zone's `reserved` flag is set to `1` when
   `len(occupancy) == max_drones`. Drones leaving on the current turn free
   capacity immediately (same-turn accounting).
4. **Connection capacity** — `get_conn_capacity()` looks up `max_link_capacity`
   and limits how many drones cross the same link in a single turn.
5. **Large-fleet shortcut** — when `nb_drones > 100`, any drone with no
   free adjacent zone is skipped instantly to avoid O(N²) stall scanning.

### Complexity

| Aspect | Complexity |
|---|---|
| Dijkstra per call | O((V + E) log V) |
| Cached lookup | O(cache_size) ≈ O(N) |
| Full simulation | O(T × N) turns × drones |
| Memory | O(V + E + N × path_length) |

where V = zones, E = connections, N = drones, T = total turns.

---

## Visual Representation

The arcade window renders the simulation network and animates drone flight.

### Graph display

- **Zones** are drawn as coloured circles. The colour comes from the `color`
  metadata in the map file; zones with no colour default to white.
- **Connections** are drawn as black lines between zone centres.
- **Zone names** appear as bold labels above each circle, slightly rotated
  for intermediate hubs to reduce overlap.

### Drone animation

- A drone sprite moves **smoothly** between zone centres using linear
  interpolation scaled by `delta_time`, giving frame-rate-independent
  animation.
- For restricted zones the sprite animates to the **midpoint** of the edge
  on turn 1, then continues to the destination on turn 2, visually conveying
  the two-turn cost.
- Each drone is labelled with its numeric ID, rendered with a drop-shadow
  using five stacked text objects.
- At the start hub, only the last drone is drawn to avoid total occlusion.
- At the end hub, each arriving drone is shown once then hidden. The
  delivered-drone tracker (`TMP`) is cleared on both manual restart (R) and
  auto-reset, so drones render correctly on every replay.

### Interactive controls

| Input | Action |
|---|---|
| **SPACE** | Play / Pause |
| **RIGHT arrow** | Advance one turn (while paused) |
| **R** | Restart from turn 0 |
| **TAB** | Toggle background music |
| **Mouse drag** (left button) | Pan the camera |
| **Mouse scroll** | Zoom in / out |

### HUD overlay

A fixed GUI camera renders the following information permanently:

- **Turn counter** — `Turns: X/Total`
- **Drone count** — `Drones: N`
- **Zoom level** — `Zoom: xN.NN`
- Button labels for each keyboard shortcut

---

## Resources

### Graph theory and pathfinding

- Dijkstra's algorithm — E. W. Dijkstra, *A note on two problems in
  connexion with graphs* (1959)
- Python `heapq` documentation: <https://docs.python.org/3/library/heapq.html>

### Python tooling

- flake8: <https://flake8.pycqa.org/>
- mypy: <https://mypy.readthedocs.io/>
- arcade library: <https://api.arcade.academy/>
- webcolors: <https://webcolors.readthedocs.io/>

### Project files

A `.gitignore` is included at the repository root to exclude Python
bytecode (`__pycache__`, `*.pyc`), type-checker caches (`.mypy_cache`),
test caches (`.pytest_cache`), virtual environments, build artefacts, and
common editor/OS metadata files.