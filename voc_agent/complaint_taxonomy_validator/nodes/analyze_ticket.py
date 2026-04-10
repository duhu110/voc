from __future__ import annotations

import json

from langchain_core.messages import HumanMessage, SystemMessage

from voc_agent.complaint_taxonomy_validator.prompts import SYSTEM_PROMPT, build_user_prompt
from voc_agent.complaint_taxonomy_validator.state import ValidatorOutput, ValidatorState
from voc_agent.complaint_taxonomy_validator.utils import normalize_result
from voc_agent.core.llm import get_chat_model
from voc_agent.share.utils import extract_json_text


def analyze_ticket(state: ValidatorState) -> ValidatorState:
    """Call the LLM and normalize the raw provider output to validator schema."""
    llm = get_chat_model()
    prompt = build_user_prompt(
        ticket=state['ticket'],
        categories=state['categories'],
        tags=state['tags'],
    )
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt + '\n\n请只返回纯 JSON，不要使用 Markdown 代码块。'),
    ])
    raw_text = response.text if hasattr(response, 'text') else str(response.content)
    raw_data = json.loads(extract_json_text(raw_text))
    normalized = normalize_result(raw_data, state['categories'], state['tags'])
    parsed = ValidatorOutput.model_validate(normalized)
    return {'result': parsed.model_dump(mode='json')}
