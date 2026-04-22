from voc_agent.complaint_taxonomy_validator.state import ValidatorOutput
from voc_agent.complaint_taxonomy_validator.utils import normalize_result


def test_normalize_result_coerces_string_candidates_in_partially_structured_payload() -> None:
    raw = {
        'summary': '用户否认订购增值业务，要求取消并退费。',
        'primary_category': {
            'code': 'DENY_ORDER',
            'full_name': '投诉/增值业务/否认订购',
            'confidence': 0.91,
            'reason': '用户明确表示不知情办理。',
        },
        'candidate_categories': [
            {
                'code': 'DENY_ORDER',
                'full_name': '投诉/增值业务/否认订购',
                'confidence': 0.91,
                'reason': '用户明确表示不知情办理。',
            }
        ],
        'candidate_tags': [
            '[PRODUCT] [VALUE_ADDED]',
            '[ROOT_CAUSE] [DENY_ORDER]',
            '[REQUEST] [CANCEL]',
        ],
        'category_keywords': ['否认订购', '不知情办理'],
        'tag_keywords': ['增值业务', '取消业务'],
        'risks': ['缺少订购凭证'],
    }
    categories = [
        {'code': 'DENY_ORDER', 'full_name': '投诉/增值业务/否认订购'},
    ]
    tags = [
        {'group_code': 'PRODUCT', 'code': 'VALUE_ADDED', 'name': '增值业务'},
        {'group_code': 'ROOT_CAUSE', 'code': 'DENY_ORDER', 'name': '否认订购'},
        {'group_code': 'REQUEST', 'code': 'CANCEL', 'name': '取消业务'},
    ]

    normalized = normalize_result(raw, categories, tags)
    parsed = ValidatorOutput.model_validate(normalized)

    assert [tag.group_code for tag in parsed.candidate_tags] == ['PRODUCT', 'ROOT_CAUSE', 'REQUEST']
    assert [tag.code for tag in parsed.candidate_tags] == ['VALUE_ADDED', 'DENY_ORDER', 'CANCEL']
    assert [keyword.keyword for keyword in parsed.category_keywords] == ['否认订购', '不知情办理']
    assert [keyword.keyword for keyword in parsed.tag_keywords] == ['增值业务', '取消业务']


def test_normalize_result_parses_bracket_codes_from_dict_tag_items() -> None:
    raw = {
        'summary': '用户否认订购会员业务。',
        'primary_category': {
            'code': 'SUBSCRIBE_DENY_VALUE_ADDED',
            'full_name': '订购与退订争议/用户否认订购/否认增值业务订购',
            'confidence': 0.91,
            'reason': '用户称未主动订购。',
        },
        'candidate_tags': [
            {
                'group_code': '',
                'code': '[PRODUCT] [VALUE_ADDED]',
                'name': '增值业务',
                'confidence': 0.8,
                'reason': '用户称未主动订购。',
            },
            {
                'group_code': '',
                'code': '[ROOT_CAUSE] [DENY_ORDER]',
                'name': '用户否认订购',
                'confidence': 0.8,
                'reason': '用户称未主动订购。',
            },
        ],
    }
    categories = [
        {'code': 'SUBSCRIBE_DENY_VALUE_ADDED', 'full_name': '订购与退订争议/用户否认订购/否认增值业务订购'},
    ]
    tags = [
        {'group_code': 'PRODUCT', 'code': 'VALUE_ADDED', 'name': '增值业务'},
        {'group_code': 'ROOT_CAUSE', 'code': 'DENY_ORDER', 'name': '用户否认订购'},
    ]

    normalized = normalize_result(raw, categories, tags)
    parsed = ValidatorOutput.model_validate(normalized)

    assert [tag.group_code for tag in parsed.candidate_tags] == ['PRODUCT', 'ROOT_CAUSE']
    assert [tag.code for tag in parsed.candidate_tags] == ['VALUE_ADDED', 'DENY_ORDER']
    assert [tag.name for tag in parsed.candidate_tags] == ['增值业务', '用户否认订购']


def test_normalize_result_keeps_primary_category_in_candidate_categories() -> None:
    raw = {
        'summary': '用户投诉办理规则不合理。',
        'primary_category': {
            'code': 'RULE_PROCESS_PROXY_ENTERPRISE',
            'full_name': '规则政策争议/办理规则争议/代办规则争议/企业经办人代办争议',
            'confidence': 0.95,
            'reason': '主诉集中在企业号码过户限制。',
        },
        'candidate_categories': [
            {
                'code': 'RULE_PROCESS',
                'full_name': '规则政策争议/办理规则争议',
                'confidence': 0.85,
                'reason': '上层规则类争议。',
            }
        ],
    }
    categories = [
        {'id': 1, 'code': 'RULE_PROCESS_PROXY_ENTERPRISE', 'full_name': '规则政策争议/办理规则争议/代办规则争议/企业经办人代办争议'},
        {'id': 2, 'code': 'RULE_PROCESS', 'full_name': '规则政策争议/办理规则争议'},
    ]

    normalized = normalize_result(raw, categories, tags=[])
    parsed = ValidatorOutput.model_validate(normalized)

    assert parsed.primary_category.code == 'RULE_PROCESS_PROXY_ENTERPRISE'
    assert [category.code for category in parsed.candidate_categories] == [
        'RULE_PROCESS_PROXY_ENTERPRISE',
        'RULE_PROCESS',
    ]
