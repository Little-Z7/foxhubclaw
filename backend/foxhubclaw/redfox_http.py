from __future__ import annotations

from typing import Any, Protocol

import httpx


class Transport(Protocol):
    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def post_form(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...


class HttpTransport:
    def __init__(self, api_key: str, base_url: str = "https://redfox.hk", timeout: float = 45.0):
        self.client = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "REDFOX_API_KEY": api_key,
                "X-API-Key": api_key,
                "User-Agent": "FoxHubClaw/0.1",
            },
        )

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._unwrap(self.client.post(path, json=payload))

    def post_form(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._unwrap(
            self.client.post(
                path,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        )

    def _unwrap(self, response: httpx.Response) -> dict[str, Any]:
        if response.status_code == 401:
            raise RuntimeError("RedFox Key 无效或已失效")
        if response.status_code == 429:
            raise RuntimeError("RedFox 调用频率超限，请稍后重试")
        if response.status_code >= 500:
            raise RuntimeError(f"RedFox 服务异常 ({response.status_code})")
        try:
            body = response.json()
        except ValueError as exc:
            raise RuntimeError("RedFox 返回无法解析") from exc
        code = body.get("code")
        if code not in (None, 2000, 200, 0):
            raise RuntimeError(body.get("msg") or f"RedFox 业务错误 {code}")
        data = body.get("data", body)
        return data if isinstance(data, dict) else {"list": data}

    def close(self) -> None:
        self.client.close()
