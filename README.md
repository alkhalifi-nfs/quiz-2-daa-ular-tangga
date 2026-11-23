# Snakes and Ladders BFS

A two-player Snakes and Ladders game built with Python and Pygame. The game uses
**Breadth-First Search (BFS)** to find the **minimum number of dice throws** needed
to reach square 100, and can show that fastest route on the board at any time.

> Quiz 2: EF234405 Design & Analysis of Algorithms (M)

## Features

- 10×10 board with 8 ladders and 8 snakes, for 2 players.
- Animated dice roll and token movement.
- **Fastest route (BFS):** press **B** to show the shortest path from the current
  player's square to square 100, with the dice value needed for each step.
- **End screen:** compares the winner's number of throws with the BFS minimum.

## Rules

1. Both players start on square 1 and take turns rolling a die (1–6).
2. Landing on the **foot of a ladder** moves the token up to its top.
   Landing on the **head of a snake** moves the token down to its tail.
3. A player must land **exactly** on square 100. If the roll would go past 100,
   the token does not move.
4. The first player to reach square 100 wins.

## Getting started

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `Space` | Roll the die |
| `B` | Show or hide the BFS fastest route |
| `R` | Restart the game |
| `Esc` | Quit |

The buttons in the side panel can also be clicked with the mouse.

### Running the tests

```bash
python -m unittest discover tests -v
```

## How BFS is used

The board is modeled as a directed graph:

| Element | Meaning |
|---------|---------|
| Node | A square from 1 to 100 |
| Edge | One die throw: from square `p` to `move(p, d)` for `d` = 1…6. If `p + d` is a ladder foot or snake head, the edge goes straight to its other end. |
| Weight | Every edge costs 1 throw |

Since every edge has the same weight, the minimum number of throws is the
shortest path in an unweighted graph, which BFS finds directly. BFS visits squares
layer by layer using a FIFO queue, so the first time a square is reached, its
distance is already the minimum. The path is rebuilt by following the `parent`
array back from square 100. If square 100 can never be reached, `bfs()` returns
`(-1, [])`.

| | Complexity |
|---|---|
| Time | O(V + E), with V = 100 and E ≤ 600 |
| Memory | O(V) for the `dist` and `parent` arrays and the queue |

On the default board, BFS finds that square 100 can be reached in **7 throws**:
`1 → 14 → 16 → 22 → 84 → 88 → 94 → 100`.

## Project structure

```
├── board.py            board data (ladders, snakes) and movement rules
├── solver.py           BFS: minimum throws and shortest path
├── game.py             game logic: turns, dice, winner
├── ui.py               Pygame drawing functions
├── main.py             entry point and main game loop
├── tests/
│   └── test_solver.py  unit tests for BFS
└── requirements.txt    dependencies (pygame)
```

## Team

| Member | Responsibility |
|--------|----------------|
| M. Nafis Al Khalifi | `board.py`, `solver.py` (BFS) |
| Dheva Alvian A. E. | `game.py`, unit tests |
| Yuwand Arteta H. W. P. | `ui.py`, `main.py` |
