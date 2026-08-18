from __future__ import annotations

DEFAULT_PROMPTS: list[str] = [
    "人工智能",
    "国货美妆",
    "新能源汽车",
    "夏季防晒",
    "数码评测",
    "减脂餐",
    "考研备考",
    "家居收纳",
    "咖啡测评",
    "亲子露营",
]


def normalize_prompts(values: list[str] | None) -> list[str]:
    seen: set[str] = set()
    cleaned: list[str] = []
    for raw in values or []:
        text = " ".join(str(raw).split())
        if not text or text in seen:
            continue
        if len(text) > 80:
            text = text[:80]
        seen.add(text)
        cleaned.append(text)
        if len(cleaned) >= 40:
            break
    return cleaned
