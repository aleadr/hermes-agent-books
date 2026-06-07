#!/usr/bin/env python3
"""
RAG CLI for PDF books — index, list, query.
Hermes Agent loads relevant chunks on demand; never permanently in context.

Usage:
  rag.py index <pdf_path>           # Index a PDF
  rag.py list                       # List all indexed books
  rag.py query "question" [--books 0,2]  # Query specific books (or all)
  rag.py remove <book_id>           # Remove a book from index
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────
RAG_HOME = Path(os.environ.get("RAG_HOME", Path.home() / "RAG"))
BOOKS_DIR = RAG_HOME / "books"
CHROMA_DIR = RAG_HOME / "chroma_db"
STATE_FILE = RAG_HOME / "index_state.json"

CHUNK_SIZE = 500       # words per chunk
CHUNK_OVERLAP = 100    # word overlap between chunks
TOP_K = 5              # chunks to retrieve per query per book
# ──────────────────────────────────────────────────────────────────

# ── Helpers ───────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def get_chroma():
    import chromadb
    return chromadb.PersistentClient(path=str(CHROMA_DIR))
# ──────────────────────────────────────────────────────────────────

# ── Index ─────────────────────────────────────────────────────────
def index(pdf_path: str):
    pdf = Path(pdf_path).resolve()
    if not pdf.exists():
        print(f"ERROR: File not found: {pdf}")
        sys.exit(1)
    if not pdf.suffix.lower() == ".pdf":
        print(f"ERROR: Not a PDF: {pdf}")
        sys.exit(1)

    # Copy to books dir if not already there
    dest = BOOKS_DIR / pdf.name
    if pdf != dest:
        import shutil
        shutil.copy2(pdf, dest)
        print(f"📄 Copied to: {dest}")
    else:
        print(f"📄 Using: {dest}")

    # Parse PDF
    import fitz  # pymupdf
    doc = fitz.open(str(dest))
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    doc.close()

    if not full_text.strip():
        print("ERROR: No extractable text in PDF (maybe scanned image?)")
        sys.exit(1)

    # Extract title from first line or filename
    lines = full_text.strip().split("\n")
    title = lines[0].strip() if lines else dest.stem
    if len(title) > 120:
        title = title[:117] + "..."

    # Chunk
    words = full_text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + CHUNK_SIZE]
        chunks.append(" ".join(chunk_words))
        i += CHUNK_SIZE - CHUNK_OVERLAP
        if i >= len(words):
            break

    print(f"🔢 Chunked into {len(chunks)} chunks ({CHUNK_SIZE} words, {CHUNK_OVERLAP} overlap)")

    # Embed & store
    print("🧠 Embedding... (this may take a minute for large books)")
    model = get_model()
    embeddings = model.encode(chunks, show_progress_bar=True).tolist()

    # Determine next book ID
    state = load_state()
    book_id = str(len(state))
    collection_name = f"rag_book_{book_id}"

    chroma = get_chroma()
    # Delete existing collection if re-indexing same ID
    try:
        chroma.delete_collection(collection_name)
    except Exception:
        pass

    collection = chroma.create_collection(name=collection_name)
    ids = [f"{book_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"book_id": book_id, "chunk_idx": i, "title": title} for i in range(len(chunks))]

    # Batch insert (chromadb limit: 5461 per batch for some versions, be safe)
    BATCH = 1000
    for b in range(0, len(chunks), BATCH):
        collection.add(
            ids=ids[b:b+BATCH],
            embeddings=embeddings[b:b+BATCH],
            documents=chunks[b:b+BATCH],
            metadatas=metadatas[b:b+BATCH],
        )

    # Save state
    state[book_id] = {
        "title": title,
        "filename": dest.name,
        "path": str(dest),
        "chunks": len(chunks),
        "indexed_at": __import__("datetime").datetime.now().isoformat(),
        "collection": collection_name,
    }
    save_state(state)

    print(f"✅ Indexed [{book_id}] «{title}» — {len(chunks)} chunks")
# ──────────────────────────────────────────────────────────────────

# ── List ──────────────────────────────────────────────────────────
def list_books():
    state = load_state()
    if not state:
        print("No indexed books.")
        return state

    print(f"{'ID':<4} {'Chunks':<8} Title")
    print("-" * 60)
    for bid in sorted(state.keys(), key=int):
        b = state[bid]
        print(f"[{bid}]  {b['chunks']:<8} {b['title'][:80]}")
    return state
# ──────────────────────────────────────────────────────────────────

# ── Query ─────────────────────────────────────────────────────────
def query(question: str, book_ids: list[int] | None = None):
    state = load_state()
    if not state:
        print("No indexed books. Index a PDF first: rag.py index <file.pdf>")
        sys.exit(1)

    # Determine which books to query
    if book_ids is not None:
        targets = {str(bid): state[str(bid)] for bid in book_ids if str(bid) in state}
        if not targets:
            print(f"No books found for IDs: {book_ids}")
            sys.exit(1)
    else:
        targets = state

    model = get_model()
    chroma = get_chroma()

    # Embed question
    print("🔍 Searching...")
    q_embedding = model.encode([question]).tolist()

    all_chunks = []
    for bid in sorted(targets.keys(), key=int):
        b = targets[bid]
        collection = chroma.get_collection(name=b["collection"])
        results = collection.query(query_embeddings=q_embedding, n_results=min(TOP_K, b["chunks"]))
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results.get("metadatas") else {}
                all_chunks.append({
                    "book_id": bid,
                    "title": b["title"],
                    "chunk_idx": meta.get("chunk_idx", "?"),
                    "text": doc,
                })

    # Print results for LLM consumption
    print(f"\n{'='*60}")
    print(f"Query: {question}")
    book_labels = [f"[{bid}] {targets[bid]['title']}" for bid in sorted(targets.keys(), key=int)]
    print(f"Books: {', '.join(book_labels)}")
    print(f"Results: {len(all_chunks)} chunks")
    print(f"{'='*60}\n")

    for i, chunk in enumerate(all_chunks):
        print(f"─── Chunk {i+1} ── [{chunk['book_id']}] {chunk['title']} (chunk #{chunk['chunk_idx']}) ───")
        print(chunk["text"][:2000])
        print()

    # Return structured for programmatic use
    return all_chunks
# ──────────────────────────────────────────────────────────────────

# ── Remove ────────────────────────────────────────────────────────
def remove(book_id: str):
    state = load_state()
    if book_id not in state:
        print(f"Book [{book_id}] not found.")
        return

    b = state[book_id]
    chroma = get_chroma()
    try:
        chroma.delete_collection(name=b["collection"])
    except Exception as e:
        print(f"Warning: could not delete collection: {e}")

    del state[book_id]
    save_state(state)
    print(f"🗑️  Removed [{book_id}] «{b['title']}»")
# ──────────────────────────────────────────────────────────────────

# ── CLI ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG CLI for PDF books")
    sub = parser.add_subparsers(dest="cmd", required=True)

    idx = sub.add_parser("index", help="Index a PDF book")
    idx.add_argument("pdf_path", help="Path to PDF file")

    sub.add_parser("list", help="List all indexed books")

    q = sub.add_parser("query", help="Query indexed books")
    q.add_argument("question", help="Search query")
    q.add_argument("--books", help="Comma-separated book IDs (e.g., 0,2). Omit for all books.")

    rm = sub.add_parser("remove", help="Remove a book from index")
    rm.add_argument("book_id", help="Book ID to remove")

    args = parser.parse_args()

    if args.cmd == "index":
        index(args.pdf_path)
    elif args.cmd == "list":
        list_books()
    elif args.cmd == "query":
        bids = None
        if args.books:
            bids = [int(x.strip()) for x in args.books.split(",")]
        query(args.question, bids)
    elif args.cmd == "remove":
        remove(args.book_id)
