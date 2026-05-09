from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "ingestion" / "sample_data" / "commute_context.json"


class ContextMatch(BaseModel):
    title: str
    content: str
    score: float


class SearchResponse(BaseModel):
    matches: list[ContextMatch]


def _fallback_search(query: str, areas: list[str]) -> list[dict[str, Any]]:
    terms = set(query.lower().split()) | {area.lower() for area in areas}
    records = json.loads(CONTEXT.read_text(encoding="utf-8"))
    scored = []
    for record in records:
        haystack = f"{record['title']} {record['content']} {record['area']} {record['category']}".lower()
        overlap = sum(1 for term in terms if term and term in haystack)
        if overlap:
            scored.append(
                {
                    "title": record["title"],
                    "content": record["content"],
                    "score": round(min(0.99, 0.55 + overlap * 0.08), 2),
                }
            )
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:5]


def _client() -> Elasticsearch | None:
    load_dotenv()
    url = os.getenv("ELASTICSEARCH_URL")
    api_key = os.getenv("ELASTICSEARCH_API_KEY")
    if not url or not api_key:
        return None
    return Elasticsearch(url, api_key=api_key)


def search_elastic_context(query: str, areas: list[str]) -> dict[str, Any]:
    client = _client()
    if not client:
        return SearchResponse(matches=_fallback_search(query, areas)).model_dump()

    try:
        response = client.search(
            index="commute_context",
            size=5,
            query={
                "bool": {
                    "should": [
                        {"multi_match": {"query": query, "fields": ["title^2", "content"]}},
                        {"terms": {"area": areas}},
                    ]
                }
            },
        )
        matches = [
            {
                "title": hit["_source"]["title"],
                "content": hit["_source"]["content"],
                "score": round(float(hit["_score"]), 2),
            }
            for hit in response["hits"]["hits"]
        ]
    except Exception:
        matches = _fallback_search(query, areas)
    return SearchResponse(matches=matches).model_dump()


if __name__ == "__main__":
    print(search_elastic_context("evening commute Spice Garden to MG Road rain metro traffic", ["Indiranagar", "Domlur", "MG Road"]))
