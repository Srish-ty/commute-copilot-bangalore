from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    aws_region: str
    bedrock_supervisor_model: str
    bedrock_route_model: str
    bedrock_light_model: str
    elasticsearch_url: str
    elasticsearch_api_key: str

    @property
    def elastic_enabled(self) -> bool:
        return bool(self.elasticsearch_url and self.elasticsearch_api_key)


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        bedrock_supervisor_model=os.getenv(
            "BEDROCK_SUPERVISOR_MODEL", "anthropic.claude-3-5-sonnet-20240620-v1:0"
        ),
        bedrock_route_model=os.getenv(
            "BEDROCK_ROUTE_MODEL", "anthropic.claude-3-5-sonnet-20240620-v1:0"
        ),
        bedrock_light_model=os.getenv("BEDROCK_LIGHT_MODEL", "amazon.nova-lite-v1:0"),
        elasticsearch_url=os.getenv("ELASTICSEARCH_URL", ""),
        elasticsearch_api_key=os.getenv("ELASTICSEARCH_API_KEY", ""),
    )
