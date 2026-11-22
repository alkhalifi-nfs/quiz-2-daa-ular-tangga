# Ular Tangga BFS

Game Ular Tangga sederhana untuk 2 pemain, dibuat dengan Python + Pygame.
Program ini juga memakai algoritma **BFS (Breadth-First Search)** untuk menghitung
**jumlah lemparan dadu paling sedikit** dari kotak 1 ke kotak 100.

> Quiz 2 — EF234405 Design & Analysis of Algorithms (M)

## Aturan main

1. Papan 10×10, kotak 1 sampai 100. Kedua pemain mulai di kotak 1.
2. Pemain bergantian menekan **SPASI** untuk melempar dadu (1–6).
3. Kalau pion berhenti di **kaki tangga**, pion naik ke puncaknya.
   Kalau pion berhenti di **kepala ular**, pion turun ke ekornya.
4. Pemain harus berhenti **tepat** di kotak 100. Kalau angka dadu membuat pion
   melewati 100, pion tidak bergerak.
5. Pemain pertama yang sampai di kotak 100 menang.
6. Tekan **B** untuk menampilkan jalur tercepat hasil BFS di papan.

## Struktur proyek

```
ular-tangga/
├── board.py            data papan (ular, tangga) + aturan gerak pion
├── solver.py           algoritma BFS
├── game.py             logika permainan: giliran, dadu, pemenang
├── ui.py               fungsi-fungsi untuk menggambar di layar (Pygame)
├── main.py             file yang dijalankan; berisi loop utama game
├── tests/
│   └── test_solver.py  unit test untuk BFS
├── requirements.txt    daftar library yang perlu di-install (pygame)
├── .gitignore          file/folder yang tidak ikut di-upload ke GitHub
└── README.md           dokumen ini
```

Alur ketergantungan antarfile:

```
board.py  ──►  solver.py
    │              │
    └──►  game.py ◄┘
              │
              ▼
     ui.py  ──►  main.py
```

`board.py` adalah fondasi, jadi file ini dikerjakan **paling pertama**.

## Cara menjalankan

```bash
pip install -r requirements.txt
python main.py                          # main game
python -m unittest discover tests -v    # jalankan unit test
```

---

## Pembagian tugas

Setiap anggota mengerjakan file miliknya sendiri, lalu **commit & push sendiri**,
karena kontribusi dinilai dari riwayat commit di GitHub.

Bagian "kontrak" di bawah menjelaskan nama fungsi, input, dan outputnya. Selama
kontrak ini dipatuhi, setiap anggota bisa bekerja tanpa menunggu kode anggota lain
selesai seluruhnya.

### Anggota 1 — Nafis: `board.py` + `solver.py` (dikerjakan pertama)

- [ ] `board.py`: konstanta `SIZE`, `LADDERS`, `SNAKES`
- [ ] `board.py`: fungsi `move(pos, dice, ladders=LADDERS, snakes=SNAKES)`
- [ ] `solver.py`: fungsi `bfs(start=1, ladders=LADDERS, snakes=SNAKES)`
- [ ] Komentar yang menjelaskan cara kerja BFS (untuk bahan laporan)

Kontrak:

```python
SIZE = 100
LADDERS = {4: 14, 9: 31, ...}   # {kaki: puncak}
SNAKES  = {17: 7, 62: 19, ...}  # {kepala: ekor}

move(pos, dice)  # -> int, posisi setelah lemparan
# contoh: move(1, 3) == 14   (1+3 = 4, ada tangga 4 -> 14)
#         move(98, 5) == 98  (lewat 100, tidak bergerak)

bfs(start=1)     # -> (jumlah_lemparan_minimum, jalur)
# contoh: (7, [1, 14, 16, 22, 84, 88, 94, 100])
#         kalau 100 tidak bisa dicapai: (-1, [])
```

### Anggota 2 — Dheva: `game.py` + `tests/test_solver.py`

Mulai setelah `move()` di `board.py` sudah di-push.

- [ ] `game.py`: class `Game` dengan atribut `positions`, `turn`, `last_dice`, `winner`
- [ ] `game.py`: method `roll()` untuk melempar dadu acak, memindahkan pemain
      dengan `move()`, mengecek pemenang, lalu mengganti giliran
- [ ] `game.py`: method `throws_of(player)` yang mengembalikan berapa kali pemain itu sudah melempar
- [ ] `tests/test_solver.py`: minimal 3 test untuk `bfs()` (papan kosong = 17 lemparan,
      papan dengan ular/tangga, dan papan mustahil = -1)

Kontrak:

```python
game = Game()          # 2 pemain, semua mulai di kotak 1
game.positions         # [1, 1]
game.turn              # 0 = giliran pemain 1, 1 = giliran pemain 2
game.roll()            # lempar dadu untuk pemain yang sedang jalan
game.last_dice         # angka dadu terakhir (1-6), None kalau belum melempar
game.winner            # None, atau 0/1 kalau sudah ada pemenang
game.throws_of(0)      # berapa kali pemain 1 sudah melempar
```

### Anggota 3 — Yuwand: `ui.py` + `main.py`

Menggambar papan bisa langsung dimulai setelah `LADDERS` dan `SNAKES` di
`board.py` sudah di-push. Bagian pion bisa dimulai setelah `Game` selesai.

- [ ] `ui.py`: `draw_board(screen)` untuk menggambar 100 kotak bernomor (urutan zig-zag),
      tangga (garis cokelat), dan ular (garis hijau/merah)
- [ ] `ui.py`: `draw_players(screen, game)` untuk menggambar pion (lingkaran berwarna)
- [ ] `ui.py`: `draw_info(screen, game)` untuk menampilkan giliran siapa, angka dadu, dan pemenang
- [ ] `ui.py`: `draw_path(screen, path)` untuk menggambar jalur BFS sebagai garis
- [ ] `main.py`: membuka jendela Pygame dan menjalankan loop utama
      (SPASI = lempar dadu, B = tampilkan/sembunyikan jalur BFS)
- [ ] Saat permainan selesai, tampilkan perbandingan: "Pemenang butuh X lemparan,
      BFS minimal Y lemparan"

### Bersama-sama

- [ ] Laporan (Report.pdf): desain, implementasi, evaluasi, kesimpulan
- [ ] Declaration.pdf yang sudah ditandatangani
- [ ] Mencoba game sampai selesai dan memperbaiki bug

## Cara kerja bareng di Git

```bash
git pull                     # SELALU ambil perubahan terbaru sebelum mulai kerja
# ... edit file milikmu ...
git add board.py
git commit -m "Tambah data tangga dan ular"
git push
```

Tips:
- Commit sedikit-sedikit dengan pesan yang jelas. Jangan sekaligus satu commit besar di akhir.
- Edit hanya file milikmu sendiri supaya tidak terjadi konflik.
