"""The handoff brief: an LLM-structured summary, next steps, mood and urgency."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from agent import Assistant  # noqa: E402


class _Chunk:
    def __init__(self, text):
        self.delta = type("D", (), {"content": text})()


class _Stream:
    def __init__(self, text):
        self._text = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    def __aiter__(self):
        async def gen():
            for piece in (self._text[:10], self._text[10:]):
                yield _Chunk(piece)

        return gen()


def _stub_llm(monkeypatch, text):
    class LLM:
        def chat(self, chat_ctx):
            return _Stream(text)

    # `llm` is a property on Agent; patch it at the class level.
    monkeypatch.setattr(Assistant, "llm", property(lambda self: LLM()))


@pytest.mark.asyncio
async def test_brief_is_parsed_into_structured_fields(monkeypatch):
    a = Assistant()
    _stub_llm(
        monkeypatch,
        'Sure: {"summary": "Sarah wants the address on order 58121 changed.",'
        ' "next_steps": ["Update the delivery address", "Confirm by text"],'
        ' "mood": "frustrated", "urgency": "high"} thanks',
    )
    b = await a._handoff_brief("fallback")
    assert b["summary"].startswith("Sarah wants")
    assert b["next_steps"] == ["Update the delivery address", "Confirm by text"]
    assert b["mood"] == "frustrated" and b["urgency"] == "high"


@pytest.mark.asyncio
async def test_brief_falls_back_to_the_tool_summary_when_llm_fails(monkeypatch):
    a = Assistant()

    class Broken:
        def chat(self, chat_ctx):
            raise RuntimeError("inference down")

    monkeypatch.setattr(Assistant, "llm", property(lambda self: Broken()))
    b = await a._handoff_brief("Sarah asked about order 58121.")
    assert b["summary"] == "Sarah asked about order 58121."
    assert b["mood"] == "calm" and b["next_steps"] == []


def test_speech_form_reads_naturally():
    text = Assistant._brief_for_speech(
        {
            "summary": "S.",
            "next_steps": ["Do A", "Do B"],
            "mood": "upset",
            "urgency": "high",
        }
    )
    assert "Caller mood: upset" in text and "Do A; Do B" in text
