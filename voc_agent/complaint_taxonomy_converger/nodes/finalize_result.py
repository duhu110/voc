from __future__ import annotations

from voc_agent.complaint_taxonomy_converger.state import ConvergerResult, ConvergerState


def finalize_result(state: ConvergerState) -> ConvergerState:
    selected_category = state.get('selected_category')
    result = ConvergerResult(
        ticket_id=state['ticket_id'],
        status='completed' if selected_category else 'skipped_no_category',
        summary=state.get('category_summary') or '',
        primary_category=selected_category,
        selected_tags=state.get('selected_tags', []),
        stop_reason=state.get('stop_reason'),
    )
    return {'result': result.model_dump(mode='json')}
