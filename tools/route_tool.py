from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_ROUTES = ROOT / "ingestion" / "sample_data" / "sample_routes.json"
KNOWN_COORDS = {
    "spice garden": (12.9585, 77.7012),
    "mg road": (12.9756, 77.6068),
    "indiranagar": (12.9784, 77.6408),
    "whitefield": (12.9698, 77.7500),
    "hsr layout": (12.9116, 77.6389),
}


class RouteOption(BaseModel):
    mode: str
    duration_min: int
    distance_km: float
    reliability_score: float


class RouteOptions(BaseModel):
    routes: list[RouteOption]


def _load_sample_routes(source: str, destination: str) -> list[dict[str, Any]]:
    records = json.loads(SAMPLE_ROUTES.read_text(encoding="utf-8"))
    source_key = source.lower()
    destination_key = destination.lower()
    matches = [
        record
        for record in records
        if record["source"].lower() == source_key and record["destination"].lower() == destination_key
    ]
    if not matches:
        matches = records[:2]
    return [
        {
            "mode": record["mode"],
            "duration_min": record["duration_min"],
            "distance_km": record["distance_km"],
            "reliability_score": record["reliability_score"],
        }
        for record in matches
    ]


def _osrm_cab_route(source: str, destination: str) -> dict[str, Any] | None:
    source_coords = KNOWN_COORDS.get(source.lower())
    destination_coords = KNOWN_COORDS.get(destination.lower())
    if not source_coords or not destination_coords:
        return None

    load_dotenv()
    base_url = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org").rstrip("/")
    src_lat, src_lon = source_coords
    dst_lat, dst_lon = destination_coords
    response = requests.get(
        f"{base_url}/route/v1/driving/{src_lon},{src_lat};{dst_lon},{dst_lat}",
        params={"overview": "false"},
        timeout=8,
    )
    response.raise_for_status()
    route = response.json()["routes"][0]
    duration_min = max(1, round(route["duration"] / 60))
    distance_km = round(route["distance"] / 1000, 1)
    reliability = 0.55 if duration_min > 35 else 0.70
    return {
        "mode": "cab",
        "duration_min": duration_min,
        "distance_km": distance_km,
        "reliability_score": reliability,
    }


def get_route_options(source: str, destination: str) -> dict[str, Any]:
    routes = _load_sample_routes(source, destination)
    try:
        live_route = _osrm_cab_route(source, destination)
        if live_route:
            routes = [live_route, *[route for route in routes if route["mode"] != "cab"]]
    except Exception:
        pass
    return RouteOptions(routes=routes).model_dump()


if __name__ == "__main__":
    print(get_route_options("Spice Garden", "MG Road"))
