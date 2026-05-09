from __future__ import annotations

import json
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class BedrockReasoner:
    """Light wrapper for Bedrock runtime text reasoning."""

    def __init__(self, region_name: str) -> None:
        self.client = boto3.client("bedrock-runtime", region_name=region_name)

    def generate_json(self, model_id: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 900,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [{"role": "user", "content": [{"type": "text", "text": user_prompt}]}],
        }
        try:
            response = self.client.invoke_model(modelId=model_id, body=json.dumps(payload))
            body = json.loads(response["body"].read())
            text = body["content"][0]["text"]
            return json.loads(text)
        except (ClientError, BotoCoreError, KeyError, json.JSONDecodeError):
            return {}
