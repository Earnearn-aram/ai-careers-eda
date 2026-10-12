"""Currency conversion. Rates are explicit inputs with a date and source, never implicit."""
from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel

ECB_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
KEEP = ("USD", "EUR", "GBP", "CHF", "SGD", "THB", "HKD")


class FxRate(BaseModel):
    currency: str
    usd_per_unit: float
    as_of: str
    source: str = "ECB euro foreign exchange reference rates"
    source_url: str = ECB_URL


def from_ecb_xml(path: Path) -> dict[str, FxRate]:
    """Cross rates via EUR: usd_per_unit = (USD per EUR) / (unit per EUR). Reference rates, not tradable quotes."""
    xml = path.read_text()
    as_of = re.search(r"time='([\d-]+)'", xml).group(1)
    per_eur = {m.group(1): float(m.group(2)) for m in re.finditer(r"currency='(\w+)' rate='([\d.]+)'", xml)}
    per_eur["EUR"] = 1.0
    return {c: FxRate(currency=c, usd_per_unit=round(per_eur["USD"] / per_eur[c], 8), as_of=as_of) for c in KEEP}


def to_usd(amount: float, rate: FxRate) -> float:
    return amount * rate.usd_per_unit
