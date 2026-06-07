#!/usr/bin/env python3
"""
Extract and condense RAG batch results per section for summary writing.
Reads batch_results_N.json, outputs condensed text per section to stdout.

USAGE:
  python extract_chapter_texts.py <results_file> [chapter_map.json]

  results_file:  batch_results_<book_id>.json (output from batch_query.py)
  chapter_map.json (optional): maps section IDs to display labels.
    If omitted, displays raw section IDs.

  chapter_map.json format:
  {
    "Preface/Introduction": "Chapter label",
    "Ch1": "Chapter 1: Is this the real life?",
    "Ch2": "Chapter 2: What is the simulation hypothesis?",
    ...
  }

  Use the section IDs that match your queries.json. The labels become the
  headers in the output — you can copy-paste directly into your summary .md.

OUTPUT (stdout):
  For each section in the results file, prints:
    ============================================================
    Chapter label
    ============================================================
    <condensed text excerpt from RAG chunks>

EXAMPLE:
  python ~/.hermes/skills/book-summary/scripts/extract_chapter_texts.py \
    batch_results_5.json chapter_map.json

  # Without chapter map:
  python ~/.hermes/skills/book-summary/scripts/extract_chapter_texts.py \
    batch_results_5.json
"""
import sys
import json
import re
from pathlib import Path


# ── Args ────────────────────────────────────────────────────────────────
if len(sys.argv) < 2:
    print(__doc__, file=sys.stderr)
    sys.exit(1)

results_path = Path(sys.argv[1])
if not results_path.exists():
    print(f"ERROR: results file not found: {results_path}", file=sys.stderr)
    sys.exit(1)

data = json.loads(results_path.read_text())

chapter_map = {}
if len(sys.argv) >= 3:
    map_path = Path(sys.argv[2])
    if map_path.exists():
        chapter_map = json.loads(map_path.read_text())
        print(f"  Loaded chapter map ({len(chapter_map)} entries)", file=sys.stderr)


# ── Helpers ─────────────────────────────────────────────────────────────
def condense_text(text, max_words=200):
    """Clean citations, page numbers, and shorten to key content."""
    # Remove isolated page numbers: "365 365 365"
    text = re.sub(r'\b\d{2,4}\b(?:\s+\d{2,4}\b)*', '', text)
    # Remove long parenthetical citations: (Author, Year, pp. 123-145)
    text = re.sub(r'\([^)]{10,200}\)', '', text)
    # Reconstruct: keep all non-empty lines
    lines = text.split('\n')
    key_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip lines that are just numbers/spaces
        if re.match(r'^[\d\s]{5,}$', stripped):
            continue
        # Skip known publisher/acknowledgment boilerplate
        if any(name in stripped for name in [
            'OceanofPDF.com', 'Acknowledgments', 'acknowledge',
            'www.ebookelo.com', 'Scan of',
        ]) and len(stripped) < 80:
            continue
        key_lines.append(stripped)
    result = ' '.join(key_lines)
    words = result.split()
    if len(words) > max_words:
        result = ' '.join(words[:max_words])
    return result


# ── Process ─────────────────────────────────────────────────────────────
for entry in data:
    section_id = entry.get("section", "?")
    chapter_label = chapter_map.get(section_id, section_id)
    chunks = entry.get("chunks", [])

    print(f"\n{'='*60}")
    print(chapter_label)
    print(f"{'='*60}")

    if not chunks:
        print("NO DATA FROM RAG")
        continue

    relevant_texts = []
    for chunk in chunks:
        txt = chunk.get("text", "")
        # Skip chunks that are mostly boilerplate
        if 'Acknowledgments' in txt[:200] and len(txt) < 500:
            continue
        if 'OceanofPDF.com' in txt[:100]:
            continue
        relevant_texts.append(condense_text(txt, 200))

    if not relevant_texts:
        print("NO USABLE DATA (all chunks filtered as boilerplate)")
    else:
        print('\n\n'.join(relevant_texts))

print(file=sys.stderr)  # trailing newline
