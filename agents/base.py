from __future__ import annotations

import re
from typing import Any

from bedrock_client import BedrockReasoner


def safe_json_extract(raw: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    if raw and isinstance(raw, dict):
        return raw
    return fallback


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


class AgentBase:
    def __init__(self, reasoner: BedrockReasoner | None, model_id: str) -> None:
        self.reasoner = reasoner
        self.model_id = model_id
