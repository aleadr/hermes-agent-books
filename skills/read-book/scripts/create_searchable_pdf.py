#!/usr/bin/env python3
"""Convert OCR markdown output to a text-searchable PDF for RAG indexing.

Takes the incremental markdown output of ocr_scanned_pdf.py (or any
markdown with "## Page N" headers) and produces a proper text-searchable
PDF with one page per original page.

Usage:
    python3 create_searchable_pdf.py <ocr_output.md> [output.pdf]

Default output: /tmp/<input-basename>-searchable.pdf

Dependencies:
    pip3 install pymupdf --break-system-packages
"""
import pymupdf
import re
import sys
import os

md_path = sys.argv[1]
pdf_path = sys.argv[2] if len(sys.argv) > 2 else re.sub(
    r'\.\w+$', '', md_path
) + '-searchable.pdf'

with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by page markers — supports "## Page N" format from ocr_scanned_pdf.py
pages = re.split(r'^## Page (\d+)', content, flags=re.MULTILINE)

doc = pymupdf.open()
page_texts = []

# Skip header (index 0), then alternate: page_num, page_content
for i in range(1, len(pages), 2):
    if i + 1 < len(pages):
        page_text = pages[i + 1].strip()
        page_texts.append(page_text)

for page_text in page_texts:
    page = doc.new_page()
    rect = pymupdf.Rect(50, 50, 550, 800)
    page.insert_textbox(rect, page_text, fontsize=8, fontname="helv", align=0)

doc.save(pdf_path)
doc.close()

# Verify
doc2 = pymupdf.open(pdf_path)
total_text = sum(len(page.get_text()) for page in doc2)
print(f"Created: {pdf_path}")
print(f"Pages:   {len(doc2)}")
print(f"Chars:   {total_text:,}")
doc2.close()
