---
name: close-book
description: Use when the user wants to exit RAG mode and return to normal agent behavior.
version: 1.0.0
author: AMBER (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [rag, close, exit]
    related_skills: [rag]
---

# close-book

The user wants to exit RAG mode.

## Action

Clear `rag_open_books`. Confirm to the user that RAG mode is closed.

Return to normal agent mode. Do NOT process any more book queries unless the user explicitly invokes `read-book`, `book-list`, or `open-book` again.