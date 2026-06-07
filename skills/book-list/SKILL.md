---
name: book-list
description: Use when the user wants to see all indexed RAG books with their IDs.
version: 1.1.0
author: AMBER (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [rag, list, books]
    related_skills: [rag]
---

# book-list

The user wants to see all indexed books in the RAG system.

## Overview

Lists every indexed book with its ID, chunk count, and auto-extracted title. Useful before opening a book for discussion or generating a summary.

## Action

Run:

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py list
```

Display the output. Stay in normal agent mode — do NOT enter RAG mode.

## Pitfalls

1. **Auto-extracted titles may be wrong.** `rag.py` extracts the title from the first line of PDF text, which can be a watermark domain, copyright notice, or random word. If a title looks suspicious (not a real book name), cross-reference with `~/RAG/index_state.json` to see the source filename, and fix the title manually if needed.

2. **No books indexed yet.** If `rag.py list` returns empty, remind the user they can index a PDF by invoking `read-book` or running `rag.py index /path/to/book.pdf` directly.
