from __future__ import annotations

from voc_agent.complaint_taxonomy_converger.chain import route_after_category
from voc_agent.complaint_taxonomy_converger.nodes.finalize_result import finalize_result


def test_route_after_category_goes_to_finalize_when_category_missing() -> None:
    state = {'ticket_id': 'T1', 'selected_category': None}

    assert route_after_category(state) == 'finalize_result'


def test_route_after_category_goes_to_tag_analysis_when_category_exists() -> None:
    state = {'ticket_id': 'T1', 'selected_category': {'code': 'CAT_A'}}

    assert route_after_category(state) == 'analyze_tags'


def test_finalize_result_marks_ticket_skipped_when_no_category() -> None:
    state = {
        'ticket_id': 'T1',
        'ticket': {'ticket_id': 'T1'},
        'selected_category': None,
        'selected_tags': [],
        'category_summary': '未找到分类',
        'stop_reason': 'category_confidence_below_threshold',
    }

    finalized = finalize_result(state)

    assert finalized['result'] == {
        'ticket_id': 'T1',
        'status': 'skipped_no_category',
        'summary': '未找到分类',
        'primary_category': None,
        'selected_tags': [],
        'stop_reason': 'category_confidence_below_threshold',
    }


def test_finalize_result_marks_ticket_completed_when_category_exists() -> None:
    state = {
        'ticket_id': 'T2',
        'ticket': {'ticket_id': 'T2'},
        'selected_category': {
            'code': 'CAT_A',
            'full_name': '分类A',
            'confidence': 0.91,
            'reason': '命中',
        },
        'selected_tags': [
            {
                'group_code': 'G1',
                'code': 'T1',
                'name': '标签1',
                'confidence': 0.77,
                'reason': '命中',
            }
        ],
        'category_summary': '找到分类',
    }

    finalized = finalize_result(state)

    assert finalized['result'] == {
        'ticket_id': 'T2',
        'status': 'completed',
        'summary': '找到分类',
        'primary_category': {
            'code': 'CAT_A',
            'full_name': '分类A',
            'confidence': 0.91,
            'reason': '命中',
        },
        'selected_tags': [
            {
                'group_code': 'G1',
                'code': 'T1',
                'name': '标签1',
                'confidence': 0.77,
                'reason': '命中',
            }
        ],
        'stop_reason': None,
    }
