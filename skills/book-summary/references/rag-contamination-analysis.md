# RAG Contamination Analysis

After running `batch_query.py`, chunks returned for each section may not actually belong to that section. This is called **contamination** and is especially common in:

- **Philosophical/aphoristic books** (Nietzsche, Pascal, Wittgenstein) — vocabulary overlap causes Prelude/poem chunks to match every section query
- **Academic books with heavy endnotes** (The Alignment Problem, etc.) — proper names and paper titles in Notes match the same terms in body chapters
- **Books with dense interconnected themes** — vector similarity returns the same chunks for queries about different sections

## Detection

Check chunk distribution by reading the first few characters of each chunk per section:

```bash
python3 -c "
import json
results = json.load(open('batch_results_<ID>.json'))
for entry in results:
    chunks = entry.get('chunks', [])
    print(f'{entry[\"id\"]}: {len(chunks)} chunks')
    for c in chunks[:3]:
        print(f'  → chunk #{c[\"chunk_id\"]}: {c[\"text\"][:120]}...')
"
```

## Contamination Signatures

| Type | Signature | Common in |
|------|-----------|-----------|
| **Prelude/puisi** | Rhymes, short lines, poetic vocabulary, German/English verse pairs | Nietzsche, philosophical works with poetry |
| **Notes/Bibliography** | "Nature 518, no. 7540 (2015): 529–33", "See Angwin et al.", DOIs, footnote numbers | Academic nonfiction, books with >50pp endnotes |
| **Cross-section overlap** | Same text chunks returned for queries about different sections | Any densely interconnected text |
| **Front/back matter** | Title page, copyright, abbreviations list returned as content | Books where front/back matter is text-heavy |

## Quantification

Count useful chunks per section (chunks whose content genuinely belongs to that section):

```python
# Pseudocode
for each section in results:
    useful = 0
    total = len(section.chunks)
    for chunk in section.chunks:
        if chunk.text contains section's actual content:
            useful += 1
    ratio = useful / total
    # if ratio < 0.5: section needs fallback
    # if ratio == 0.0: must use pdftotext fallback
```

## Fallback Strategy

| Contamination Rate | Action |
|-------------------|--------|
| 0–20% (low) | Use RAG results, cross-check opening via pdftotext |
| 20–50% (moderate) | RAG as supplement, pdftotext openings as primary |
| 50–80% (high) | pdftotext primary for all sections, RAG for quotes only |
| >80% or 0% section | **Skip RAG entirely.** Read all content via pdftotext range-by-range |

## Real-World Example: The Gay Science (Book ID 2)

| Section | Useful/Total | Contamination Source |
|---------|:-----------:|---------------------|
| Translator's Introduction | 4/5 | Front matter mixed |
| Nietzsche's Preface | 1/5 | Translator's Intro, Prelude, Book Three |
| Prelude | 1/5 | Translator's Intro, Appendix, Book Two |
| Book One | 1/5 | Translator's Intro, Book Two |
| Book Two | 2/5 | Translator's Intro, Book Four, Appendix |
| Book Three | 1/5 | Preface, Contents, Appendix |
| Book Four | 1/5 | Appendix, Prelude |
| Book Five | **0/5** | Prelude, Book Four, Appendix |
| Appendix | 3/5 | Translator's Intro, Prelude |
| **Overall** | **14/45 (31%)** | |

Book Five had 0% useful chunks — every returned chunk was from Prelude, Book Four, or Appendix. This is why the fallback strategy exists.
