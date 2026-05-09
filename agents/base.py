from __future__ import annotations

import re
from typing import Any

from llm_provider import LangChainReasoner


def safe_json_extract(raw: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    if raw and isinstance(raw, dict):
        return raw
    return fallback


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class AgentBase:
    def __init__(self, reasoner: LangChainReasoner | None) -> None:
        self.reasoner = reasoner
