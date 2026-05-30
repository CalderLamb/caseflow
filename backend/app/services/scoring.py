"""
Consequence scorer — assigns a 0–100 rank to any CaseItem.
All factors are logged to score_factors so the 'critical because…' line renders on the card.
"""
from datetime import datetime, timezone
from typing import Optional


MALPRACTICE_KINDS = {"deadline"}  # kinds where a blown item is malpractice-class


def score_deadline_item(
    due_date: datetime,
    has_calendar_block: bool,
    is_malpractice_class: bool,
) -> tuple[float, list[dict]]:
    now = datetime.now(timezone.utc)
    days_out = (due_date.replace(tzinfo=timezone.utc) - now).days
    factors = []
    score = 0.0

    if is_malpractice_class:
        score += 45
        factors.append({"label": "malpractice-class deadline", "weight": 45})
    else:
        score += 20
        factors.append({"label": "deadline", "weight": 20})

    if days_out <= 0:
        urgency = 30
        factors.append({"label": "past due", "weight": urgency})
    elif days_out <= 7:
        urgency = 25
        factors.append({"label": f"{days_out}d remaining (critical window)", "weight": urgency})
    elif days_out <= 30:
        urgency = 15
        factors.append({"label": f"{days_out}d remaining", "weight": urgency})
    elif days_out <= 60:
        urgency = 8
        factors.append({"label": f"{days_out}d remaining", "weight": urgency})
    else:
        urgency = 2
        factors.append({"label": f"{days_out}d remaining", "weight": urgency})
    score += urgency

    if not has_calendar_block:
        score += 15
        factors.append({"label": "no calendar protection", "weight": 15})

    return min(score, 100), factors


def score_client_update_item(
    last_contact_days: Optional[int],
    matter_stakes_high: bool,
) -> tuple[float, list[dict]]:
    factors = []
    score = 10.0
    factors.append({"label": "client update needed", "weight": 10})

    if last_contact_days is not None:
        if last_contact_days >= 30:
            score += 20
            factors.append({"label": f"{last_contact_days}d since last contact", "weight": 20})
        elif last_contact_days >= 14:
            score += 10
            factors.append({"label": f"{last_contact_days}d since last contact", "weight": 10})
        else:
            score += 3
            factors.append({"label": f"{last_contact_days}d since last contact", "weight": 3})

    if matter_stakes_high:
        score += 10
        factors.append({"label": "high-stakes matter", "weight": 10})

    return min(score, 100), factors


def score_generic_item(kind: str) -> tuple[float, list[dict]]:
    base = {
        "discovery": 35,
        "motion_response": 40,
        "records_request": 25,
        "conflict": 50,
        "gap": 30,
        "chronology_flag": 28,
        "billing": 15,
        "other": 10,
    }
    weight = base.get(kind, 10)
    return float(weight), [{"label": kind.replace("_", " "), "weight": weight}]
