from __future__ import annotations

import os
from datetime import datetime
from typing import Any

import requests
from dotenv import load_dotenv
from pydantic import BaseModel


BENGALURU_COORDS = {"latitude": 12.9716, "longitude": 77.5946}


class WeatherContext(BaseModel):
    condition: str
    rain_probability: float
    walking_risk: str
    weather_risk_score: float
    summary: str


def _condition_from_code(code: int | None) -> str:
    if code in {51, 53, 55, 61, 63, 65, 80, 81, 82}:
        return "rain"
    if code in {1, 2, 3, 45, 48}:
        return "cloudy"
    if code == 0:
        return "clear"
    return "cloudy"


def _fallback_weather() -> WeatherContext:
    return WeatherContext(
        condition="cloudy",
        rain_probability=0.42,
        walking_risk="medium",
        weather_risk_score=0.55,
        summary="Moderate rain risk. Walking is possible but umbrella recommended.",
    )


def get_weather_context(source: str, destination: str, target_time: str) -> dict[str, Any]:
    load_dotenv()
    base_url = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com").rstrip("/")
    try:
        response = requests.get(
            f"{base_url}/v1/forecast",
            params={
                **BENGALURU_COORDS,
                "hourly": "precipitation_probability,weather_code",
                "forecast_days": 1,
                "timezone": "Asia/Kolkata",
            },
            timeout=8,
        )
        response.raise_for_status()
        hourly = response.json()["hourly"]
        probabilities = hourly.get("precipitation_probability", [])
        codes = hourly.get("weather_code", [])
        times = hourly.get("time", [])
        target_hour = target_time[:2] if target_time else datetime.now().strftime("%H")
        index = next((i for i, value in enumerate(times) if f"T{target_hour}:" in value), 0)
        rain_probability = (probabilities[index] if probabilities else 42) / 100
        condition = _condition_from_code(codes[index] if codes else None)
    except Exception:
        return _fallback_weather().model_dump()

    walking_risk = "low"
    if rain_probability >= 0.6:
        walking_risk = "high"
    elif rain_probability >= 0.3:
        walking_risk = "medium"

    score = round(min(0.95, rain_probability + (0.12 if walking_risk == "medium" else 0.2 if walking_risk == "high" else 0.05)), 2)
    summary = (
        "High rain risk. Prefer lower walking exposure."
        if walking_risk == "high"
        else "Moderate rain risk. Walking is possible but umbrella recommended."
        if walking_risk == "medium"
        else "Low weather risk. Walking comfort looks acceptable."
    )
    return WeatherContext(
        condition=condition,
        rain_probability=round(rain_probability, 2),
        walking_risk=walking_risk,
        weather_risk_score=score,
        summary=summary,
    ).model_dump()


if __name__ == "__main__":
    print(get_weather_context("Spice Garden", "MG Road", "18:00"))
