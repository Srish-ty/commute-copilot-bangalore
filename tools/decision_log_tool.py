from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


def _client() -> Elasticsearch | None:
    load_dotenv()
    url = os.getenv("ELASTICSEARCH_URL")
    api_key = os.getenv("ELASTICSEARCH_API_KEY")
    if not url or not api_key:
        return None
    return Elasticsearch(url, api_key=api_key)


def log_decision(decision: dict[str, Any]) -> dict[str, Any]:
    record = {
        "id": decision.get("id", str(uuid4())),
        "created_at": decision.get("created_at", datetime.now(timezone.utc).isoformat()),
        **decision,
    }
    client = _client()
    if not client:
        return {
            "logged": False,
            "reason": "Elasticsearch credentials not configured; returning demo log payload.",
            "decision": record,
        }

    client.index(index="commute_decision_logs", id=record["id"], document=record)
    return {"logged": True, "index": "commute_decision_logs", "id": record["id"]}


if __name__ == "__main__":
    print(
        log_decision(
            {
                "user_query": "I am at Spice Garden and need to reach MG Road by 6 PM.",
                "source": "Spice Garden",
                "destination": "MG Road",
                "target_time": "18:00",
                "selected_mode": "metro_walk",
                "selected_route": "Spice Garden -> Indiranagar Metro -> MG Road -> walk 900m",
                "reasoning": "Metro is more predictable than cab during evening congestion.",
                "risks": ["Moderate rain risk", "Peak-hour crowding"],
                "alternatives": ["Cab via Old Airport Road"],
                "confidence": 0.84,
            }
        )
    )
