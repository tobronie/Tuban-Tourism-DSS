# Panduan gaya — caption di atas wajah

Dirangkum dari referensi konten short-form (screenshot yang diberikan user). Prinsip umum yang sama di semua referensi:

1. **Teks hidup di ruang kosong di atas kepala**: antara batas atas aman (±6% tinggi layar, area status/UI) dan ubun-ubun. Wajah, mata, dan mulut tidak pernah tertutup.
2. **Satu ide per layar**: 1–4 kata. Penonton membaca dalam sekali lirik.
3. **Hierarki lewat warna dan ukuran, bukan lewat banyak font**: putih untuk kata biasa, 1 warna aksen (oranye `#F0845C` atau merah `#E3201B`) untuk kata kunci.
4. **Sinkron per kata**: kata muncul tepat saat diucapkan (pop/slam/rise), sehingga caption terasa "bergerak mengikuti ritme".
5. **Bayangan lembut**, bukan outline tebal — tetap terbaca di latar terang maupun gelap.

## Kapan pakai preset apa

| Situasi dalam narasi | Preset | Tips |
|---|---|---|
| Kalimat biasa, tempo cepat, gaya energik | `pop` | 2–3 kata, 1 kata penting oranye. |
| Penjelasan / storytelling santai, ingin penonton "membaca bersama" | `redbox` | 3–5 kata; kata berikutnya terlihat redup (efek karaoke). |
| Pernyataan kunci / plot twist ("Dan gilanya, semua pakai AI.") | `editorial` | Kata pengantar → `kicker`, kata kejutan → `emph` (merah sans), sisanya serif italic. Biasanya disertai `subtitle`. |
| Hook di 1–3 detik pertama, judul besar, angka/klaim utama | `impact` | 1 kata saja (maks 8 huruf ideal), tanda seru boleh. Teks berada di belakang kepala. |
| Subtitle lengkap pendamping headline | `subtitle` | Diletakkan di dada; highlight kata yang sama dengan headline. |

## Ritme

- Video 30–60 detik biasanya: 1 `impact` untuk hook, 1–3 `editorial` untuk momen kunci, sisanya `pop` atau `redbox` (pilih salah satu, jangan bergantian keduanya).
- Jangan ada caption yang tampil < 0,4 detik; gabungkan kata pendek ("di", "yang", "dan") dengan kata sebelah.
- Saat ada B-roll/screen recording tanpa wajah, pindahkan caption ke `center` atau `bottom`, atau hilangkan.

## Warna yang terbukti di referensi

- Putih `#FFFFFF` (kata biasa)
- Oranye Claude `#F0845C` (aksen gaya `pop`)
- Merah `#E3201B` (kotak `redbox`/`subtitle`, aksen `editorial`)
- Kuning `#F5D35B` (alternatif badge/aksen; set `emph_color` atau `emph_box`)
