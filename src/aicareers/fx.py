"""Currency conversion. Rates are explicit inputs with a date and source, never implicit."""
from __future__ import annotations

from pydantic import BaseModel


class FxRate(BaseModel):
    currency: str
    usd_per_unit: float
    as_of: str
    source: str
    source_url: str


# Populated from data/fx_rates.json by build.py; no rate is hard-coded here.
def to_usd(amount: float, rate: FxRate) -> float:
    return amount * rate.usd_per_unit
