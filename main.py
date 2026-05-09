from __future__ import annotations

import argparse
import json

from agents.route_traffic_agent import RouteTrafficAgent
from agents.supervisor_agent import SupervisorAgent
from agents.transit_context_agent import TransitContextAgent
from agents.weather_agent import WeatherAgent
from config import load_settings
from llm_provider import LangChainReasoner
from orchestration_graph import CommuteCopilotGraphRunner


def build_graph_runner(use_bedrock: bool) -> CommuteCopilotGraphRunner:
    settings = load_settings()
    supervisor_reasoner = None
    route_reasoner = None
    light_reasoner = None

    if use_bedrock:
        supervisor_reasoner = LangChainReasoner(
            region_name=settings.aws_region,
            model_id=settings.bedrock_supervisor_model,
        )
        route_reasoner = LangChainReasoner(
            region_name=settings.aws_region,
            model_id=settings.bedrock_route_model,
        )
        light_reasoner = LangChainReasoner(
            region_name=settings.aws_region,
            model_id=settings.bedrock_light_model,
        )

    supervisor = SupervisorAgent(reasoner=supervisor_reasoner)
    weather = WeatherAgent(reasoner=light_reasoner)
    route = RouteTrafficAgent(reasoner=route_reasoner)
    transit = TransitContextAgent(reasoner=light_reasoner)
    return CommuteCopilotGraphRunner(
        supervisor=supervisor,
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

    runner = build_graph_runner(use_bedrock=args.use_bedrock)
    result = runner.run(args.query)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
