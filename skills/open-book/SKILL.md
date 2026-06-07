---
name: open-book
description: Use when the user wants to enter RAG mode and discuss specific indexed books. Open the books by ID.
version: 1.0.0
author: AMBER (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [rag, open, discuss]
    related_skills: [rag]
---

# open-book

The user wants to enter RAG mode and discuss specific books.

## Action

Parse the book IDs from the user's message (e.g., "0,2"). Remember these IDs as `rag_open_books`. Confirm to the user which books are now open.

Enter RAG mode. All subsequent natural-language questions from the user will automatically query these open books via:

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py query "<question>" --books <ids>
```

Only exit RAG mode when the user says `close-book`.

## Pitfalls

- The `rag.py query` command can be slow and may timeout on the search step. If it fails after a generous timeout (≥60s), fall back to extracting text directly from the source PDF in `~/RAG/books/` using `pdftotext`.