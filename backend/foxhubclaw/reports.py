from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF
from jinja2 import Template
from openpyxl import Workbook

HTML_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>FoxHubClaw Report</title>
  <style>
    body { font-family: "Iowan Old Style", "Palatino Linotype", serif; background: #14110e; color: #f3e6d4; margin: 0; }
    main { max-width: 960px; margin: 0 auto; padding: 48px 24px 80px; }
    .eyebrow { letter-spacing: 0.28em; text-transform: uppercase; color: #c45c26; font-size: 12px; }
    h1 { font-weight: 500; font-size: 42px; margin: 8px 0 12px; }
    .meta { color: #b7a48f; margin-bottom: 32px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #3a322b; padding: 10px 8px; text-align: left; font-size: 14px; }
    th { color: #c45c26; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; }
    a { color: #e8c39e; }
    .fail { color: #e08a5a; }
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">FoxHubClaw</div>
    <h1>{{ keyword }}</h1>
    <p class="meta">Generated {{ generated_at }} · {{ item_count }} rows · {{ fail_count }} platform warnings</p>
    {% if failures %}
    <p class="fail">Partial: {{ failures | map(attribute='platform') | join(', ') }}</p>
    {% endif %}
    <table>
      <thead>
        <tr><th>Platform</th><th>Kind</th><th>Title</th><th>Author</th><th>Likes</th><th>Time</th></tr>
      </thead>
      <tbody>
        {% for item in items %}
        <tr>
          <td>{{ item.platform }}</td>
          <td>{{ item.kind }}</td>
          <td>{% if item.url %}<a href="{{ item.url }}">{{ item.title }}</a>{% else %}{{ item.title }}{% endif %}</td>
          <td>{{ item.author }}</td>
          <td>{{ item.likes }}</td>
          <td>{{ item.published_at }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </main>
</body>
</html>
"""
)


def write_report_files(
    output_dir: Path,
    keyword: str,
    items: list[dict[str, Any]],
    failures: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = "".join(ch for ch in keyword if ch.isalnum() or ch in ("-", "_"))[:24] or "query"
    xlsx_path = output_dir / f"{safe}-{stamp}.xlsx"
    html_path = output_dir / f"{safe}-{stamp}.html"
    pdf_path = output_dir / f"{safe}-{stamp}.pdf"

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Results"
    sheet.append(["platform", "kind", "title", "author", "url", "published_at", "likes", "comments", "shares"])
    for item in items:
        sheet.append(
            [
                item.get("platform"),
                item.get("kind"),
                item.get("title"),
                item.get("author"),
                item.get("url"),
                item.get("published_at"),
                item.get("likes"),
                item.get("comments"),
                item.get("shares"),
            ]
        )
    workbook.save(xlsx_path)

    html = HTML_TEMPLATE.render(
        keyword=keyword,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        items=items,
        item_count=len(items),
        failures=failures or [],
        fail_count=len(failures or []),
    )
    html_path.write_text(html, encoding="utf-8")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_font("Helvetica", size=14)
    header = f"FoxHubClaw / {keyword}".encode("latin-1", "replace").decode("latin-1")
    pdf.cell(0, 10, header, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.cell(
        0,
        8,
        f"Rows: {len(items)}  Warnings: {len(failures or [])}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    for item in items[:40]:
        raw = f"{item.get('platform')} | {item.get('title', '')}"
        line = raw.encode("latin-1", "replace").decode("latin-1")[:90]
        pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(pdf_path))

    return {"xlsx": str(xlsx_path), "html": str(html_path), "pdf": str(pdf_path)}
