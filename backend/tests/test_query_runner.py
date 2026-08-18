from foxhubclaw.query_runner import QueryRunner


class FakeTransport:
    def __init__(self):
        self.calls = []

    def post_json(self, path: str, payload: dict) -> dict:
        self.calls.append((path, payload))
        if path.endswith("searchArticle") or path.endswith("workSearch") or path.endswith("searchWork"):
            return {
                "list": [
                    {
                        "title": "Hit",
                        "userName": "n",
                        "url": "https://example.com/p",
                        "likeCount": 4,
                        "photoId": "abc",
                    }
                ]
            }
        if path.endswith("commentList"):
            return {"comments": [{"content": "nice", "nickname": "c", "likeNum": 2}]}
        raise AssertionError(path)


def test_runner_skips_unsupported_and_searches_supported():
    transport = FakeTransport()
    runner = QueryRunner(api_key="ak_test", transport=transport)
    items, failures = runner.run(
        keyword="AI",
        platforms=["douyin", "tiktok", "kuaishou"],
        kinds=["post", "comment"],
        limit_per_platform=5,
        comment_depth=1,
    )
    platforms = {(item["platform"], item["kind"]) for item in items}
    assert ("douyin", "post") in platforms
    assert ("kuaishou", "post") in platforms
    assert ("kuaishou", "comment") in platforms
    assert any(fail["platform"] == "tiktok" for fail in failures)
    assert any(path.endswith("commentList") for path, _ in transport.calls)
