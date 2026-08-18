from pathlib import Path

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
