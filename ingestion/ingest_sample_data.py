from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers


ROOT = Path(__file__).resolve().parent
SAMPLE_DATA = ROOT / "sample_data"


def get_client() -> Elasticsearch:
    load_dotenv()
    url = os.getenv("ELASTICSEARCH_URL")
    api_key = os.getenv("ELASTICSEARCH_API_KEY")
    if not url or not api_key:
        raise RuntimeError("Set ELASTICSEARCH_URL and ELASTICSEARCH_API_KEY in .env")
    return Elasticsearch(url, api_key=api_key)


def read_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def bulk_actions(index: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"_index": index, "_id": record["id"], "_source": record} for record in records]


def ingest() -> None:
    client = get_client()

    places = []
    places.extend(read_json(SAMPLE_DATA / "bengaluru_hotspots.json"))
    places.extend(read_json(SAMPLE_DATA / "metro_stations.json"))
    places.extend(read_json(SAMPLE_DATA / "parking_zones.json"))

    context_path = SAMPLE_DATA / "commute_context.embedded.json"
    routes_path = SAMPLE_DATA / "sample_routes.embedded.json"
    context = read_json(context_path if context_path.exists() else SAMPLE_DATA / "commute_context.json")
    routes = read_json(routes_path if routes_path.exists() else SAMPLE_DATA / "sample_routes.json")

    actions = []
    actions.extend(bulk_actions("commute_places", places))
    actions.extend(bulk_actions("commute_context", context))
    actions.extend(bulk_actions("commute_routes", routes))
    helpers.bulk(client, actions)
    print(f"ingested {len(actions)} records")


if __name__ == "__main__":
    ingest()
