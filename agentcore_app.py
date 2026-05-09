from __future__ import annotations

import json
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from main import build_graph_runner


app = BedrockAgentCoreApp()


def _coerce_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        prompt = payload.get("prompt")
        if isinstance(prompt, str) and prompt.strip().startswith("{"):
            try:
                nested = json.loads(prompt)
                if isinstance(nested, dict):
                    return nested
            except json.JSONDecodeError:
                pass
        return payload
    if isinstance(payload, str):
        try:
            parsed = json.loads(payload)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {"prompt": payload}
    return {}


def _as_bool(value: Any, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)


@app.entrypoint
def commutecopilot_agent(payload: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    payload = _coerce_payload(payload)
    query = payload.get("prompt") or payload.get("query") or payload.get("input")
    if not query:
        return {
            "error": "Missing prompt. Send {'prompt': 'I am at Spice Garden and need to reach MG Road by 6 PM.'}"
        }

    use_bedrock = _as_bool(payload.get("use_bedrock"), default=True)
    verbose = _as_bool(payload.get("verbose"), default=False)
    runner = build_graph_runner(use_bedrock=use_bedrock, verbose=verbose)
    return runner.run(str(query))


if __name__ == "__main__":
    app.run()
