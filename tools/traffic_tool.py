from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
HOTSPOTS = ROOT / "ingestion" / "sample_data" / "bengaluru_hotspots.json"


class TrafficRisk(BaseModel):
    traffic_risk: str
    risk_score: float
    hotspots: list[str]
    reason: str


def get_traffic_risk(route_summary: str) -> dict[str, Any]:
    summary = route_summary.lower()
    hotspots = json.loads(HOTSPOTS.read_text(encoding="utf-8"))
    matched = [item for item in hotspots if item["area"].lower() in summary or item["name"].lower() in summary]
    if not matched:
        matched = [item for item in hotspots if item["area"] in {"Domlur", "Indiranagar"}]

    risk_score = round(max(item["risk_score"] for item in matched), 2)
    traffic_risk = "high" if risk_score >= 0.7 else "medium" if risk_score >= 0.4 else "low"
    names = [item["area"] for item in matched]
    reason = f"Evening congestion risk is {traffic_risk} around {', '.join(names)}."
    return TrafficRisk(
        traffic_risk=traffic_risk,
        risk_score=risk_score,
        hotspots=names,
        reason=reason,
    ).model_dump()


if __name__ == "__main__":
    print(get_traffic_risk("Spice Garden to MG Road via Domlur and Indiranagar"))
