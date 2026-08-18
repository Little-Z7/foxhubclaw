from foxhubclaw.query_runner import QueryRunner


class FakeTransport:
    def __init__(self):
        self.calls = []

    def post_json(self, path: str, payload: dict) -> dict:
        self.calls.append(("json", path, payload))
        if path.endswith(("searchArticle", "workSearch", "searchWork", "search")):
            return {
                "list": [
                    {
                        "title": "Hit",
                        "userName": "n",
                        "url": "https://weibo.com/1/Abcde",
                        "likeCount": 4,
                        "commentNum": 6,
                        "photoId": "abc",
                        "bvId": "BV1xx411c7mD",
                    }
                ]
            }
        if path.endswith("commentList") or path.endswith("commentSubmit"):
            return {"commentList": [{"content": "nice", "nickname": "c", "likeNum": 2}]}
        raise AssertionError(path)

    def post_form(self, path: str, payload: dict) -> dict:
        self.calls.append(("form", path, payload))
        return {"commentList": [{"content": "polled", "nickname": "c"}]}


def test_runner_skips_unsupported_and_searches_supported():
    transport = FakeTransport()
    runner = QueryRunner(api_key="ak_test", transport=transport)
    items, failures = runner.run(
        keyword="AI",
        platforms=["douyin", "tiktok", "kuaishou", "bilibili", "weibo"],
        kinds=["post", "comment"],
        limit_per_platform=5,
        comment_depth=1,
    )
    platforms = {(item["platform"], item["kind"]) for item in items}
    assert ("douyin", "post") in platforms
    assert ("kuaishou", "post") in platforms
    assert ("kuaishou", "comment") in platforms
    assert ("bilibili", "comment") in platforms
    assert ("weibo", "post") in platforms
    assert ("weibo", "comment") in platforms
    assert any(fail["platform"] == "tiktok" for fail in failures)
    assert any(path.endswith("commentList") for _, path, _ in transport.calls)
    assert any(path.endswith("commentSubmit") for _, path, _ in transport.calls)


class EmptyTransport:
    def post_json(self, path: str, payload: dict) -> dict:
        return {"list": []}


def test_empty_platform_is_reported_as_failure():
    items, failures = QueryRunner(api_key="ak_test", transport=EmptyTransport()).run(
        keyword="AI",
        platforms=["douyin"],
        kinds=["post"],
    )
    assert items == []
    assert any(fail["platform"] == "douyin" and "未解析到结果" in fail["message"] for fail in failures)
