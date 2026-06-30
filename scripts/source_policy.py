"""Human-readable source policy for the three morning news workflows.

This makes the source universe explicit in generated artifacts so the briefs do
not behave like a black box.
"""
from __future__ import annotations

US_SOURCE_POLICY = [
    "CNBC — global markets/economy/business headlines",
    "ZeroHedge — market stress, macro, positioning, geopolitical risk",
    "WSJ — markets, economy, business, policy (via Google News RSS because WSJ RSS is limited/paywalled)",
    "Financial Times — companies, markets, macro, policy (direct RSS + Google News RSS)",
    "Official US data/policy sources — Federal Reserve, Treasury, BLS, SEC",
]

AI_SOURCE_POLICY = [
    "Frontier labs — OpenAI, Anthropic, Google DeepMind/Google AI, Meta AI, xAI/Grok",
    "AI infrastructure — NVIDIA, AMD, TSMC, Broadcom, Microsoft/Azure, AWS, Oracle/datacenters",
    "Open-source / developer ecosystem — Hugging Face, Llama/Qwen/DeepSeek/Mistral coverage",
    "Tier-1 financial/tech press — Reuters, Bloomberg, FT, TechCrunch, The Verge, MIT Tech Review, Wired",
    "Policy/legal — AI regulation, copyright, safety, antitrust, major lawsuits",
]

THAILAND_SOURCE_POLICY = [
    "ประชาชาติธุรกิจ — เศรษฐกิจ / การเงิน / ธุรกิจ / การเมือง; exclude crypto, gold-only, FX-only, auto, world/tech/SD/PR noise",
    "กรุงเทพธุรกิจ — เศรษฐกิจ / การเงิน / world economy; exclude crypto, PR, FX-only, auto/lifestyle noise",
    "RYT9 — economic, business, marketing and policy news; exclude crypto/PR noise",
    "InfoQuest — economic, business, market and policy news; exclude crypto/PR noise",
    "Official Thailand market sources — BoT, SET, MoF/คลัง, SEC/ก.ล.ต. when market-moving",
]

MANUAL_X_SOURCE_POLICY = [
    "Nut's X list from the Google Doc is part of Jack's manual/scouting desk.",
    "GitHub Actions do not currently ingest X directly because the runner has no X API/xAI search integration wired in.",
]


def _section(title: str, rows: list[str]) -> list[str]:
    return [f"## Source Policy — {title}", "", *[f"- {row}" for row in rows], ""]


def markdown_for(kind: str) -> str:
    if kind == "us":
        rows = US_SOURCE_POLICY + MANUAL_X_SOURCE_POLICY
        title = "US / Global"
    elif kind == "ai":
        rows = AI_SOURCE_POLICY
        title = "AI"
    elif kind == "thailand":
        rows = THAILAND_SOURCE_POLICY
        title = "Thailand"
    else:
        rows = []
        title = kind
    return "\n".join(_section(title, rows))


def one_line(kind: str) -> str:
    if kind == "us":
        return "Sources: CNBC, ZeroHedge, WSJ, FT, Fed/Treasury/BLS/SEC. X list = manual Jack scouting, not GitHub-ingested yet."
    if kind == "ai":
        return "Sources: frontier labs, AI infra/chips, open-source AI, Reuters/Bloomberg/FT/TechCrunch/The Verge/MIT/Wired."
    if kind == "thailand":
        return "Sources: Prachachat, Bangkok Biz News, RYT9, InfoQuest, plus BoT/SET/MoF/SEC when market-moving."
    return ""
