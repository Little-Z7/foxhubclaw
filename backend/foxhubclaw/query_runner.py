from __future__ import annotations

from typing import Any

from foxhubclaw.capabilities import filter_requested
from foxhubclaw.comments import collect_comments
from foxhubclaw.normalize import extract_list, normalize_item
from foxhubclaw.redfox_http import HttpTransport, Transport

POST_PATHS = {
    "douyin": ("/story/api/dyData/searchArticle", lambda keyword, limit: {"keyword": keyword, "offset": 0}),
    "xiaohongshu": (
        "/story/api/xhs/search/search",
        lambda keyword, limit: {
            "keyword": keyword,
            "pageNum": 1,
            "pageSize": limit,
            "startDate": "",
            "endDate": "",
            "source": "FoxHubClaw",
        },
    ),
    "wechat": ("/story/api/gzhData/searchArticle", lambda keyword, limit: {"keyword": keyword, "offset": 0}),
    "bilibili": (
        "/story/api/bili/search",
        lambda keyword, limit: {
            "keyword": keyword,
            "sortType": "3",
            "publishTime": "0",
            "page": 1,
            "source": "FoxHubClaw",
        },
    ),
    "toutiao": ("/story/api/toutiao/searchWork", lambda keyword, limit: {"keyword": keyword, "offset": "0"}),
    "kuaishou": (
        "/story/api/ksAllData/searchWork",
        lambda keyword, limit: {"keyword": keyword, "sort": "最多点赞", "page": 1, "size": limit},
    ),
    "weibo": (
        "/story/api/weibo/ability/searchWork",
        lambda keyword, limit: {
            "keyword": keyword,
            "searchType": "1",
            "page": "1",
            "extParam": "",
            "source": "FoxHubClaw",
        },
    ),
}


class QueryRunner:
    def __init__(self, api_key: str, transport: Transport | None = None):
        self.api_key = api_key
        self.transport = transport or HttpTransport(api_key)

    def run(
        self,
        keyword: str,
        platforms: list[str],
        kinds: list[str],
        limit_per_platform: int = 20,
        comment_depth: int = 3,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        kept, skipped = filter_requested(platforms, kinds)
        items: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = [
            {"platform": platform, "kind": kind, "message": "暂不支持"} for platform, kind in skipped
        ]
        posts_by_platform: dict[str, list[dict[str, Any]]] = {}

        for platform, kind in kept:
            if kind != "post":
                continue
            try:
                batch = self._search_posts(platform, keyword, limit_per_platform)
                posts_by_platform[platform] = batch
                items.extend(batch)
                if not batch:
                    failures.append(
                        {"platform": platform, "kind": kind, "message": "接口成功但未解析到结果"}
                    )
            except Exception as exc:  # noqa: BLE001
                failures.append({"platform": platform, "kind": kind, "message": str(exc)})

        for platform, kind in kept:
            if kind != "comment":
                continue
            try:
                batch = self._search_comments(
                    platform,
                    keyword,
                    posts_by_platform.get(platform, []),
                    comment_depth,
                )
                items.extend(batch)
            except Exception as exc:  # noqa: BLE001
                failures.append({"platform": platform, "kind": kind, "message": str(exc)})

        return items, failures

    def _search_posts(self, platform: str, keyword: str, limit: int) -> list[dict[str, Any]]:
        path, builder = POST_PATHS[platform]
        payload = self.transport.post_json(path, builder(keyword, limit))
        raw_items = extract_list(payload)[:limit]
        return [normalize_item(platform, "post", item) for item in raw_items]

    def _search_comments(
        self,
        platform: str,
        keyword: str,
        posts: list[dict[str, Any]],
        comment_depth: int,
    ) -> list[dict[str, Any]]:
        if not posts:
            posts = self._search_posts(platform, keyword, max(comment_depth, 1))
        return collect_comments(self.transport, platform, posts, comment_depth)
