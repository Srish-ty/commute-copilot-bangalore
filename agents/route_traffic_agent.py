from __future__ import annotations

from typing import Any

from agents.base import AgentBase, safe_json_extract
from tools.elastic_search_tool import search_elastic_context
from tools.route_tool import get_route_options
from tools.traffic_tool import get_traffic_risk


class RouteTrafficAgent(AgentBase):
    SYSTEM_PROMPT = (
        "You are the Route + Traffic Agent for Bengaluru commute planning. "
        "Return only valid JSON with keys: recommended_route_candidate, routes, elastic_evidence."
    )

    def run(self, source: str, destination: str) -> dict[str, Any]:
        route_options = get_route_options(source, destination)
        enriched_routes = []
        for route in route_options["routes"]:
            summary = f"{source} to {destination} via mode {route['mode']}"
            traffic = get_traffic_risk(summary)
            parking_risk = "high" if route["mode"] == "cab" else "none"
            enriched_routes.append(
                {
                    **route,
                    "traffic_risk": traffic["traffic_risk"],
                    "parking_risk": parking_risk,
                    "reliability": route["reliability_score"],
                    "reason": traffic["reason"],
                }
            )
        enriched_routes.sort(key=lambda item: (-item["reliability"], item["duration_min"]))
        top = enriched_routes[0]
        areas = ["Domlur", "Indiranagar", "MG Road", source, destination]
        elastic_hits = search_elastic_context(
            f"{source} {destination} evening commute traffic parking metro", areas
        )
        fallback = {
            "recommended_route_candidate": top["mode"],
            "routes": enriched_routes,
            "elastic_evidence": [
                {"title": m["title"], "score": m["score"]} for m in elastic_hits["matches"]
            ],
        }
        if not self.reasoner:
            return fallback

        prompt = (
            f"Source: {source}\nDestination: {destination}\n"
            f"Route options and risks: {enriched_routes}\n"
            f"Elasticsearch evidence: {elastic_hits}\n"
            "Prefer predictable route over shortest route."
        )
        raw = self.reasoner.generate_json(self.SYSTEM_PROMPT, prompt)
        return safe_json_extract(raw, fallback)
