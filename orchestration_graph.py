from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from agents.route_traffic_agent import RouteTrafficAgent
from agents.supervisor_agent import SupervisorAgent
from agents.transit_context_agent import TransitContextAgent
from agents.weather_agent import WeatherAgent
from models import AgentBundle, CommuteRequest
from tools.decision_log_tool import log_decision


class CommuteCopilotState(TypedDict, total=False):
    user_query: str
    request: CommuteRequest
    weather: dict[str, Any]
    route_traffic: dict[str, Any]
    transit: dict[str, Any]
    decision: dict[str, Any]
    trace: list[str]


class CommuteCopilotGraphRunner:
    def __init__(
        self,
        supervisor: SupervisorAgent,
        weather_agent: WeatherAgent,
        route_traffic_agent: RouteTrafficAgent,
        transit_agent: TransitContextAgent,
        verbose: bool = False,
    ) -> None:
        self.supervisor = supervisor
        self.weather_agent = weather_agent
        self.route_traffic_agent = route_traffic_agent
        self.transit_agent = transit_agent
        self.verbose = verbose
        self.graph = self._build_graph()

    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"[CommuteCopilot] {message}")

    def _build_graph(self):
        builder = StateGraph(CommuteCopilotState)
        builder.add_node("parse_query", self._parse_query)
        builder.add_node("weather_agent", self._weather_agent_node)
        builder.add_node("route_traffic_agent", self._route_traffic_agent_node)
        builder.add_node("transit_agent", self._transit_agent_node)
        builder.add_node("supervisor_decide", self._supervisor_decide_node)
        builder.add_edge(START, "parse_query")
        builder.add_edge("parse_query", "weather_agent")
        builder.add_edge("weather_agent", "route_traffic_agent")
        builder.add_edge("route_traffic_agent", "transit_agent")
        builder.add_edge("transit_agent", "supervisor_decide")
        builder.add_edge("supervisor_decide", END)
        return builder.compile()

    def _parse_query(self, state: CommuteCopilotState) -> CommuteCopilotState:
        self._log("Supervisor parsing user query")
        req = self.supervisor.parse_user_query(state["user_query"])
        self._log(
            f"Parsed source={req.source!r}, destination={req.destination!r}, target_time={req.target_time!r}"
        )
        return {"request": req, "trace": [*state.get("trace", []), "parse_query"]}

    def _weather_agent_node(self, state: CommuteCopilotState) -> CommuteCopilotState:
        req = state["request"]
        self._log("Weather Agent fetching weather context")
        weather = self.weather_agent.run(req.source, req.destination, req.target_time)
        self._log(
            "Weather Agent returned "
            f"condition={weather.get('condition')!r}, walking_risk={weather.get('walking_risk')!r}, "
            f"risk_score={weather.get('weather_risk_score')!r}"
        )
        return {"weather": weather, "trace": [*state.get("trace", []), "weather_agent"]}

    def _route_traffic_agent_node(self, state: CommuteCopilotState) -> CommuteCopilotState:
        req = state["request"]
        self._log("Route + Traffic Agent fetching routes and Elastic traffic context")
        route_traffic = self.route_traffic_agent.run(req.source, req.destination)
        self._log(
            "Route + Traffic Agent returned "
            f"{len(route_traffic.get('routes', []))} route(s), "
            f"candidate={route_traffic.get('recommended_route_candidate')!r}, "
            f"elastic_hits={len(route_traffic.get('elastic_evidence', []))}"
        )
        return {
            "route_traffic": route_traffic,
            "trace": [*state.get("trace", []), "route_traffic_agent"],
        }

    def _transit_agent_node(self, state: CommuteCopilotState) -> CommuteCopilotState:
        req = state["request"]
        self._log("Transit Context Agent fetching metro/BMTC and Elastic context")
        transit = self.transit_agent.run(req.source, req.destination)
        self._log(
            "Transit Context Agent returned "
            f"metro_possible={transit.get('metro_possible')!r}, "
            f"source_station={transit.get('nearest_source_metro')!r}, "
            f"destination_station={transit.get('nearest_destination_metro')!r}"
        )
        return {"transit": transit, "trace": [*state.get("trace", []), "transit_agent"]}

    def _supervisor_decide_node(self, state: CommuteCopilotState) -> CommuteCopilotState:
        req = state["request"]
        self._log("Supervisor comparing evidence and creating final decision")
        evidence = AgentBundle(
            weather=state["weather"], route_traffic=state["route_traffic"], transit=state["transit"]
        )
        decision = self.supervisor.decide(req, evidence)
        self._log(
            "Supervisor selected "
            f"mode={decision.get('recommended_mode')!r}, confidence={decision.get('confidence')!r}"
        )
        decision["decision_log"] = log_decision(
            {
                "user_query": req.user_query,
                "source": req.source,
                "destination": req.destination,
                "target_time": req.target_time,
                "selected_mode": decision.get("recommended_mode", ""),
                "selected_route": decision.get("route", ""),
                "reasoning": " | ".join(decision.get("reasoning", [])),
                "risks": decision.get("risks", []),
                "alternatives": decision.get("alternatives", []),
                "confidence": decision.get("confidence", 0.0),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        self._log(f"Decision log status={decision['decision_log'].get('logged')!r}")
        decision["evidence"] = evidence.model_dump()
        return {"decision": decision, "trace": [*state.get("trace", []), "supervisor_decide"]}

    def run(self, user_query: str) -> dict[str, Any]:
        final_state = self.graph.invoke({"user_query": user_query, "trace": []})
        decision = final_state["decision"]
        decision["trace"] = final_state.get("trace", [])
        decision["bedrock_status"] = {
            "weather_agent": (
                "disabled"
                if not self.weather_agent.reasoner
                else "ok" if not self.weather_agent.reasoner.last_error else "fallback"
            ),
            "route_traffic_agent": (
                "disabled"
                if not self.route_traffic_agent.reasoner
                else "ok" if not self.route_traffic_agent.reasoner.last_error else "fallback"
            ),
            "transit_agent": (
                "disabled"
                if not self.transit_agent.reasoner
                else "ok" if not self.transit_agent.reasoner.last_error else "fallback"
            ),
            "supervisor_agent": (
                "disabled"
                if not self.supervisor.reasoner
                else "ok" if not self.supervisor.reasoner.last_error else "fallback"
            ),
        }
        decision["bedrock_errors"] = {
            key: value
            for key, value in {
                "weather_agent": None if not self.weather_agent.reasoner else self.weather_agent.reasoner.last_error,
                "route_traffic_agent": None
                if not self.route_traffic_agent.reasoner
                else self.route_traffic_agent.reasoner.last_error,
                "transit_agent": None
                if not self.transit_agent.reasoner
                else self.transit_agent.reasoner.last_error,
                "supervisor_agent": None
                if not self.supervisor.reasoner
                else self.supervisor.reasoner.last_error,
            }.items()
            if value
        }
        return decision
