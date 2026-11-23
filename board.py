# board.py — Snakes and Ladders board data
#
# SIZE     : number of squares on the board (100)
# LADDERS  : ladder positions, as {foot: top}
# SNAKES   : snake positions, as {head: tail}
# move(pos, dice, ladders, snakes) -> token position after one die throw

SIZE = 100

LADDERS = {
    4: 14,
    9: 31,
    20: 38,
    28: 84,
    40: 59,
    51: 67,
    63: 81,
    71: 91,
}

SNAKES = {
    17: 7,
    54: 34,
    62: 19,
    64: 60,
    87: 24,
    93: 73,
    95: 75,
    99: 78,
}

def move(pos, dice, ladders=LADDERS, snakes=SNAKES):
    new_pos = pos + dice

    if new_pos > SIZE:
        return pos

    if new_pos in ladders:
        return ladders[new_pos]

    if new_pos in snakes:
        return snakes[new_pos]

    return new_pos