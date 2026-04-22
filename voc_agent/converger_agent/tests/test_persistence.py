from __future__ import annotations

from sqlalchemy import create_engine, text

from voc_agent.converger_agent.persistence import save_converger_result


def _build_test_engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    ddl_statements = [
        """
        create table raw_complaint_tickets (
            ticket_id varchar(100) primary key,
            converger_agent_status boolean not null default false
        )
        """,
        """
        create table converger_agent_result (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null unique,
            primary_level1_code varchar(100) not null,
            primary_level1_name varchar(100) not null,
            primary_level2_code varchar(100) not null,
            primary_level2_name varchar(100) not null,
            primary_leaf_code varchar(100) not null,
            primary_leaf_name varchar(100) not null,
            request_tag_code varchar(100),
            request_tag_name varchar(100),
            emotion_tag_code varchar(100),
            emotion_tag_name varchar(100),
            risk_tag_code varchar(100),
            risk_tag_name varchar(100),
            product_tag_code varchar(100),
            product_tag_name varchar(100),
            line_category varchar(255),
            model_name varchar(100),
            taxonomy_version varchar(50) not null,
            agent_version varchar(50),
            status varchar(50) not null,
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp
        )
        """,
        """
        create table converger_resolution_summary_atomic (
            id integer primary key autoincrement,
            source_ticket_id varchar(100) not null unique,
            primary_leaf_code varchar(100) not null,
            primary_leaf_name varchar(100) not null,
            product_tag_code varchar(100),
            product_tag_name varchar(100),
            request_tag_code varchar(100),
            request_tag_name varchar(100),
            risk_tag_code varchar(100),
            risk_tag_name varchar(100),
            emotion_tag_code varchar(100),
            emotion_tag_name varchar(100),
            line_category varchar(255),
            resolution_summary text,
            model_name varchar(100),
            taxonomy_version varchar(50) not null,
            agent_version varchar(50),
            status varchar(50) not null default 'active',
            created_at timestamp default current_timestamp,
            updated_at timestamp default current_timestamp
        )
        """,
    ]
    with engine.begin() as conn:
        for ddl in ddl_statements:
            conn.execute(text(ddl))
    return engine


def _sample_completed_result() -> dict:
    return {
        "ticket_id": "T-1",
        "status": "completed",
        "summary": "用户认为套餐收费规则不合理，要求解释。",
        "primary_category": {
            "level1_code": "FEE_BILLING",
            "level1_name": "费用与账务",
            "level2_code": "PACKAGE_AND_USAGE_FEE",
            "level2_name": "套餐与使用费用",
            "leaf_code": "PACKAGE_FEE_DISPUTE",
            "leaf_name": "套餐收费争议",
            "reason": "文本核心是套餐收费不认可。",
        },
        "request_tag": {"code": "EXPLAIN", "name": "解释说明", "reason": "要求解释收费规则。"},
        "emotion_tag": {"code": "UNSATISFIED", "name": "不满", "reason": "明显表达不满。"},
        "risk_tag": {"code": "NORMAL", "name": "正常", "reason": "普通工单。"},
        "product_tag": {"code": "MOBILE", "name": "移动业务", "reason": "涉及手机套餐。"},
        "line_category": {"value": "市场条线", "reason": "直接来自原始工单"},
        "resolution_summary": "先核对套餐生效时间，再补充收费规则解释。",
    }


def test_save_converger_result_persists_rows_and_marks_ticket_processed(monkeypatch) -> None:
    engine = _build_test_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into raw_complaint_tickets (ticket_id, converger_agent_status) values (:ticket_id, :status)"
            ),
            {"ticket_id": "T-1", "status": False},
        )

    monkeypatch.setattr("voc_agent.converger_agent.persistence.get_engine", lambda: engine)

    summary = save_converger_result(
        ticket_id="T-1",
        result=_sample_completed_result(),
        model_name="Qwen3-Max",
        taxonomy_version="v1",
        agent_version="v1",
    )

    assert summary == {
        "result_rows": 1,
        "resolution_summary_rows": 1,
    }

    with engine.connect() as conn:
        processed = conn.execute(
            text("select converger_agent_status from raw_complaint_tickets where ticket_id = :ticket_id"),
            {"ticket_id": "T-1"},
        ).scalar_one()
        result_count = conn.execute(text("select count(*) from converger_agent_result")).scalar_one()
        summary_count = conn.execute(
            text("select count(*) from converger_resolution_summary_atomic")
        ).scalar_one()

    assert bool(processed) is True
    assert result_count == 1
    assert summary_count == 1


def test_save_converger_result_skipped_only_marks_ticket_processed(monkeypatch) -> None:
    engine = _build_test_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                "insert into raw_complaint_tickets (ticket_id, converger_agent_status) values (:ticket_id, :status)"
            ),
            {"ticket_id": "T-2", "status": False},
        )

    monkeypatch.setattr("voc_agent.converger_agent.persistence.get_engine", lambda: engine)

    summary = save_converger_result(
        ticket_id="T-2",
        result={
            "ticket_id": "T-2",
            "status": "skipped_no_category",
            "stop_reason": "未命中可信分类",
        },
        model_name="Qwen3-Max",
        taxonomy_version="v1",
        agent_version="v1",
    )

    assert summary == {
        "result_rows": 0,
        "resolution_summary_rows": 0,
    }

    with engine.connect() as conn:
        processed = conn.execute(
            text("select converger_agent_status from raw_complaint_tickets where ticket_id = :ticket_id"),
            {"ticket_id": "T-2"},
        ).scalar_one()
        result_count = conn.execute(text("select count(*) from converger_agent_result")).scalar_one()
        summary_count = conn.execute(
            text("select count(*) from converger_resolution_summary_atomic")
        ).scalar_one()

    assert bool(processed) is True
    assert result_count == 0
    assert summary_count == 0
