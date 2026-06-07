# Hermes Agent Books

**RAG-powered book companion skills for Hermes Agent.** Index PDFs, query books with natural language, and generate chapter-by-chapter summaries — all locally, no API keys needed.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Hermes Agent](https://img.shields.io/badge/Hermes%20Agent-%3E%3D0.13.0-blue)](https://hermes-agent.nousresearch.com)
[![Skills](https://img.shields.io/badge/Skills-5-green)]()

---

## What's Included

| Skill | What it does |
|-------|-------------|
| `read-book` | Index a PDF into the RAG system. Handles scanned PDFs (OCR via Tesseract). Works with any PDF source — local files, downloads, or platform attachments — each agent defines its own source handling locally. |
| `book-list` | List all indexed books with ID, title, and chunk counts. |
| `open-book` | Enter RAG mode — ask natural-language questions across one or more books. |
| `close-book` | Exit RAG mode, return to normal agent behavior. |
| `book-summary` | Generate per-chapter summaries (Bahasa Indonesia or English). Outputs to `.md` files. Supports batch querying for large books, parallel subagent delegation, and fallback strategies for contaminated RAG results. |

Plus the **RAG backend** (`rag.py`) — a standalone CLI for PDF indexing, chunking, embedding, and vector search using sentence-transformers and ChromaDB.

---

## Prerequisites

- **Hermes Agent** ≥ 0.13.0 ([install guide](https://hermes-agent.nousresearch.com/docs))
- **Python 3.10+**
- **~2 GB disk space** (for embedding model + venv + dependencies)
- **Internet** on first run (embedding model auto-downloads)

---
## Installation

**One-command install** — clone and run the installer:

```bash
git clone https://github.com/aleadr/hermes-agent-books.git /tmp/hermes-agent-books && \
  cd /tmp/hermes-agent-books && \
  chmod +x install.sh && \
  ./install.sh && \
  rm -rf /tmp/hermes-agent-books
```

Or step-by-step:

```bash
git clone https://github.com/aleadr/hermes-agent-books.git
cd hermes-agent-books
chmod +x install.sh
./install.sh
```

**After install, register with Hermes Agent** so skills are discoverable:

```bash
hermes skills tap add https://github.com/aleadr/hermes-agent-books
```

Verify:

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py list   # Should show "No books indexed yet"
ls ~/.hermes/skills/read-book/SKILL.md      # Should exist
```

The installer:
1. Creates `~/RAG/` with a Python virtual environment
2. Installs dependencies: `chromadb`, `sentence-transformers`, `pymupdf`
3. Copies `rag.py` to `~/RAG/`
4. Copies all 5 skills to `~/.hermes/skills/`

**For AI agents:** When a user says `install https://github.com/aleadr/hermes-agent-books`, execute the one-command install above, then run `hermes skills tap add https://github.com/aleadr/hermes-agent-books`, then verify with both verification commands. Report back what was installed and whether verification passed.

---

## Quick Start

### 1. Index a book

Place a PDF anywhere accessible and invoke `read-book`. The agent will locate and index it:

```
read-book
```

Or directly from the terminal:

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py index /path/to/book.pdf
```

The first run downloads the embedding model (~420 MB, cached locally).

### 2. See your library

```
book-list
```

Or:

```bash
~/RAG/.venv/bin/python ~/RAG/rag.py list
```

### 3. Chat with a book

```
open-book 3,7
```

Then ask anything:

> "What are the main 16 personality types described in the book?"
>
> "How does the alignment problem relate to reinforcement learning?"

### 4. Generate summaries

```
book-summary 7
```

Creates a `summary-{title}.md` file with one paragraph per chapter.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Hermes Agent                    │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐  │
│  │read-book │ │book-list │ │book-summary │  │
│  │open-book │ │close-book│ │   (5 total) │  │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘  │
│       │             │              │         │
│       └─────────────┼──────────────┘         │
│                     ▼                        │
│              ~/RAG/rag.py                    │
│         ┌──────────┴──────────┐              │
│         │  sentence-          │              │
│         │  transformers       │              │
│         │  (MiniLM-L12-v2)    │              │
│         └──────────┬──────────┘              │
│                    ▼                         │
│         ┌─────────────────────┐              │
│         │     ChromaDB        │              │
│         │  (vector store)     │              │
│         └─────────────────────┘              │
└─────────────────────────────────────────────┘
```

**Key design decisions:**

- **Fully local** — No API keys, no cloud services. Embeddings and vector search run on your machine.
- **Multilingual embedding** — Uses `paraphrase-multilingual-MiniLM-L12-v2`, works well with English, Indonesian, German, French, and 50+ languages.
- **On-demand retrieval** — Books are never loaded into context permanently. Chunks are fetched only when you query.
- **Chunking:** 500 words per chunk, 100-word overlap.
- **Top-K:** 5 most relevant chunks per query per book.

---

## PDF Sources

`read-book` is designed to be source-agnostic. The skill provides the core indexing pipeline; each agent on each machine builds its own local skills and memory for where to find PDFs (local filesystem, network shares, web downloads, platform caches, etc.).

Common patterns agents may implement locally:

- **Local files** — Index any PDF by absolute or relative path.
- **Web URLs** — Download from a direct PDF link, then index.
- **Platform caches** — Check the agent's platform cache directory for recently shared files.
- **Network shares** — Mount and copy from a NAS or file server.
- **Scanned books** — OCR via Tesseract before indexing (built into the skill).

---

## Book Summarization Details

`book-summary` handles complex books with a multi-stage pipeline:

1. **Pre-flight check** — Assesses chunk density; if too sparse, falls back to direct PDF extraction.
2. **TOC extraction** — Uses `pdftotext` (not RAG) for accurate table of contents.
3. **Batch query** — Queries all chapters in one process (model loads once, not per chapter).
4. **Contamination detection** — Identifies Notes/Bibliography contamination, omnibus chunk pollution, and cross-section thematic overlap.
5. **Automatic fallback** — When RAG fails, switches to direct `pdftotext` + `delegate_task` parallel extraction.

See the skill's `references/` directory for detailed case studies and anti-contamination strategies.

---

## File Locations

| Path | Purpose |
|------|---------|
| `~/RAG/rag.py` | RAG CLI |
| `~/RAG/books/` | Source PDFs (copied on index) |
| `~/RAG/chroma_db/` | ChromaDB vector store |
| `~/RAG/index_state.json` | Book metadata (titles, chunk counts, filenames) |
| `~/.hermes/skills/read-book/` | read-book skill |
| `~/.hermes/skills/book-summary/` | book-summary skill + scripts |
| `~/.hermes/skills/book-list/` | book-list skill |
| `~/.hermes/skills/open-book/` | open-book skill |
| `~/.hermes/skills/close-book/` | close-book skill |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| First query takes long | Embedding model is downloading (~420 MB). This happens once. |
| `Permission denied` on `rag.py` | `chmod +x ~/RAG/rag.py` |
| `ModuleNotFoundError: sentence_transformers` | Run install.sh again, or: `~/RAG/.venv/bin/pip install -r requirements.txt` |
| Wrong book title after index | Edit `~/RAG/index_state.json` — some PDFs have watermarks as first line. |
| Book has 0 chunks | The PDF is likely scanned (image-only). Use OCR fallback in `read-book`. |
| RAG query timeout | Run `rag.py query` with a longer timeout, or fall back to `pdftotext` directly. |

---

## Contributing

These skills evolve with real-world use. If you encounter edge cases (unusual PDF formats, multi-language books, contamination patterns), open an issue or PR.

---

## License

MIT — use freely, modify, share.
