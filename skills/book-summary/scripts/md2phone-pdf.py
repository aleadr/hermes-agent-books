#!/usr/bin/env python3
"""
Convert markdown book summary to phone-friendly A5 PDF.

USAGE:
  python md2phone-pdf.py <input.md> [output.pdf]

  If output.pdf omitted, replaces .md with .pdf in same directory.

DEPENDENCIES:
  pip install markdown weasyprint

  Font: Noto Sans (available on Ubuntu at /usr/share/fonts/truetype/noto/)
  Falls back to DejaVu Sans if Noto Sans not found.

OUTPUT:
  A5 portrait PDF (148 x 210 mm / 419.5 x 595.3 pt)
  - 8.5pt body text, Noto Sans
  - 16pt title, 11pt chapter headings
  - Page numbers in footer
  - Justified text with hyphenation
"""

import sys
import markdown
from pathlib import Path
from weasyprint import HTML

def convert(md_path: Path, output_path: Path | None = None):
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown.markdown(md_text, extensions=["extra"])

    if output_path is None:
        output_path = md_path.with_suffix(".pdf")

    CSS = """
    @page {
      size: A5 portrait;
      margin: 12mm 10mm 15mm 10mm;
      @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 6pt;
        color: #999;
        font-family: sans-serif;
      }
    }
    body {
      font-family: 'Noto Sans', 'DejaVu Sans', sans-serif;
      font-size: 8.5pt;
      line-height: 1.45;
      color: #1a1a1a;
      widows: 2;
      orphans: 2;
    }
    h1 { font-size: 16pt; text-align: center; margin-top: 3mm; margin-bottom: 2mm; }
    h2 { font-size: 11pt; color: #2c3e50; margin-top: 4mm; margin-bottom: 1.5mm; }
    p { margin: 0 0 0.8mm 0; text-align: justify; hyphens: auto; }
    hr { border: none; border-top: 0.5px solid #ccc; margin: 3mm 0; }
    strong { font-weight: 700; }
    em { font-style: italic; }
    blockquote {
      margin: 1.5mm 2mm;
      padding: 1mm 2mm;
      border-left: 2px solid #95a5a6;
      color: #444;
      font-style: italic;
    }
    code { font-size: 7.5pt; background: #f0f0f0; padding: 0.5mm 1mm; }
    """  # noqa: E501

    html_full = f"""<!DOCTYPE html>
<html lang="id">
<head><meta charset="utf-8"><style>{CSS}</style></head>
<body>{html_body}</body>
</html>"""

    HTML(string=html_full).write_pdf(str(output_path))
    kb = output_path.stat().st_size / 1024
    print(f"✅ PDF: {output_path} ({kb:.0f} KB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    md_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    convert(md_path, out_path)
