from __future__ import annotations

import math

from app.config import settings


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def estimate_openai_cost_usd(input_tokens: int, output_tokens: int) -> float:
    input_cost = (input_tokens / 1_000_000) * settings.openai_input_usd_per_1m_tokens
    output_cost = (output_tokens / 1_000_000) * settings.openai_output_usd_per_1m_tokens
    return round(input_cost + output_cost, 8)
