# Epilogue Contamination Case Study: Nexus (Harari)

## Context

Book: *Nexus: A Brief History of Information Networks from the Stone Age to AI* by Yuval Noah Harari
- 533 pages, 436 RAG chunks, Book ID 15
- Structure: Prologue → Ch 1-11 (across 3 Parts) → Epilogue → Acknowledgements → Notes (~160pp) → Index

## Batch Query Results — Epilogue Section

Query: "Epilogue: Harari's concluding arguments and warnings, his vision for the future of information networks, any proposed solutions or calls to action, final reflections on the relationship between information, power, and wisdom"

**Result: 0/5 useful chunks (100% contamination)**

| Chunk | Actual Source | Content |
|-------|--------------|---------|
| 1 | Front matter (praise page) | "first word to the last … It may be the best book I've ever read" — book blurbs |
| 2 | Chapter 10 body | "CHAPTER 10 Totalitarianism: All Power to the Algorithms?" — wrong chapter |
| 3 | Notes section | "Tonia Sharlach, 'Princely Employments in the Reign of Shulgi', Journal of Ancient Near Eastern History 9, no. 1 (2022): 1–68" — endnote |
| 4 | Chapter 11 conclusion (overlap) | "common but misleading approaches to information networks..." — actually from Epilogue body, but embedded in Ch11 context |
| 5 | Chapter 4 body | "all possibility of error. What happens when an information network believes itself to be utterly incapable of any error?" — wrong chapter |

## Root Cause

1. **Physical adjacency**: Epilogue body (pages 368-373) sits right before Notes (pages 375-530+). The embedding batches cover page ranges that straddle this boundary.
2. **Thematic overlap**: Epilogue recapitulates themes, proper names, and concepts from the entire book — the same ones that appear in dense citation format in Notes.
3. **BM25/keyword bias**: Notes pages are dense with proper names, journal titles, and years — these create stronger BM25 matches than narrative prose.
4. **Vector similarity confusion**: The Epilogue's big-picture philosophical language matches the front matter (praise pages, "About the Author") which uses similar "grand" vocabulary.

## Acknowledgements Section — Partial Contamination

Query for Acknowledgements: **2/5 useful chunks (60% contamination)**

| Chunk | Actual Source |
|-------|--------------|
| 1 | Real Acknowledgements body ✓ |
| 2 | "About the Author" page |
| 3 | Real Acknowledgements body ✓ |
| 4 | Notes section |
| 5 | Front matter (praise page) |

## Resolution

Used **page-by-page pdftotext search** to locate the Epilogue body:

```bash
for p in $(seq 350 400); do
  text=$(pdftotext -f $p -l $p ~/RAG/books/Nexus_-_Yuval_Noah_Harari.pdf - 2>/dev/null)
  if echo "$text" | grep -qi "epilogue\|acknowledgement"; then
    echo "Page $p: FOUND"
    echo "$text" | head -5
  fi
done
```

Epilogue body found at pages 368-373. Acknowledgements at pages 374-377. Extracted with:
```bash
pdftotext -f 368 -l 374 ~/RAG/books/Nexus_-_Yuval_Noah_Harari.pdf -
```

## Generalizable Pattern

**Any book with extensive endnotes (50+ pages) will have this problem for its final narrative sections.** The pattern applies to:
- Epilogue
- Afterword
- Conclusion
- Postscript
- Appendix (if narrative, not reference)
- Acknowledgements

**Rule of thumb**: If a section appears AFTER the last numbered chapter and BEFORE the Notes/Index, assume 100% RAG contamination. Go directly to pdftotext.
