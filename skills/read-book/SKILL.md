---
name: read-book
description: "Use when the user wants to index a PDF into the RAG system. Core pipeline: locate the PDF → verify it has extractable text → index via rag.py → report. Each agent builds its own local skills for finding PDFs (filesystem, network, web, platform caches)."
version: 2.0.0
author: AMBER (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [rag, pdf, index]
    related_skills: [rag]
---

# read-book

The user has invoked `read-book`. They want a PDF indexed into the RAG system for querying and summarization.

## Overview

`read-book` provides the full indexing pipeline: locate a PDF → verify it's a real book → run `rag.py index` → verify the result → report. It also handles scanned/image-only PDFs via OCR (Tesseract). Each agent builds its own local skills for finding PDFs (filesystem, network, web, platform caches).

## Core Principle

This skill provides the **indexing pipeline** only. How the PDF is obtained (local path, download, platform attachment, network share) is left to each agent to handle based on its local context, memory, and companion skills.

**The agent should:**
1. Determine where the PDF is (check local files, platform caches, ask user if needed)
2. Copy it to a known path (e.g. `/tmp/<filename>.pdf`)
3. Verify it's a real book PDF, not a preview or watermark-only file
4. Run `rag.py index`
5. Report the result

## Workflow

### Step 1: Locate the PDF

The PDF might be:

- **Already on disk** — user mentions a path or filename
- **In a platform cache** — check the agent's document cache directory (e.g. `~/.hermes/cache/documents/`)
- **At a URL** — user provides a link; download with `curl -L -o /tmp/<filename>.pdf "<url>"`
- **On a network share** — mount and copy if the agent has access

If uncertain, ask the user for the PDF location or a download link.

### Step 2: Pre-index verification (MANDATORY)

Before indexing, preview the PDF to catch common issues:

```bash
# Check page count and file size
pdfinfo /tmp/<filename>.pdf | grep Pages
ls -la /tmp/<filename>.pdf

# Check the first text line (watermark detection)
pdftotext -f 1 -l 1 /tmp/<filename>.pdf - | head -5
```

**Red flags:**
- **4 pages / ~270 KB** → likely a preview/sample, not the full book. Ask user for the full version.
- **First line is a website name** → the RAG title will be wrong. Fix after indexing (see pitfalls below).
- **File is <100 KB** → likely not a real book.
- **First line is blank or copyright notice** → the auto-extracted title will be wrong. Note the real title for fixing after index.

### Step 3: Index

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py index /tmp/<filename>.pdf
```

If the output says `ERROR: No extractable text in PDF (maybe scanned image?)`, the PDF is image-only — go to the Scanned PDF section below.

### Step 4: Verify index result (MANDATORY)

`rag.py index` reports success, but the ID may have stale ChromaDB data from a previous book. Always verify:

```bash
# Check the list
~/RAG/.venv/bin/python ~/RAG/rag.py list | grep "<new_id>"

# Verify title and chunk count in state
python3 -c "
import json
s = json.load(open('$HOME/RAG/index_state.json'))
v = s['<ID>']
print(f'Title: {v[\"title\"]}, Chunks: {v[\"chunks\"]}, File: {v[\"filename\"]}')
"
```

If the title is wrong (watermark, copyright line, etc.), fix it immediately — see pitfall #1.

### Step 5: Report

Always report: book ID, title, chunk count, and confirmation the book is ready to query.

---

## Scanned PDF (image-only, no embedded text)

If `rag.py index` returns `ERROR: No extractable text in PDF (maybe scanned image?)`:

1. **Ask first** — before attempting OCR, ask the user if they have a text version (non-scanned) of the same PDF. Users often have a text edition available from another source, which saves the entire OCR step.

2. **Detect** — verify it's scanned:
   ```bash
   python3 -c "
import pymupdf
doc = pymupdf.open('/tmp/<filename>')
print(f'Pages: {len(doc)}')
text = sum(len(page.get_text()) for page in doc)
print(f'Total text: {text} chars')
   ```
   Zero or near-zero chars = scanned image PDF.

3. **Choose OCR approach:**

   | Tool | When to use |
   |------|-------------|
   | **tesseract** (pymupdf + tesseract-ocr) | **Default.** Lightweight, fast on CPU. ~220 pages in ~2-3 min. |
   | **marker-pdf** | Complex layouts, equations, multilingual. Needs ~3-5GB for models. Slow on CPU (~10+ min for 220pp). |

4. **Determine book language** — before OCR, identify the book's primary language from title/author/first page. Install the corresponding tesseract language pack:
   ```bash
   sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
   sudo apt-get install -y tesseract-ocr-ind   # example: Indonesian
   ```

5. **Run OCR** using the bundled script:
   ```bash
   # English only (default)
   python3 -u ~/.hermes/skills/read-book/scripts/ocr_scanned_pdf.py /tmp/<filename> /tmp/output.md
   # Indonesian + English
   python3 -u ~/.hermes/skills/read-book/scripts/ocr_scanned_pdf.py /tmp/<filename> /tmp/output.md eng+ind
   ```

6. **Convert to searchable PDF and index:**
   ```bash
   ~/.hermes/skills/read-book/scripts/create_searchable_pdf.py /tmp/ocr_output.md
   ~/RAG/.venv/bin/python ~/RAG/rag.py index /tmp/ocr_output-searchable.pdf
   ```

   ⚠️ **Post-OCR title is "Page 1":** The generated searchable PDF's first text line will be "Page 1". Fix by editing `~/RAG/index_state.json`:
   ```bash
   python3 -c "
import json
s = json.load(open('$HOME/RAG/index_state.json'))
ids = sorted(int(k) for k in s)
s[str(ids[-1])]['title'] = 'Actual Book Title'
open('$HOME/RAG/index_state.json','w').write(json.dumps(s, indent=2, ensure_ascii=False))
   "
   ```

---

## Pitfalls

1. **Wrong book title after index.** `rag.py` extracts the title from `lines[0].strip()` — the first line of text in the PDF. This can be:
   - A watermark or website name
   - Copyright notice
   - A random word from the body text (when cover page is blank)
   - The first chapter's title
   
   **Mitigation:** Always preview with `pdftotext -f 1 -l 1` before indexing. If the title is wrong after indexing, fix via:
   ```bash
   python3 -c "
import json
s = json.load(open('$HOME/RAG/index_state.json'))
s['<ID>']['title'] = 'Correct Book Title'
open('$HOME/RAG/index_state.json','w').write(json.dumps(s, indent=2, ensure_ascii=False))
   "
   ```

2. **Duplicate indexing.** Running `rag.py index` on the same PDF again creates a new ID with duplicate ChromaDB data. Before indexing, check if the PDF is already indexed:
   ```bash
   python3 -c "
import json
s = json.load(open('$HOME/RAG/index_state.json'))
[print(f'ID {k}: {v[\"filename\"]}') for k,v in s.items()]
   "
   ```
   If the filename already exists, use the existing ID.

3. **Fake preview instead of full book.** Some download sites return a promotional page (~4 pages, ~270 KB) instead of the actual book. Always verify: real books are 100+ pages and multiple MB.

4. **OCR language mismatch.** Non-English books need the correct tesseract language pack. OCR with wrong language = poor quality output.

5. **ChromaDB ID collision.** `rag.py index` may report success for an ID that already has data from a different book. Root cause: `index_state.json` and ChromaDB can be out of sync. Always verify with step 4 after indexing. If the title or chunk count doesn't match expectations, run `rag.py index` again — it will use the next available clean ID.
