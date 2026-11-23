# game.py — Game logic (turns, dice, winner)
#
# class Game
#   * positions   : position of each player, e.g. [1, 1]
#   * turn        : index of the player whose turn it is (0 or 1)
#   * last_dice   : last dice value (1-6), None before the first throw
#   * winner      : index of the winner, or None if there is no winner yet
#   * roll()      : roll a random die (1-6), move the player, switch turns
#   * throws_of(player) : number of throws made by player 0 or 1

import random
from board import SIZE, LADDERS, SNAKES, move


class Game:
    """
    Manages the game logic for two-player Snakes and Ladders.

    Rules:
    - Board squares 1–100; both players start on square 1.
    - The die gives a random value from 1 to 6.
    - A player must land EXACTLY on square 100 to win
      (if the roll goes past 100, the position does not change — handled by move()).
    - Players take turns; after one roll, the turn passes to the other player
      unless that player has just won.
    """

    def __init__(self):
        # Both players start on square 1
        self.positions = [1, 1]

        # Player 0 goes first
        self.turn = 0

        # No die has been thrown yet
        self.last_dice = None

        # No winner yet
        self.winner = None

        # Number of throws made by each player
        self._throws = [0, 0]

    def roll(self):
        """
        Roll the die for the current player (self.turn):
        1. If the game is already over (there is a winner), do nothing.
        2. Roll a random die (1–6) and store it in self.last_dice.
        3. Increase the current player's throw count.
        4. Move the current player using move() from board.py.
        5. Check whether the player reached square 100:
           - If so, set self.winner = self.turn (game over).
           - Otherwise, pass the turn to the other player (0 <-> 1).
        """
        # Do nothing if the game is already over
        if self.winner is not None:
            return

        # Roll the die (1–6)
        dice = random.randint(1, 6)
        self.last_dice = dice

        # Increase the current player's throw count
        self._throws[self.turn] += 1

        # Move the current player
        current = self.turn
        self.positions[current] = move(self.positions[current], dice)

        # Check whether the current player has won
        if self.positions[current] == SIZE:
            self.winner = current
        else:
            # Pass the turn to the other player
            self.turn = 1 - self.turn

    def throws_of(self, player):
        """
        Return how many times `player` (0 or 1) has thrown the die.

        Parameters:
            player : 0 (player 1) or 1 (player 2)

        Returns:
            int — the number of throws made by that player
        """
        return self._throws[player]
