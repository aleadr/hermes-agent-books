#!/usr/bin/env python3
"""OCR a scanned PDF using pymupdf + tesseract.

Usage:
    python3 -u scripts/ocr_scanned_pdf.py <input.pdf> [output.md] [lang]

Default lang is 'eng'. For non-English books pass the appropriate
tesseract language code, e.g. 'eng+ind' for Indonesian, 'eng+fra' for French.
Install the corresponding language pack first:
    sudo apt-get install tesseract-ocr-<code>

Writes incrementally so partial results survive cancellation.
Default DPI is 150 (fast, adequate for book scans).
"""
import pymupdf
import subprocess
import tempfile
import os
import sys

pdf_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else '/tmp/ocr_output.md'
# Language pack(s) for tesseract, e.g. 'eng', 'eng+ind', 'eng+fra'
# Pass as 3rd argument; default 'eng'
lang = sys.argv[3] if len(sys.argv) > 3 else 'eng'

doc = pymupdf.open(pdf_path)
total = len(doc)
print(f"Total pages: {total}", flush=True)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"# OCR Output: {os.path.basename(pdf_path)}\n\n")

for i in range(total):
    page = doc[i]
    pix = page.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")

    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        f.write(img_bytes)
        img_path = f.name

    page_text = f"## Page {i+1}\n\n"
    try:
        result = subprocess.run(
            ['tesseract', img_path, 'stdout', '-l', lang, '--psm', '6'],
            capture_output=True, text=True, timeout=30
        )
        text = result.stdout.strip()
        page_text += (text if text else "[No text detected]\n")
    except Exception as e:
        page_text += f"[OCR error: {e}]\n"
    finally:
        os.unlink(img_path)

    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(page_text + "\n")

    if (i+1) % 5 == 0:
        print(f"  {i+1}/{total} pages done...", flush=True)

print(f"Done! Output: {output_path}", flush=True)
