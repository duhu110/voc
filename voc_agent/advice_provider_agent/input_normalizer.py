from __future__ import annotations

import base64
import hashlib
import mimetypes
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from openai import OpenAI

from voc_agent.core.config import get_settings


class VisionModelError(RuntimeError):
    """Raised when image input cannot be interpreted by the configured vision model."""


@dataclass(frozen=True)
class ImageInput:
    path: Path
    mime_type: str | None = None
    name: str | None = None


def build_temporary_ticket_id(text: str, images: Iterable[ImageInput] = ()) -> str:
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    digest_source = [text.strip()]
    for image in images:
        digest_source.append(str(image.path))
        if image.path.exists():
            digest_source.append(str(image.path.stat().st_size))
    digest = hashlib.sha1("|".join(digest_source).encode("utf-8")).hexdigest()[:10]
    return f"ui-{now}-{digest}"


def normalize_user_input_to_ticket(
    *,
    text: str = "",
    images: list[ImageInput] | None = None,
) -> dict[str, Any]:
    cleaned_text = text.strip()
    image_inputs = images or []
    if not cleaned_text and not image_inputs:
        raise ValueError("请输入投诉描述，或上传一张包含投诉信息的图片。")

    ticket_id = build_temporary_ticket_id(cleaned_text, image_inputs)
    if not image_inputs:
        return _ticket_from_text(ticket_id, cleaned_text)

    image_text = _text_from_vision_model(cleaned_text, image_inputs)
    combined_text = _combine_user_and_image_text(cleaned_text, image_text)
    if not combined_text:
        raise VisionModelError("图片中未识别到足够的投诉文字，请补充文字说明后重试。")
    ticket = _ticket_from_text(ticket_id, combined_text)
    ticket["complaint_source"] = "chainlit_multimodal"
    ticket["image_translated_text"] = image_text
    return ticket


def _ticket_from_text(ticket_id: str, text: str) -> dict[str, Any]:
    return {
        "ticket_id": ticket_id,
        "biz_content": text,
        "complaint_phenomenon": text,
        "line_category": "",
        "complaint_source": "chainlit_text",
    }


def _text_from_vision_model(text: str, images: list[ImageInput]) -> str:
    settings = get_settings()
    client = OpenAI(base_url=settings.vision_base_url, api_key=settings.vision_api_key)
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": _build_vision_prompt(text),
        }
    ]
    for image in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": _image_to_data_url(image)},
            }
        )

    try:
        response = client.chat.completions.create(
            model=settings.vision_model_name,
            temperature=settings.llm_temperature,
            messages=[
                {
                    "role": "system",
                    "content": "你是图片文字转写和翻译助手，只负责读图、转写、翻译，不做业务判断。",
                },
                {
                    "role": "user",
                    "content": content,
                },
            ],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as exc:
        raise VisionModelError(
            "图片直读失败。请确认 VOC_VISION_MODEL_NAME / VOC_VISION_BASE_URL / "
            "VOC_VISION_API_KEY 指向支持 image_url 多模态消息的 OpenAI-compatible 模型。"
        ) from exc


def _build_vision_prompt(text: str) -> str:
    sections = [
        "请只读取图片中的可见文字，并翻译/整理成中文纯文本。",
        "不要分类，不要打标签，不要判断诉求、风险或处理建议。",
        "不要补全图片里没有的信息，不要编造金额、时限、套餐、处理结果或身份信息。",
        "如果图片里是表单或聊天记录，请尽量保留关键字段名、用户原话、时间、金额、业务名称等可见事实。",
        "只输出纯文本，不要输出 JSON，不要输出 Markdown。",
    ]
    if text.strip():
        sections.extend(["", "用户另有补充文字；补充文字不用改写，图片转写时只需避免与补充文字冲突：", text.strip()])
    return "\n".join(sections)


def _image_to_data_url(image: ImageInput) -> str:
    if not image.path.exists() or not image.path.is_file():
        raise VisionModelError(f"图片文件不存在：{image.path}")
    mime_type = image.mime_type or mimetypes.guess_type(image.path.name)[0] or "image/png"
    encoded = base64.b64encode(image.path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _combine_user_and_image_text(user_text: str, image_text: str) -> str:
    parts: list[str] = []
    if user_text.strip():
        parts.append(f"用户输入：{user_text.strip()}")
    if image_text.strip():
        parts.append(f"图片转写：{image_text.strip()}")
    return "\n\n".join(parts)
