from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from agents.base import AgentBase, normalize_text, safe_json_extract
from models import AgentBundle, CommuteRequest, SupervisorDecision


class SupervisorAgent(AgentBase):
    SYSTEM_PROMPT = (
        "You are the CommuteCopilot Supervisor Agent. "
        "Always reason from specialist evidence and return only valid JSON with keys: "
        "leave_in_minutes, recommended_mode, route, reasoning, risks, alternatives, confidence."
    )

    def parse_user_query(self, query: str) -> CommuteRequest:
        compact = normalize_text(query)
        source = "Spice Garden"
        destination = "MG Road"
        target_time = "18:00"
        match = re.search(r"from (.+?) to (.+?)(?: by| at|$)", compact, flags=re.IGNORECASE)
        if match:
            source = match.group(1).strip()
            destination = match.group(2).strip()
        at_match = re.search(r"\bby\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|AM|PM)?)", compact)
        if at_match:
            target_time = at_match.group(1)
        return CommuteRequest(
            user_query=query,
            source=source,
            destination=destination,
            target_time=target_time,
            preferences=[],
        )

    def fallback_decision(self, req: CommuteRequest, evidence: AgentBundle) -> SupervisorDecision:
        top_route = evidence.route_traffic["routes"][0]
        weather = evidence.weather
        transit = evidence.transit
        leave_in_minutes = 18 if top_route["mode"] == "metro_walk" else 10
        route_text = (
            f"{req.source} -> {transit['nearest_source_metro']} Metro -> "
            f"{transit['nearest_destination_metro']} -> walk last kilometre"
            if top_route["mode"] in {"metro_walk", "metro"}
            else f"{req.source} -> {req.destination} by {top_route['mode']}"
        )
        confidence = round(
            min(
                0.95,
                0.45
                + (top_route["reliability"] * 0.35)
                + (transit["transit_reliability"] * 0.15)
                - (weather["weather_risk_score"] * 0.08),
            ),
            2,
        )
        return SupervisorDecision(
            leave_in_minutes=leave_in_minutes,
            recommended_mode=top_route["mode"],
            route=route_text,
            reasoning=[
                "Selected option has better reliability under Bengaluru peak variability.",
                f"Traffic risk on alternatives is higher ({top_route['traffic_risk']}).",
                f"Weather walking risk is {weather['walking_risk']}.",
                f"Transit reliability observed at {transit['transit_reliability']}.",
            ],
            risks=[
                "Last-mile comfort may drop if rain intensifies.",
                "Peak-hour crowding may affect boarding comfort.",
            ],
            alternatives=[
                {
                    "mode": route["mode"],
                    "reason": f"Duration {route['duration_min']} min with reliability {route['reliability']}.",
                }
                for route in evidence.route_traffic["routes"][1:3]
            ],
            confidence=confidence,
        )

    def decide(self, req: CommuteRequest, evidence: AgentBundle) -> dict[str, Any]:
        fallback = self.fallback_decision(req, evidence).model_dump()
        if not self.reasoner:
            decision = fallback
        else:
            prompt = (
                f"User query: {req.user_query}\n"
                f"Parsed request: {req.model_dump()}\n"
                f"Weather evidence: {evidence.weather}\n"
                f"Route/traffic evidence: {evidence.route_traffic}\n"
                f"Transit evidence: {evidence.transit}\n"
                "Prefer predictable commute over shortest one."
            )
            decision = safe_json_extract(self.reasoner.generate_json(self.SYSTEM_PROMPT, prompt), fallback)

        decision["computed_leave_time"] = (
            datetime.now() + timedelta(minutes=int(decision.get("leave_in_minutes", 0)))
        ).strftime("%H:%M")
        return decision
