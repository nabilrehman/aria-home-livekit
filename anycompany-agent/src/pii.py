"""PII masking applied inside the agent, before text leaves the process.

Anything that gets persisted (call memory), forwarded to a human (the desk
brief), or logged is passed through here. The room audio and the live LLM
context are untouched — the model needs the real values to do its job — but
nothing downstream of the call needs a customer's phone number or card digits.

What is masked:
  phone numbers   +1 737 205 9240, (512) 555-1188, 512.555.1188 → [phone]
  emails          anyone@example.com                             → [email]
  card numbers    13-19 digit runs with separators                → [card]
  SSN-like        123-45-6789                                     → [ssn]
  account numbers AH-4821 → AH-••21 (last two kept so a human can confirm)
  long digit runs 8+ digits (order numbers are 5, so they survive) → [number]
"""

from __future__ import annotations

import re

_PHONE = re.compile(
    r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)"
)
_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_CARD = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_SSN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")
_ACCOUNT = re.compile(r"\b(AH)[\s-]?(\d{2})(\d{2})\b", re.I)
_LONG_DIGITS = re.compile(r"(?<!\d)\d{8,}(?!\d)")


def mask(text: str) -> str:
    """Redact PII in free text. Order matters: cards before phones (a card looks
    like several phones), accounts before the generic digit sweep."""
    if not text:
        return text
    out = _CARD.sub("[card]", text)
    out = _SSN.sub("[ssn]", out)
    out = _LONG_DIGITS.sub("[number]", out)  # before phones: an 11-digit run isn't a phone
    out = _PHONE.sub("[phone]", out)
    out = _EMAIL.sub("[email]", out)
    out = _ACCOUNT.sub(lambda m: f"{m.group(1).upper()}-••{m.group(3)}", out)
    return out


def mask_brief(brief: dict) -> dict:
    """Mask the free-text parts of a handoff/call brief, leave structure intact."""
    out = dict(brief)
    if isinstance(out.get("summary"), str):
        out["summary"] = mask(out["summary"])
    if isinstance(out.get("next_steps"), list):
        out["next_steps"] = [mask(str(x)) for x in out["next_steps"]]
    return out


def mask_transcript(lines: list[dict]) -> list[dict]:
    return [{**ln, "text": mask(str(ln.get("text", "")))} for ln in lines]
