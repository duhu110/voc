from __future__ import annotations

from voc_agent.advice_builder_agent.builder import build_advice_hash, normalize_advice_text


def test_normalize_advice_text_collapses_whitespace_and_case() -> None:
    assert normalize_advice_text("  先 核实\n业务状态  ") == "先 核实 业务状态"
    assert normalize_advice_text("ABC") == "abc"


def test_build_advice_hash_is_stable_for_equivalent_text() -> None:
    first = build_advice_hash("核实状态", "  先核实业务状态\n再回访用户 ", "适用于退费场景")
    second = build_advice_hash("核实状态", "先核实业务状态 再回访用户", "适用于退费场景")
    assert first == second
