#!/usr/bin/env python3
"""Convert a Markdown file to HTML.

Usage:
    python tools/md2html.py <input.md> [output.html]

If output path is omitted, uses the same name with .html extension.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.audit_service.html_converter import markdown_to_html


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.md> [output.html]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix(".html")

    md_content = input_path.read_text(encoding="utf-8")
    html_content = markdown_to_html(md_content, title=input_path.stem)
    output_path.write_text(html_content, encoding="utf-8")
    print(f"{input_path} -> {output_path} ({len(html_content)} bytes)")


if __name__ == "__main__":
    main()
