from foxhubclaw.normalize import extract_list, normalize_item


def test_extract_list_from_nested_data():
    payload = {"list": [{"title": "a"}, {"title": "b"}]}
    assert len(extract_list(payload)) == 2


def test_extract_list_opus_info_list():
    assert extract_list({"opusInfoList": [{"title": "bv"}]}) == [{"title": "bv"}]


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


def test_normalize_douyin_account_name_and_toutiao_url():
    douyin = normalize_item(
        "douyin",
        "post",
        {"title": "视频", "accountName": "抖音号", "workUrl": "https://www.douyin.com/video/1", "workId": "1"},
    )
    assert douyin["author"] == "抖音号"
    toutiao = normalize_item(
        "toutiao",
        "post",
        {"title": "文章", "nickname": "头条号", "opusUrl": "https://www.toutiao.com/a1", "opusId": "1"},
    )
    assert toutiao["url"] == "https://www.toutiao.com/a1"
    assert toutiao["author"] == "头条号"


def test_normalize_xiaohongshu_and_bilibili_fields():
    xhs = normalize_item(
        "xiaohongshu",
        "post",
        {
            "title": "笔记",
            "authorNickname": "红薯",
            "shareInfoLink": "https://www.xiaohongshu.com/explore/1",
            "likedCount": 8,
            "createTime": "2026-08-01 10:00:00",
            "id": "note1",
        },
    )
    assert xhs["author"] == "红薯"
    assert "xiaohongshu.com" in xhs["url"]
    assert xhs["likes"] == 8
    bili = normalize_item(
        "bilibili",
        "post",
        {
            "title": "视频",
            "nickname": "UP主",
            "likeNum": 11,
            "commentNum": 3,
            "bvId": "BV1xx",
            "url": "https://www.bilibili.com/video/BV1xx",
        },
    )
    assert bili["author"] == "UP主"
    assert bili["likes"] == 11
    assert bili["extra"]["work_id"] == "BV1xx"
