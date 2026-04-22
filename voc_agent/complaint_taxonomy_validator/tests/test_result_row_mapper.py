from voc_agent.complaint_taxonomy_validator.utils.result_row_mapper import build_result_rows


def test_build_result_rows_generates_db_ready_payloads() -> None:
    result = {
        'summary': '用户认为企业号码过户规则不合理，要求解释并尽快处理。',
        'primary_category': {
            'code': 'RULE_PROCESS_PROXY_ENTERPRISE',
            'full_name': '规则政策争议/办理规则争议/代办规则争议/企业经办人代办争议',
            'confidence': 0.95,
            'reason': '主诉集中在企业号码过户限制。',
        },
        'candidate_categories': [
            {
                'code': 'RULE_PROCESS_PROXY_ENTERPRISE',
                'full_name': '规则政策争议/办理规则争议/代办规则争议/企业经办人代办争议',
                'confidence': 0.95,
                'reason': '主诉集中在企业号码过户限制。',
            },
            {
                'code': 'RULE_PROCESS',
                'full_name': '规则政策争议/办理规则争议',
                'confidence': 0.85,
                'reason': '上层规则类争议。',
            },
        ],
        'candidate_tags': [
            {
                'group_code': 'PRODUCT',
                'code': 'MOBILE',
                'name': '移动业务',
                'confidence': 0.9,
                'reason': '投诉对象为移动号码。',
            },
            {
                'group_code': 'REQUEST',
                'code': 'EXPLAIN',
                'name': '解释说明',
                'confidence': 0.8,
                'reason': '用户要求解释规则。',
            },
        ],
        'category_keywords': [
            {'keyword': '过户', 'reason': '直接体现主分类场景', 'confidence': 0.9},
        ],
        'tag_keywords': [
            {'keyword': '移动号码', 'reason': '体现产品标签', 'confidence': 0.8},
        ],
        'risks': ['缺少现场受理录音'],
    }
    categories = [
        {'id': 101, 'code': 'RULE_PROCESS_PROXY_ENTERPRISE', 'full_name': '规则政策争议/办理规则争议/代办规则争议/企业经办人代办争议'},
        {'id': 102, 'code': 'RULE_PROCESS', 'full_name': '规则政策争议/办理规则争议'},
    ]
    tags = [
        {'id': 201, 'group_code': 'PRODUCT', 'code': 'MOBILE', 'name': '移动业务'},
        {'id': 202, 'group_code': 'REQUEST', 'code': 'EXPLAIN', 'name': '解释说明'},
    ]

    rows = build_result_rows(
        ticket_id='2024070513552328517778',
        result=result,
        categories=categories,
        tags=tags,
        model_version='Qwen3-Max',
    )

    assert rows['category_results'] == [
        {
            'ticket_id': '2024070513552328517778',
            'category_id': 101,
            'result_source': 'ai',
            'model_version': 'Qwen3-Max',
            'rule_version': None,
            'confidence_score': 0.95,
            'ranking_no': 1,
            'is_final': True,
            'is_manual_confirmed': False,
            'manual_confirmed_by': None,
            'manual_confirmed_at': None,
            'matched_by': 'ai',
            'explanation': '主诉集中在企业号码过户限制。',
            'evaluation_status': 'pending',
        },
        {
            'ticket_id': '2024070513552328517778',
            'category_id': 102,
            'result_source': 'ai',
            'model_version': 'Qwen3-Max',
            'rule_version': None,
            'confidence_score': 0.85,
            'ranking_no': 2,
            'is_final': False,
            'is_manual_confirmed': False,
            'manual_confirmed_by': None,
            'manual_confirmed_at': None,
            'matched_by': 'ai',
            'explanation': '上层规则类争议。',
            'evaluation_status': 'pending',
        },
    ]
    assert rows['tag_results'] == [
        {
            'ticket_id': '2024070513552328517778',
            'tag_id': 201,
            'result_source': 'ai',
            'model_version': 'Qwen3-Max',
            'rule_version': None,
            'confidence_score': 0.9,
            'ranking_no': 1,
            'is_final': True,
            'is_manual_confirmed': False,
            'manual_confirmed_by': None,
            'manual_confirmed_at': None,
            'matched_by': 'ai',
            'explanation': '投诉对象为移动号码。',
            'evaluation_status': 'pending',
        },
        {
            'ticket_id': '2024070513552328517778',
            'tag_id': 202,
            'result_source': 'ai',
            'model_version': 'Qwen3-Max',
            'rule_version': None,
            'confidence_score': 0.8,
            'ranking_no': 2,
            'is_final': True,
            'is_manual_confirmed': False,
            'manual_confirmed_by': None,
            'manual_confirmed_at': None,
            'matched_by': 'ai',
            'explanation': '用户要求解释规则。',
            'evaluation_status': 'pending',
        },
    ]
    assert rows['keyword_results'] == [
        {
            'ticket_id': '2024070513552328517778',
            'keyword': '过户',
            'keyword_type': 'category',
            'weight': 0.9,
            'source': 'ai',
        },
        {
            'ticket_id': '2024070513552328517778',
            'keyword': '移动号码',
            'keyword_type': 'tag',
            'weight': 0.8,
            'source': 'ai',
        },
    ]
    assert rows['match_details'] == [
        {
            'ticket_id': '2024070513552328517778',
            'target_type': 'category',
            'target_id': 101,
            'rule_type': 'llm_reason',
            'rule_id': None,
            'matched_text': '主诉集中在企业号码过户限制。',
            'matched_score': 0.95,
            'matched_by': 'ai',
        },
        {
            'ticket_id': '2024070513552328517778',
            'target_type': 'category',
            'target_id': 102,
            'rule_type': 'llm_reason',
            'rule_id': None,
            'matched_text': '上层规则类争议。',
            'matched_score': 0.85,
            'matched_by': 'ai',
        },
        {
            'ticket_id': '2024070513552328517778',
            'target_type': 'tag',
            'target_id': 201,
            'rule_type': 'llm_reason',
            'rule_id': None,
            'matched_text': '投诉对象为移动号码。',
            'matched_score': 0.9,
            'matched_by': 'ai',
        },
        {
            'ticket_id': '2024070513552328517778',
            'target_type': 'tag',
            'target_id': 202,
            'rule_type': 'llm_reason',
            'rule_id': None,
            'matched_text': '用户要求解释规则。',
            'matched_score': 0.8,
            'matched_by': 'ai',
        },
    ]
