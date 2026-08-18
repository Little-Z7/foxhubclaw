from __future__ import annotations

from typing import Iterable

PlatformId = str
Kind = str

CATALOG: list[dict[str, object]] = [
    {
        "id": "douyin",
        "name": "抖音",
        "name_en": "Douyin",
        "post": True,
        "comment": False,
        "comment_note": "暂无关键词评论接口",
    },
    {
        "id": "xiaohongshu",
        "name": "小红书",
        "name_en": "Xiaohongshu",
        "post": True,
        "comment": False,
        "comment_note": "暂无关键词评论接口",
    },
    {
        "id": "wechat",
        "name": "公众号",
        "name_en": "WeChat",
        "post": True,
        "comment": False,
        "comment_note": "暂无关键词评论接口",
    },
    {
        "id": "bilibili",
        "name": "B站",
        "name_en": "Bilibili",
        "post": True,
        "comment": True,
        "comment_note": "先搜作品，再拉取热门作品评论",
    },
    {
        "id": "toutiao",
        "name": "今日头条",
        "name_en": "Toutiao",
        "post": True,
        "comment": False,
        "comment_note": "暂无关键词评论接口",
    },
    {
        "id": "kuaishou",
        "name": "快手",
        "name_en": "Kuaishou",
        "post": True,
        "comment": True,
        "comment_note": "先搜作品，再取热门作品评论",
    },
    {
        "id": "tiktok",
        "name": "TikTok",
        "name_en": "TikTok",
        "post": False,
        "comment": False,
        "comment_note": "当前仅有用户搜索，不支持关键词帖子/评论",
    },
    {
        "id": "weibo",
        "name": "微博",
        "name_en": "Weibo",
        "post": True,
        "comment": True,
        "comment_note": "先搜博文，再拉取热门博文评论",
    },
]


def list_platforms() -> list[dict[str, object]]:
    return [dict(item) for item in CATALOG]


def platform_name(platform_id: str) -> str:
    for item in CATALOG:
        if item["id"] == platform_id:
            return str(item["name"])
    return platform_id


def platform_supports(platform_id: str, kind: Kind) -> bool:
    for item in CATALOG:
        if item["id"] == platform_id:
            return bool(item.get(kind))
    return False


def filter_requested(
    platforms: Iterable[str],
    kinds: Iterable[Kind],
) -> tuple[list[tuple[str, Kind]], list[tuple[str, Kind]]]:
    kept: list[tuple[str, Kind]] = []
    skipped: list[tuple[str, Kind]] = []
    for platform in platforms:
        for kind in kinds:
            target = (platform, kind)
            if platform_supports(platform, kind):
                kept.append(target)
            else:
                skipped.append(target)
    return kept, skipped
