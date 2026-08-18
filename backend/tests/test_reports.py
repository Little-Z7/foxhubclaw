from pathlib import Path

from pypdf import PdfReader

from foxhubclaw.reports import write_report_files


def test_write_report_files_creates_three_artifacts(tmp_path: Path):
    items = [
        {
            "platform": "douyin",
            "kind": "post",
            "title": "Sample",
            "author": "bob",
            "url": "https://example.com/1",
            "published_at": "2026-08-01 10:00:00",
            "likes": 9,
            "comments": 2,
            "shares": 1,
        }
    ]
    paths = write_report_files(
        output_dir=tmp_path,
        keyword="AI",
        items=items,
        failures=[{"platform": "tiktok", "kind": "post", "message": "Not supported"}],
    )
    assert Path(paths["xlsx"]).is_file()
    assert Path(paths["html"]).is_file()
    assert Path(paths["pdf"]).is_file()
    html = Path(paths["html"]).read_text(encoding="utf-8")
    assert "Sample" in html
    assert "AI" in html


def test_pdf_keeps_chinese_text(tmp_path: Path):
    items = [
        {
            "platform": "小红书",
            "kind": "post",
            "title": "国货美妆测评",
            "author": "阿狸",
            "url": "https://example.com/1",
            "published_at": "2026-08-01 10:00:00",
            "likes": 9,
            "comments": 2,
            "shares": 1,
        }
    ]
    paths = write_report_files(output_dir=tmp_path, keyword="人工智能", items=items)
    text = PdfReader(paths["pdf"]).pages[0].extract_text()
    assert "人工智能" in text
    assert "国货美妆测评" in text
    assert "小红书" in text
