# Hybrid Strategy for Philosophical / Aphoristic Books

Books like Nietzsche's *The Gay Science*, Pascal's *Pensées*, or Wittgenstein's works are structured as collections of aphorisms/sections grouped into larger "Books" or "Parts." Standard RAG vector search performs poorly on these because:

1. Sections are thematically interleaved — a query for "Book Two" may return chunks from Books One or Three
2. The table of contents is a simple list of section titles without descriptive chapter summaries
3. Key concepts (God is dead, eternal recurrence, amor fati) appear across multiple sections
4. **Poetry/Prelude contamination**: Unique vocabulary in interleaved poems matches many queries, causing RAG to return the same poem chunks for ALL section queries

## Strategy

### Step 1: TOC via pdftotext (always)
```bash
# Extract TOC from the PDF directly
pdftotext -f 5 -l 22 ~/RAG/books/<filename>.pdf - 2>/dev/null | head -300
```
Adjust `-f` and `-l` to cover all TOC pages. Note:
- Section names exactly as they appear
- Page numbers for each section start
- Sub-section numbering (e.g., sections 1–56 for Book One)

### Step 2: Determine summary granularity
For aphoristic works, summary granularity should be at the **Book/Part level**, not per-aphorism. E.g., *The Gay Science* has 383 numbered sections but only 5 Books + Preface + Prelude + Appendix = 9 summary entries.

### Step 3: Targeted RAG queries
Construct queries that combine:
- The section's formal title (from TOC)
- Key topics known to be in that section (from TOC sub-items)
- The section's placement context (e.g., "first book after the preface")

Example for Nietzsche Book One:
```
~/RAG/.venv/bin/python ~/RAG/rag.py query "Book One sections 1-56: teachers of purpose of existence, intellectual conscience, morality as illusion" --books 2
```

### Step 4: Verify with pdftotext (PRIMARY SOURCE for aphoristic books)
**For aphoristic books, pdftotext of opening sections is the primary source, not RAG.** Read the first few aphorisms of each Book directly from PDF:

```bash
pdftotext -f <start_page> -l <start_page+5> ~/RAG/books/<filename>.pdf - 2>/dev/null | head -150
```

This confirms the section's actual opening content. For Nietzsche, reading sections 1-5 of Book One, 57-60 of Book Two, 108-115 of Book Three, 276-280 of Book Four, and 343-347 of Book Five gives you the concrete, specific content that RAG cannot reliably return.

### Step 5: Cross-check RAG results
After batch_query, verify chunk source distribution BEFORE writing summaries:
```bash
python3 -c "
import json
results = json.load(open('batch_results_<ID>.json'))
for entry in results: 
    chunks = entry.get('chunks', [])
    # Check where chunks actually come from — identify Prelude/poetry contamination
    for c in chunks[:2]:
        print(f'{entry[\"id\"]} → chunk #{c[\"chunk_id\"]}: {c[\"text\"][:120]}...')
"
```

If chunks mention topics from *other* sections → discard those, query again with more specific terms.
If chunks are from Kaufmann's commentary/notes (common in translated editions) → verify they're relevant to the section, not just tangentially related.

### Step 6: For sections with 0% useful RAG chunks
When a section query returns zero useful chunks (e.g., Book Five of Nietzsche had 0/5 useful — all were from the Prelude or Appendix), **do not** attempt to write summary from RAG alone. Instead:
1. Use pdftotext to read the opening sections directly from PDF
2. Note the specific section numbers and their titles from TOC
3. Write summary based on the pdftotext content
4. Supplement with any cross-section context you have verified

## When to skip RAG entirely

If RAG queries keep returning the same chunks regardless of which section you query (common for very dense, interconnected texts), skip RAG for structure and use it only as a content cross-check. Write summaries based on:
- TOC section titles and page numbers
- Direct pdftotext reading of section openings
- Known themes from the book's established structure

RAG's value in this case is catching quotes or specific details you'd miss, not providing the summary's skeleton.

## Real-World Contamination Example: Nietzsche's The Gay Science

From an actual batch query on book ID [2] (45 total chunks across 9 sections):

| Section | Useful | Total | Rate |
|---------|--------|-------|------|
| Translators-Introduction | 4 | 5 | 80% |
| Nietzsches-Preface | 1 | 5 | 20% |
| Prelude | 1 | 5 | 20% |
| Book One | 1 | 5 | 20% |
| Book Two | 2 | 5 | 40% |
| Book Three | 1 | 5 | 20% |
| Book Four | 1 | 5 | 20% |
| Book Five | **0** | 5 | **0%** |
| Appendix | 3 | 5 | 60% |
| **Overall** | **14** | **45** | **31%** |

**Key observations:**
- Only 31% of chunks genuinely belonged to their labeled section
- Book Five (added in 2nd edition, 1887) had 0% useful — all 5 chunks were from the Prelude, Book Four, or Appendix
- The Prelude poems contaminated ALL section queries because their unique vocabulary (rhymes, short lines) scored high in vector search
- This pattern is predictable for any book with interleaved poetry sections

**Mitigation used successfully:**
- Read opening aphorisms of each Book via pdftotext (sections 1-5, 57-60, 108-115, 276-280, 343-347)
- PDF page ranges used: Book One pdftotext -f 85 -l 93; Book Two pdftotext -f 134 -l 138; Book Three pdftotext -f 180 -l 191; Book Four pdftotext -f 234 -l 240; Book Five pdftotext -f 290 -l 302
- Used RAG chunks only for specific supplemental details (Translator's Introduction, Appendix poems)
- Result: concrete, specific summaries anchored in Nietzsche's actual arguments and imagery
