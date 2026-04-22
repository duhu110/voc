from __future__ import annotations

from sqlalchemy import create_engine, text

from voc_agent.complaint_taxonomy_validator.persistence import save_validator_result


def _build_test_engine():
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    ddl_statements = [
        """
        create table raw_complaint_tickets (
            ticket_id varchar(100) primary key,
            process_status boolean not null default false
        )
        """,
        """
        create table complaint_ticket_category_result (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            category_id bigint not null,
            result_source varchar(50) not null,
            model_version varchar(100),
            rule_version varchar(100),
            confidence_score numeric,
            ranking_no integer not null,
            is_final boolean not null,
            is_manual_confirmed boolean not null,
            manual_confirmed_by varchar(100),
            manual_confirmed_at timestamp,
            matched_by varchar(50) not null,
            explanation text,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp,
            evaluation_status varchar(50)
        )
        """,
        """
        create table complaint_ticket_tag_result (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            tag_id bigint not null,
            result_source varchar(50) not null,
            model_version varchar(100),
            rule_version varchar(100),
            confidence_score numeric,
            ranking_no integer not null,
            is_final boolean not null,
            is_manual_confirmed boolean not null,
            manual_confirmed_by varchar(100),
            manual_confirmed_at timestamp,
            matched_by varchar(50) not null,
            explanation text,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp,
            evaluation_status varchar(50)
        )
        """,
        """
        create table complaint_ticket_keyword_result (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            keyword varchar(200) not null,
            keyword_type varchar(50) not null,
            weight numeric,
            source varchar(50) not null,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp
        )
        """,
        """
        create table complaint_ticket_match_detail (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            target_type varchar(20) not null,
            target_id bigint not null,
            rule_type varchar(50) not null,
            rule_id bigint,
            matched_text text,
            matched_score numeric,
            matched_by varchar(50) not null,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp
        )
        """,
    ]
    with engine.begin() as conn:
        for ddl in ddl_statements:
            conn.execute(text(ddl))
    return engine


def _sample_result() -> dict:
    return {
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


def _sample_categories() -> list[dict]:
    return [
        {'id': 101, 'code': 'RULE_PROCESS_PROXY_ENTERPRISE', 'full_name': '规则政策争议/办理规则争议/代办规则争议/企业经办人代办争议'},
        {'id': 102, 'code': 'RULE_PROCESS', 'full_name': '规则政策争议/办理规则争议'},
    ]


def _sample_tags() -> list[dict]:
    return [
        {'id': 201, 'group_code': 'PRODUCT', 'code': 'MOBILE', 'name': '移动业务'},
        {'id': 202, 'group_code': 'REQUEST', 'code': 'EXPLAIN', 'name': '解释说明'},
    ]


def test_save_validator_result_persists_rows_and_marks_ticket_processed(monkeypatch) -> None:
    engine = _build_test_engine()
    with engine.begin() as conn:
        conn.execute(
            text("insert into raw_complaint_tickets (ticket_id, process_status) values (:ticket_id, :process_status)"),
            {'ticket_id': '2024070513552328517778', 'process_status': False},
        )

    monkeypatch.setattr('voc_agent.complaint_taxonomy_validator.persistence.get_engine', lambda: engine)

    summary = save_validator_result(
        ticket_id='2024070513552328517778',
        result=_sample_result(),
        categories=_sample_categories(),
        tags=_sample_tags(),
        model_version='Qwen3-Max',
    )

    assert summary == {
        'category_results': 2,
        'tag_results': 2,
        'keyword_results': 2,
        'match_details': 4,
    }

    with engine.connect() as conn:
        process_status = conn.execute(
            text("select process_status from raw_complaint_tickets where ticket_id = :ticket_id"),
            {'ticket_id': '2024070513552328517778'},
        ).scalar_one()
        category_count = conn.execute(text("select count(*) from complaint_ticket_category_result")).scalar_one()
        tag_count = conn.execute(text("select count(*) from complaint_ticket_tag_result")).scalar_one()
        keyword_count = conn.execute(text("select count(*) from complaint_ticket_keyword_result")).scalar_one()
        match_detail_count = conn.execute(text("select count(*) from complaint_ticket_match_detail")).scalar_one()

    assert bool(process_status) is True
    assert category_count == 2
    assert tag_count == 2
    assert keyword_count == 2
    assert match_detail_count == 4


def test_save_validator_result_replaces_existing_ai_rows_for_same_ticket(monkeypatch) -> None:
    engine = _build_test_engine()
    with engine.begin() as conn:
        conn.execute(
            text("insert into raw_complaint_tickets (ticket_id, process_status) values (:ticket_id, :process_status)"),
            {'ticket_id': '2024070513552328517778', 'process_status': False},
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_category_result (
                    ticket_id, category_id, result_source, model_version, ranking_no,
                    is_final, is_manual_confirmed, matched_by, evaluation_status
                ) values (
                    :ticket_id, :category_id, :result_source, :model_version, :ranking_no,
                    :is_final, :is_manual_confirmed, :matched_by, :evaluation_status
                )
                """
            ),
            {
                'ticket_id': '2024070513552328517778',
                'category_id': 999,
                'result_source': 'ai',
                'model_version': 'OldModel',
                'ranking_no': 1,
                'is_final': True,
                'is_manual_confirmed': False,
                'matched_by': 'ai',
                'evaluation_status': 'pending',
            },
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_tag_result (
                    ticket_id, tag_id, result_source, model_version, ranking_no,
                    is_final, is_manual_confirmed, matched_by, evaluation_status
                ) values (
                    :ticket_id, :tag_id, :result_source, :model_version, :ranking_no,
                    :is_final, :is_manual_confirmed, :matched_by, :evaluation_status
                )
                """
            ),
            {
                'ticket_id': '2024070513552328517778',
                'tag_id': 998,
                'result_source': 'ai',
                'model_version': 'OldModel',
                'ranking_no': 1,
                'is_final': True,
                'is_manual_confirmed': False,
                'matched_by': 'ai',
                'evaluation_status': 'pending',
            },
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_keyword_result (
                    ticket_id, keyword, keyword_type, weight, source
                ) values (
                    :ticket_id, :keyword, :keyword_type, :weight, :source
                )
                """
            ),
            {
                'ticket_id': '2024070513552328517778',
                'keyword': '旧关键词',
                'keyword_type': 'category',
                'weight': 0.5,
                'source': 'ai',
            },
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_match_detail (
                    ticket_id, target_type, target_id, rule_type, rule_id, matched_text, matched_score, matched_by
                ) values (
                    :ticket_id, :target_type, :target_id, :rule_type, :rule_id, :matched_text, :matched_score, :matched_by
                )
                """
            ),
            {
                'ticket_id': '2024070513552328517778',
                'target_type': 'category',
                'target_id': 999,
                'rule_type': 'llm_reason',
                'rule_id': None,
                'matched_text': '旧解释',
                'matched_score': 0.5,
                'matched_by': 'ai',
            },
        )

    monkeypatch.setattr('voc_agent.complaint_taxonomy_validator.persistence.get_engine', lambda: engine)

    save_validator_result(
        ticket_id='2024070513552328517778',
        result=_sample_result(),
        categories=_sample_categories(),
        tags=_sample_tags(),
        model_version='Qwen3-Max',
    )

    with engine.connect() as conn:
        category_ids = conn.execute(
            text("select category_id from complaint_ticket_category_result order by ranking_no")
        ).scalars().all()
        tag_ids = conn.execute(
            text("select tag_id from complaint_ticket_tag_result order by ranking_no")
        ).scalars().all()
        keywords = conn.execute(
            text("select keyword from complaint_ticket_keyword_result order by keyword")
        ).scalars().all()
        matched_texts = conn.execute(
            text("select matched_text from complaint_ticket_match_detail order by matched_text")
        ).scalars().all()

    assert category_ids == [101, 102]
    assert tag_ids == [201, 202]
    assert keywords == ['移动号码', '过户']
    assert matched_texts == ['上层规则类争议。', '主诉集中在企业号码过户限制。', '投诉对象为移动号码。', '用户要求解释规则。']
