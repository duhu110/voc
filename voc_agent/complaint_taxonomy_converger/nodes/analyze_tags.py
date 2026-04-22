from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from voc_agent.complaint_taxonomy_converger.prompts import (
    TAG_CONFIDENCE_THRESHOLD,
    TAG_SYSTEM_PROMPT,
    build_tag_prompt,
)
from voc_agent.complaint_taxonomy_converger.state import ConvergerState
from voc_agent.complaint_taxonomy_converger.utils import normalize_tag_output
from voc_agent.core.llm import get_chat_model
from voc_agent.share.utils import parse_json_payload_once


def analyze_tags(state: ConvergerState) -> ConvergerState:
    prompt = build_tag_prompt(state['ticket'], state['selected_category'], state['tags'])
    llm = get_chat_model()
    response = llm.invoke([
        SystemMessage(content=TAG_SYSTEM_PROMPT),
        HumanMessage(content=prompt + '\n\n请只返回纯 JSON，不要使用 Markdown 代码块。'),
    ])
    raw_text = response.text if hasattr(response, 'text') else str(response.content)
    raw_data = parse_json_payload_once(raw_text)
    selected_tags = normalize_tag_output(
        raw_data,
        state['tags'],
        threshold=TAG_CONFIDENCE_THRESHOLD,
    )
    return {'selected_tags': selected_tags}
