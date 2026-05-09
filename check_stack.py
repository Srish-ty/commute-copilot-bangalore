from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv
from elasticsearch import Elasticsearch


ROOT = Path(__file__).resolve().parent


def check_elastic() -> dict[str, Any]:
    url = os.getenv("ELASTICSEARCH_URL", "")
    api_key = os.getenv("ELASTICSEARCH_API_KEY", "")
    if not url or not api_key:
        return {"ok": False, "reason": "Missing ELASTICSEARCH_URL or ELASTICSEARCH_API_KEY"}
    try:
        client = Elasticsearch(url, api_key=api_key)
        indices = ["commute_context", "commute_places", "commute_routes", "commute_decision_logs"]
        counts = {index: client.count(index=index)["count"] for index in indices}
        return {"ok": True, "counts": counts}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "reason": str(exc)}


def check_bedrock() -> dict[str, Any]:
    region = os.getenv("AWS_REGION", "us-east-1")
    model_ids = [
        os.getenv("BEDROCK_SUPERVISOR_MODEL", ""),
        os.getenv("BEDROCK_ROUTE_MODEL", ""),
        os.getenv("BEDROCK_LIGHT_MODEL", ""),
    ]
    model_ids = [mid for mid in model_ids if mid]
    if not model_ids:
        return {"ok": False, "reason": "Missing BEDROCK_* model env vars"}

    client = boto3.client("bedrock-runtime", region_name=region)
    results = {}
    for model_id in model_ids:
        try:
            response = client.converse(
                modelId=model_id,
                messages=[{"role": "user", "content": [{"text": "Reply with JSON: {\"ok\": true}"}]}],
                inferenceConfig={"maxTokens": 64, "temperature": 0.0},
            )
            text = response["output"]["message"]["content"][0]["text"]
            results[model_id] = {"ok": True, "sample": text[:120]}
        except (NoCredentialsError, ClientError, BotoCoreError) as exc:
            results[model_id] = {"ok": False, "reason": str(exc)}
    return {"ok": all(item["ok"] for item in results.values()), "models": results}


def main() -> None:
    load_dotenv(dotenv_path=ROOT / ".env", override=True)
    report = {"elastic": check_elastic(), "bedrock": check_bedrock()}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
