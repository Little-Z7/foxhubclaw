from foxhubclaw.normalize import extract_list, normalize_item


def test_extract_list_from_nested_data():
    payload = {"list": [{"title": "a"}, {"title": "b"}]}
    assert len(extract_list(payload)) == 2


def test_extract_list_accepts_bare_list():
    assert extract_list([{"title": "a"}]) == [{"title": "a"}]


def test_normalize_post_maps_common_fields():
    item = normalize_item(
        "douyin",
        "post",
        {
            "title": "Hello AI",
            "userName": "alice",
            "url": "https://www.douyin.com/video/1",
            "likeCount": 12,
            "commentCount": 3,
            "shareCount": 1,
            "gmtCreate": "2026-08-01 10:00:00",
        },
    )
    assert item["platform"] == "douyin"
    assert item["kind"] == "post"
    assert item["title"] == "Hello AI"
    assert item["author"] == "alice"
    assert item["url"] == "https://www.douyin.com/video/1"
    assert item["likes"] == 12
    assert item["comments"] == 3
    assert item["shares"] == 1
    assert "2026-08-01" in item["published_at"]


def test_normalize_skips_empty_title_and_url():
    item = normalize_item("douyin", "post", {"likeCount": 1})
    assert item["title"] == "(untitled)"
    assert item["url"] == ""
