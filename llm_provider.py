from __future__ import annotations

import json
import re
from typing import Any

from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, SystemMessage


def _extract_json_blob(text: str) -> str | None:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    fenced = re.search(r"```json\s*(\{.*\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    any_obj = re.search(r"(\{.*\})", text, flags=re.DOTALL)
    if any_obj:
        return any_obj.group(1)
    return None


class LangChainReasoner:
    """Bedrock-backed JSON reasoner using LangChain."""

    def __init__(self, region_name: str, model_id: str, temperature: float = 0.2) -> None:
        self.model = ChatBedrockConverse(
            model_id=model_id,
            region_name=region_name,
            temperature=temperature,
            max_tokens=900,
        )
        self.last_error: str | None = None

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        try:
            response = self.model.invoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
            )
            content = response.content if isinstance(response.content, str) else str(response.content)
        except Exception as exc:  # noqa: BLE001
            self.last_error = str(exc)
            return {}

        blob = _extract_json_blob(content)
        if not blob:
            return {}
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            return {}
