"""
Draft service — the ONE expensive operation.
Generates a single draft on attorney request, then runs the self-critique pass.
MUST NOT be called from any ingestion, scoring, or scheduling path.
"""
import anthropic
from app.config import settings
from app.schemas.common import Confidence, WeaknessCategory


_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


SYSTEM_PROMPT = """You are a legal drafting assistant for a Louisiana personal injury law firm.
You draft concise, professional legal correspondence and documents.
Every factual assertion must cite its source using [Source: <label>] notation.
If you cannot cite a fact, flag it with [UNVERIFIED].
Write in plain, direct prose. No unnecessary boilerplate."""


def _build_draft_prompt(item_kind: str, trigger_text: str, facts: list[dict], matter_name: str) -> str:
    facts_block = "\n".join(
        f"- {f['text']} [Source: {f['citation']['label']}]"
        for f in facts
    ) if facts else "No assembled facts available."

    return f"""Draft a {item_kind.replace('_', ' ')} document for matter: {matter_name}

TRIGGER: {trigger_text}

ASSEMBLED FACTS:
{facts_block}

Draft the document now. Cite every fact. Flag anything unverified."""


CRITIQUE_SYSTEM = """You are a risk reviewer for a Louisiana personal injury law firm.
Your job: analyze a legal draft and produce a structured JSON self-critique.

Return ONLY valid JSON in this exact format:
{{
  "confidence": "high" | "medium" | "low",
  "reasoning": "one sentence explaining the grade",
  "annotations": [
    {{
      "span_start": <char offset>,
      "span_end": <char offset>,
      "category": "law" | "facts" | "data" | "contradiction" | "procedure",
      "note": "actionable note"
    }}
  ]
}}

Confidence definitions:
- high: every fact traces to a cited source AND every cited authority is verified AND no novel legal proposition
- medium: all facts sourced but ≥1 authority unverified, OR argument rests on partial data, OR known gap unaddressed
- low: ≥1 unverifiable legal proposition, or a material fact with no source

Annotation taxonomy:
- law: citation or legal standard may be wrong/outdated
- facts: assertion thinly sourced
- data: draft assumes something not in the file
- contradiction: internal inconsistency or vs. prior filing
- procedure: format/required-element issue"""


def generate_draft(
    item_kind: str,
    trigger_text: str,
    assembled_facts: list[dict],
    matter_name: str,
) -> tuple[str, str, list[dict], int]:
    """
    Returns (draft_body, confidence, annotations, token_cost).
    Raises on API error — caller should handle and set draft state accordingly.
    """
    prompt = _build_draft_prompt(item_kind, trigger_text, assembled_facts, matter_name)

    draft_response = _client.messages.create(
        model="claude-opus-4-8-20251101",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    draft_body = draft_response.content[0].text
    draft_tokens = draft_response.usage.input_tokens + draft_response.usage.output_tokens

    critique_response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=CRITIQUE_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Self-critique this draft:\n\n{draft_body}",
            }
        ],
    )
    critique_raw = critique_response.content[0].text
    critique_tokens = critique_response.usage.input_tokens + critique_response.usage.output_tokens

    import json, re
    json_match = re.search(r"\{.*\}", critique_raw, re.DOTALL)
    if json_match:
        critique = json.loads(json_match.group())
    else:
        critique = {"confidence": "medium", "annotations": []}

    confidence = critique.get("confidence", "medium")
    annotations = critique.get("annotations", [])
    total_tokens = draft_tokens + critique_tokens

    return draft_body, confidence, annotations, total_tokens
