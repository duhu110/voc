from __future__ import annotations

from voc_agent.complaint_taxonomy_converger.utils.output_normalizer import (
    normalize_category_output,
    normalize_tag_output,
)


def test_normalize_category_output_returns_none_below_threshold() -> None:
    categories = [{'code': 'CAT_A', 'full_name': '分类A'}]

    selected = normalize_category_output(
        {
            'summary': '工单摘要',
            'primary_category': {
                'code': 'CAT_A',
                'confidence': 0.6,
                'reason': '证据不足',
            },
        },
        categories,
        threshold=0.75,
    )

    assert selected is None


def test_normalize_category_output_accepts_single_valid_category() -> None:
    categories = [{'code': 'CAT_A', 'full_name': '分类A'}]

    selected = normalize_category_output(
        {
            'summary': '工单摘要',
            'primary_category': {
                'code': 'CAT_A',
                'confidence': 0.86,
                'reason': '问题直指分类A',
            },
        },
        categories,
        threshold=0.75,
    )

    assert selected == {
        'code': 'CAT_A',
        'full_name': '分类A',
        'confidence': 0.86,
        'reason': '问题直指分类A',
    }


def test_normalize_tag_output_keeps_only_one_tag_per_group_above_threshold() -> None:
    tags = [
        {'group_code': 'G1', 'code': 'T1', 'name': '标签1'},
        {'group_code': 'G1', 'code': 'T2', 'name': '标签2'},
        {'group_code': 'G2', 'code': 'T3', 'name': '标签3'},
        {'group_code': 'G2', 'code': 'T4', 'name': '标签4'},
    ]

    selected = normalize_tag_output(
        {
            'candidate_tags': [
                {'group_code': 'G1', 'code': 'T1', 'confidence': 0.76, 'reason': '较弱'},
                {'group_code': 'G1', 'code': 'T2', 'confidence': 0.88, 'reason': '更强'},
                {'group_code': 'G2', 'code': 'T3', 'confidence': 0.64, 'reason': '低于阈值'},
                {'group_code': 'G2', 'code': 'T4', 'confidence': 0.79, 'reason': '满足阈值'},
                {'group_code': 'G9', 'code': 'TX', 'confidence': 0.99, 'reason': '无效标签'},
            ]
        },
        tags,
        threshold=0.7,
    )

    assert selected == [
        {
            'group_code': 'G1',
            'code': 'T2',
            'name': '标签2',
            'confidence': 0.88,
            'reason': '更强',
        },
        {
            'group_code': 'G2',
            'code': 'T4',
            'name': '标签4',
            'confidence': 0.79,
            'reason': '满足阈值',
        },
    ]
