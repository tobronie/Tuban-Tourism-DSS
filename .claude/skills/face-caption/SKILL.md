---
name: face-caption
description: Tambahkan caption animasi per-kata yang melayang di atas wajah/kepala pembicara pada video (gaya konten TikTok/Reels/Shorts). Kata muncul sinkron dengan ucapan, kata penting di-highlight, posisi mengikuti wajah, bisa teks raksasa di belakang kepala. Gunakan saat user minta caption/subtitle animasi, "caption di atas kepala", kinetic typography, atau memanggil /face-caption.
argument-hint: <video> [pop|redbox|editorial|impact|subtitle] [catatan gaya]
---

# Face Caption — caption bergerak di atas wajah

Pipeline: **transkrip per kata → Claude menyusun caption (pemenggalan, kata penting, headline) → render dengan face tracking → cek preview → video final**.

Semua skrip ada di `scripts/` di folder skill ini (selanjutnya `$S`). Font (Poppins, Anton, Playfair Display – OFL) sudah dibundel di `fonts/`.

## Argumen

`$ARGUMENTS` = path video, opsional nama preset dan catatan gaya bebas.
Jika path video tidak diberikan, tanya user (atau cari `*.mp4/*.mov` terbaru di folder kerja).

## Preset (lihat `references/style-guide.md` untuk detail & kapan dipakai)

| preset | tampilan | referensi |
|---|---|---|
| `pop` (default) | UPPERCASE putih tebal, kata penting oranye lebih besar + glow, muncul per kata dengan efek "pop" | "KATA-KATANYA BERGERAK … RITME" |
| `redbox` | huruf kecil, tiap kata yang sudah diucapkan masuk kotak merah, kata berikutnya tampil redup | "cuan puluhan juta di" |
| `editorial` | kicker kecil berspasi + kata penting merah sans tebal + sisanya serif italic putih | "DAN GILANYA, Semua pakai AI." |
| `impact` | 1 kata RAKSASA condensed, bagian bawahnya **tertutup kepala** (segmentasi orang) | "GRATIS!" |
| `subtitle` | subtitle kecil di dada, kata penting berkotak merah — dipadukan dengan headline di atas kepala | "dibuat pakai AI" |

Preset bisa dicampur per segmen dalam satu video.

## Langkah kerja

1. **Cek dependency** (sekali): `bash $S/setup.sh` (butuh ffmpeg; memasang numpy, pillow, opencv, faster-whisper, mediapipe).

2. **Transkrip per kata**:
   ```bash
   python3 $S/transcribe.py VIDEO --lang id --model small      # -> VIDEO.words.json
   ```
   - Bahasa Inggris: `--lang en`; campur: `--lang auto`. Akurasi lebih baik: `--model medium`/`large-v3`.
   - Sudah punya SRT? `--srt file.srt` (tanpa ASR; waktu per kata dibagi rata per cue).
   - Baca hasilnya, perbaiki salah dengar yang jelas (nama, istilah, merek) langsung di JSON — jangan ubah timestamp.

3. **Draf caption**:
   ```bash
   python3 $S/build_captions.py VIDEO.words.json --preset pop --emph "kata,penting" -o VIDEO.captions.json
   # headline di atas kepala + subtitle berjalan:
   python3 $S/build_captions.py VIDEO.words.json --preset editorial --sub subtitle
   ```

4. **Sunting caption sesuai narasi (bagian terpenting — lakukan sendiri, jangan cuma pakai draf):**
   Baca seluruh transkrip, pahami alurnya (hook → isi → CTA), lalu edit `captions.json`:
   - **Pemenggalan**: 1 segmen = 1 ide/frasa pendek (2–4 kata untuk `pop`, ≤5 untuk `redbox`). Pecah di jeda napas, jangan memisah frasa ("puluhan | juta" ✗).
   - **Kata penting** (`"emph": true`): angka, uang, kata kunci topik, kata emosional/kejutan ("gratis", "gilanya", "AI", "cuan"). Maksimal 1–2 per segmen, kalau semua di-highlight jadi tidak ada yang menonjol.
   - **Momen hook/klimaks** → ganti preset segmen itu ke `impact` (1 kata) atau `editorial` (+ `"kicker": "DAN GILANYA,"` diambil dari kata pengantarnya).
   - Paksa ganti baris dengan `"br": true` pada kata terakhir sebuah baris; perbesar satu kata dengan `"scale": 1.3`.
   - Kata yang tidak perlu tampil (eh, emm, pengulangan) boleh dihapus dari `words`.
   - Ubah posisi bila wajah tertutup grafik/klip B-roll: `"style": {"anchor": "center"}` atau `"top"`/`"bottom"`/`"pos": [0.5, 0.3]`.
   Skema lengkap: lihat bagian *Format captions.json* di bawah.

5. **Preview dulu** (cepat, tanpa render penuh) di momen-momen kunci:
   ```bash
   python3 $S/render.py VIDEO VIDEO.captions.json --preview 1.2,3.5,8,12.4
   ```
   Buka `…_preview/preview_sheet.jpg` dengan Read dan **periksa**: teks tidak menutupi mata/mulut, tidak terpotong tepi layar/area UI (atas ±6%, bawah ±12%), tidak bertumpuk dengan teks bawaan video, kontras cukup. Perbaiki lalu ulangi.

6. **Render final**:
   ```bash
   python3 $S/render.py VIDEO VIDEO.captions.json -o VIDEO_captioned.mp4
   ```
   Opsi: `--start 10 --duration 5` (render potongan uji), `--no-face` (tanpa tracking, posisi tengah), `--retrack` (hitung ulang wajah), `--no-behind`, `--crf 18`, `--preset slow`.
   Hasil face tracking di-cache di `VIDEO.face.json`.

7. Laporkan ke user: path output, preset yang dipakai, kata-kata yang di-highlight, dan hal yang perlu dicek manual.

## Format captions.json

```json
{
  "preset": "pop",
  "style": {"emph_color": "#F0845C"},
  "segments": [
    {"start": 0.20, "end": 1.95,
     "words": [
       {"w": "kata-katanya", "s": 0.20, "e": 0.60},
       {"w": "bergerak", "s": 0.60, "e": 1.00, "emph": true, "br": true},
       {"w": "ritme", "s": 1.40, "e": 1.80, "emph": true, "scale": 1.2}
     ]},
    {"preset": "editorial", "kicker": "Dan gilanya,",
     "words": [{"w": "Semua", "s": 3.9, "e": 4.3, "emph": true}, {"w": "pakai", "s": 4.3, "e": 4.6}, {"w": "AI.", "s": 4.6, "e": 5.0}]},
    {"preset": "subtitle", "words": [{"w": "dibuat", "s": 3.9, "e": 4.3}, {"w": "AI", "s": 4.6, "e": 5.0, "emph": true}]},
    {"preset": "impact", "words": [{"w": "gratis!", "s": 5.6, "e": 6.6}]}
  ]
}
```

- `start`/`end` segmen opsional (default: kata pertama → kata terakhir + `hold`). Segmen dengan preset sama otomatis hilang saat segmen berikutnya mulai; preset berbeda boleh tampil bersamaan (headline + subtitle).
- `style` (global atau per segmen) menimpa field preset apa pun di `presets.json`: `font`, `size` (pecahan lebar video), `case` (`upper|lower|none`), `color`, `emph_color`, `emph_font`, `emph_scale`, `emph_glow`, `spoken_box`, `active_box`, `emph_box`, `upcoming` (`hidden|dim`), `anim` (`pop|slam|rise|fade|none`), `anim_dur`, `anchor` (`above_face|below_face|top|center|bottom`), `pos`, `gap`, `overlap`, `follow` (`smooth` = ikut gerak kepala, `lock` = posisi dikunci saat segmen mulai), `follow_x`, `behind`, `max_words_per_line`, `max_width`, `fit_width`, `shadow`, `stroke`, `strip_punct`.
- Font lain: taruh .ttf di `fonts/` atau beri path absolut / nama font sistem.

## Catatan

- Face tracking memakai OpenCV Haar cascade (tanpa download model); bila wajah tidak terdeteksi, posisi diinterpolasi dari frame sekitar, dan perpindahan klip (hard cut) dideteksi agar teks tidak "meluncur" antar klip.
- Efek di belakang kepala (`behind: true`, preset `impact`) memakai mediapipe selfie segmenter (model ±250 KB diunduh sekali ke `~/.cache/face-caption`). Tanpa mediapipe, teks tetap tampil di depan.
- Kecepatan render ±15–20 fps pada 1080×1920 di CPU (video 60 detik ≈ 1,5–2 menit).
- Untuk video landscape semua ukuran otomatis relatif terhadap lebar; kecilkan `size` bila perlu.
