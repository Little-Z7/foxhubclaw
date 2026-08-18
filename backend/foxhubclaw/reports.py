from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF
from jinja2 import Template
from openpyxl import Workbook

from foxhubclaw.capabilities import platform_name

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
        <tr><th>平台</th><th>类型</th><th>标题</th><th>作者</th><th>点赞</th><th>时间</th></tr>
      </thead>
      <tbody>
        {% for item in items %}
        <tr>
          <td>{{ item.platform_label }}</td>
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


def resolve_cjk_font() -> Path | None:
    bundled = Path(__file__).resolve().parent / "assets" / "fonts"
    meipass = Path(getattr(sys, "_MEIPASS", ".")) / "foxhubclaw" / "assets" / "fonts"
    windir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    candidates = [
        *sorted(bundled.glob("*.ttf")),
        *sorted(meipass.glob("*.ttf")),
        windir / "simhei.ttf",
        windir / "msyh.ttf",
        windir / "msyh.ttc",
        windir / "simsun.ttc",
        windir / "simkai.ttf",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None


def _write_pdf(pdf_path: Path, keyword: str, items: list[dict[str, Any]], failures: list[dict[str, Any]]) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    font = resolve_cjk_font()
    if font is not None:
        pdf.add_font("FoxCJK", fname=str(font))
        pdf.set_font("FoxCJK", size=14)
    else:
        pdf.set_font("Helvetica", size=14)

    def draw(value: str, size: int, height: int) -> None:
        pdf.set_x(pdf.l_margin)
        if font is not None:
            pdf.set_font("FoxCJK", size=size)
            pdf.multi_cell(0, height, value, new_x="LMARGIN", new_y="NEXT", wrapmode="CHAR")
            return
        pdf.set_font("Helvetica", size=size)
        pdf.multi_cell(
            0,
            height,
            value.encode("latin-1", "replace").decode("latin-1"),
            new_x="LMARGIN",
            new_y="NEXT",
        )

    draw(f"FoxHubClaw / {keyword}", 14, 10)
    draw(f"共 {len(items)} 条 · {len(failures)} 条平台警告", 10, 8)
    for item in items:
        name = platform_name(str(item.get("platform") or ""))
        draw(f"{name} | {item.get('title') or ''}", 10, 6)
    pdf.output(str(pdf_path))


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
                platform_name(str(item.get("platform") or "")),
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

    html_items = [
        {**item, "platform_label": platform_name(str(item.get("platform") or ""))} for item in items
    ]
    html = HTML_TEMPLATE.render(
        keyword=keyword,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        items=html_items,
        item_count=len(items),
        failures=failures or [],
        fail_count=len(failures or []),
    )
    html_path.write_text(html, encoding="utf-8")

    _write_pdf(pdf_path, keyword, items, failures or [])

    return {"xlsx": str(xlsx_path), "html": str(html_path), "pdf": str(pdf_path)}
