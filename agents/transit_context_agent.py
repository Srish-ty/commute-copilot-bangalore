from __future__ import annotations

from typing import Any

from agents.base import AgentBase, safe_json_extract
from tools.elastic_search_tool import search_elastic_context
from tools.transit_tool import get_transit_context


class TransitContextAgent(AgentBase):
    SYSTEM_PROMPT = (
        "You are the Transit Context Agent for Bengaluru commute planning. "
        "Return only valid JSON with keys: metro_possible, nearest_source_metro, "
        "nearest_destination_metro, last_mile_walk_min, transit_reliability, summary."
    )

    def run(self, source: str, destination: str) -> dict[str, Any]:
        base = get_transit_context(source, destination)
        context = search_elastic_context(
            f"{source} {destination} metro bmtc last mile reliability",
            [source, destination, "Indiranagar", "MG Road"],
        )
        fallback = {
            **base,
            "summary": "Metro is feasible and reliable for this route."
            if base["metro_possible"]
            else "Metro coverage is weaker; BMTC or cab may be needed.",
            "elastic_evidence": [{"title": m["title"], "score": m["score"]} for m in context["matches"]],
        }
        if not self.reasoner:
            return fallback

        prompt = (
            f"Source: {source}\nDestination: {destination}\n"
            f"Transit context: {base}\n"
            f"Elasticsearch evidence: {context}\n"
            "Summarize transit feasibility and last-mile effort."
        )
        raw = self.reasoner.generate_json(self.model_id, self.SYSTEM_PROMPT, prompt)
        return safe_json_extract(raw, fallback)
