"""Merge all markdown files under .audit/ into a single document, then convert to HTML."""

from pathlib import Path

from .html_converter import markdown_to_html


def merge_audit_markdown(audit_dir: Path) -> str:
    """Merge all .md files in the .audit directory into a single markdown string.

    Ordering:
      1. blueprints/*.md sorted by filename (0_Setup, 1_..., 2_..., etc.)
      2. Audit-Report.md (the final summary) appended last

    Each file is separated by a horizontal rule.
    """
    if not audit_dir.is_dir():
        return ""

    parts: list[str] = []

    # Collect blueprint files first (sorted by name for phase ordering)
    blueprints_dir = audit_dir / "blueprints"
    if blueprints_dir.is_dir():
        for md_file in sorted(blueprints_dir.rglob("*.md")):
            content = md_file.read_text(encoding="utf-8").strip()
            if content:
                parts.append(content)

    # Collect top-level .md files (e.g. Audit-Report.md), excluding blueprints
    for md_file in sorted(audit_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8").strip()
        if content:
            parts.append(content)

    return "\n\n---\n\n".join(parts)


def merge_and_convert(audit_dir: Path, title: str = "Audit Report") -> tuple[str, str]:
    """Merge .audit/ markdown files and return both merged markdown and HTML.

    Returns:
        (merged_md, html) tuple.
    """
    merged_md = merge_audit_markdown(audit_dir)
    html = markdown_to_html(merged_md, title=title) if merged_md else ""
    return merged_md, html
