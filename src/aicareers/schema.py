"""Pydantic data model. Every number in the report is an Observation tied to a Source."""
from __future__ import annotations

import re
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class Confidence(str, Enum):
    A = "A"  # primary, method documented
    B = "B"  # primary but self-reported / vendor-measured, or small sample
    C = "C"  # secondary, "reported via X", or untraceable method


class Tier(str, Enum):
    primary = "primary"
    secondary = "secondary"


class Source(BaseModel):
    id: str
    name: str
    url: str
    retrieved_on: date | None = None  # None = not yet retrieved / not reachable
    tier: Tier
    status: str = "pending"  # fetched | unreachable | pending
    notes: str = ""


class Observation(BaseModel):
    id: str
    metric: str  # e.g. ai_keyword_share, ai_skill_share, salary_median_total
    role: str = "all"
    region: str
    period: str  # YYYY, YYYY-MM or YYYY-MM-DD
    value: float
    unit: str  # %, count, THB, USD, SGD, EUR, GBP
    source_id: str
    retrieved_on: date
    definition: str
    confidence: Confidence
    is_estimate: bool = False
    sample_size: int | None = None
    notes: str = ""
    reported_via: str | None = None  # set when the primary page was not reached
    skill: str | None = None  # for skill-demand metrics
    segment: str | None = None  # e.g. seniority level or occupation exposure group

    @field_validator("period")
    @classmethod
    def _period(cls, v: str) -> str:
        if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?|-Q[1-4])?", v):
            raise ValueError(f"bad period {v!r}")
        return v

    @model_validator(mode="after")
    def _secondary_is_c(self) -> "Observation":
        if self.reported_via and self.confidence != Confidence.C:
            raise ValueError("figures reported via a secondary source must be confidence C")
        return self

    @property
    def small_n(self) -> bool:
        return self.sample_size is not None and self.sample_size < 30
