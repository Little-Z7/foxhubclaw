from foxhubclaw.comments import collect_comments, work_id_of


def test_work_id_from_extra_and_weibo_url():
    assert work_id_of({"extra": {"work_id": "BV1xx"}}) == "BV1xx"
    assert work_id_of({"url": "https://weibo.com/1784473157/R8X4f2lnq", "extra": {"work_id": "12345"}}) == "R8X4f2lnq"
    assert work_id_of({"url": "https://www.bilibili.com/video/BV1xx411c7mD", "extra": {}}) == "BV1xx411c7mD"


class _NoopTransport:
    def __init__(self):
        self.calls = []

    def post_json(self, path: str, payload: dict) -> dict:
        self.calls.append(path)
        raise AssertionError(path)


def test_bilibili_skips_zero_comment_posts():
    posts = [
        {
            "comments": 0,
            "likes": 1,
            "url": "https://www.bilibili.com/video/BV1xx411c7mD",
            "extra": {"work_id": "BV1xx411c7mD"},
        }
    ]
    transport = _NoopTransport()
    assert collect_comments(transport, "bilibili", posts, 1) == []
    assert transport.calls == []
