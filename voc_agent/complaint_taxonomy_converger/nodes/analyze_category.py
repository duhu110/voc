from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from voc_agent.complaint_taxonomy_converger.prompts import (
    CATEGORY_CONFIDENCE_THRESHOLD,
    CATEGORY_SYSTEM_PROMPT,
    build_category_prompt,
)
from voc_agent.complaint_taxonomy_converger.state import ConvergerState
from voc_agent.complaint_taxonomy_converger.utils import normalize_category_output
from voc_agent.core.llm import get_chat_model
from voc_agent.share.utils import parse_json_payload_once


def analyze_category(state: ConvergerState) -> ConvergerState:
    prompt = build_category_prompt(state['ticket'], state['categories'])
    llm = get_chat_model()
    response = llm.invoke([
        SystemMessage(content=CATEGORY_SYSTEM_PROMPT),
        HumanMessage(content=prompt + '\n\n请只返回纯 JSON，不要使用 Markdown 代码块。'),
    ])
    raw_text = response.text if hasattr(response, 'text') else str(response.content)
    raw_data = parse_json_payload_once(raw_text)
    selected_category = normalize_category_output(
        raw_data,
        state['categories'],
        threshold=CATEGORY_CONFIDENCE_THRESHOLD,
    )
    if selected_category is None:
        return {
            'category_summary': raw_data.get('summary') or '未找到满足阈值的主分类。',
            'selected_category': None,
            'stop_reason': 'category_confidence_below_threshold',
        }
    return {
        'category_summary': raw_data.get('summary') or selected_category['reason'],
        'selected_category': selected_category,
        'stop_reason': None,
    }
