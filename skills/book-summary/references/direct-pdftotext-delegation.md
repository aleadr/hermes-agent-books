# Direct pdftotext Fallback + Parallel Delegation

Untuk buku akademik dengan kontaminasi Notes/Bibliography tinggi (>50%), RAG batch_query sering mengembalikan chunk dari Notes alih-alih body chapter. Solusi paling efisien: **lewati RAG sama sekali** untuk ekstraksi konten, gunakan pdftotext full-text + sed + delegate_task paralel.

## ⚠️ Buku Scanned / OCR

Untuk buku scanned (image-only PDF): `pdftotext` pada source PDF menghasilkan 0 karakter. Gunakan **file OCR markdown** (output `ocr_scanned_pdf.py`, format `## Page N` markers) sebagai pengganti `pdftotext` output. Cari page marker bukan `\f` marker. Subagent membaca dengan `read_file --offset --limit`, bukan `sed`. Lihat pitfall #30 di SKILL.md untuk resep lengkap.

## Kapan pakai

- Buku akademik dengan >30 halaman endnotes
- Batch_query menunjukkan >50% chunk dari Notes/Bibliography
- Buku dengan proper names/paper titles yang muncul di body dan Notes (kontaminasi tak terhindarkan)

## Workflow

### 1. Export full text sekali

```bash
pdftotext ~/RAG/books/<filename>.pdf /tmp/fullbook.txt
```

### 2. Cari \f markers untuk line number setiap chapter

```bash
grep -n $'\\\\f' /tmp/fullbook.txt | grep -i "chapter\\|introduction\\|notes\\|acknowledgments\\|appendix"
```

Output contoh (dari buku *Democracy, Power, and Legitimacy*):

```
92:\fAcknowledgments
124:\fIntroduction
494:\fChapter 1
892:\fChapter 2
1911:\fChapter 3
2704:\fChapter 4
3439:\fChapter 5
4345:\fChapter 6
5388:\fChapter 7
6279:\fNotes
```

### 3. Tentukan line range setiap chapter

Dari `\fMarkerNext` - 1:

| Chapter | Lines |
|---------|-------|
| Acknowledgments | 92–123 |
| Introduction | 124–493 |
| Chapter 1 | 494–891 |
| Chapter 2 | 892–1910 |
| dst | ... |

### 4. Delegasikan ke subagents paralel (maks 3 per batch)

Setiap task di delegate_task mendapat:
- Tujuan: baca sed range dan tulis ringkasan 1 paragraf
- `toolsets: ["terminal"]`
- Instruksi: `sed -n '<start>,<end>p' /tmp/fullbook.txt`

Contoh task spec:

```json
{
  "goal": "Baca dan buat ringkasan 1 paragraf Bahasa Indonesia untuk Introduction (lines 124-493) dari /tmp/fullbook.txt. Gunakan: sed -n '124,493p' /tmp/fullbook.txt. Ringkasan konkret dari teks asli, tidak halusinasi.",
  "toolsets": ["terminal"]
}
```

### 5. Compile hasil dari semua subagent ke file summary

Gabungkan output dalam urutan yang benar.

## Keuntungan

- **Zero contamination** — tidak ada chunk dari Notes/Bibliography
- **Cepat** — 3 subagents paralel membaca ~1000 line per task
- **Akurat** — ringkasan berdasarkan teks asli, bukan vektor similarity
- **Skalabel** — untuk buku 10+ chapter, 3 batch sudah cukup

## Pendekatan Alternatif: Chapter Title Grep (ketika `\f` terlalu noisy)

Beberapa PDF — terutama dari situs download — menyisipkan watermark domain di SETIAP halaman (dengan `\f` di depannya). Akibatnya, `grep -n $'\\f'` mengembalikan ratusan baris dan tidak berguna untuk menemukan batas chapter. Gunakan pendekatan **judul chapter spesifik**:

### 1. Cari judul chapter dari TOC yang sudah diekstrak

```bash
grep -n "VOC Mentality\|Assembling the Jigsaw\|Colonial Steamship\|Land of the Rising\|Into the Light\|Epilogue$\|Acknowledgements$\|Bibliographical Essay" /tmp/fullbook.txt
```

### 2. Output langsung memberi line number chapter header

```
177:The VOC Mentality
954:Assembling the Jigsaw Puzzle
1904:The Colonial Steamship
...
16791:Epilogue
16893:Acknowledgements
17073:Bibliographical Essay
```

### 3. Map line ranges: [header_line, next_header_line - 1]

Gunakan judul chapter persis seperti yang muncul di body text (bukan TOC). Judul body text MUNGKIN berbeda dari judul TOC — misal TOC menulis "Chapter 1: The VOC Mentality" tapi body text hanya "The VOC Mentality". Selalu verifikasi dengan membaca 2-3 baris setelah line yang ditemukan.

### 4. Prolog biasanya ada di awal file — cek manual

`\fPrologue` atau `Prologue` di awal file. Bisa ditemukan dengan:
```bash
grep -n "^Prologue" /tmp/fullbook.txt
```

### Contoh nyata

Buku *Revolusi* (David Van Reybrouck, 654 hlm, 22.302 baris full text):
- `\f` markers: 44 hits (satu per halaman + watermark domain) — tidak berguna
- Chapter title grep: 18 hits dari 19 chapter — langsung memberikan line numbers akurat
- 3 subagent paralel membaca via `read_file` offset/limit — total ~13 menit untuk 19 section

## Catatan

- Pastikan `/tmp/fullbook.txt` sudah ada sebelum delegate_task dipanggil
- Line numbers dari `grep -n` dengan judul chapter akurat untuk buku yang chapter titles-nya unik
- Jika dua chapter memiliki judul yang sangat mirip, grep mungkin menggabungkan — selalu verifikasi dengan membaca 2-3 baris setelah setiap match
- Untuk buku tanpa `\f` markers (PDF dari HTML), gunakan `grep -n "^Chapter\|^Introduction\|^PART "` sebagai alternatif
- Untuk buku dengan `\f` di setiap halaman (watermark), LEWATI `\f` approach — langsung gunakan chapter title grep
- Subagent tidak perlu tahu tentang RAG — beri mereka path file dan sed command atau offset/limit langsung
