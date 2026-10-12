import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from aicareers.build import ROOT, collect, load_sources
from aicareers.schema import Confidence, Observation


@pytest.fixture(scope="module")
def obs():
    return collect()


def test_every_observation_has_known_source(obs):
    ids = {s.id for s in load_sources()}
    assert {o.source_id for o in obs} <= ids


def test_ids_unique(obs):
    assert len({o.id for o in obs}) == len(obs)


def test_secondary_or_unfetched_sources_are_confidence_c(obs):
    src = {s.id: s for s in load_sources()}
    for o in obs:
        if src[o.source_id].status != "fetched" or src[o.source_id].tier.value == "secondary":
            assert o.confidence == Confidence.C, o.id


def test_one_unit_and_definition_family_per_metric(obs):
    """A metric must not mix units; different definitions need different metric names."""
    units = {}
    for o in obs:
        if o.metric.startswith("salary"):
            continue  # pay is shown per currency, never merged
        units.setdefault(o.metric, set()).add(o.unit)
    assert all(len(u) == 1 for u in units.values()), units


def test_indeed_and_lightcast_not_same_metric(obs):
    m = {o.source_id: o.metric for o in obs if o.source_id in ("indeed_ai_tracker", "stanford_ai_index_2026")}
    assert m["indeed_ai_tracker"] != m["stanford_ai_index_2026"]


def test_no_interpolated_months(obs):
    """Indeed monthly series must have no internal gaps (we do not fill any)."""
    by = {}
    for o in obs:
        if o.source_id == "indeed_ai_tracker":
            by.setdefault(o.region, []).append(o.period)
    for c, ps in by.items():
        ps.sort()
        y, m = map(int, ps[0].split("-"))
        for p in ps:
            assert p == f"{y:04d}-{m:02d}", (c, p)
            m += 1
            if m == 13:
                y, m = y + 1, 1


def test_reported_via_forces_c():
    with pytest.raises(ValidationError):
        Observation(id="x", metric="m", region="US", period="2025", value=1, unit="%", source_id="s",
                    retrieved_on="2026-10-12", definition="d", confidence="A", reported_via="blog")


def test_small_n_flag(obs):
    assert next(o for o in obs if o.id == "lv-ds-TH").small_n


def test_site_json_matches_build(obs):
    p = ROOT / "site" / "data" / "observations.json"
    assert len(json.loads(p.read_text())) == len(obs)


def test_site_prose_uses_neutral_words():
    banned = re.compile(r"\b(boom\w*|collaps\w*|crisis|plummet\w*|skyrocket\w*)\b", re.I)
    for f in (ROOT / "site").rglob("*.html"):
        assert not banned.search(f.read_text()), f
