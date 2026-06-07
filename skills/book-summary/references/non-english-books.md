# Non-English Books: Strategy Guide

This reference covers strategies for generating book summaries for books in languages other than English.

## Use Case: German Books

Based on real session with *Angststillstand: Warum die Meinungsfreiheit schwindet* by Richard David Precht (2025, 220pp, 102 chunks, 13 chapters + Dank + Anmerkungen).

### RAG Query Strategy

1. **Write queries in the book's language (German).** English-language queries can work because the embedding model (all-MiniLM-L6-v2) is multilingual, but they lose key terms that only appear in the original language. Better: write queries in German with topic cues, e.g.:
   - "Kapitel I: Ein beispielloses Phänomen — vollständiger Inhalt, Hauptargumente, Allensbach-Daten, subjektive Meinungsfreiheit"
   - NOT: "Chapter I: A unique phenomenon — full content..."

2. **Include roman numeral chapter numbers.** German non-fiction books commonly use Roman numerals (I, II, III...) rather than "Chapter 1, 2, 3". The actual PDF text uses these, so include them in queries for better matching.

3. **Include key German terms from the TOC** in each query. The more unique German phrases from the chapter title/subtitle you include, the better RAG can distinguish sections.

### Translation to Indonesian

- The summary must be in Indonesian (per book-summary skill rule), meaning you translate the German RAG output into Indonesian.
- For the format: `**Judul asli:**` shows the German title, `**Judul Bahasa Indonesia:**` shows the free translation.
- "Judul Bahasa Indonesia" should be a meaningful translation that preserves the core idea, not a literal word-for-word translation.

### Pitfalls Specific to German Books

1. **Number/date stripping in RAG chunks.** The chunker may strip or redact numbers and years. If the extracted text shows gaps like "im Jahr auf gerade einmal Prozent!" (missing "2023" and "40"), cross-check with pdftotext.

2. **Form feed separators** — German PDFs often use `\f` (form feed) between chapters but may not have explicit "Chapter X:" labels. Verify TOC via pdftotext before trusting RAG chapter boundaries.

3. **First text extraction failure** — The first text-bearing page may be a quote, not the book title. In *Angststillstand*, the first text was "Buch" (from a long quote by Karl-Hermann Flach that starts page 1). The RAG title became "Buch". Fix in index_state.json.

4. **Quotation marks** — German uses „Gänsefüßchen" („...") and »Guillemets« («...»). These may cause encoding issues in RAG output. Verify with pdftotext if rendering seems off.

### When to Fall Back to pdftotext Directly

- If RAG results show >50% Notes/Bibliography contamination (common for academic German books with dense endnotes).
- If the German text has heavy use of complex compound nouns (e.g., "Bund-Länder-Projektgruppe zur Bekämpfung von Hasspostings") that the embedding model doesn't handle well.
- If the book is an essay-style continuous prose (<15 pages total).

## General Non-English Strategy

For any non-English book:

1. **TOC extraction**: `pdftotext -f 5 -l 30` works the same regardless of language. Look for section headers.
2. **RAG queries**: Write in the book's language + include English topic cues for safety: "Kapitel I: Ein beispielloses Phänomen — Warum schwindet die subjektive Meinungsfreiheit? [Chapter about free speech decline, Allensbach survey]"
3. **Verification**: Check 1-2 chunks per section to confirm RAG returned content from the correct language and not contaminating from English-language books in the same RAG collection.
4. **Translation**: Write summary in Indonesian. Do NOT copy-paste RAG output — you are synthesizing from the original language into Indonesian.
