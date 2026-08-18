from foxhubclaw.capabilities import (
    filter_requested,
    list_platforms,
    platform_supports,
)


def test_catalog_includes_core_platforms():
    ids = {p["id"] for p in list_platforms()}
    assert {"douyin", "xiaohongshu", "wechat", "bilibili", "toutiao", "kuaishou"} <= ids


def test_tiktok_posts_unsupported():
    assert platform_supports("tiktok", "post") is False
    assert platform_supports("douyin", "post") is True
    assert platform_supports("kuaishou", "comment") is True
    assert platform_supports("douyin", "comment") is False


def test_filter_requested_drops_unsupported():
    kept, skipped = filter_requested(["douyin", "tiktok"], ["post", "comment"])
    assert ("douyin", "post") in kept
    assert ("tiktok", "post") in skipped
    assert ("douyin", "comment") in skipped
    assert ("kuaishou", "comment") not in kept
