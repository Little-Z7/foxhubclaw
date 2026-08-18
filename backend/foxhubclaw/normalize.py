from __future__ import annotations

from typing import Any


def extract_list(payload: Any) -> list[dict[str, Any]]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in (
        "list",
        "articles",
        "comments",
        "commentList",
        "items",
        "records",
        "opusInfoList",
        "workList",
        "noteList",
        "articleList",
        "notes",
        "works",
        "videos",
        "data",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = extract_list(value)
            if nested:
                return nested
    return []


def _first(item: dict[str, Any], *keys: str, default: Any = "") -> Any:
    for key in keys:
        value = item.get(key)
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return default


def _as_int(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_item(platform: str, kind: str, item: dict[str, Any]) -> dict[str, Any]:
    title = str(
        _first(
            item,
            "title",
            "workTitle",
            "caption",
            "desc",
            "content",
            "text",
            "noteTitle",
            default="(untitled)",
        )
    ).strip() or "(untitled)"
    author = str(
        _first(
            item,
            "userName",
            "accountName",
            "authorNickname",
            "author",
            "authorName",
            "nickname",
            "name",
            "upName",
            default="",
        )
    ).strip()
    url = str(
        _first(
            item,
            "url",
            "workUrl",
            "opusUrl",
            "shareInfoLink",
            "shareUrl",
            "sourceUrl",
            "link",
            "videoUrl",
            default="",
        )
    ).strip()
    published = str(
        _first(
            item,
            "gmtCreate",
            "publishTime",
            "releaseTime",
            "createTime",
            "published_at",
            "pubTime",
            default="",
        )
    )
    return {
        "platform": platform,
        "kind": kind,
        "title": title,
        "author": author,
        "url": url,
        "published_at": published,
        "likes": _as_int(_first(item, "likeCount", "likedCount", "like_count", "likeNum", "commentLikeNum", "diggCount", default=0)),
        "comments": _as_int(_first(item, "commentCount", "commentsCount", "comment_count", "commentNum", "replyNum", default=0)),
        "shares": _as_int(_first(item, "shareCount", "sharedCount", "share_count", "forwardCount", "forwardNum", default=0)),
        "extra": {
            "work_id": _first(item, "workId", "photoId", "opusId", "awemeId", "bvid", "bvId", "workUuid", "mid", "cid", "id"),
            "cover": _first(item, "coverUrl", "cover", "userHeadUrl"),
        },
    }
