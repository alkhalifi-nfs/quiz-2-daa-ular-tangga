# solver.py — Algoritma BFS (Breadth-First Search)
#
# bfs(start, ladders, snakes) -> (jumlah_lemparan_minimum, jalur)
#       * jalur = daftar kotak yang dilewati, misal [1, 14, 22, 84, ..., 100]
#       * jika kotak 100 tidak bisa dicapai -> (-1, [])

from collections import deque

from board import SIZE, LADDERS, SNAKES, move


def bfs(start=1, ladders=LADDERS, snakes=SNAKES):
    dist = [-1] * (SIZE + 1)
    parent = [-1] * (SIZE + 1)

    dist[start] = 0
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for dice in range(1, 7):
            next_pos = move(current, dice, ladders, snakes)

            if dist[next_pos] == -1:
                dist[next_pos] = dist[current] + 1
                parent[next_pos] = current
                queue.append(next_pos)

    if dist[SIZE] == -1:
        return -1, []

    path = []
    pos = SIZE
    while pos != -1:
        path.append(pos)
        pos = parent[pos]
    path.reverse()

    return dist[SIZE], path