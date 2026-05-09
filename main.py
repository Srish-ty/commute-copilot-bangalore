from __future__ import annotations

import argparse
import json

from agents.route_traffic_agent import RouteTrafficAgent
from agents.supervisor_agent import SupervisorAgent
from agents.transit_context_agent import TransitContextAgent
from agents.weather_agent import WeatherAgent
from bedrock_client import BedrockReasoner
from config import load_settings


def build_supervisor(use_bedrock: bool) -> SupervisorAgent:
    settings = load_settings()
    reasoner = BedrockReasoner(region_name=settings.aws_region) if use_bedrock else None
    weather = WeatherAgent(reasoner=reasoner, model_id=settings.bedrock_light_model)
    route = RouteTrafficAgent(reasoner=reasoner, model_id=settings.bedrock_route_model)
    transit = TransitContextAgent(reasoner=reasoner, model_id=settings.bedrock_light_model)
    return SupervisorAgent(
        reasoner=reasoner,
        model_id=settings.bedrock_supervisor_model,
        weather_agent=weather,
        route_traffic_agent=route,
        transit_agent=transit,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="CommuteCopilot Bengaluru CLI")
    parser.add_argument("query", help="Commute question, e.g. 'I am at Spice Garden and need MG Road by 6 PM'")
    parser.add_argument(
        "--use-bedrock",
        action="store_true",
        help="Use Amazon Bedrock for reasoning. Without this flag, tool-driven local fallback is used.",
    )
    args = parser.parse_args()

    supervisor = build_supervisor(use_bedrock=args.use_bedrock)
    result = supervisor.run(args.query)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
