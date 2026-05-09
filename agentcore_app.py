from __future__ import annotations

from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from main import build_graph_runner


app = BedrockAgentCoreApp()


@app.entrypoint
def commutecopilot_agent(payload: dict[str, Any], context: Any | None = None) -> dict[str, Any]:
    query = payload.get("prompt") or payload.get("query") or payload.get("input")
    if not query:
        return {
            "error": "Missing prompt. Send {'prompt': 'I am at Spice Garden and need to reach MG Road by 6 PM.'}"
        }

    use_bedrock = bool(payload.get("use_bedrock", True))
    verbose = bool(payload.get("verbose", False))
    runner = build_graph_runner(use_bedrock=use_bedrock, verbose=verbose)
    return runner.run(str(query))


if __name__ == "__main__":
    app.run()
