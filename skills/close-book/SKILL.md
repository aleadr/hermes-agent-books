---
name: close-book
description: Use when the user wants to exit RAG mode and return to normal agent behavior.
version: 1.1.0
author: AMBER (Hermes Agent)
license: MIT
metadata:
  hermes:
    tags: [rag, close, exit]
    related_skills: [rag]
---

# close-book

The user wants to exit RAG mode.

## Overview

Clears the active RAG book selection and returns the agent to normal operation. After closing, book-related queries are no longer routed through the vector database.

## Action

Clear `rag_open_books`. Confirm to the user that RAG mode is closed.

Return to normal agent mode. Do NOT process any more book queries unless the user explicitly invokes `read-book`, `book-list`, or `open-book` again.

## Pitfalls

1. **User mentions a book name after close.** If the user says a book title casually after closing, do NOT re-enter RAG mode unless they explicitly invoke `open-book`. A passing mention is not a command.
