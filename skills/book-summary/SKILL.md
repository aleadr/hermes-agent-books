---
name: book-summary
description: "Membuat file summary per-chapter dari buku RAG. Format: summary-{judul-buku}.md dengan judul asli, judul bahasa, dan ringkasan (nonfiksi: paragraf; fiksi: tokoh+setting+alur). Nama file pakai hyphens, tanpa spasi."
version: 2.10.0
author: AMBER
license: MIT
metadata:
  hermes:
    tags: [rag, book, summary, chapter]
    related_skills: [rag]
---

# book-summary

Gunakan skill ini ketika user meminta membuat ringkasan per-bab dari buku yang sudah di-index di RAG.

## Trigger

- "buat summary buku"
- "ringkasan per chapter"
- "siapkan summary - {judul}.MD"
- File hasil indeks RAG (check dengan `rag.py list`)

## Format Output

File: `summary-{judul-buku}.md` (nama file pakai hyphens, tanpa spasi)

### Lokasi penyimpanan

Simpan file summary (.md) di direktori lokal yang ditentukan agent. Default: `~/RAG/summaries/`.
User dapat mengakses file langsung dari filesystem.

### Mode Nonfiksi / Filosofis (default)

Setiap chapter memiliki format:

```
## Chapter X: [Original English Title]

**Judul asli:** [English Title]
**Judul Bahasa Indonesia:** [Terjemahan Bahasa Indonesia]

[1 paragraf ringkasan dalam Bahasa Indonesia — berdasarkan hasil query RAG, tidak halusinasi]
```

### Mode Fiksi / Novel

Setiap chapter memiliki format:

```
## Chapter X: [Original Title]

**Judul asli:** [English Title]
**Judul Bahasa Indonesia:** [Terjemahan Bahasa Indonesia]

**Tokoh:** [Nama tokoh yang muncul di chapter ini, dipisah koma]
**Setting:** [Lokasi, waktu, suasana]
**Alur:** [Ringkasan plot chapter — 3-5 kalimat, mencakup: kejadian utama, konflik, perkembangan karakter, dan cliffhanger jika ada]
```

Pilih mode berdasarkan jenis buku:
- Nonfiksi, filsafat, sains, akademik → mode default (paragraf ringkasan)
- Fiksi, novel, cerita → mode fiksi (tokoh + setting + alur)

## Aturan

### Aturan Umum
- **Preface** (Introduction/Pengantar) dimasukkan sebagai chapter.
- **Appendix** (Notes/Catatan Akhir) dimasukkan sebagai chapter.
- **Dank/Acknowledgements** jika ada di TOC, dimasukkan sebagai chapter (biasanya pendek — 1 paragraf cukup).
- **Index** dan **Glossary** dilewati.
- **Prolog/Epilog** jika ada, dimasukkan sebagai chapter.
- Setiap summary **tepat 1 paragraf** (mode nonfiksi) atau **tokoh + setting + alur** (mode fiksi). Panjang bervariasi tergantung isi chapter.
- **Tidak boleh halusinasi.** Semua konten berdasar hasil query RAG (`rag.py query`) atau pembacaan langsung PDF via pdftotext.
- **Tidak boleh kering/mengambang.** Ringkasan harus konkret dan spesifik — anchor pada argumen aktual, contoh, metafora, dan kutipan langsung dari teks. Bukan deskripsi topik generik ("bagian ini membahas X, Y, Z") melainkan reportase isi.
- Gunakan bahasa Indonesia yang baik dan alami.
- Judul Bahasa Indonesia diterjemahkan bebas dengan mempertahankan makna; tidak perlu harfiah.

### Aturan Khusus Fiksi
- **Tokoh:** Daftar semua karakter yang muncul di chapter, termasuk yang hanya disebut. Gunakan nama seperti di teks asli. Jika karakter baru pertama muncul, tambahkan deskripsi singkat dalam tanda kurung — misal: "Sherlock Holmes (detektif konsultan)".
- **Setting:** Lokasi fisik, waktu (pagi/siang/malam, musim, tahun jika disebut), dan suasana (tegang, damai, mencekam, dll).
- **Alur:** 3-5 kalimat yang mencakup: (a) kejadian pembuka, (b) konflik atau ketegangan utama, (c) perkembangan/plot twist, (d) ending/cliffhanger.
- **Karakter baru:** Catat karakter yang pertama kali muncul di chapter ini secara khusus.

### Aturan Khusus Nonfiksi
- **Sumber TUNGGAL:** Ringkasan hanya boleh berdasar satu buku tunggal yang sedang dibaca. DILARANG keras menggunakan:
  - Ringkasan internet (Wikipedia, SparkNotes, Blinkist, Goodreads, dll)
  - Pengetahuan umum AI tentang topik buku
  - Buku lain oleh penulis yang sama
  - Artikel, paper, atau sumber luar lain
  - Cross-reference dengan buku lain di RAG yang berbeda
- **Jika RAG gagal:** Jika RAG tidak mengembalikan konten yang cukup untuk suatu chapter dan pdftotext juga tidak memberikan konten yang memadai, tulis "Tidak ada data dari sumber buku untuk chapter ini." — jangan mengarang, jangan mengambil dari luar.
- **Larangan inovasi:** Tidak boleh menambahkan interpretasi, analisis, atau elaborasi di luar apa yang tertulis dalam buku. Ringkasan adalah reportase isi buku, bukan esai kritik.
- **Kutipan:** Jika mengutip, pastikan berasal dari chunk RAG atau pdftotext yang terverifikasi dari buku yang sama. Jangan "mengingat" kutipan dari luar.
- Hindari kalimat template seperti "bagian ini memperkenalkan gagasan tentang" — sebutkan gagasannya secara spesifik.

## Workflow

### 0. Starting point: pre-extracted RAG JSON (alternative)

Jika user sudah menyediakan file JSON berisi konten RAG yang sudah diekstrak (keys = nama section, values = teks hasil retrieval), **lewati steps 1-4**. Langsung ke step 5 (verifikasi kualitas konten yang ada di JSON) lalu step 6 (compile summary). Format input tipikal:
```json
{
  "Prologue": "...",
  "Chapter1": "...",
  "Chapter2": "..."
}
```
File bisa di `/tmp/` atau path mana pun yang user sebutkan. Baca konten, verifikasi setiap section punya cukup teks untuk ringkasan, lalu tulis summary sesuai format. Aturan sumber tunggal tetap berlaku — jangan tambahkan konten dari luar buku meskipun RAG JSON terlihat tidak lengkap.

### 1. Identifikasi buku
Cek daftar buku di RAG:
```bash
~/RAG/.venv/bin/python ~/RAG/rag.py list
```
Catat ID dan judul buku.

**⚠️ Cek watermark title.** `rag.py` mengekstrak judul dari baris pertama teks PDF (`lines[0].strip()`). PDF dari situs download sering punya watermark domain, "PDF Compressor", atau teks promosi sebagai baris pertama — sehingga judul buku di RAG jadi tidak bermakna. Jika judul di list mencurigakan (bukan nama buku sesungguhnya), cek filename asli di state:

```bash
python3 -c "import json; s=json.load(open('$HOME/RAG/index_state.json')); [print(f'ID {k}: {v[\"filename\"]}') for k,v in s.items()]"
```

Jika judul salah, fix manual di `~/RAG/index_state.json` dengan mengedit field `title` untuk book ID yang sesuai.

Jika user menyebut judul buku yang belum terindeks, cek dulu apakah PDF-nya sudah ada di `~/RAG/books/`:
```bash
ls ~/RAG/books/*.pdf 2>/dev/null | grep -i "<kata kunci judul>"
```
Jika ada, index langsung tanpa perlu download ulang.

### 1a. Verifikasi hasil index (WAJIB — setelah menjalankan `rag.py index`)

`rag.py index` dapat menampilkan pesan sukses dengan ID tertentu, namun ID tersebut mungkin sudah memiliki koleksi ChromaDB untuk buku yang berbeda (index_state.json dan ChromaDB bisa tidak sinkron). **Selalu verifikasi setelah indexing:**

```bash
# 1. Cek rag.py list — pastikan judul dan chunk count sesuai ekspektasi
~/RAG/.venv/bin/python ~/RAG/rag.py list | grep "\[<ID>\]"

# 2. Cek index_state.json — pastikan filename benar
python3 -c "import json; s=json.load(open('$HOME/RAG/index_state.json')); v=s['<ID>']; print(f'Title: {v[\"title\"]}, Chunks: {v[\"chunks\"]}, File: {v[\"filename\"]}')"

# 3. Jika ada ketidakcocokan (judul salah, chunk count tidak sesuai ekspektasi),
#    jangan lanjutkan — index ulang. ID akan bertambah jika sebelumnya sudah terpakai.
#    Lihat pitfall #27.
```

**Jika ragu, selalu jalankan `rag.py list` lagi setelah index.** Jangan percaya output sukses `rag.py index` begitu saja — ChromaDB mungkin menyimpan data buku lain di ID yang sama (lihat pitfall #27).

### 1b. Pre-flight: Assess RAG granularity (WAJIB — sebelum lanjut ke TOC)

Sebelum mengalokasikan waktu untuk query RAG, cek apakah chunk density cukup untuk chapter-level retrieval:

```bash
# Cek chunk count dan halaman dari state
python3 -c "
import json
s = json.load(open('$HOME/RAG/index_state.json'))
b = s['<BOOK_ID>']
print(f'Chunks: {b[\"chunks\"]}, Title: {b[\"title\"]}')
"
# Cek page count dari PDF
pdfinfo ~/RAG/books/<filename>.pdf 2>/dev/null | grep Pages
```

Hitung ratio: `chunks / pages`. **Rule of thumb:**
- **≥ 0.33 chunks/page (≥ 1 chunk per 3 halaman):** RAG layak dicoba. Lanjut ke step 2.
- **0.15–0.33 chunks/page:** RAG marginal. Tetap ekstrak TOC (step 2), tapi siap fallback ke pdftotext.
- **< 0.15 chunks/page (contoh nyata: 9 chunks / 149 hlm = 0.06, atau 9 chunks / 182 hlm = 0.05):** RAG **tidak berguna** untuk chapter-level queries — setiap chunk mencakup >10 halaman, vector search akan mengembalikan chunk yang sama untuk query berbeda. **Langsung ke strategi pdftotext-only** (lihat pitfall #22): lewati batch_query, export full text, dan gunakan `delegate_task` paralel dengan `sed` line ranges.

**Faktor risiko tambahan — buku dengan endnotes/bibliography tebal:** Buku akademik, sejarah, atau nonfiksi dengan riset berat yang memiliki Bibliographical Essay + Bibliography + Notes di akhir (indicators: ada "Bibliographical Essay" atau "Notes" di TOC, atau >50 halaman notes) SANGAT berisiko tinggi mengalami kontaminasi RAG meskipun chunk density >0.33. Contoh nyata: *Revolusi* (Van Reybrouck, 654 hlm, 0.88 chunks/page) — batch_query menghasilkan 80-100% chunk dari Notes untuk Prologue dan chapter awal. Untuk buku jenis ini: **tetap jalankan batch_query tapi SIAPKAN mental untuk fallback cepat ke pdftotext** setelah verifikasi (step 5). Jangan habiskan waktu memperbaiki hasil RAG yang terkontaminasi — langsung switch ke strategi pdftotext + delegate_task.

Jika RAG tidak layak, tetap ekstrak TOC (step 2) untuk struktur chapter → kemudian langsung ke `delegate_task` paralel — tidak perlu jalankan batch_query sama sekali.

### 2. Ekstrak Table of Contents via pdftotext (WAJIB)
**Jangan andalkan RAG query untuk struktur buku.** Vector search tidak bisa diandalkan untuk mengembalikan daftar isi yang utuh dan terstruktur. Gunakan `pdftotext` langsung dari source PDF:

**Pendekatan A — PDF dengan page numbers (default):**
```bash
# Cari tahu halaman TOC (biasanya di awal, coba f 5-20 dulu)
pdftotext -f 5 -l 20 ~/RAG/books/<filename>.pdf - 2>/dev/null | head -300
```

**Jika tidak ketemu di awal, coba di halaman akhir PDF.** Beberapa buku menempatkan TOC di bagian paling akhir (setelah semua konten), bukan di depan. Cek halaman terakhir:
```bash
# Cari tahu total halaman via pdfinfo
pdfinfo ~/RAG/books/<filename>.pdf 2>/dev/null | grep Pages
# Lalu coba range halaman terakhir (misal total 182: -f 175 -l 182)
pdftotext -f <total-20> -l <total> ~/RAG/books/<filename>.pdf - 2>/dev/null | head -300
```

**Pendekatan B — Full-text grep (PDF tanpa page numbers yang jelas):**
PDF hasil konversi HTML (seperti dari documentacatholicaomnia.eu) sering tidak punya page numbers yang dapat diandalkan. Sebagai gantinya, export full text lalu grep untuk structural markers:

```bash
# Export full text
pdftotext ~/RAG/books/<filename>.pdf /tmp/fullbook.txt

# Cari part/chapter markers — format tergantung sumber PDF
# Untuk PDF documentacatholicaomnia: gunakan \fSECTIONNAME: markers
grep -n $'\\fPRIMAPARS:\\|\\fPRIMASECUNDAE:\\|\\fSECUNDASECUNDAE:\\|\\fTERTIAPARS:\\|\\fSUPPLEMENTUM:' /tmp/fullbook.txt

# Cari judul bab utama (QUESTION, CHAPTER, PART, BOOK)
grep -n "^QUESTION\|^CHAPTER\|^PART\|^BOOK\|^SECTION" /tmp/fullbook.txt | head -40

# Cari major division headers
grep -n "^FIRST PART$\|^SECOND PART$\|^THIRD PART$\|^SUPPLEMENT$" /tmp/fullbook.txt
```

Ini bekerja baik untuk buku dengan struktur hierarkis jelas (Summa, manual teologis, buku teks). Catat line number setiap part/chapter — gunakan sebagai referensi `sed -n '<start>,<end>p'` untuk membaca konten per bagian.

Geser range halaman sampai dapat semua konten daftar isi. Catat:
- Judul resmi setiap bab/bagian
- Section/aphorism numbers jika ada
- Halaman awal setiap bab

Untuk buku dengan sub-bagian kecil (mis. aphorisms bernomor), cukup catat struktur level atas saja (Book I, Book II, dst.) — jangan buat summary per-aphorism.

### 3. Susun daftar chapter target
Berdasarkan TOC, tentukan chapter mana yang perlu summary. Ikuti aturan:
- Preface/Introduction → jadi chapter
- Setiap Book / Part utama → jadi chapter
- Appendix → jadi chapter
- Index / Glossary → lewati
- Prolog/Epilog → jadi chapter (jika ada)

**Untuk fiksi:** Catat juga daftar karakter utama dari TOC atau early pages (dramatis personae jika ada). Buat tracking sheet sementara: nama karakter → first appearance chapter.

### 4. Query konten per chapter
**Dua pendekatan:**

**A. Sequential (buku kecil, <10 chapter):** Query setiap chapter satu per satu:
```bash
~/RAG/.venv/bin/python ~/RAG/rag.py query "Chapter X: [judul]" --book <ID>
```

**B. Batch query (buku besar, >10 chapter — LEBIH CEPAT):** Gunakan `scripts/batch_query.py` yang sudah distandarisasi:

```bash
# 1. Buat file queries JSON (misal: queries-book-<ID>.json):
#    Array of {id, query} objects — id = label section, query = prompt RAG
#
# 2. Jalankan batch query (model load SEKALI):
#    ⚠️ Untuk buku dengan >30 section: jalankan di BACKGROUND dengan
#    notify_on_complete=true + timeout=900. Script hanya menulis hasil di
#    akhir (tidak ada incremental save) — foreground timeout di 600s akan
#    membuang semua hasil. Lihat pitfall #26.
~/RAG/.venv/bin/python ~/.hermes/skills/book-summary/scripts/batch_query.py <BOOK_ID> queries-book-<ID>.json

# 3. Ekstrak teks per chapter (opsional — dengan chapter map):
~/RAG/.venv/bin/python ~/.hermes/skills/book-summary/scripts/extract_chapter_texts.py \
  batch_results_<ID>.json chapter_map.json
```

**Template queries file** — copy dan isi per buku:
```json
[
  {"id": "Preface/Introduction", "query": "Full content of the introduction: main topics, arguments, background"},
  {"id": "Ch1", "query": "Chapter 1: full content, main arguments, key examples, philosophical positions"},
  {"id": "Ch2", "query": "Chapter 2: full content..."}
]
```
Simpan sebagai `queries-book-<ID>.json` di `~/RAG/` atau direktori kerja.

**Template chapter map file** (opsional — untuk extract readable labels):
```json
{
  "Preface/Introduction": "Introduction",
  "Ch1": "Chapter 1: Is this the real life?",
  "Ch2": "Chapter 2: What is the simulation hypothesis?"
}
```

**Tips query sukses:**\\\\n- **WAJIB:** Query hanya pada satu book ID yang sedang dibaca. Jangan cross-query dengan buku lain. Parameter `--books <ID>` atau `book_ids=[<ID>]` harus spesifik.\\\\n- Sertakan keywords spesifik dari judul section dan sub-section (dari TOC) dalam query — ini membantu RAG memisahkan section yang tematis mirip.

- **Buku non-Inggris (Jerman, Prancis, Belanda, dll):** Tulis query DALAM BAHASA ASLI buku untuk hasil RAG optimal. Query Inggris bisa berfungsi untuk buku berbahasa non-Inggris karena model embedding multilingual, tapi akan kehilangan istilah kunci yang hanya muncul dalam bahasa asli. Tambahkan istilah kunci dari TOC (judul chapter, konsep sentral) dalam bahasa asli ke dalam query. Summary tetap ditulis dalam Bahasa Indonesia — artinya kamu menerjemahkan konten asli, bukan menyalin output RAG mentah.\\\\n- **Untuk buku philosophis/aphoristic (Nietzsche, Pascal, Wittgenstein):** RAG sangat rentan kontaminasi — vector similarity mengembalikan chunk puisi/Prelude untuk query section mana pun karena vocabulary puitis lebih unik/mudah di-match. Jangan andalkan RAG sebagai sumber PRIMER. Strategi: (1) jalankan batch_query tetap sebagai bahan awal, (2) verifikasi secara manual setiap chunk per section — buang yang terkontaminasi, (3) baca opening paragraphs tiap section langsung via pdftotext sebagai sumber PRIMER, (4) gunakan RAG hanya sebagai cross-check untuk kutipan spesifik.\\\\n- **Untuk buku dengan endnotes/bibliography tebal** (akademik, teknis, nonfiksi dengan riset berat): proper names, paper titles, dan konsep kunci dari chapter narrative juga muncul di halaman Notes/Bibliography. Akibatnya, RAG sering mengembalikan chunk dari Notes/Bibliography, bukan dari body chapter. Untuk mitigasi:\\\\n  1. Dalam query, tambahkan konteks naratif spesifik: bukan hanya topik, tapi juga setting, tokoh, anekdot, atau urutan kejadian yang membedakan narrative chapter dari daftar referensi.\\\\n  2. Setelah batch_query selesai, verifikasi output: apakah chunk yang dikembalikan benar-benar dari body chapter atau dari Notes? Ciri Notes: format footnote, halaman belakang, nama jurnal, tahun, volume, DOI.\\\\n  3. Jika kontaminasi parah (>50% chunk dari Notes), fallback ke `pdftotext -f <page_start> -l <page_end>` langsung dari source PDF untuk chapter tersebut. Jangan mengambil dari luar.\\\\n\\\\n### 5. Verifikasi kualitas hasil batch query (WAJIB)\\\\nSebelum menulis summary, verifikasi output batch_query dengan cepat. Periksa dua jenis kontaminasi:\\\\n\\\\n**Kontaminasi Notes/Bibliography:** Ciri — kalimat mengandung doi, nama jurnal, tahun volume, footnote numbers. Jika dominan, fallback ke pdftotext.\\\\n\\\\n**Kontaminasi aphoristic/puisi:** Ciri — chunk dari Prelude/puisi berima muncul di hasil query untuk Book/Part section. Sangat umum pada Nietzsche. Identifikasi dengan membaca sample chunk tiap section.

**Kontaminasi omnibus final chunk:** Ciri — satu chunk index yang sama muncul di >3 query berbeda. Chunk terakhir buku sering menggabungkan Acknowledgments + About the Author + Notes, menciptakan keyword density tinggi yang membuatnya match untuk query apa pun. Abaikan chunk ini untuk semua section kecuali Acknowledgments/About the Author (lihat pitfall #23).

**Kontaminasi tematik lintas-section (cross-section thematic overlap):** Ciri — chunk yang sama (chunk_idx identik) muncul di >2 section berbeda, tapi isinya BUKAN Notes/Bibliography (lolos filter Notes di langkah verifikasi di atas). Ini terjadi pada buku dengan tema berulang di banyak chapter (pop-science, esai, buku filosofis ringan seperti Tyson atau Harari). Contoh nyata: chunk #67 tentang Bruno dan antimatter muncul di Prologue, Alien To Them, Alien To Me, dan Epilogue — semuanya konten naratif valid, tapi tidak bisa dipastikan section mana yang benar. **Deteksi:**\n```bash\npython3 -c \"\nimport json\nfrom collections import Counter\nwith open('batch_results_<ID>.json') as f:\n    results = json.load(f)\nchunk_map = Counter()\nfor item in results:\n    seen = set()\n    for chunk in item['chunks']:\n        cid = chunk['chunk_idx']\n        if cid not in seen:\n            chunk_map[cid] += 1\n            seen.add(cid)\nfor cid, count in chunk_map.most_common(20):\n    if count > 2:\n        print(f'Chunk #{cid}: muncul di {count} section — OVERLAP')\n\"\n```\n**Jika >30% section memiliki chunk yang tumpang tindih:** RAG tidak bisa diandalkan untuk memisahkan konten per-chapter. **Abaikan batch_query, langsung gunakan pdftotext + line ranges** (lihat strategi fallback di bawah) sebagai sumber PRIMER untuk SEMUA section. Jangan buang waktu memperbaiki hasil RAG yang terkontaminasi tematik.\n\n**Strategi fallback pdftotext + line ranges (gunakan saat kontaminasi tematik terdeteksi):**\n1. Export full text: `pdftotext ~/RAG/books/<file>.pdf /tmp/fullbook.txt`\n2. Cari chapter boundaries via grep untuk judul section ALL-CAPS:\n   ```bash\n   grep -n \"^[A-Z][A-Z .,'\\\"\\\\]\\\\{10,60\\\\}$\" /tmp/fullbook.txt | head -30\n   ```\n3. Catat line number setiap section header. Hitung line range: [header_line, next_header_line - 1]\n4. Split section list ke 3 grup merata, delegasikan ke 3 subagent paralel via `delegate_task`:\n   - Masing-masing subagent membaca konten dengan `sed -n '<start>,<end>p' /tmp/fullbook.txt`\n   - Tulis summary per chapter dalam Bahasa Indonesia (satu paragraf per section)\n   - Output ke file terpisah: `/tmp/summary_part1.md`, `/tmp/summary_part2.md`, `/tmp/summary_part3.md`\n5. Merge hasil dengan `cat`, tambahkan header metadata buku, copy ke SMB share\nPola ini menghemat ~6-10 menit vs sequential dan menghasilkan summary yang bersih dari kontaminasi RAG.\\\\n\\\\n**⚠️ Section akhir buku (Epilogue, Afterword, Conclusion) sangat rentan:** Karena bersebelahan fisik dengan Notes/Bibliography dan tematis mirip (mengulang proper names, konsep kunci, paper titles), section ini sering mengalami **100% kontaminasi** — 0 dari 5 chunk berguna, semuanya dari Notes, front matter, atau chapter lain. Contoh nyata: Epilogue *Nexus* (Harari) — 0/5 chunk berguna. **Untuk Epilogue/Afterword/Conclusion: langsung gunakan pdftotext, jangan buang waktu dengan batch query.** Gunakan teknik page-by-page search untuk menemukan halaman tepatnya (lihat pitfall #21).\\\\\\\\n\\\\\\\\n**Jika <50% chunk per section berguna** atau **suatu section memiliki 0% useful chunks** (contoh nyata: Book Five Nietzsche — 0 dari 5 chunk berguna; Epilogue Nexus — 0/5 chunk), langsung ubah strategi:\\\\n  1. `pdftotext -f <start_page> -l <start_page+5>` untuk membaca opening paragraphs langsung dari PDF\\\\n  2. Catat argumen spesifik, nomor aphorism, kutipan langsung\\\\n  3. Tulis summary dari konten PDF, bukan dari RAG\\\\n  4. Tidak perlu menyebut \"tidak ada data\" — cukup tulis summary dari pembacaan langsung, pastikan konten berasal dari buku yang sama\\\\n\\\\n**Jika total contamination rate >60%** untuk semua section, ubah strategi global: jadikan pdftotext sebagai sumber PRIMER untuk semua section, RAG hanya sebagai pelengkap kutipan spesifik. Proses dengan delegate_task agar paralel — lihat `references/direct-pdftotext-delegation.md` untuk resep lengkap. Jangan sekali-kali mengambil konten dari luar buku.

### 6. Compile summary
Tulis ke file `summary-{judul-buku}.md` (nama file pakai hyphens, tanpa spasi). Lokasi:
```
~/RAG/summaries/summary-{judul-buku}.md
```
(Simpan di direktori output agent — user ambil langsung dari filesystem.)

**Default:** .md saja. A5 PDF hanya jika user meminta secara eksplisit.

**Mode nonfiksi:** Tulis paragraf ringkasan per chapter sesuai format Nonfiksi/Filosofis.

**Mode fiksi:** Tulis **Tokoh**, **Setting**, dan **Alur** per chapter. Pastikan:
- Konsistensi nama karakter di seluruh chapter (jangan ganti ejaan)
- Setting yang berubah dicatat dengan jelas
- Alur mencakup sebab-akibat, bukan hanya kronologi
- Jika karakter tidak muncul lagi setelah chapter tertentu, catat di summary
- Gunakan tracking sheet karakter: nama → first appearance → last appearance → peran

### 7. Optimasi waktu
Jika total chapter >6, gunakan `delegate_task` untuk menulis summary beberapa bagian secara paralel (maks 3 subagents bersamaan). Untuk buku 6-15 section: split menjadi 3 grup merata. Untuk buku >15 section: batch_query + delegate_task hybrid (batch_query dulu untuk konten, lalu delegate_task untuk menulis). Untuk buku dengan kontaminasi tematik terdeteksi (step 5): gunakan delegate_task dengan pdftotext + line ranges — ini adalah pola yang paling hemat waktu untuk buku yang RAG-nya tidak bisa diandalkan.

**Delegate task pattern:** Gunakan `toolsets: ["terminal", "file"]` — subagent hanya perlu membaca file (batch results, full text via sed) dan menulis summary. Tidak perlu web, browser, atau tools lain. Setiap subagent diberi:
- Assigned sections dengan exact line ranges dari full text
- RAG keys untuk batch_results file
- Format template lengkap (termasuk aturan sumber tunggal, larangan halusinasi)
- Path file output terpisah (`/tmp/summary_part1.md`, `/tmp/summary_part2.md`, `/tmp/summary_part3.md`)
- Instruksi untuk skip chunk yang jelas berasal dari Notes/Bibliography

Setelah semua subagent selesai, merge dengan `cat` atau Python, tambahkan header, lalu copy ke direktori output. Output files dipisah untuk menghindari konflik write antar subagent.

**⚠️ Verifikasi output subagent sebelum merge (WAJIB):** Baca 3-5 baris pertama setiap file output (`/tmp/summary_part1.md`, dst.) untuk memastikan proper names, judul section, dan konsep kunci cocok dengan buku target. Subagent dapat secara diam-diam menulis konten dari buku yang berbeda (lihat pitfall #28). Jika konten mencurigakan, tulis ulang section tersebut secara langsung — jangan pakai hasil subagent.

## Post-Summary Deep-Dive Q&A

Setelah summary selesai, user sering mengajukan pertanyaan filosofis spesifik yang tidak tercakup dalam ringkasan per-chapter (misal: "apakah buku membahas X?", "bagaimana penjelasan tentang Y?"). Teknik berikut lebih efektif daripada RAG query saja:

### 1. Cari keyword di full PDF text terlebih dahulu

Export full text dari PDF sekali, lalu grep untuk keyword:
```bash
pdftotext ~/RAG/books/<filename>.pdf /tmp/fullbook.txt
grep -n -i "keyword1\|keyword2" /tmp/fullbook.txt | head -20
```
Ini memberi tahu halaman mana yang relevan (line number ~ page).

### 2. Baca bagian spesifik via pdftotext range

Setelah tahu line/page yang relevan, baca konteks penuh:
```bash
# Jika ada page number dari TOC, langsung:
pdftotext -f <start_page> -l <end_page> ~/RAG/books/<filename>.pdf -
```

Atau baca range line dari full text:
```bash
sed -n '<start_line>,<end_line>p' /tmp/fullbook.txt
```

### 3. Gunakan RAG hanya sebagai pelengkap

RAG bagus untuk menemukan chunk relevan secara tematis, tapi sering:
- Melewatkan detail spesifik karena vector search mengutamakan similaritas semantik
- Terkontaminasi chunk dari Bibliography/Notes (untuk buku dengan proper names yang muncul di halaman referensi)

Untuk pertanyaan filosofis teknis, **pdftotext adalah sumber PRIMER**, RAG adalah cross-check.

### 4. Cari halaman dari referensi TOC

Table of Contents (diekstrak di langkah #2 workflow) mencantumkan nomor halaman untuk setiap section. Saat user bertanya tentang topik spesifik:
- Cocokkan topik dengan section/judul di TOC
- Gunakan nomor halaman dari TOC sebagai target `pdftotext -f <page>`
- Baca paragraf pembuka section untuk konten PRIMER

### 5. Kompilasi jawaban dengan citation

Berikan jawaban dengan:
- Kutipan langsung dari teks (dengan nomor halaman)
- Referensi Question number Summa jika ada (q. XX, a. Y)
- Konteks: jelaskan letak topik dalam struktur buku (Chapter/Part/Section)

Contoh output lihat `references/deep-dive-qa-example.md`.

### Pendekatan C: Short / Essay-Style Books (<15 halaman, no numbered chapters)

**Kapan:** Buku pendek (<15 halaman, <10 chunks), pamflet filosofis, esai, pidato — seperti *Perpetual Peace*, *Essence of the Bhagavad Gita*, *Communist Manifesto*.

**Jangan gunakan batch_query.** Untuk buku pendek:
1. **Full-text export langsung:**
   ```bash
   pdftotext ~/RAG/books/<filename>.pdf /tmp/fullbook.txt
   ```
2. **Identifikasi section headers** — cari form feed markers (`\f`) atau baris judul dari full text:
   ```bash
   grep -n $'\\f\\|^[A-Z][A-Za-z ]\\{3,50\\}$' /tmp/fullbook.txt | head -30
   ```
3. **Baca langsung** — buku pendek bisa dibaca penuh dalam 1-2 menit via `cat /tmp/fullbook.txt`. Tidak perlu RAG query.
4. **Tulis summary langsung** — pisahkan berdasarkan section headers yang ditemukan. Gunakan judul asli dari PDF, bukan hasil RAG.
5. **Untuk buku dengan struktur continuous prose** (ayat berkesinambungan tanpa chapter break, seperti kompilasi ayat Gita): bagi summary berdasarkan section judul yang ada (Introduction, Main Body, Appendix/References). Jika tidak ada section judul sama sekali, cukup satu bagian summary kontinu.

**Pitfall:** RAG query untuk buku pendek sering timeout karena overhead loading model embedding (~5-8s) sama dengan buku besar, tapi vector search tidak memberi manfaat berarti karena total teks bisa dibaca langsung lebih cepat. Fallback ke pdftotext langsung adalah pilihan default, bukan exception.

### Unnumbered / Non-Standard Structure

Beberapa buku tidak memiliki chapter bernomor (Chapter 1, 2, 3...) tetapi menggunakan:
- Section judul saja (Introduction, Part I, Appendix)
- Form feed markers (`\f`) sebagai pemisah visual antar bagian
- Halaman kosong dengan angka halaman sebagai pemisah

**Strategi fallback pdftotext + line ranges (gunakan saat kontaminasi tematik terdeteksi):**  
**⚠️ Untuk buku scanned/OCR:** pdftotext tidak berfungsi pada source PDF (0 teks). Gunakan file OCR markdown (`/tmp/<buku>-ocr.md`) sebagai full text — lihat pitfall #30. Untuk buku non-scanned, lanjutkan:  
1. Export full text: `pdftotext ~/RAG/books/<file>.pdf /tmp/fullbook.txt`
2. Cari judul section ALL-CAPS — ini adalah pola paling andal untuk buku pop-science/esai modern yang menggunakan judul bab tanpa nomor (seperti buku Neil deGrasse Tyson, Malcolm Gladwell, dll):
   ```bash
   grep -n "^[A-Z][A-Z .,'\"\\]\\{10,60\\}$" /tmp/full.txt | head -30
   ```
3. Cari juga `\f` (form feed) — marker halaman baru yang menandai section break:
   ```bash
   grep -n $'\\f' /tmp/full.txt
   ```
4. Di sekitar setiap judul ALL-CAPS atau `\f`, baca 3-5 baris setelahnya untuk mengidentifikasi judul section.
5. Gunakan judul-judul tersebut sebagai struktur summary. Jika buku hanya punya section ALL-CAPS tanpa nomor (seperti "ALIEN TO US", "ALIEN TO THEM"), gunakan judul asli apa adanya — jangan menambahkan nomor chapter.

**Contoh nyata:** *Essence of the Bhagavad Gita* (8 halaman) — memiliki 3 section: Introduction (1 paragraf), Main Body (prosa 42 ayat, paling panjang), Apposite References (kutipan Talks). Tidak perlu batch_query, tidak perlu TOC extraction, langsung compile dari pdftotext.

## Common Pitfalls

1. **Mengandalkan RAG query untuk TOC.** Vector search mengembalikan chunk yang *konseptual* relevan, bukan yang mengandung tabel isi. Selalu gunakan pdftotext pada source PDF di `~/RAG/books/` untuk mengekstrak daftar isi yang akurat (Workflow langkah #2).

2. **Vector search overlap untuk section yang mirip tematis.** Buku dengan tema berulang antar chapter — baik filosofis/aphoristic (Nietzsche) MAUPUN pop-science/esai (Tyson, Harari) — sering mengalami RAG mengembalikan chunk yang sama untuk query section berbeda. Contoh nyata: buku *Take Me to Your Leader* (Tyson) — chunk tentang radio bubble, Giordano Bruno, dan antimatter muncul di hasil Prologue, Alien To Them, Alien To Me, dan Epilogue karena topik-topik ini dibahas di banyak chapter. Ini berbeda dari kontaminasi Notes (pitfall #7) karena chunk lolos filter Notes tapi tetap salah section. **Deteksi:** setelah batch_query, cek apakah chunk_idx yang sama muncul di >2 section berbeda. Jika iya, RAG tidak bisa diandalkan untuk memisahkan section — **langsung fallback ke pdftotext + line ranges** (lihat strategi fallback di step 5).

3. **Query RAG timeout.** `rag.py query` bisa lambat/search timeout untuk buku besar. Jika gagal dengan timeout ≥60s, fallback ke pdftotext langsung.

4. **Scripts ada di skill directory, jalankan dari mana saja.** Kedua script (`batch_query.py`, `extract_chapter_texts.py`) ada di `~/.hermes/skills/book-summary/scripts/`. Jalankan langsung dengan path absolut — tidak perlu di-copy ke `~/RAG/`. Output file (`batch_results_<ID>.json`) akan dibuat di direktori kerja saat ini.

5. **Duplicate indexing karena watermark title.** Jika PDF berasal dari situs dengan watermark, baris pertama domain menjadi judul buku di RAG. Saat meng-index PDF yang sama lagi, `rag.py list` menampilkan dua entry dengan judul domain yang sama dan jumlah chunk yang identik — sulit dibedakan tanpa cek filename. Solusi: sebelum index, selalu cek state file untuk filename duplikat: `python3 -c "import json; s=json.load(open('$HOME/RAG/index_state.json')); [print(f'ID {k}: {v[\"filename\"]}') for k,v in s.items()]"`. Jika filename sudah ada, remove ID lama dulu atau gunakan ID yang sudah ada. Atau lebih baik: fix title di index_state.json dulu agar buku teridentifikasi dengan benar.

6. **TOC di akhir PDF, bukan di awal.** Beberapa buku menempatkan Table of Contents setelah semua konten (halaman akhir). Jika `pdftotext -f 5 -l 20` tidak menghasilkan struktur TOC, coba range halaman terakhir. Gunakan `pdfinfo` untuk cek total halaman, lalu `pdftotext -f <total-20> -l <total>`.

7. **Kontaminasi Notes/Bibliography di hasil batch query.** Buku akademik, teknis, atau nonfiksi dengan riset berat (mis. *The Alignment Problem* oleh Brian Christian, ~100+ halaman endnotes) sering punya proper names dan paper titles yang sama antara body chapter dan halaman Notes/Bibliography. RAG vector search mengembalikan chunk dari Notes karena BM25/keyword match lebih tinggi untuk chunk yang penuh dengan nama jurnal dan sitasi. **Section akhir buku (Epilogue, Afterword, Conclusion) adalah yang paling parah — sering mencapai 100% kontaminasi (0 chunk berguna).** Ciri: batch output berisi kalimat seperti "Nature 518, no. 7540 (2015): 529–33" atau "See Angwin et al., 'Machine Bias.'" alih-alih narasi chapter. Mitigasi: lihat Tips query sukses (teknik #3: konteks naratif + verifikasi output + fallback pdftotext). Untuk Epilogue/Afterword: langsung pdftotext, jangan RAG.

8. **batch_query.py perlu execute permission.** Script `batch_query.py` mungkin tidak punya izin eksekusi. Jika dapat error "Permission denied", jalankan dengan `python3` eksplisit via venv: `~/RAG/.venv/bin/python <script_path>`, atau chmod +x sekali saja.

9. **Filename harus tanpa spasi.** User menolak filename dengan spasi (`summary - Judul Buku.md`). Selalu gunakan hyphens: `summary-judul-buku.md`. Juga hindari koma, tanda kurung, dan simbol lain — hapus atau ganti dengan hyphens. Contoh: "The Classics of Marxism, Volume One" → `summary-the-classics-of-marxism-volume-one.md`.

10. **File delivery failure via platform.** File `.md` yang dikirim via platform attachment mungkin tidak tampil di beberapa platform. Jika user melaporkan file tidak ter-attach:
    - Simpan file ke direktori output yang bisa diakses user langsung.
    - Atau paste konten summary langsung ke chat sebagai teks.
    - Pastikan file path absolut dan ada (cek dengan `ls -la`) sebelum dikirim.

11. **Response truncation mengganggu delivery.** Jika summary panjang (8+ chapter, >10KB) dan model memiliki context terbatas (misal 64K), ada risiko output terpotong oleh system sebelum `send_message` sempat dipanggil. Mitigasi:
    - Tulis file summary di sesi awal, kirim di langkah berikutnya sebagai langkah terpisah.
    - Prioritaskan delivery segera setelah file selesai — jangan delay dengan langkah lain.
    - Jika model rawan truncation, gunakan terminal background + `notify_on_complete` untuk workflow, atau delegasikan ke cronjob dengan model override.

12. **Permission mismatch saat menyimpan summary ke external mount.** Jika direktori output berada di external/FUSE mount dengan owner berbeda dari agent user, `write_file` tool akan gagal dengan "Permission denied". Solusi:
    - Tulis file ke `/tmp/` dulu, lalu gunakan `sudo cp` ke direktori target.
    - Atau tambahkan agent user ke group owner mount, lalu restart gateway agar group baru ter-load.

13. **Judul buku salah setelah index (bukan hanya watermark).** `rag.py` mengekstrak judul dari `lines[0].strip()` — baris pertama teks dalam PDF. Ini bisa berupa:
   - **Watermark** (domain website, "PDF Compressor", teks promosi) — dari situs download.
   - **Kata acak dari blok kutipan** (misal \"Buch\" dari kutipan panjang di halaman 1) — karena halaman sampul kosong, teks pertama yang terbaca adalah kata pertama dari body text.
   - **Judul chapter pertama** — jika buku tidak punya halaman judul yang jelas.
   - **Informasi hak cipta** — baris teks pertama bisa berupa copyright notice.

   Akibatnya, judul buku di RAG tidak bermakna. Jika judul di `rag.py list` mencurigakan (bukan nama buku sesungguhnya), cek filename asli di state, lalu fix judul di `~/RAG/index_state.json`.
   ```bash
   python3 -c "
   import json
   s = json.load(open('/home/ubuntu/RAG/index_state.json'))
   s['4']['title'] = \"Preparing for Tomorrow's AI-Enhanced Work Environment by Aftab Ara\"
   open('/home/ubuntu/RAG/index_state.json','w').write(json.dumps(s, indent=2, ensure_ascii=False))
   print('Fixed title for book [4]')
   "
   ```
   Cek juga di `rag.py list` apakah ada buku lain dengan judul watermark domain yang sebenarnya adalah judul berbeda — jika iya, ganti satu per satu.
   
   **Pencegahan:** sebelum index PDF dari sumber yang tidak dikenal, cek dulu baris pertama PDF dengan `pdftotext -f 1 -l 1 <file.pdf> - | head -5`. Jika outputnya domain watermark, teks promosi, atau teks yang jelas bukan judul buku (kata tunggal, baris copyright, dll), judul akan salah. Siapkan untuk fix manual di index_state.json setelah index. Strategi lebih baik: rename PDF dengan nama buku yang benar sebelum index, lalu setelah index cek judul dan fix jika perlu.

14. **Kontaminasi puisi/Prelude pada buku aphoristic.** Buku seperti Nietzsche's *The Gay Science* memiliki Prelude puisi yang sering mengkontaminasi RAG untuk SEMUA section query. Polanya: RAG me-return chunk dari Prelude (puisi pendek dengan vocabulary unik) untuk query Book One sampai Book Five karena vector similarity menganggap vocabulary puisi lebih match. Identifikasi: setelah batch_query, cek apakah chunk dari section Prelude muncul di hasil query untuk section lain. Mitigasi: verifikasi chunk distribution sebelum pakai hasil batch; jadikan pdftotext sebagai sumber PRIMER, RAG sebagai cross-check saja. Filter manual: buang chunk yang jelas dari Prelude/poetry.

15. **Section dengan 0% RAG coverage.** Pada buku aphoristic, beberapa section bisa memiliki 0% useful chunks (contoh nyata: Book Five Nietzsche — 0 dari 5 chunk berguna; semuanya dari Prelude, Book Four, atau Appendix). Jangan lanjutkan dengan RAG saja untuk section ini karena akan menghasilkan summary generik/dry. Solusi: gunakan `pdftotext -f <start_page> -l <start_page+5>` untuk membaca opening paragraphs langsung dari PDF, catat argumen spesifik dan kutipan dari aphorism pembuka, lalu tulis summary dari konten tersebut. Supplement dengan pengetahuan yang sudah terverifikasi dari section lain jika relevan.

16. **Karakter baru tidak tercatat di fiksi.** Pada novel, karakter bisa muncul di chapter mana pun tanpa diperkenalkan ulang. Jika tracking sheet tidak dibuat sejak awal, risiko terlewat karakter penting tinggi. Mitigasi: buat tracking sheet karakter saat membaca Chapter 1 (nama → first appearance → deskripsi), update setiap chapter. Untuk RAG, tambahkan \"nama karakter\" dalam query agar vector search lebih akurat mengembalikan chunk yang relevan.

17. **Setting berubah tanpa transisi eksplisit.** Novel sering berganti setting antar chapter tanpa narasi transisi. RAG tidak bisa diandalkan untuk mendeteksi perubahan setting — selalu verifikasi setting tiap chapter via pdftotext pada halaman pertama dan terakhir chapter. Catat: lokasi, waktu, dan suasana secara eksplisit.

18. **Embedding time untuk buku sangat besar (>5000 halaman).** Buku seperti Summa Theologica (9.453 halaman, 6.886 chunks, 216 embedding batches) butuh ~30-40 menit untuk embedding penuh. Jangan timeout default — gunakan `notify_on_complete=true` di terminal background dan lanjutkan eksplorasi struktur PDF sambil menunggu. Pantau progress via progress bar (batches X/216) jika output tertangkap; jika tidak, cek `ps aux | grep rag.py` untuk memastikan proses masih jalan (CPU usage tinggi = aktif embedding).

19. **PDF tanpa page numbers (HTML-to-PDF).** Beberapa PDF (khususnya dari situs seperti documentacatholicaomnia.eu) dikonversi dari HTML dan tidak memiliki page numbers yang dapat diandalkan. `pdftotext -f <N> -l <M>` tidak berguna karena page numbers tidak sesuai konten. Solusi: export full text (`pdftotext file.pdf /tmp/full.txt`), lalu cari structural markers via grep. HTML-derived PDFs sering punya `\\fSECTIONNAME:` markers (form feed + judul section) yang menandai batas antar bagian. Gunakan ini untuk map struktur.

20. **Daftar isi di PDF dari HTML source sering redundant.** PDF hasil konversi HTML sering menyertakan index/TOC lengkap di awal (bisa puluhan halaman), lalu mengulang konten yang sama persis di bagian body. Jangan bingung — bedakan TOC dari konten aktual dengan mencari marker konten pertama (biasanya `\\fPRIMAPARS:` atau `PROLOGUE` setelah TOC selesai).

21. **Section akhir buku (Epilogue, Afterword, Conclusion) sulit ditemukan via full-text grep.** Pada buku dengan endnotes tebal, full-text export mencampur endnotes dari SEMUA chapter — grep untuk "Epilogue" atau "Acknowledgements" hanya menemukan header endnotes, bukan body chapter. Header section akhir buku sering berupa elemen grafis (bukan teks terekstrak) atau format berbeda. **Teknik page-by-page search:** loop pdftotext per halaman untuk menemukan halaman tepat section target:
    ```bash
    for p in $(seq <start_page> <end_page>); do
      text=$(pdftotext -f $p -l $p ~/RAG/books/<file>.pdf - 2>/dev/null)
      if echo "$text" | grep -qi "<keyword unik dari section>"; then
        echo "Page $p: FOUND"
        echo "$text" | head -5
      fi
    done
    ```
    Setelah halaman ditemukan, ekstrak range: `pdftotext -f <found_page> -l <found_page+6>`. Untuk menemukan akhir section, cari halaman dengan watermark domain atau marker pemisah chapter berikutnya. Teknik ini jauh lebih andal daripada full-text grep untuk section di akhir buku.

22. **RAG chunk density terlalu rendah untuk chapter-level queries.** Buku dengan banyak halaman tapi sedikit chunk karena ukuran chunk besar relatif terhadap isi buku (contoh: 9 chunks / 149 halaman = 0.06 chunks/page, seperti edisi Mandarin *The Thinking Machine* oleh Stephen Witt) tidak bisa diandalkan untuk query per-chapter — setiap chunk mencakup ~17 halaman, vector search mengembalikan chunk yang sama untuk query berbeda. **Deteksi di pre-flight (step 1b), bukan setelah batch_query gagal.** Jika ratio < 0.15, langsung ke strategi pdftotext-only:

23. **Omnibus final chunk — kontaminasi universal dari chunk terakhir.** Chunk terakhir sebuah buku (chunk index tertinggi) sering kali menggabungkan Acknowledgments + About the Author + Notes bibliografi menjadi SATU chunk padat. Karena chunk ini mengandung: nama penulis, judul buku, judul semua chapter (dari daftar referensi per-chapter di Notes), nama editor/penerbit/orang yang disebut di Acknowledgments — ia memiliki keyword density yang sangat tinggi dan mencakup istilah dari seluruh buku. Akibatnya, chunk ini muncul di hasil RAG untuk query section MANA PUN, bahkan untuk Author's Note, Introduction, atau chapter awal yang secara fisik jauh darinya. Contoh nyata: buku *Are You Mad at Me?* (Meg Josephson, 160 chunks), chunk #156 (terakhir) muncul di hasil untuk Author's Note, Introduction, Acknowledgments, About the Author, Ch4, Ch10, dan Ch11 — 7 dari 15 query terkontaminasi chunk yang sama. **Deteksi:** setelah batch_query, periksa apakah ada satu chunk index yang muncul di >3 query berbeda — jika iya, itu omnibus final chunk. **Mitigasi:** abaikan chunk tersebut untuk semua section kecuali yang memang relevan (Acknowledgments, About the Author); gunakan pdftotext sebagai sumber primer untuk section depan buku (Author's Note, Introduction) yang paling rentan.

24. **`read_file` truncation untuk konten RAG besar.** Ketika konten RAG per section melebihi ~13K karakter, `read_file` otomatis memotong output (menampilkan "[truncated]"). Ini menyulitkan membaca konten penuh untuk menulis summary. **Workaround:** ekstrak konten ke file terpisah via Python, lalu baca masing-masing:
    ```bash
    python3 -c "
    import json
    with open('rag_output.json', 'r') as f:
        data = json.load(f)
    for key in ['Section1', 'Section2']:
        with open(f'/tmp/{key}.txt', 'w') as out:
            out.write(data[key])
    "
    ```
    Atau baca langsung via `terminal` dengan `python3 -c "print(data['Section1'])"` yang tidak terpotong. Setelah konten ada di file terpisah, `read_file` bisa membacanya tanpa truncation (kecuali masih >100K chars — gunakan offset/limit untuk itu).

25. **Verifikasi klaim otomatis setelah menulis summary.** Setelah menulis ringkasan, jalankan verifikasi terprogram untuk cross-check setiap klaim faktual terhadap teks sumber. Ini menangkap misattribution (klaim dari section X malah ditulis di summary section Y), klaim yang tidak ada di sumber, atau data numerik yang melenceng:
    ```python
    # checks: dict of {label: boolean condition}
    checks = {
        "Drake 1961": "1961" in data["Prologue"] and "Frank Drake" in data["Prologue"],
        "100 civilizations": "hundred" in data["Prologue"],
        # ... dst untuk semua klaim faktual di summary
    }
    for claim, ok in checks.items():
        if not ok:
            print(f"MISSING: {claim}")
    ```
    Pola ini menyelamatkan dari 2 jenis kesalahan umum: (a) klaim dari section lain (misal square-cube law dari AlienPowers ditulis di summary AlienToUs), dan (b) nilai spesifik yang tidak ada di teks sumber (misal "$700M Halloween" padahal teks hanya menyebut "uang untuk hewan peliharaan" tanpa angka). Gunakan setelah menulis summary, sebelum finalisasi.

26. **batch_query.py foreground timeout membuang semua hasil.** Script `batch_query.py` menulis file output HANYA di akhir setelah semua query selesai (tidak ada incremental save per-section). Untuk buku dengan 50+ section, total runtime bisa >600 detik karena setiap query me-load ulang embedding model (~8-10s/query). Jika dijalankan di foreground dengan timeout default (600s), script bisa ter-timeout sebelum selesai — dan **semua hasil hilang** karena file output belum ditulis. **Mitigasi:** untuk buku dengan >30 section, selalu jalankan `batch_query.py` di background:
    ```bash
    terminal(
      command="~/RAG/.venv/bin/python ~/.hermes/skills/book-summary/scripts/batch_query.py 20 queries.json 2>&1",
      background=true,
      notify_on_complete=true,
      timeout=900
    )
    ```
    Gunakan `process(action="poll")` untuk cek progress (line count bertambah per query) atau tunggu notifikasi. Setelah notifikasi, file `batch_results_<ID>.json` siap di cwd. Pola ini mencegah total work loss akibat timeout. Jika foreground timeout tetap terjadi dan file belum ditulis, JANGAN ulang semua — buat file queries sisa (section yang belum selesai) dan jalankan hanya sisa tersebut, lalu merge hasilnya dengan Python.

27. **`rag.py index` silent ID collision — batch_query mengembalikan buku yang salah.** `rag.py index` menampilkan pesan sukses (`✅ Indexed [N] «JUDUL» — X chunks`), tetapi ID N mungkin sudah memiliki koleksi ChromaDB untuk buku yang berbeda. Akibatnya, `batch_query` mengembalikan chunk dari buku lain — tanpa error atau peringatan sama sekali. Root cause: index_state.json dan ChromaDB bisa tidak sinkron (entry ada di ChromaDB tapi tidak di index_state, atau sebaliknya). Contoh nyata: `rag.py index` melaporkan "Indexed [22] «ALSO BY MICHAEL POLLAN» — 242 chunks" tetapi ChromaDB `rag_book_22` masih berisi 577 chunk Revolusi. `batch_query` terhadap [22] mengembalikan teks tentang kemerdekaan Indonesia, bukan tentang sains kesadaran. **Deteksi:** setelah indexing, selalu verifikasi dengan step 1a. Jalankan `rag.py list` dan pastikan judul + chunk count sesuai ekspektasi. Jika mencurigakan (judul tidak cocok, chunk count berbeda dari yang dilaporkan saat index), cek ChromaDB langsung:
    ```bash
    cd ~/RAG && .venv/bin/python -c "
    import chromadb
    client = chromadb.PersistentClient(path='./chroma_db')
    col = client.get_collection('rag_book_<N>')
    results = col.get(limit=3, include=['documents','metadatas'])
    for doc, meta in zip(results['documents'], results['metadatas']):
        print(doc[:200])
        print('---')
    print(f'Total: {col.count()} chunks')
    "
    ```
    Jika konten tidak sesuai buku yang baru di-index: **index ulang**. `rag.py index` akan otomatis memilih ID berikutnya yang benar-benar kosong (contoh: dari [22] ke [23]). Jangan lanjutkan dengan ID yang salah — seluruh alur batch_query akan terbuang.

28. **Subagent hallucination — delegate_task menulis konten dari buku yang salah.** Ketika subagent diberi tugas membaca section via `sed` line ranges dari full text dan menulis summary, subagent dapat secara diam-diam *(silently)* menulis konten dari buku yang berbeda — sementara self-report (verbal summary di hasil delegate_task) mendeskripsikan konten yang benar. Contoh nyata: subagent ditugaskan membaca Ch8–About the Author dari *You've Changed* (Denizet-Lewis), self-report menyebutkan "Epilogue tentang Dennis Lewis di La-Z-Boy" dan "495 endnotes" — tetapi file yang ditulis berisi "Coda: The Cave" tentang Michael Pollan dan "Acknowledgments" untuk Ann Godoff dari Penguin Press. **Root cause:** subagent tidak memiliki memory sesi — prompt awalnya mungkin terpapar residual context dari buku sebelumnya, atau model mencampur pengetahuan dari training data. **Deteksi & mitigasi:**
    - Setelah semua subagent selesai, **verifikasi setiap output file** sebelum merge. Baca 3-5 baris pertama setiap file untuk memastikan proper names, judul section, dan konsep kunci cocok dengan buku target.
    - Dalam prompt subagent, sebutkan judul buku lengkap DAN nama penulis di awal konteks (bukan hanya di goal).
    - Jika subagent timeout atau output mencurigakan, jangan pakai hasilnya — tulis ulang section tersebut secara langsung oleh parent agent.

30. **Scanned PDF — pdftotext fallback tidak berfungsi, gunakan OCR output.** Buku scanned (image-only, 0 karakter teks terekstrak) memerlukan OCR via `read-book` skill sebelum indexing. Namun setelah RAG indexing dan deteksi kontaminasi, **strategi fallback `pdftotext ~/RAG/books/<file>.pdf /tmp/fullbook.txt` TIDAK BEKERJA** karena source PDF tidak punya teks terekstrak. Sumber teks fallback yang benar adalah **file OCR markdown** (output dari `ocr_scanned_pdf.py`, format `## Page N`). Adaptasi strategi fallback untuk scanned books:\n    1. Gunakan file OCR markdown (mis. `/tmp/etika-jawa-ocr.md`) sebagai full text — bukan hasil pdftotext\n    2. Petakan chapter boundaries menggunakan `## Page N` markers (bukan grep ALL-CAPS)\n    3. Subagent membaca konten dengan `read_file` (offset/limit) terhadap file OCR markdown, bukan `sed`\n    4. File OCR mungkin punya gap (halaman yang gagal OCR dengan `[OCR error: ...]`) — subagent harus membaca halaman sebelum dan sesudah gap untuk merekonstruksi konten\n    5. Sisanya sama: 3 subagent paralel, merge dengan `cat`, copy ke SMB\n    Contoh nyata: *Etika Jawa* (274 hlm scanned, 0 teks) — setelah OCR 569K karakter, indexing ke RAG, batch_query kontaminasi 78%, fallback ke file OCR markdown (11.837 baris) dengan 3 subagent membaca via `read_file`. Hasil: 9 section summary bersih dari kontaminasi.\n\n29. **Jangan gunakan `execute_code` untuk merge file summary — pakai `cat` di terminal.** Execute_code berjalan dalam sandbox dengan filesystem terisolasi. `write_file` dari dalam execute_code dapat menulis ke lokasi berbeda dari yang diharapkan, dan `read_file` dari dalam execute_code menambahkan prefix nomor baris (`"     1|content"`) yang mencemari konten. Akibat nyata: file summary_part1.md dan summary_part2.md hilang setelah operasi merge via execute_code, dan konten yang tersisa memiliki line numbers yang rusak. **Selalu merge dengan `cat` di terminal:**
    ```bash
    cat /tmp/header.md /tmp/summary_part1.md /tmp/summary_part2.md /tmp/summary_part3.md > /tmp/summary-final.md
    ```
    Lalu copy ke direktori output dengan `sudo cp` jika diperlukan. `rag.py index` menampilkan pesan sukses (`✅ Indexed [N] «JUDUL» — X chunks`), tetapi ID N mungkin sudah memiliki koleksi ChromaDB untuk buku yang berbeda. Akibatnya, `batch_query` mengembalikan chunk dari buku lain — tanpa error atau peringatan sama sekali. Root cause: index_state.json dan ChromaDB bisa tidak sinkron (entry ada di ChromaDB tapi tidak di index_state, atau sebaliknya). Contoh nyata: `rag.py index` melaporkan "Indexed [22] «ALSO BY MICHAEL POLLAN» — 242 chunks" tetapi ChromaDB `rag_book_22` masih berisi 577 chunk Revolusi. `batch_query` terhadap [22] mengembalikan teks tentang kemerdekaan Indonesia, bukan tentang sains kesadaran. **Deteksi:** setelah indexing, selalu verifikasi dengan step 1a. Jalankan `rag.py list` dan pastikan judul + chunk count sesuai ekspektasi. Jika mencurigakan (judul tidak cocok, chunk count berbeda dari yang dilaporkan saat index), cek ChromaDB langsung:
    ```bash
    cd ~/RAG && .venv/bin/python -c "
    import chromadb
    client = chromadb.PersistentClient(path='./chroma_db')
    col = client.get_collection('rag_book_<N>')
    results = col.get(limit=3, include=['documents','metadatas'])
    for doc, meta in zip(results['documents'], results['metadatas']):
        print(doc[:200])
        print('---')
    print(f'Total: {col.count()} chunks')
    "
    ```
    Jika konten tidak sesuai buku yang baru di-index: **index ulang**. `rag.py index` akan otomatis memilih ID berikutnya yang benar-benar kosong (contoh: dari [22] ke [23]). Jangan lanjutkan dengan ID yang salah — seluruh alur batch_query akan terbuang.

## Referensi

Lihat `references/` untuk:
- `references/format-example.md` — contoh struktur file output
- `references/deep-dive-qa-example.md` — contoh output Q&A filosofis terstruktur dengan citation asli
- `references/rag-contamination-analysis.md` — cara mendeteksi dan mengukur kontaminasi chunk RAG per section, dengan tabel kontaminasi real-world dari The Gay Science
- `references/rag-performance.md` — detail teknis RAG, ChromaDB, model embedding
- `references/summa-theologica-structure.md` — structural map of Summa Theologica (9.453 halaman), contoh nyata teknik full-text grep untuk PDF tanpa page numbers
- `references/non-english-books.md` — strategi spesifik untuk buku berbahasa non-Inggris (Jerman, Prancis, Belanda, dll): query dalam bahasa asli, mitigasi kontaminasi lintas-bahasa, kapan fallback ke pdftotext langsung
- `references/direct-pdftotext-delegation.md` — strategi anti-kontaminasi untuk buku akademik: lewati RAG sepenuhnya, baca langsung dari full-text via pdftotext + sed + delegate_task paralel
- `references/epilogue-contamination-case-study.md` — studi kasus kontaminasi 100% pada Epilogue (*Nexus*, Harari): analisis chunk-by-chunk, root cause, dan teknik page-by-page pdftotext search

## Arsitektur Lengkap

Untuk arsitektur menyeluruh dari sistem baca buku (termasuk bagaimana book-summary cocok dalam pipeline end-to-end dari PDF → podcast), lihat:

- `/home/ubuntu/github/notes/books-skill.md` — architecture doc komprehensif
- Referensi `end-to-end-workflow.md` di skill `rag` — ringkasan pipeline 5 fase

## Scripts

- `scripts/batch_query.py` — parameterized: `batch_query.py <book_id> <queries.json>`. Load model sekali, query N chapter, output `batch_results_<book_id>.json`
- `scripts/extract_chapter_texts.py` — parameterized: `extract_chapter_texts.py <results.json> [chapter_map.json]`. Bersihkan dan kondensasi output RAG per chapter ke stdout
- `scripts/md2phone-pdf.py` — konversi markdown summary ke A5 PDF (hape-friendly) via weasyprint + Noto Sans. `~/RAG/.venv/bin/python md2phone-pdf.py input.md [output.pdf]` (gunakan RAG venv karena weasyprint terinstal di sana)
