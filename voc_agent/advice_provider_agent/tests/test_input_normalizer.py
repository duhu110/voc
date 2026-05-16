from __future__ import annotations

from pathlib import Path

import pytest

from voc_agent.advice_provider_agent import input_normalizer
from voc_agent.advice_provider_agent.input_normalizer import (
    ImageInput,
    VisionModelError,
    normalize_user_input_to_ticket,
)


def test_normalize_text_input_builds_temporary_ticket() -> None:
    ticket = normalize_user_input_to_ticket(text="用户投诉套餐扣费异常，要求退费。")

    assert ticket["ticket_id"].startswith("ui-")
    assert ticket["biz_content"] == "用户投诉套餐扣费异常，要求退费。"
    assert ticket["complaint_phenomenon"] == "用户投诉套餐扣费异常，要求退费。"
    assert ticket["line_category"] == ""
    assert ticket["complaint_source"] == "chainlit_text"


def test_normalize_multimodal_input_uses_vision_only_as_translator(monkeypatch) -> None:
    def fake_vision_model(text, images):
        assert text == "用户补充：已经多次投诉。"
        assert images == [ImageInput(path=Path("sample.png"), mime_type="image/png", name=None)]
        return "截图可见：用户投诉增值业务扣费，要求取消并退费。"

    monkeypatch.setattr(input_normalizer, "_text_from_vision_model", fake_vision_model)

    ticket = normalize_user_input_to_ticket(
        text="用户补充：已经多次投诉。",
        images=[ImageInput(path=Path("sample.png"), mime_type="image/png")],
    )

    assert ticket["ticket_id"].startswith("ui-")
    assert ticket["biz_content"] == "用户输入：用户补充：已经多次投诉。\n\n图片转写：截图可见：用户投诉增值业务扣费，要求取消并退费。"
    assert ticket["complaint_phenomenon"] == ticket["biz_content"]
    assert ticket["line_category"] == ""
    assert ticket["complaint_source"] == "chainlit_multimodal"
    assert ticket["image_translated_text"] == "截图可见：用户投诉增值业务扣费，要求取消并退费。"


def test_normalize_empty_input_rejects() -> None:
    with pytest.raises(ValueError, match="请输入投诉描述"):
        normalize_user_input_to_ticket(text=" ")


def test_normalize_image_without_text_requires_recognized_facts(monkeypatch) -> None:
    monkeypatch.setattr(input_normalizer, "_text_from_vision_model", lambda text, images: "")

    with pytest.raises(VisionModelError, match="未识别到足够的投诉文字"):
        normalize_user_input_to_ticket(images=[ImageInput(path=Path("sample.png"))])


def test_normalize_image_model_error_is_not_hidden(monkeypatch) -> None:
    def fail_vision_model(text, images):
        raise VisionModelError("vision unavailable")

    monkeypatch.setattr(input_normalizer, "_text_from_vision_model", fail_vision_model)

    with pytest.raises(VisionModelError, match="vision unavailable"):
        normalize_user_input_to_ticket(text="用户投诉", images=[ImageInput(path=Path("sample.png"))])
