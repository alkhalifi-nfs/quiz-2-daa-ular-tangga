# tests/test_solver.py — Unit test untuk BFS
# Penanggung jawab: Dheva (Anggota 2)
#
# Mencakup 3 skenario pengujian:
#   1. Papan kosong (tanpa ular & tangga) -> minimal 17 lemparan
#   2. Papan dengan tangga/ular           -> memanfaatkan tangga, menghindari ular
#   3. Papan mustahil                     -> BFS mengembalikan -1

import sys
import os
import unittest

# Tambahkan root project ke sys.path agar bisa import solver & board
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from solver import bfs


class TestBFSEmptyBoard(unittest.TestCase):
    """
    Skenario 1: Papan kosong — tanpa ular dan tangga.

    Pada papan kosong, setiap lemparan paling banyak maju 6 kotak.
    Dari kotak 1 ke kotak 100 ada jarak 99 kotak.
    Minimum secara teoretis: ceil(99/6) = 17 lemparan.
    BFS harus menemukan tepat 17 lemparan.
    """

    def setUp(self):
        self.empty_ladders = {}
        self.empty_snakes = {}

    def test_empty_board_minimum_throws(self):
        """BFS di papan kosong harus membutuhkan tepat 17 lemparan."""
        throws, path = bfs(start=1, ladders=self.empty_ladders, snakes=self.empty_snakes)
        self.assertEqual(
            throws, 17,
            f"Papan kosong harus butuh 17 lemparan, tapi BFS mengembalikan {throws}"
        )

    def test_empty_board_path_starts_and_ends_correctly(self):
        """Jalur BFS di papan kosong harus mulai di kotak 1 dan berakhir di kotak 100."""
        throws, path = bfs(start=1, ladders=self.empty_ladders, snakes=self.empty_snakes)
        self.assertEqual(path[0], 1, "Jalur harus dimulai dari kotak 1")
        self.assertEqual(path[-1], 100, "Jalur harus berakhir di kotak 100")
        # Panjang jalur = jumlah lemparan + 1 (kotak awal ikut dihitung)
        self.assertEqual(len(path), throws + 1)


class TestBFSWithLaddersAndSnakes(unittest.TestCase):
    """
    Skenario 2: Papan dengan tangga dan ular.

    Tangga mempersingkat perjalanan (BFS memanfaatkannya).
    Ular mengharuskan BFS menghindari kotak kepala ular.

    Papan percobaan:
      LADDERS = {4: 50, 60: 90}  — tangga besar dari kotak 4 ke 50, lalu 60 ke 90
      SNAKES  = {80: 10}         — ular dari kotak 80 ke 10 (dihindari)

    Ekspektasi: BFS menemukan jalur yang memanfaatkan tangga, bukan lewat kepala ular.
    """

    def setUp(self):
        # Tangga: 4->50 dan 60->90
        self.ladders = {4: 50, 60: 90}
        # Ular: 80->10
        self.snakes = {80: 10}

    def test_path_uses_ladder(self):
        """BFS harus memanfaatkan tangga dalam jalurnya."""
        throws, path = bfs(start=1, ladders=self.ladders, snakes=self.snakes)

        # Pastikan kotak 100 bisa dicapai
        self.assertNotEqual(throws, -1, "Kotak 100 seharusnya bisa dicapai")
        self.assertEqual(path[-1], 100, "Jalur harus berakhir di kotak 100")

        # Jika melewati kotak 4 (kaki tangga), posisi berikutnya harus 50
        # Jika melewati kotak 60 (kaki tangga), posisi berikutnya harus 90
        for i in range(len(path) - 1):
            if path[i] == 50:
                # Berarti sebelumnya di kotak 4 (kaki tangga), lompat ke 50
                # Verifikasi: 50 ada di path dan merupakan hasil dari tangga 4->50
                pass
        # Verifikasi bahwa 50 ada di jalur (hasil naik tangga 4->50)
        self.assertIn(50, path, "Jalur harus melewati kotak 50 (puncak tangga dari 4)")

    def test_path_avoids_snake(self):
        """BFS tidak boleh melewati kepala ular (kotak 80) dalam jalur optimalnya."""
        throws, path = bfs(start=1, ladders=self.ladders, snakes=self.snakes)
        # Kepala ular di kotak 80 membuat mundur ke 10 — jalur optimal seharusnya
        # tidak mendarat di kotak 80
        self.assertNotIn(80, path, "Jalur optimal tidak boleh melewati kepala ular di kotak 80")

    def test_fewer_throws_than_empty_board(self):
        """
        Dengan adanya tangga besar, BFS harus bisa selesai dalam lebih
        sedikit lemparan dibandingkan papan kosong (17).
        """
        throws, path = bfs(start=1, ladders=self.ladders, snakes=self.snakes)
        self.assertLess(
            throws, 17,
            f"Dengan tangga besar, BFS seharusnya < 17 lemparan, tapi {throws}"
        )


class TestBFSImpossibleBoard(unittest.TestCase):
    """
    Skenario 3: Papan mustahil (unreachable).

    Strategi: Semua kotak 94–99 (6 kotak sebelum 100) adalah kepala ular
    yang menarik mundur ke belakang kotak 94. Dengan demikian, dari kotak
    manapun di kisaran 88–93, lemparan 1–6 selalu mendarat di 94–99
    (kepala ular) atau di kotak > 100 (tidak bergerak), sehingga kotak 100
    tidak pernah bisa dicapai tepat.

    Konfigurasi konkret:
      Kotak 94: ular ke 2  (mundur jauh)
      Kotak 95: ular ke 2
      Kotak 96: ular ke 2
      Kotak 97: ular ke 2
      Kotak 98: ular ke 2
      Kotak 99: ular ke 2

    Dari kotak 93 kebawah:
      - Lempar 7+ : tidak bergerak (melewati 100)   — tidak ada dadu 7+
      - Lempar 1 : ke 94 -> ular -> ke 2
      - Lempar 2 : ke 95 -> ular -> ke 2
      - Lempar 3 : ke 96 -> ular -> ke 2
      - Lempar 4 : ke 97 -> ular -> ke 2
      - Lempar 5 : ke 98 -> ular -> ke 2
      - Lempar 6 : ke 99 -> ular -> ke 2

    Maka dari kotak 93 tidak bisa mencapai 100.
    Pastikan semua kotak yang bisa dicapai juga tidak bisa mencapai 93 tanpa
    akhirnya terjebak. Kita cukup tes bahwa BFS mengembalikan -1.
    """

    def setUp(self):
        # 6 kotak sebelum 100 semuanya kepala ular yang mundur jauh
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
        """BFS harus mengembalikan -1 jika kotak 100 tidak bisa dicapai."""
        throws, path = bfs(
            start=1,
            ladders=self.empty_ladders,
            snakes=self.impossible_snakes
        )
        self.assertEqual(
            throws, -1,
            "Papan mustahil harus mengembalikan -1 sebagai jumlah lemparan"
        )

    def test_impossible_board_returns_empty_path(self):
        """BFS harus mengembalikan [] sebagai jalur jika kotak 100 tidak bisa dicapai."""
        throws, path = bfs(
            start=1,
            ladders=self.empty_ladders,
            snakes=self.impossible_snakes
        )
        self.assertEqual(
            path, [],
            "Papan mustahil harus mengembalikan jalur kosong []"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
