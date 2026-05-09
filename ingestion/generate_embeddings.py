from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Iterable

import requests
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
SAMPLE_DATA = ROOT / "sample_data"
EMBEDDING_DIMS = 1024


def fallback_embedding(text: str, dims: int = EMBEDDING_DIMS) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    for i in range(dims):
        byte = digest[i % len(digest)]
        values.append((byte / 255.0) - 0.5)
    return values


def get_jina_embeddings(texts: Iterable[str]) -> list[list[float]]:
    load_dotenv()
    api_key = os.getenv("JINA_API_KEY")
    model = os.getenv("JINA_EMBEDDING_MODEL", "jina-embeddings-v5-text-small")
    text_list = list(texts)
    if not api_key:
        return [fallback_embedding(text) for text in text_list]

    response = requests.post(
        "https://api.jina.ai/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "input": text_list},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()["data"]
    return [item["embedding"] for item in data]


def embed_context_file() -> Path:
    source = SAMPLE_DATA / "commute_context.json"
    output = SAMPLE_DATA / "commute_context.embedded.json"
    records = json.loads(source.read_text(encoding="utf-8"))
    texts = [f"{record['title']}\n{record['content']}" for record in records]
    for record, embedding in zip(records, get_jina_embeddings(texts), strict=True):
        record["embedding"] = embedding
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return output


def embed_routes_file() -> Path:
    source = SAMPLE_DATA / "sample_routes.json"
    output = SAMPLE_DATA / "sample_routes.embedded.json"
    records = json.loads(source.read_text(encoding="utf-8"))
    texts = [record["route_summary"] for record in records]
    for record, embedding in zip(records, get_jina_embeddings(texts), strict=True):
        record["embedding"] = embedding
    output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(f"wrote: {embed_context_file()}")
    print(f"wrote: {embed_routes_file()}")
