"""Figures read directly from fetched primary pages (2026-10-12). Each row names where it was found."""
from __future__ import annotations

from datetime import date

from ..schema import Confidence, Observation

R = date(2026, 10, 12)
IDX = "stanford_ai_index_2026"
CNT = "Postings listing the skill among US AI job postings (a posting can list several skills). Lightcast, AI Index 2026 report."


def _o(id, metric, region, period, value, unit, src, defn, conf=Confidence.A, role="all", **kw):
    return Observation(id=id, metric=metric, role=role, region=region, period=period, value=value, unit=unit, source_id=src,
                       retrieved_on=R, definition=defn, confidence=conf, **kw)


def load() -> list[Observation]:
    o = []
    # AI Index 2026, section 4.4 (Jobs), "Generative AI skills in AI job postings in the US, 2024 vs 2025" and "AI agent skills ..."
    skills = [("rag", "Retrieval augmented generation", 2885, 12609), ("genai", "Generative artificial intelligence", 65557, 138188),
              ("llm", "Large language modeling", 19045, 38526), ("prompt", "Prompt engineering", 6152, 22227),
              ("agentic-ai", "Agentic AI (single skill)", 151, 16541), ("ai-agents", "AI agents", 1310, 15217),
              ("chatgpt", "ChatGPT", 5535, 14376), ("conv-ai", "Conversational AI", 5430, 6976), ("langgraph", "LangGraph", 194, 4294),
              ("copilot", "Microsoft Copilot", 1416, 6395), ("chatbot", "Chatbot", 2316, 4596)]
    for key, name, a, b in skills:
        for yr, v in (("2024", a), ("2025", b)):
            o.append(_o(f"aix-skill-{key}-{yr}", "ai_skill_postings_count", "US", yr, float(v), "count", IDX, CNT, skill=name,
                        notes="AI Index 2026, section 4.4 skill charts (2024 vs 2025)."))
    o.append(_o("aix-py-2025", "ai_skill_postings_count", "US", "2025", 258674.0, "count", IDX,
                "Postings listing Python (most frequent specialised skill in US AI postings). AI Index 2026 section 4.4.", skill="Python"))
    # Lightcast blog (Lightcast is the data owner), cluster-level shares of ALL US postings
    for yr, v in (("2024", 0.06), ("2025", 0.23)):
        o.append(_o(f"lcblog-agentic-cluster-{yr}", "agentic_cluster_share_all_postings", "US", yr, v, "%", "lightcast_blog_ai_index_2026",
                    "Share of all US job postings with Agentic AI cluster skills (agents, agentic systems). Lightcast blog quoting AI Index 2026.",
                    conf=Confidence.B, notes='Blog: "more than 280% increase", "nearly 90,000 job postings in the US". Different slice from the single skill "Agentic AI" (151 to 16,541 postings).'))
    # Stanford Digital Economy Lab, Canaries (rev. 12 Aug 2026), ADP payroll, descriptive
    D = "stanford_del_canaries"
    ddef = "Employment of 22-25 year-olds in highly AI-exposed occupations is this % below where it would be had it kept pace with less-exposed peers (descriptive 'kept-pace shortfall'; ADP payroll data; not causal)."
    o += [_o("del-gap-2025-07", "employment_shortfall_age22_25", "US", "2025-07", 15.0, "%", D, ddef, conf=Confidence.B, notes="Data vintage July 2025 (paper, Aug 2026 revision)."),
          _o("del-gap-2026-06", "employment_shortfall_age22_25", "US", "2026-06", 19.0, "%", D, ddef, conf=Confidence.B, notes="Data through June 2026. Experienced workers show no comparable gap; no economy-wide displacement found."),
          _o("del-reg-2025-07", "employment_decline_age22_25_regression", "US", "2025-07", 13.0, "%", D, "Earlier headline regression estimate (adjusting for firm-level shocks), relative decline for 22-25 year-olds in exposed occupations.", conf=Confidence.B, notes="Superseded as the headline; different method from the shortfall metric."),
          _o("del-reg-2025-09", "employment_decline_age22_25_regression", "US", "2025-09", 16.0, "%", D, "Same regression estimate, September 2025 data.", conf=Confidence.B)]
    return o
