from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
METRO = ROOT / "ingestion" / "sample_data" / "metro_stations.json"


class TransitContext(BaseModel):
    metro_possible: bool
    nearest_source_metro: str
    nearest_destination_metro: str
    last_mile_walk_min: int
    transit_reliability: float


def get_transit_context(source: str, destination: str) -> dict[str, Any]:
    stations = json.loads(METRO.read_text(encoding="utf-8"))
    station_names = {station["area"].lower(): station["name"] for station in stations}

    source_key = source.lower()
    destination_key = destination.lower()
    nearest_source = station_names.get(source_key, "Indiranagar")
    nearest_destination = station_names.get(destination_key, "MG Road")
    metro_possible = destination_key in station_names or "mg road" in destination_key
    last_mile_walk_min = 9 if nearest_destination == "MG Road" else 12
    reliability = 0.87 if metro_possible else 0.62

    return TransitContext(
        metro_possible=metro_possible,
        nearest_source_metro=nearest_source,
        nearest_destination_metro=nearest_destination,
        last_mile_walk_min=last_mile_walk_min,
        transit_reliability=reliability,
    ).model_dump()


if __name__ == "__main__":
    print(get_transit_context("Spice Garden", "MG Road"))
