from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text

from streamlit_app.app_services import (
    build_batch_result_rows,
    dumps_for_ui,
    fetch_dashboard_snapshot,
    fetch_random_pending_ticket_id,
    fetch_ticket_result_rows,
    fetch_table_rows,
    list_batch_summaries,
    load_summary_artifact,
    run_batch_job,
    stream_single_ticket_job,
)


def _build_engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    ddl_statements = [
        """
        create table raw_complaint_tickets (
            ticket_id varchar(100) primary key,
            process_status boolean not null default 0
        )
        """,
        """
        create table complaint_ticket_category_result (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            category_id bigint not null,
            result_source varchar(50) not null,
            confidence_score numeric,
            ranking_no integer not null,
            is_final boolean not null,
            matched_by varchar(50) not null,
            explanation text,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_ticket_tag_result (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            tag_id bigint not null,
            result_source varchar(50) not null,
            confidence_score numeric,
            ranking_no integer not null,
            is_final boolean not null,
            matched_by varchar(50) not null,
            explanation text,
            created_at timestamp not null default current_timestamp
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
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_ticket_match_detail (
            id integer primary key autoincrement,
            ticket_id varchar(100) not null,
            target_type varchar(50) not null,
            target_id bigint not null,
            matched_text text,
            matched_score numeric,
            matched_by varchar(50) not null,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_category_stats (
            id integer primary key autoincrement,
            category_id bigint not null,
            stat_date date not null,
            total_predicted_count integer not null default 0,
            total_final_count integer not null default 0,
            avg_confidence_score numeric
        )
        """,
        """
        create table complaint_tag_stats (
            id integer primary key autoincrement,
            tag_id bigint not null,
            stat_date date not null,
            total_predicted_count integer not null default 0,
            total_final_count integer not null default 0,
            avg_confidence_score numeric
        )
        """,
    ]
    with engine.begin() as conn:
        for ddl in ddl_statements:
            conn.execute(text(ddl))
        conn.execute(
            text(
                """
                insert into raw_complaint_tickets (ticket_id, process_status) values
                ('T1', 0),
                ('T2', 1),
                ('T3', 0)
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_category_result (
                    ticket_id, category_id, result_source, confidence_score, ranking_no, is_final, matched_by, explanation
                ) values
                ('T2', 101, 'ai', 0.92, 1, 1, 'ai', 'ok'),
                ('T2', 102, 'ai', 0.61, 2, 0, 'ai', 'candidate')
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_tag_result (
                    ticket_id, tag_id, result_source, confidence_score, ranking_no, is_final, matched_by, explanation
                ) values
                ('T2', 201, 'ai', 0.88, 1, 1, 'ai', 'tag')
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_keyword_result (
                    ticket_id, keyword, keyword_type, weight, source
                ) values
                ('T2', '过户', 'category', 0.9, 'ai')
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_match_detail (
                    ticket_id, target_type, target_id, matched_text, matched_score, matched_by
                ) values
                ('T2', 'category', 101, '过户问题', 0.9, 'ai')
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_category_stats (
                    category_id, stat_date, total_predicted_count, total_final_count, avg_confidence_score
                ) values
                (101, '2026-04-10', 2, 1, 0.76)
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_tag_stats (
                    tag_id, stat_date, total_predicted_count, total_final_count, avg_confidence_score
                ) values
                (201, '2026-04-10', 1, 1, 0.88)
                """
            )
        )
    return engine


def test_list_batch_summaries_sorts_latest_first(tmp_path: Path) -> None:
    older = tmp_path / "summary__2026-04-10T17-00-00.json"
    newer = tmp_path / "summary__2026-04-10T18-00-00.json"
    ignored = tmp_path / "ticket__2026-04-10T18-00-00.json"
    older.write_text("{}", encoding="utf-8")
    newer.write_text("{}", encoding="utf-8")
    ignored.write_text("{}", encoding="utf-8")

    results = list_batch_summaries(tmp_path)

    assert results == [newer, older]


def test_load_summary_artifact_and_build_batch_result_rows(tmp_path: Path) -> None:
    path = tmp_path / "summary__2026-04-10T18-00-00.json"
    path.write_text(
        json.dumps(
            {
                "timestamp": "2026-04-10T18:00:00",
                "sample_size": 2,
                "success_count": 1,
                "failure_count": 1,
                "results": [
                    {
                        "ticket_id": "T1",
                        "status": "success",
                        "duration_ms": 1234,
                        "write_summary": {
                            "category_results": 3,
                            "tag_results": 5,
                            "keyword_results": 8,
                            "match_details": 6,
                        },
                    },
                    {
                        "ticket_id": "T2",
                        "status": "failed",
                        "duration_ms": 567,
                        "error_type": "RuntimeError",
                        "error_message": "boom",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    summary = load_summary_artifact(path)
    rows = build_batch_result_rows(summary)

    assert summary["success_count"] == 1
    assert rows == [
        {
            "ticket_id": "T1",
            "status": "success",
            "duration_ms": 1234,
            "category_results": 3,
            "tag_results": 5,
            "keyword_results": 8,
            "match_details": 6,
            "error_type": None,
            "error_message": None,
        },
        {
            "ticket_id": "T2",
            "status": "failed",
            "duration_ms": 567,
            "category_results": 0,
            "tag_results": 0,
            "keyword_results": 0,
            "match_details": 0,
            "error_type": "RuntimeError",
            "error_message": "boom",
        },
    ]


def test_fetch_dashboard_snapshot_and_table_rows() -> None:
    engine = _build_engine()

    snapshot = fetch_dashboard_snapshot(engine=engine)
    pending_rows = fetch_table_rows("pending_tickets", limit=10, engine=engine)
    category_stats_rows = fetch_table_rows("category_stats", limit=10, engine=engine)

    assert snapshot == {
        "pending_tickets": 2,
        "processed_tickets": 1,
        "category_results": 2,
        "tag_results": 1,
        "keyword_results": 1,
        "match_details": 1,
        "category_stats": 1,
        "tag_stats": 1,
    }
    assert pending_rows == [
        {"ticket_id": "T3", "process_status": 0},
        {"ticket_id": "T1", "process_status": 0},
    ]
    assert category_stats_rows == [
        {
            "category_id": 101,
            "stat_date": "2026-04-10",
            "total_predicted_count": 2,
            "total_final_count": 1,
            "avg_confidence_score": pytest.approx(0.76),
        }
    ]


def test_fetch_table_rows_rejects_unknown_table_key() -> None:
    engine = _build_engine()

    with pytest.raises(ValueError, match="Unsupported table key"):
        fetch_table_rows("unknown", engine=engine)


def test_fetch_ticket_result_rows_returns_all_result_groups() -> None:
    engine = _build_engine()

    result_rows = fetch_ticket_result_rows("T2", engine=engine)

    assert result_rows == {
        "category_results": [
            {
                "ticket_id": "T2",
                "category_id": 101,
                "confidence_score": pytest.approx(0.92),
                "ranking_no": 1,
                "is_final": 1,
                "created_at": result_rows["category_results"][0]["created_at"],
            },
            {
                "ticket_id": "T2",
                "category_id": 102,
                "confidence_score": pytest.approx(0.61),
                "ranking_no": 2,
                "is_final": 0,
                "created_at": result_rows["category_results"][1]["created_at"],
            },
        ],
        "tag_results": [
            {
                "ticket_id": "T2",
                "tag_id": 201,
                "confidence_score": pytest.approx(0.88),
                "ranking_no": 1,
                "is_final": 1,
                "created_at": result_rows["tag_results"][0]["created_at"],
            }
        ],
        "keyword_results": [
            {
                "ticket_id": "T2",
                "keyword": "过户",
                "keyword_type": "category",
                "weight": pytest.approx(0.9),
                "source": "ai",
                "created_at": result_rows["keyword_results"][0]["created_at"],
            }
        ],
        "match_details": [
            {
                "ticket_id": "T2",
                "target_type": "category",
                "target_id": 101,
                "matched_text": "过户问题",
                "matched_score": pytest.approx(0.9),
                "matched_by": "ai",
                "created_at": result_rows["match_details"][0]["created_at"],
            }
        ],
    }


def test_fetch_random_pending_ticket_id_returns_unprocessed_ticket() -> None:
    engine = _build_engine()

    ticket_id = fetch_random_pending_ticket_id(engine=engine)

    assert ticket_id in {'T1', 'T3'}


def test_dumps_for_ui_serializes_datetime_and_decimal() -> None:
    payload = {
        'timestamp': datetime(2026, 4, 10, 18, 30, 45),
        'score': Decimal('0.88'),
    }

    rendered = dumps_for_ui(payload)

    assert '"timestamp": "2026-04-10T18:30:45"' in rendered
    assert '"score": 0.88' in rendered


def test_run_batch_job_executes_without_writing_artifacts(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_fetch_pending_ticket_ids(limit: int) -> list[str]:
        assert limit == 2
        return ["T1", "T2"]

    def fake_run_validator_and_persist(ticket_id: str) -> dict[str, object]:
        calls.append(ticket_id)
        if ticket_id == "T2":
            raise RuntimeError("bad ticket")
        return {
            "ticket_id": ticket_id,
            "result": {"summary": "ok"},
            "write_summary": {
                "category_results": 1,
                "tag_results": 2,
                "keyword_results": 3,
                "match_details": 4,
            },
        }

    monkeypatch.setattr("streamlit_app.app_services.fetch_pending_ticket_ids", fake_fetch_pending_ticket_ids)
    monkeypatch.setattr("streamlit_app.app_services.run_validator_and_persist", fake_run_validator_and_persist)
    monkeypatch.chdir(tmp_path)

    summary = run_batch_job(2)

    assert calls == ["T1", "T2"]
    assert summary["sample_size"] == 2
    assert summary["success_count"] == 1
    assert summary["failure_count"] == 1
    assert summary["success_rate"] == pytest.approx(0.5)
    assert summary["results"][0]["status"] == "success"
    assert summary["results"][1]["status"] == "failed"
    assert "summary_path" not in summary
    assert "report_path" not in summary
    assert "result_files" not in summary
    assert list(tmp_path.glob("*.json")) == []


def test_stream_single_ticket_job_yields_rich_events(monkeypatch) -> None:
    class FakeResponse:
        text = '{"summary":"ok"}'

    class FakeLLM:
        def invoke(self, messages):
            assert len(messages) == 2
            return FakeResponse()

    def fake_load_context(state):
        assert state == {'ticket_id': 'T100'}
        return {
            'ticket_id': 'T100',
            'ticket': {'ticket_id': 'T100', 'biz_content': '需要观察'},
            'categories': [{'id': 1, 'code': 'CAT_A', 'full_name': '分类A'}],
            'tags': [{'id': 2, 'group_code': 'GRP', 'code': 'TAG_A', 'name': '标签A'}],
        }

    def fake_build_user_prompt(ticket, categories, tags):
        assert ticket['ticket_id'] == 'T100'
        assert categories[0]['code'] == 'CAT_A'
        assert tags[0]['code'] == 'TAG_A'
        return 'PROMPT BODY'

    def fake_parse_json_payload_once(raw_text):
        assert raw_text == '{"summary":"ok"}'
        return {'summary': 'ok'}

    def fake_normalize_result(raw_data, categories, tags):
        assert raw_data == {'summary': 'ok'}
        return {
            'summary': 'ok',
            'primary_category': {'code': 'CAT_A', 'full_name': '分类A', 'confidence': 0.9, 'reason': '命中'},
            'candidate_categories': [],
            'candidate_tags': [],
            'category_keywords': [],
            'tag_keywords': [],
            'risks': [],
        }

    class FakeParsed:
        def model_dump(self, mode='json'):
            assert mode == 'json'
            return {
                'summary': 'ok',
                'primary_category': {'code': 'CAT_A', 'full_name': '分类A', 'confidence': 0.9, 'reason': '命中'},
                'candidate_categories': [],
                'candidate_tags': [],
                'category_keywords': [],
                'tag_keywords': [],
                'risks': [],
            }

    class FakeValidatorOutput:
        @staticmethod
        def model_validate(data):
            assert data['primary_category']['code'] == 'CAT_A'
            return FakeParsed()

    def fake_save_validator_result(ticket_id, result, categories, tags, *, model_version):
        assert ticket_id == 'T100'
        assert result['summary'] == 'ok'
        assert categories[0]['id'] == 1
        assert tags[0]['id'] == 2
        assert model_version == 'test-model'
        return {
            'category_results': 1,
            'tag_results': 1,
            'keyword_results': 0,
            'match_details': 1,
        }

    def fake_fetch_ticket_result_rows(ticket_id):
        assert ticket_id == 'T100'
        return {
            'category_results': [{'ticket_id': 'T100', 'category_id': 1}],
            'tag_results': [{'ticket_id': 'T100', 'tag_id': 2}],
            'keyword_results': [],
            'match_details': [{'ticket_id': 'T100', 'target_type': 'category'}],
        }

    class FakeSettings:
        llm_model_name = 'test-model'

    monkeypatch.setattr('streamlit_app.app_services.load_context', fake_load_context)
    monkeypatch.setattr('streamlit_app.app_services.build_user_prompt', fake_build_user_prompt)
    monkeypatch.setattr('streamlit_app.app_services.get_chat_model', lambda: FakeLLM())
    monkeypatch.setattr('streamlit_app.app_services.parse_json_payload_once', fake_parse_json_payload_once)
    monkeypatch.setattr('streamlit_app.app_services.normalize_result', fake_normalize_result)
    monkeypatch.setattr('streamlit_app.app_services.ValidatorOutput', FakeValidatorOutput)
    monkeypatch.setattr('streamlit_app.app_services.save_validator_result', fake_save_validator_result)
    monkeypatch.setattr('streamlit_app.app_services.fetch_ticket_result_rows', fake_fetch_ticket_result_rows)
    monkeypatch.setattr('streamlit_app.app_services.get_settings', lambda: FakeSettings())

    events = list(stream_single_ticket_job('T100'))

    assert [event['stage'] for event in events] == [
        'start',
        'context_loaded',
        'prompt_built',
        'llm_response',
        'result_parsed',
        'persisted',
        'database_rows_loaded',
    ]
    assert events[1]['category_count'] == 1
    assert events[1]['tag_count'] == 1
    assert events[2]['prompt'] == 'PROMPT BODY'
    assert events[3]['raw_text'] == '{"summary":"ok"}'
    assert events[4]['result']['primary_category']['code'] == 'CAT_A'
    assert events[5]['write_summary']['category_results'] == 1
    assert events[6]['database_rows']['category_results'][0]['category_id'] == 1


def test_stream_single_ticket_job_uses_random_pending_ticket_when_blank(monkeypatch) -> None:
    monkeypatch.setattr('streamlit_app.app_services.fetch_random_pending_ticket_id', lambda: 'T200')

    def fake_load_context(state):
        assert state == {'ticket_id': 'T200'}
        return {
            'ticket_id': 'T200',
            'ticket': {'ticket_id': 'T200'},
            'categories': [],
            'tags': [],
        }

    class FakeResponse:
        text = '{"summary":"ok"}'

    class FakeLLM:
        def invoke(self, messages):
            return FakeResponse()

    class FakeParsed:
        def model_dump(self, mode='json'):
            return {
                'summary': 'ok',
                'primary_category': None,
                'candidate_categories': [],
                'candidate_tags': [],
                'category_keywords': [],
                'tag_keywords': [],
                'risks': [],
            }

    class FakeValidatorOutput:
        @staticmethod
        def model_validate(data):
            return FakeParsed()

    monkeypatch.setattr('streamlit_app.app_services.load_context', fake_load_context)
    monkeypatch.setattr('streamlit_app.app_services.build_user_prompt', lambda **kwargs: 'PROMPT')
    monkeypatch.setattr('streamlit_app.app_services.get_chat_model', lambda: FakeLLM())
    monkeypatch.setattr('streamlit_app.app_services.parse_json_payload_once', lambda raw_text: {'summary': 'ok'})
    monkeypatch.setattr('streamlit_app.app_services.normalize_result', lambda raw_data, categories, tags: raw_data | {
        'primary_category': None,
        'candidate_categories': [],
        'candidate_tags': [],
        'category_keywords': [],
        'tag_keywords': [],
        'risks': [],
    })
    monkeypatch.setattr('streamlit_app.app_services.ValidatorOutput', FakeValidatorOutput)
    monkeypatch.setattr('streamlit_app.app_services.save_validator_result', lambda *args, **kwargs: {})
    monkeypatch.setattr('streamlit_app.app_services.fetch_ticket_result_rows', lambda ticket_id: {
        'category_results': [],
        'tag_results': [],
        'keyword_results': [],
        'match_details': [],
    })
    monkeypatch.setattr('streamlit_app.app_services.get_settings', lambda: type('S', (), {'llm_model_name': 'test-model'})())

    events = list(stream_single_ticket_job('   '))

    assert events[0]['ticket_id'] == 'T200'
    assert events[1]['ticket_id'] == 'T200'
