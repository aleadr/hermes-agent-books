#!/usr/bin/env python3
"""
Batch query RAG for ALL sections of a book.
Loads embedding model ONCE, queries N sections, saves structured results.

USAGE:
  python batch_query.py <book_id> <queries.json>

  queries.json format:
  [
    {"id": "Preface", "query": "Full content of the introduction: main topics and arguments"},
    {"id": "Ch1",     "query": "Chapter 1: full content, main arguments, key examples"},
    {"id": "Ch2",     "query": "Chapter 2: full content..."},
    ...
  ]

  Section IDs (id field) are arbitrary labels used by extract_chapter_texts.py
  to match against its chapter map. Convention:
    "Preface/Introduction" for preface/intro
    "Ch1", "Ch2", ... "ChN" for numbered chapters
    "Notes" for appendix/endnotes
    Custom IDs for non-standard structures (Book I, Part 1, etc.)

OUTPUT:
  batch_results_<book_id>.json  — written to current working directory

EXAMPLE:
  # 1. Create queries-book-5.json for book ID 5
  # 2. Run from ~/RAG/ or any working directory:
  python ~/.hermes/skills/book-summary/scripts/batch_query.py 5 queries-book-5.json
"""
import sys
import json
import os
from pathlib import Path

RAG_HOME = Path(os.environ.get("RAG_HOME", Path.home() / "RAG"))
sys.path.insert(0, str(RAG_HOME))

import importlib.util
spec = importlib.util.spec_from_file_location("rag", RAG_HOME / "rag.py")
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)


# ── Args ────────────────────────────────────────────────────────────────
if len(sys.argv) < 3:
    print(__doc__, file=sys.stderr)
    sys.exit(1)

try:
    book_id = int(sys.argv[1])
except ValueError:
    print(f"ERROR: book_id must be an integer, got: {sys.argv[1]}", file=sys.stderr)
    sys.exit(1)

queries_path = Path(sys.argv[2])
if not queries_path.exists():
    print(f"ERROR: queries file not found: {queries_path}", file=sys.stderr)
    sys.exit(1)

queries = json.loads(queries_path.read_text())
if not isinstance(queries, list) or not queries:
    print(f"ERROR: queries file must contain a non-empty JSON array", file=sys.stderr)
    sys.exit(1)

# ── Load model ONCE ─────────────────────────────────────────────────────
print("Loading model...", file=sys.stderr)
model = rag.get_model()
chroma = rag.get_chroma()
state = rag.load_state()

book_key = str(book_id)
if book_key not in state:
    print(f"ERROR: Book [{book_id}] not found in index.", file=sys.stderr)
    print(f"Available: {', '.join(sorted(state.keys(), key=int))}", file=sys.stderr)
    sys.exit(1)

print(f"Model loaded. Book [{book_id}]: {state[book_key]['title']}", file=sys.stderr)

# ── Query all sections ──────────────────────────────────────────────────
results = []
for item in queries:
    section_id = item["id"]
    question = item["query"]
    print(f"  [{section_id}] Querying...", file=sys.stderr)
    try:
        chunks = rag.query(question, book_ids=[book_id])
        results.append({"section": section_id, "chunks": chunks})
    except Exception as e:
        print(f"  [{section_id}] ERROR: {e}", file=sys.stderr)
        results.append({"section": section_id, "chunks": []})

# ── Output ──────────────────────────────────────────────────────────────
output_file = Path.cwd() / f"batch_results_{book_id}.json"
output_file.write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"\n✅ Saved to {output_file} ({output_file.stat().st_size} bytes)", file=sys.stderr)
