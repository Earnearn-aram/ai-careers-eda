"""Seed figures from PLAN.md section 4. NOT verified against primary pages.

Every row is confidence C with `reported_via` set. When a primary page is later fetched, replace
the row (keep the id history in notes) and raise the confidence.
"""
from __future__ import annotations

from datetime import date

from ..schema import Confidence, Observation

R = date(2026, 10, 12)
VIA = "PLAN.md seed list (first research pass, 12 Oct 2026); primary page not re-fetched"
LC_DEF = "Share of job postings requiring at least one AI skill (Lightcast, via Stanford AI Index)."


def _o(id, metric, region, period, value, unit, src, defn, role="all", **kw):
    return Observation(id=id, metric=metric, role=role, region=region, period=period, value=value,
                       unit=unit, source_id=src, retrieved_on=R, definition=defn,
                       confidence=Confidence.C, reported_via=kw.pop("via", VIA), **kw)


def _pay(id, role, region, value, unit, src, defn, **kw):
    d = defn.lower()
    metric = "salary_median_total" if d.startswith("median") else "salary_range_bound" if "end of" in d else "salary_average"
    return _o(id, metric, region, "2026", value, unit, src, defn, role=role, **kw)


def load() -> list[Observation]:
    A26, A25 = "stanford_ai_index_2026", "stanford_ai_index_2025"
    o = [
        _o("th-talent-51", "org_share_cites_talent_shortage", "TH", "2026-05", 51.0, "%", "aws_summit_bkk_2026", "Share of organisations citing talent shortage as top barrier to AI adoption (AWS Summit Bangkok, May 2026). Employer survey, context only."),
        _o("th-ai-grads", "ai_graduates_per_year", "TH", "2026", 1500.0, "count", "plan_seed_2026_10_12", "Approximate AI graduates per year in Thailand.", is_estimate=True, notes="Origin unverified."),
        _o("th-invest-79", "org_share_plan_ai_invest_up_50", "TH", "2026", 79.0, "%", "alibaba_nielseniq_apac", "Share of Thai enterprises planning to raise AI investment by 50% or more (Alibaba Cloud / NielsenIQ). Survey, context only."),
        # Thailand leads found via web search summaries (pages not fetched; hosts blocked). Confidence C, hidden by default.
        _o("th-rw-skill-67", "org_share_cites_skill_shortage", "TH", "2026", 67.0, "%", "robert_walters_th_2026", "Share of organisations citing lack of skilled and experienced candidates as the primary hiring obstacle (Robert Walters Thailand 2026 survey). Reported as 'over 67%'. All sectors, not AI-specific.", is_estimate=True, via="The Story Thailand article quoting Robert Walters (search-result summary; page not fetched)"),
        _o("th-depa-sw-need", "software_workforce_per_year", "TH", "2025", 21450.0, "count", "depa_digital_survey_2025", "New people needed per year by software and software services (DEPA 2025 digital industry survey).", segment="New people needed per year", via="Thairath Online article on the DEPA survey (search-result summary; page not fetched)", notes="Whole software sector, not AI-specific."),
        _o("th-depa-sw-grads", "software_workforce_per_year", "TH", "2025", 7247.0, "count", "depa_digital_survey_2025", "Graduates entering software-related fields per year (same survey).", segment="Graduates entering related fields per year", via="Thairath Online article on the DEPA survey (search-result summary; page not fetched)", notes="The same article says digital services has more graduates than jobs, with a skills mismatch in AI and data analytics."),
        _o("th-tdri-ai-postings-growth", "ai_posting_growth_yoy", "TH", "2025", 31.0, "%", "tdri_ai_labour_2025", "Growth in AI-related job postings over a year (TDRI, 2025 AI labour market report). Source, definition and base are not stated.", via="aitif.bde.go.th page citing TDRI (search-result summary; undated; page not fetched)"),
        _o("th-tdri-aiml-roles-growth", "ai_ml_engineer_posting_growth_yoy", "TH", "2025", 278.0, "%", "tdri_ai_labour_2025", "Growth in AI/ML engineer role postings over a year (TDRI). Definition and base are not stated.", via="aitif.bde.go.th page citing TDRI (search-result summary; undated; page not fetched)"),
        _o("th-tdri-ai-share", "ai_posting_share_tdri", "TH", "2025", 37.0, "%", "tdri_ai_labour_2025", "Share of job postings calling for AI-related skills (TDRI). Far above Lightcast (2-5%) and Indeed keyword shares; the definition is unknown, so it is not comparable and is not plotted with them.", via="aitif.bde.go.th page citing TDRI (search-result summary; undated; page not fetched)"),
        _pay("mp-mle-TH-lo", "Machine Learning Engineer", "TH", 1296000, "THB", "michaelpage_th", "Annual, low end of the range advertised in one Michael Page Bangkok listing (Senior Machine Learning Engineer).", is_estimate=True, via="Michael Page Thailand job-search page (search-result summary; page not fetched)", notes="A single advertised range, not a survey."),
        _pay("mp-mle-TH-hi", "Machine Learning Engineer", "TH", 1584000, "THB", "michaelpage_th", "Annual, high end of the same advertised range.", is_estimate=True, via="Michael Page Thailand job-search page (search-result summary; page not fetched)"),
        # Pay. Local currency as reported; no USD conversion until an FX source is retrieved.
        _pay("lv-ai-TH", "AI / LLM Engineer", "TH", 874323, "THB", "levels_fyi", "Median total comp, self-reported.", notes="Sample size not recorded."),
        _pay("eri-ai-TH", "AI / LLM Engineer", "TH", 1167539, "THB", "eri_salaryexpert", "Average base salary, model estimate.", is_estimate=True),
        _pay("lv-ds-TH", "Data Scientist", "TH", 1176555, "THB", "levels_fyi", "Median total comp, self-reported.", sample_size=13,
             notes="n=13 (small). A second page gives Bangkok THB 909,379; the two disagree."),
        _pay("lv-de-TH", "Data Engineer", "TH", 711359, "THB", "levels_fyi", "Median total comp, self-reported.", notes="Sample size not recorded."),
        _pay("lv-da-TH", "Data Analyst / BI", "TH", 869724, "THB", "levels_fyi", "Median total comp, self-reported.", notes="Sample size not recorded."),
        _pay("ev-ai-TH-lo", "AI / LLM Engineer", "TH", 100000, "THB", "evantis_th_2026", "Monthly base, low end of experienced specialist/manager band (AI, Data and Analytics).", is_estimate=True, notes="Role mapping is loose: band covers AI, data and analytics."),
        _pay("ev-ai-TH-hi", "AI / LLM Engineer", "TH", 230000, "THB", "evantis_th_2026", "Monthly base, high end of the same band.", is_estimate=True),
        _pay("mm-ai-SG-lo", "AI / LLM Engineer", "SG", 100000, "SGD", "morgan_mckinley_sg", "Annual, low end of AI/ML Engineer range.", is_estimate=True),
        _pay("mm-ai-SG-hi", "AI / LLM Engineer", "SG", 170000, "SGD", "morgan_mckinley_sg", "Annual, high end of AI/ML Engineer range.", is_estimate=True),
        _pay("eri-ai-DE", "AI / LLM Engineer", "DE", 92000, "EUR", "eri_salaryexpert", "Average annual, model estimate.", is_estimate=True, notes="Title definitions differ widely between sources."),
    ]
    return o
