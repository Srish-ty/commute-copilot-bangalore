from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommuteRequest(BaseModel):
    user_query: str
    source: str
    destination: str
    target_time: str = "18:00"
    preferences: list[str] = Field(default_factory=list)


class SupervisorDecision(BaseModel):
    leave_in_minutes: int
    recommended_mode: str
    route: str
    reasoning: list[str]
    risks: list[str]
    alternatives: list[dict[str, str]]
    confidence: float


class AgentBundle(BaseModel):
    weather: dict[str, Any]
    route_traffic: dict[str, Any]
    transit: dict[str, Any]
