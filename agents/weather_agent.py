from __future__ import annotations

from typing import Any

from agents.base import AgentBase, safe_json_extract
from tools.weather_tool import get_weather_context


class WeatherAgent(AgentBase):
    SYSTEM_PROMPT = (
        "You are the Weather Agent for Bengaluru commute planning. "
        "Return only valid JSON with keys: condition, rain_probability, walking_risk, "
        "weather_risk_score, summary."
    )

    def run(self, source: str, destination: str, target_time: str) -> dict[str, Any]:
        tool_data = get_weather_context(source, destination, target_time)
        if not self.reasoner:
            return tool_data

        prompt = (
            f"Source: {source}\nDestination: {destination}\nTarget time: {target_time}\n"
            f"Tool weather context: {tool_data}\n"
            "Refine wording if needed but keep numeric values trustworthy."
        )
        raw = self.reasoner.generate_json(self.SYSTEM_PROMPT, prompt)
        return safe_json_extract(raw, tool_data)
