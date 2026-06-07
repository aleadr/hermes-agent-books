#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────
# Hermes Agent Books — Installer
# Sets up the RAG backend + all 5 book skills
# ──────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAG_HOME="${RAG_HOME:-$HOME/RAG}"
HERMES_SKILLS="${HOME}/.hermes/skills"

echo "═══ Hermes Agent Books — Installer ═══"
echo ""

# ── 0. Prerequisites ────────────────────────────────
echo "[1/5] Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is required but not installed."
    exit 1
fi

if [ ! -d "$HERMES_SKILLS" ]; then
    echo "WARNING: $HERMES_SKILLS not found."
    echo "  Hermes Agent may not be installed. Skills will still be copied,"
    echo "  but Hermes Agent is needed to use them."
    echo "  Install: https://hermes-agent.nousresearch.com/docs"
    echo ""
fi

# ── 1. RAG Backend ─────────────────────────────────
echo "[2/5] Setting up RAG backend at $RAG_HOME..."

mkdir -p "$RAG_HOME/books" "$RAG_HOME/chroma_db"

# Create Python venv
if [ ! -d "$RAG_HOME/.venv" ]; then
    python3 -m venv "$RAG_HOME/.venv"
fi

# Install dependencies
"$RAG_HOME/.venv/bin/pip" install --quiet --upgrade pip
"$RAG_HOME/.venv/bin/pip" install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Copy rag.py
cp "$SCRIPT_DIR/rag/rag.py" "$RAG_HOME/rag.py"

echo "  ✓ RAG backend installed"
echo "  Model: paraphrase-multilingual-MiniLM-L12-v2"
echo "  (downloaded automatically on first use)"
echo ""

# ── 2. Book Skills ─────────────────────────────────
echo "[3/5] Installing book skills..."

SKILL_DIRS=(
    "read-book"
    "book-list"
    "open-book"
    "close-book"
    "book-summary"
)

for skill in "${SKILL_DIRS[@]}"; do
    mkdir -p "$HERMES_SKILLS/$skill"
    cp -r "$SCRIPT_DIR/skills/$skill/"* "$HERMES_SKILLS/$skill/"
    echo "  ✓ $skill"
done

echo ""

# ── 3. Verify ──────────────────────────────────────
echo "[4/5] Verifying installation..."

# Test rag.py
if "$RAG_HOME/.venv/bin/python" "$RAG_HOME/rag.py" list &>/dev/null; then
    echo "  ✓ rag.py is functional"
else
    echo "  ⚠ rag.py responded (may be empty — no books indexed yet)"
fi

# Count installed skills
skill_count=$(find "$HERMES_SKILLS" -maxdepth 2 -name "SKILL.md" | wc -l)
echo "  ✓ $skill_count skills installed"

echo ""

# ── 4. Done ────────────────────────────────────────
echo "[5/5] Installation complete!"
echo ""
echo "─── What's installed ───"
echo "  RAG backend : $RAG_HOME/rag.py"
echo "  Skills dir  : $HERMES_SKILLS/"
echo ""
echo "  Skills:"
echo "    read-book     — Index a PDF into RAG"
echo "    book-list     — List all indexed books"
echo "    open-book     — Open books for RAG discussion"
echo "    close-book    — Exit RAG mode"
echo "    book-summary  — Generate per-chapter summaries"
echo ""
echo "─── Quick start ───"
echo "  1. Index a book:"
echo "     Send a PDF to Hermes and say 'read-book'"
echo ""
echo "  2. See all books:"
echo "     Ask 'list my books' or run:"
echo "     ~/RAG/.venv/bin/python ~/RAG/rag.py list"
echo ""
echo "  3. Chat with a book:"
echo "     open-book <id>"
echo "     Then ask questions naturally."
echo ""
echo "  4. Summarize a book:"
echo "     book-summary <id>"
echo ""
echo "Note: The embedding model (~420 MB) downloads on first use."
echo "      Ensure you have disk space and internet."
