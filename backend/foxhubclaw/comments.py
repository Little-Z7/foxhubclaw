from __future__ import annotations

import re
import time
from typing import Any

from foxhubclaw.normalize import extract_list, normalize_item


def work_id_of(post: dict[str, Any]) -> str:
    url = str(post.get("url") or "")
    weibo = re.search(r"weibo\.com/\d+/([A-Za-z0-9]+)", url)
    if weibo:
        return weibo.group(1)
    bili = re.search(r"(BV[A-Za-z0-9]+)", url)
    if bili:
        return bili.group(1)
    extra = post.get("extra") or {}
    return str(extra.get("work_id") or "").strip()


def _post_form(transport: Any, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    fn = getattr(transport, "post_form", None)
    if fn is not None:
        return fn(path, payload)
    return transport.post_json(path, payload)


def _normalize_comments(platform: str, post: dict[str, Any], raw_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    for raw in raw_items:
        item = normalize_item(platform, "comment", raw)
        if item["url"] == "":
            item["url"] = post.get("url") or ""
        comments.append(item)
    return comments


def fetch_kuaishou_comments(transport: Any, work_id: str) -> list[dict[str, Any]]:
    payload = transport.post_json(
        "/story/api/ks/ability/commentList",
        {"opusId": work_id, "cursor": "", "source": "FoxHubClaw"},
    )
    return extract_list(payload)


def fetch_weibo_comments(transport: Any, work_id: str) -> list[dict[str, Any]]:
    payload = transport.post_json(
        "/story/api/weibo/ability/commentList",
        {"opusId": work_id, "maxCursor": "0", "maxIdType": "0", "source": "FoxHubClaw"},
    )
    comments = payload.get("comments")
    if isinstance(comments, list):
        return [item for item in comments if isinstance(item, dict)]
    return extract_list(payload)


def fetch_bilibili_comments(transport: Any, work_id: str, attempts: int = 30, interval: float = 2.0) -> list[dict[str, Any]]:
    submitted = transport.post_json(
        "/story/api/bili/commentSubmit",
        {
            "opusId": work_id,
            "sortType": "2",
            "dataNum": "20",
            "offset": "0",
            "source": "FoxHubClaw",
        },
    )
    immediate = extract_list(submitted)
    if immediate:
        return immediate
    task_id = str(submitted.get("taskId") or submitted.get("task_id") or "")
    if not task_id:
        return []
    for _ in range(attempts):
        time.sleep(interval)
        result = _post_form(
            transport,
            "/story/api/bili/commentResult",
            {"taskId": task_id, "source": "FoxHubClaw"},
        )
        comments = extract_list(result)
        status = str(result.get("status") or result.get("state") or "").lower()
        if comments:
            return comments
        if status in {"pending", "processing", "running", ""}:
            continue
        return []
    raise RuntimeError("B站评论获取超时")


FETCHERS = {
    "kuaishou": fetch_kuaishou_comments,
    "weibo": fetch_weibo_comments,
    "bilibili": fetch_bilibili_comments,
}


def _comment_targets(posts: list[dict[str, Any]], comment_depth: int) -> list[dict[str, Any]]:
    ranked = sorted(
        posts,
        key=lambda post: (int(post.get("comments") or 0), int(post.get("likes") or 0)),
        reverse=True,
    )
    hot = [post for post in ranked if int(post.get("comments") or 0) > 0]
    return (hot or ranked)[:comment_depth]


def collect_comments(
    transport: Any,
    platform: str,
    posts: list[dict[str, Any]],
    comment_depth: int,
) -> list[dict[str, Any]]:
    fetcher = FETCHERS.get(platform)
    if fetcher is None:
        raise RuntimeError("该平台暂无评论检索")
    targets = _comment_targets(posts, comment_depth)
    if platform == "bilibili" and targets and all(int(post.get("comments") or 0) <= 0 for post in targets):
        return []
    comments: list[dict[str, Any]] = []
    errors: list[Exception] = []
    for post in targets:
        work_id = work_id_of(post)
        if not work_id:
            continue
        try:
            comments.extend(_normalize_comments(platform, post, fetcher(transport, work_id)))
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)
    if not comments and errors:
        raise errors[-1]
    return comments
