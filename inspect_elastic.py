from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


INDICES = ["commute_context", "commute_places", "commute_routes", "commute_decision_logs"]
ROOT = Path(__file__).resolve().parent


def without_embedding(doc: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in doc.items() if key != "embedding"}


def main() -> None:
    load_dotenv(dotenv_path=ROOT / ".env", override=True)
    client = Elasticsearch(os.getenv("ELASTICSEARCH_URL"), api_key=os.getenv("ELASTICSEARCH_API_KEY"))
    for index in INDICES:
        count = client.count(index=index)["count"]
        print(f"\n{index}: {count} document(s)")
        response = client.search(index=index, size=3, query={"match_all": {}})
        for hit in response["hits"]["hits"]:
            print(json.dumps(without_embedding(hit["_source"]), indent=2))


if __name__ == "__main__":
    main()
