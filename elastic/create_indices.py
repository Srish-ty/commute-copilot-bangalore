from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


ROOT = Path(__file__).resolve().parent
MAPPINGS = ROOT / "mappings"
INDEX_MAPPINGS = {
    "commute_context": "commute_context.json",
    "commute_places": "commute_places.json",
    "commute_routes": "commute_routes.json",
    "commute_decision_logs": "commute_decision_logs.json",
}


def get_client() -> Elasticsearch:
    load_dotenv()
    url = os.getenv("ELASTICSEARCH_URL")
    api_key = os.getenv("ELASTICSEARCH_API_KEY")
    if not url or not api_key:
        raise RuntimeError("Set ELASTICSEARCH_URL and ELASTICSEARCH_API_KEY in .env")
    return Elasticsearch(url, api_key=api_key)


def create_indices(recreate: bool = False) -> None:
    client = get_client()
    for index_name, mapping_file in INDEX_MAPPINGS.items():
        mapping = json.loads((MAPPINGS / mapping_file).read_text(encoding="utf-8"))
        if client.indices.exists(index=index_name):
            if not recreate:
                print(f"exists: {index_name}")
                continue
            client.indices.delete(index=index_name)
        client.indices.create(index=index_name, **mapping)
        print(f"created: {index_name}")


if __name__ == "__main__":
    create_indices(recreate=os.getenv("RECREATE_INDICES") == "true")
