# game.py — Logika permainan (giliran, dadu, pemenang)
# Penanggung jawab: Dheva (Anggota 2)
#
# class Game
#   * positions   : posisi tiap pemain, misal [1, 1]
#   * turn        : indeks pemain yang sedang jalan (0 atau 1)
#   * last_dice   : angka dadu terakhir (1-6), None sebelum ada lemparan
#   * winner      : indeks pemenang, atau None kalau belum ada
#   * roll()      : lempar dadu acak 1-6, gerakkan pemain, ganti giliran
#   * throws_of(player) : jumlah lemparan pemain 0 atau 1

import random
from board import SIZE, LADDERS, SNAKES, move


class Game:
    """
    Kelas yang mengelola logika permainan Ular Tangga 2 pemain.

    Aturan:
    - Papan 1–100; kedua pemain mulai di kotak 1.
    - Dadu bernilai acak 1–6.
    - Pemain harus berhenti TEPAT di kotak 100 untuk menang
      (jika melampaui 100, posisi tidak berubah — ditangani oleh move()).
    - Pemain bergantian; setelah satu roll, giliran pindah ke pemain lain
      kecuali jika pemain tersebut baru saja menang.
    """

    def __init__(self):
        # Posisi awal kedua pemain di kotak 1
        self.positions = [1, 1]

        # Giliran pertama adalah pemain 0
        self.turn = 0

        # Belum ada lemparan dadu
        self.last_dice = None

        # Belum ada pemenang
        self.winner = None

        # Hitung berapa kali masing-masing pemain sudah melempar dadu
        self._throws = [0, 0]

    def roll(self):
        """
        Melempar dadu untuk pemain yang sedang giliran (self.turn):
        1. Jika permainan sudah selesai (winner sudah ada), tidak melakukan apa-apa.
        2. Lempar dadu acak 1–6, simpan ke self.last_dice.
        3. Tambah hitungan lemparan pemain aktif.
        4. Pindahkan posisi pemain aktif menggunakan move() dari board.py.
        5. Cek apakah pemain mencapai kotak 100:
           - Jika ya, set self.winner = self.turn (permainan selesai).
           - Jika tidak, ganti self.turn ke pemain berikutnya (0 <-> 1).
        """
        # Jangan lakukan apa-apa jika permainan sudah selesai
        if self.winner is not None:
            return

        # Lempar dadu (1–6)
        dice = random.randint(1, 6)
        self.last_dice = dice

        # Tambah hitungan lemparan pemain aktif
        self._throws[self.turn] += 1

        # Gerakkan pemain aktif
        current = self.turn
        self.positions[current] = move(self.positions[current], dice)

        # Cek apakah pemain aktif menang
        if self.positions[current] == SIZE:
            self.winner = current
        else:
            # Ganti giliran ke pemain berikutnya
            self.turn = 1 - self.turn

    def throws_of(self, player):
        """
        Mengembalikan berapa kali `player` (0 atau 1) sudah melempar dadu.

        Parameter:
            player : 0 (pemain 1) atau 1 (pemain 2)

        Return:
            int — jumlah lemparan dadu pemain tersebut
        """
        return self._throws[player]
