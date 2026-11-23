# tests/test_solver.py — Unit tests for BFS
#
# Covers 3 test scenarios:
#   1. Empty board (no snakes or ladders) -> at least 17 throws
#   2. Board with ladders/snakes          -> uses ladders, avoids snakes
#   3. Impossible board                   -> BFS returns -1

import sys
import os
import unittest

# Add the project root to sys.path so solver & board can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver import bfs


class TestBFSEmptyBoard(unittest.TestCase):
    """
    Scenario 1: Empty board — no snakes and no ladders.

    On an empty board, each throw moves at most 6 squares.
    From square 1 to square 100 is a distance of 99 squares.
    Theoretical minimum: ceil(99/6) = 17 throws.
    BFS must find exactly 17 throws.
    """

    def setUp(self):
        self.empty_ladders = {}
        self.empty_snakes = {}

    def test_empty_board_minimum_throws(self):
        """BFS on an empty board must need exactly 17 throws."""
        throws, path = bfs(start=1, ladders=self.empty_ladders, snakes=self.empty_snakes)
        self.assertEqual(
            throws, 17,
            f"An empty board must need 17 throws, but BFS returned {throws}"
        )

    def test_empty_board_path_starts_and_ends_correctly(self):
        """The BFS path on an empty board must start at square 1 and end at square 100."""
        throws, path = bfs(start=1, ladders=self.empty_ladders, snakes=self.empty_snakes)
        self.assertEqual(path[0], 1, "The path must start at square 1")
        self.assertEqual(path[-1], 100, "The path must end at square 100")
        # Path length = number of throws + 1 (the starting square is included)
        self.assertEqual(len(path), throws + 1)


class TestBFSWithLaddersAndSnakes(unittest.TestCase):
    """
    Scenario 2: Board with ladders and snakes.

    Ladders shorten the trip (BFS takes advantage of them).
    Snakes require BFS to avoid the snake head squares.

    Test board:
      LADDERS = {4: 50, 60: 90}  — big ladders from square 4 to 50, and 60 to 90
      SNAKES  = {80: 10}         — snake from square 80 to 10 (to be avoided)

    Expected: BFS finds a path that uses the ladders, not one through the snake head.
    """

    def setUp(self):
        # Ladders: 4->50 and 60->90
        self.ladders = {4: 50, 60: 90}
        # Snake: 80->10
        self.snakes = {80: 10}

    def test_path_uses_ladder(self):
        """BFS must use a ladder in its path."""
        throws, path = bfs(start=1, ladders=self.ladders, snakes=self.snakes)

        # Make sure square 100 can be reached
        self.assertNotEqual(throws, -1, "Square 100 should be reachable")
        self.assertEqual(path[-1], 100, "The path must end at square 100")

        # If the path passes square 4 (ladder foot), the next position must be 50
        # If the path passes square 60 (ladder foot), the next position must be 90
        for i in range(len(path) - 1):
            if path[i] == 50:
                # This means the previous square was 4 (ladder foot), jumping to 50
                # Check: 50 is in the path and comes from the 4->50 ladder
                pass
        # Check that 50 is in the path (result of climbing the 4->50 ladder)
        self.assertIn(50, path, "The path must pass square 50 (top of the ladder from 4)")

    def test_path_avoids_snake(self):
        """BFS must not pass through the snake head (square 80) in its optimal path."""
        throws, path = bfs(start=1, ladders=self.ladders, snakes=self.snakes)
        # The snake head on square 80 sends the token back to 10 — the optimal path
        # should not land on square 80
        self.assertNotIn(80, path, "The optimal path must not pass the snake head on square 80")

    def test_fewer_throws_than_empty_board(self):
        """
        With big ladders, BFS must finish in fewer
        throws than on an empty board (17).
        """
        throws, path = bfs(start=1, ladders=self.ladders, snakes=self.snakes)
        self.assertLess(
            throws, 17,
            f"With big ladders, BFS should need < 17 throws, but got {throws}"
        )


class TestBFSImpossibleBoard(unittest.TestCase):
    """
    Scenario 3: Impossible (unreachable) board.

    Strategy: every square from 94 to 99 (the 6 squares before 100) is a snake
    head that pulls the token back behind square 94. So from any square in the
    range 88–93, a throw of 1–6 always lands on 94–99 (snake head) or on a
    square > 100 (no movement), so square 100 can never be reached exactly.

    Concrete configuration:
      Square 94: snake to 2  (far back)
      Square 95: snake to 2
      Square 96: snake to 2
      Square 97: snake to 2
      Square 98: snake to 2
      Square 99: snake to 2

    From square 93 and below:
      - Throw 7+ : no movement (past 100)          — no die shows 7+
      - Throw 1  : to 94 -> snake -> to 2
      - Throw 2  : to 95 -> snake -> to 2
      - Throw 3  : to 96 -> snake -> to 2
      - Throw 4  : to 97 -> snake -> to 2
      - Throw 5  : to 98 -> snake -> to 2
      - Throw 6  : to 99 -> snake -> to 2

    So square 100 cannot be reached from square 93.
    Every reachable square also cannot get past 93 without eventually
    being trapped. It is enough to test that BFS returns -1.
    """

    def setUp(self):
        # The 6 squares before 100 are all snake heads that go far back
        self.impossible_snakes = {
            94: 2,
            95: 2,
            96: 2,
            97: 2,
            98: 2,
            99: 2,
        }
        self.empty_ladders = {}

    def test_impossible_board_returns_minus_one(self):
        """BFS must return -1 if square 100 cannot be reached."""
        throws, path = bfs(
            start=1,
            ladders=self.empty_ladders,
            snakes=self.impossible_snakes
        )
        self.assertEqual(
            throws, -1,
            "An impossible board must return -1 as the number of throws"
        )

    def test_impossible_board_returns_empty_path(self):
        """BFS must return [] as the path if square 100 cannot be reached."""
        throws, path = bfs(
            start=1,
            ladders=self.empty_ladders,
            snakes=self.impossible_snakes
        )
        self.assertEqual(
            path, [],
            "An impossible board must return an empty path []"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
