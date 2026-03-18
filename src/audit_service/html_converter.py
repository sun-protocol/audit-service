import markdown2

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --bg: #ffffff;
    --fg: #1a1a1a;
    --fg-muted: #64748b;
    --accent: #2563eb;
    --accent-light: #eff6ff;
    --border: #e2e8f0;
    --code-bg: #1e293b;
    --code-fg: #e2e8f0;
    --inline-code-bg: #f1f5f9;
    --inline-code-fg: #be185d;
    --table-header: #1e293b;
    --table-stripe: #f8fafc;
    --blockquote-bg: #eff6ff;
    --blockquote-border: #2563eb;
    --blockquote-fg: #1e40af;
    --critical: #dc2626;
    --high: #ea580c;
    --medium: #d97706;
    --low: #2563eb;
    --info: #64748b;
  }}

  *, *::before, *::after {{
    box-sizing: border-box;
  }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "PingFang SC", "Noto Sans SC", "Microsoft YaHei",
                 "Helvetica Neue", Arial, sans-serif;
    font-size: 15px;
    line-height: 1.75;
    color: var(--fg);
    background: var(--bg);
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 32px 80px;
    -webkit-font-smoothing: antialiased;
  }}

  /* === Headings === */
  h1 {{
    font-size: 2em;
    font-weight: 700;
    color: #0f172a;
    border-bottom: 3px solid var(--accent);
    padding-bottom: 12px;
    margin: 0 0 24px 0;
  }}
  h2 {{
    font-size: 1.5em;
    font-weight: 600;
    color: #1e293b;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin: 40px 0 16px 0;
  }}
  h3 {{
    font-size: 1.2em;
    font-weight: 600;
    color: #334155;
    margin: 32px 0 12px 0;
  }}
  h4 {{
    font-size: 1.05em;
    font-weight: 600;
    color: #475569;
    margin: 24px 0 8px 0;
  }}

  /* === Text === */
  p {{
    margin: 10px 0;
  }}
  a {{
    color: var(--accent);
    text-decoration: none;
  }}
  a:hover {{
    text-decoration: underline;
  }}
  strong {{
    font-weight: 600;
    color: #0f172a;
  }}
  hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 28px 0;
  }}

  /* === Inline Code === */
  code {{
    font-family: "SF Mono", "Fira Code", "JetBrains Mono", "Cascadia Code",
                 "Source Code Pro", Menlo, Consolas, monospace;
    font-size: 0.875em;
    background: var(--inline-code-bg);
    color: var(--inline-code-fg);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--border);
  }}

  /* === Code Blocks === */
  pre {{
    background: var(--code-bg);
    color: var(--code-fg);
    padding: 20px 24px;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.6;
    overflow-x: auto;
    margin: 16px 0;
    position: relative;
  }}
  pre code {{
    background: none;
    color: inherit;
    padding: 0;
    border: none;
    font-size: inherit;
  }}

  /* === Tables === */
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 14px;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  th {{
    background: var(--table-header);
    color: #fff;
    font-weight: 600;
    padding: 12px 16px;
    text-align: left;
  }}
  td {{
    padding: 10px 16px;
    border-top: 1px solid var(--border);
    vertical-align: top;
  }}
  tr:nth-child(even) td {{
    background: var(--table-stripe);
  }}

  /* === Blockquotes === */
  blockquote {{
    border-left: 4px solid var(--blockquote-border);
    margin: 16px 0;
    padding: 12px 20px;
    background: var(--blockquote-bg);
    color: var(--blockquote-fg);
    border-radius: 0 6px 6px 0;
    font-size: 14px;
  }}
  blockquote p {{
    margin: 4px 0;
  }}

  /* === Lists === */
  ul, ol {{
    margin: 10px 0;
    padding-left: 28px;
  }}
  li {{
    margin: 4px 0;
  }}
  li > ul, li > ol {{
    margin: 2px 0;
  }}

  /* === Task Lists === */
  ul.task-list {{
    list-style: none;
    padding-left: 4px;
  }}
  ul.task-list li {{
    position: relative;
    padding-left: 28px;
  }}
  ul.task-list li input[type="checkbox"] {{
    position: absolute;
    left: 0;
    top: 5px;
    width: 16px;
    height: 16px;
    accent-color: var(--accent);
  }}

  /* === Images === */
  img {{
    max-width: 100%;
    height: auto;
    border-radius: 6px;
  }}

  /* === Severity Tags === */
  .severity-critical {{ color: var(--critical); font-weight: 700; }}
  .severity-high {{ color: var(--high); font-weight: 700; }}
  .severity-medium {{ color: var(--medium); font-weight: 600; }}
  .severity-low {{ color: var(--low); font-weight: 600; }}
  .severity-info {{ color: var(--info); }}

  /* === Print === */
  @media print {{
    body {{
      max-width: none;
      padding: 0;
      font-size: 11pt;
    }}
    pre {{
      white-space: pre-wrap;
      word-wrap: break-word;
    }}
    h1, h2, h3, h4 {{
      page-break-after: avoid;
    }}
    table, pre, blockquote {{
      page-break-inside: avoid;
    }}
  }}
</style>
</head>
<body>
{content}
</body>
</html>"""


def markdown_to_html(md_content: str, title: str = "Audit Report") -> str:
    """Convert Markdown content to a standalone HTML string."""
    html_body = markdown2.markdown(
        md_content,
        extras=[
            "fenced-code-blocks",
            "tables",
            "code-friendly",
            "cuddled-lists",
            "strike",
            "task_list",
            "header-ids",
            "break-on-newline",
            "smarty-pants",
        ],
    )
    return HTML_TEMPLATE.format(content=html_body, title=title)
