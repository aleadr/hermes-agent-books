# Reference: RAG Query Performance Guide

## Model Loading
- RAG uses `paraphrase-multilingual-MiniLM-L12-v2` (~100MB loaded into RAM)
- Loading takes ~2 seconds, then encoding is fast
- Each `rag.py query` call reloads the model from scratch (~30s overhead)
- Batch approach: import `rag.py` as module, load model ONCE, query N times

## Batch Query (Recommended for >5 chapters)
Instead of per-chapter queries (which reload model each time):
1. Import rag.py's query function directly in a Python script
2. Load model once at the top
3. Call `rag.query(question, book_ids=[N])` for each chapter
4. Save results to JSON

## ChromaDB Details
- Data stored at: `~/RAG/chroma_db/`
- Collection naming: `rag_book_{id}`
- Index state: `~/RAG/index_state.json` (maps book IDs to collections)
- TOP_K = 5 chunks returned per query per book
- Chunk size: 500 words, 100 word overlap

## Embedding Model Details
- Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Supports 50+ languages (including Indonesian)
- Output dimension: 384
- Max sequence length: 128 tokens per sentence (longer texts are truncated)
