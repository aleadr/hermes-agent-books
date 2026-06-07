---
name: book-list
description: Use when the user wants to see all indexed RAG books with their IDs.
version: 1.0.0
author: AMBER (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [rag, list, books]
    related_skills: [rag]
---

# book-list

The user wants to see all indexed books in the RAG system.

## Action

Run:

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py list
```

Display the output. Stay in normal agent mode — do NOT enter RAG mode.