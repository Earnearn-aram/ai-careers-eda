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
    m = {o.source_id: o.metric for o in obs if o.source_id in ("indeed_ai_tracker", "owid_lightcast_ai_index_2026")}
    assert m["indeed_ai_tracker"] != m["owid_lightcast_ai_index_2026"]


def test_lightcast_values_are_single_edition(obs):
    """Lightcast shares must all come from one AI Index edition (skill list changes yearly)."""
    srcs = {o.source_id for o in obs if o.metric == "ai_skill_share"}
    assert srcs == {"owid_lightcast_ai_index_2026"}


def test_thailand_not_invented_in_lightcast_or_indeed(obs):
    for o in obs:
        if o.metric in ("ai_skill_share", "ai_keyword_share"):
            assert o.region != "TH"


def test_owid_matches_ai_index_figure_labels(obs):
    """AI Index 2026 Figure 4.4.2 labels (2025) as read from the report PDF text."""
    fig = {"AU": 1.78, "CH": 1.59, "MX": 1.38, "BE": 1.36, "IT": 1.33, "DE": 1.13, "NL": 1.04, "FR": 0.99, "AT": 0.84, "NZ": 0.81, "HR": 0.38}
    got = {o.region: o.value for o in obs if o.metric == "ai_skill_share" and o.period == "2025"}
    for c, v in fig.items():
        assert abs(got[c] - v) < 0.006, c


def test_levels_us_ai_engineer_page_values(obs):
    o = {x.id: x for x in obs}
    assert o["levels-aillmengineer-US-median"].value == 151000 and o["levels-aillmengineer-US-median"].sample_size == 331


def test_levels_inferred_region_is_confidence_c(obs):
    for o in obs:
        if o.source_id == "levels_fyi" and "requested URL" in o.notes:
            assert o.confidence == Confidence.C


def test_fx_rates_have_date_and_source():
    from aicareers.fx import from_ecb_xml
    r = from_ecb_xml(ROOT / "data" / "raw" / "ecb" / "eurofxref-daily.xml")
    assert r["USD"].usd_per_unit == 1.0 and r["THB"].usd_per_unit < 0.05 and all(x.as_of and x.source_url for x in r.values())


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


def test_manual_loader_validates(tmp_path):
    from aicareers.ingest import manual
    hdr = "id,metric,role,region,period,value,unit,source_id,retrieved_on,definition,confidence,is_estimate,sample_size,notes\n"
    (tmp_path / "a.csv").write_text(hdr + "t1,salary_median_total,Data Scientist,TH,2026,\"1,000,000\",THB,levels_fyi,2026-10-12,Median total comp,B,false,12,page 3\n")
    o = manual.load(tmp_path)
    assert o[0].value == 1_000_000 and o[0].small_n
    (tmp_path / "b.csv").write_text(hdr + "t2,m,all,TH,2026-13,1,%,s,2026-10-12,d,B,false,,\n")
    with pytest.raises(ValueError, match="b.csv line 2"):
        manual.load(tmp_path)


def test_manual_rows_reference_known_sources(obs):
    ids = {s.id for s in load_sources()}
    assert all(o.source_id in ids for o in obs)


def test_thai_rows_split_cleanly_between_read_pages_and_search_summaries(obs):
    th_src = {"robert_walters_th_2026", "michaelpage_th", "depa_digital_survey_2025", "tdri_ai_labour_2025"}
    rows = [o for o in obs if o.source_id in th_src]
    assert rows
    for o in rows:
        if o.reported_via:  # seen only in a search summary: unverified
            assert o.confidence == Confidence.C, o.id
        else:  # read on the page: must name it
            assert o.notes.count("http") >= 1, o.id
    assert "ai_posting_share_tdri" not in {o.metric for o in obs if o.metric in ("ai_skill_share", "ai_keyword_share")}


def test_rw_calculator_claims_in_prose_match_data(obs):
    by = {}
    for o in obs:
        if o.metric in ("pay_range_low_base", "pay_range_high_base"):
            title, yr = o.segment.rsplit(" (", 1)
            by.setdefault(title, {}).setdefault(yr.rstrip(")"), {})[o.metric] = o.value
    assert all(v["2025"]["pay_range_low_base"] < v["2025"]["pay_range_high_base"] for v in by.values())
    changed = {t for t, v in by.items() if v["2025"] != v["2026"]}
    assert changed == {"Head of Product / Chief of Product", "Head of Software Development", "Senior Product Manager"}
    ai = {"AI Engineer", "Senior AI Engineer", "Head of AI", "Chief of AI"}
    assert ai <= set(by) and not (ai & changed)


def test_site_has_licence_section_and_levels_attribution():
    idx = (ROOT / "site" / "index.html").read_text()
    assert 'id="licences"' in idx and "not legal advice" in idx
    assert "Data source: Levels.fyi" in idx
