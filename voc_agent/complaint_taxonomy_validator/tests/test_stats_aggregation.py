from __future__ import annotations

import pytest
from sqlalchemy import create_engine, text

from voc_agent.complaint_taxonomy_validator.stats_aggregation import refresh_statistics


def _build_stats_engine():
    engine = create_engine('sqlite+pysqlite:///:memory:', future=True)
    ddl_statements = [
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
            created_at timestamp not null,
            updated_at timestamp not null,
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
            created_at timestamp not null,
            updated_at timestamp not null,
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
            created_at timestamp not null,
            updated_at timestamp not null
        )
        """,
        """
        create table complaint_category_stats (
            id integer primary key autoincrement,
            category_id bigint not null,
            stat_date date not null,
            total_predicted_count integer not null default 0,
            total_final_count integer not null default 0,
            total_manual_confirmed_count integer not null default 0,
            total_correct_count integer not null default 0,
            total_wrong_count integer not null default 0,
            avg_confidence_score numeric,
            hit_rate numeric,
            accuracy_rate numeric,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_tag_stats (
            id integer primary key autoincrement,
            tag_id bigint not null,
            stat_date date not null,
            total_predicted_count integer not null default 0,
            total_final_count integer not null default 0,
            total_manual_confirmed_count integer not null default 0,
            total_correct_count integer not null default 0,
            total_wrong_count integer not null default 0,
            avg_confidence_score numeric,
            hit_rate numeric,
            accuracy_rate numeric,
            created_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_category_tag_stat_relation (
            id integer primary key autoincrement,
            category_id bigint not null,
            tag_id bigint not null,
            sample_count integer not null default 0,
            cooccurrence_count integer not null default 0,
            cooccurrence_rate numeric,
            confidence_score numeric,
            relation_strength numeric,
            last_calculated_at timestamp,
            created_at timestamp not null default current_timestamp,
            updated_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_category_keyword_stat (
            id integer primary key autoincrement,
            category_id bigint not null,
            keyword varchar(200) not null,
            sample_count integer not null default 0,
            hit_count integer not null default 0,
            confidence_score numeric,
            source varchar(50) not null default 'mining',
            last_calculated_at timestamp,
            created_at timestamp not null default current_timestamp,
            updated_at timestamp not null default current_timestamp
        )
        """,
        """
        create table complaint_tag_keyword_stat (
            id integer primary key autoincrement,
            tag_id bigint not null,
            keyword varchar(200) not null,
            sample_count integer not null default 0,
            hit_count integer not null default 0,
            confidence_score numeric,
            source varchar(50) not null default 'mining',
            last_calculated_at timestamp,
            created_at timestamp not null default current_timestamp,
            updated_at timestamp not null default current_timestamp
        )
        """,
    ]
    with engine.begin() as conn:
        for ddl in ddl_statements:
            conn.execute(text(ddl))
    return engine


def _seed_stats_source_data(engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                insert into complaint_ticket_category_result (
                    ticket_id, category_id, result_source, model_version, confidence_score,
                    ranking_no, is_final, is_manual_confirmed, matched_by, explanation,
                    created_at, updated_at, evaluation_status
                ) values
                ('T1', 101, 'ai', 'Qwen3-Max', 0.90, 1, 1, 0, 'ai', 'x', '2026-04-10 10:00:00', '2026-04-10 10:00:00', 'correct'),
                ('T1', 102, 'ai', 'Qwen3-Max', 0.70, 2, 0, 0, 'ai', 'x', '2026-04-10 10:00:00', '2026-04-10 10:00:00', null),
                ('T2', 101, 'ai', 'Qwen3-Max', 0.80, 1, 1, 1, 'ai', 'x', '2026-04-10 11:00:00', '2026-04-10 11:00:00', 'wrong'),
                ('T3', 103, 'ai', 'Qwen3-Max', 0.88, 1, 1, 0, 'ai', 'x', '2026-04-10 12:00:00', '2026-04-10 12:00:00', 'correct')
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_tag_result (
                    ticket_id, tag_id, result_source, model_version, confidence_score,
                    ranking_no, is_final, is_manual_confirmed, matched_by, explanation,
                    created_at, updated_at, evaluation_status
                ) values
                ('T1', 201, 'ai', 'Qwen3-Max', 0.95, 1, 1, 0, 'ai', 'x', '2026-04-10 10:00:00', '2026-04-10 10:00:00', 'correct'),
                ('T1', 202, 'ai', 'Qwen3-Max', 0.85, 2, 1, 0, 'ai', 'x', '2026-04-10 10:00:00', '2026-04-10 10:00:00', null),
                ('T2', 201, 'ai', 'Qwen3-Max', 0.75, 1, 1, 0, 'ai', 'x', '2026-04-10 11:00:00', '2026-04-10 11:00:00', 'wrong'),
                ('T3', 203, 'ai', 'Qwen3-Max', 0.82, 1, 1, 1, 'ai', 'x', '2026-04-10 12:00:00', '2026-04-10 12:00:00', 'correct')
                """
            )
        )
        conn.execute(
            text(
                """
                insert into complaint_ticket_keyword_result (
                    ticket_id, keyword, keyword_type, weight, source, created_at, updated_at
                ) values
                ('T1', '过户', 'category', 0.90, 'ai', '2026-04-10 10:00:00', '2026-04-10 10:00:00'),
                ('T1', '移动号码', 'tag', 0.80, 'ai', '2026-04-10 10:00:00', '2026-04-10 10:00:00'),
                ('T2', '过户', 'category', 0.70, 'ai', '2026-04-10 11:00:00', '2026-04-10 11:00:00'),
                ('T2', '解释规则', 'tag', 0.60, 'ai', '2026-04-10 11:00:00', '2026-04-10 11:00:00'),
                ('T3', '拆机', 'category', 0.88, 'ai', '2026-04-10 12:00:00', '2026-04-10 12:00:00'),
                ('T3', '宽带', 'tag', 0.85, 'ai', '2026-04-10 12:00:00', '2026-04-10 12:00:00')
                """
            )
        )


def test_refresh_statistics_populates_all_five_stat_tables(monkeypatch) -> None:
    engine = _build_stats_engine()
    _seed_stats_source_data(engine)

    monkeypatch.setattr('voc_agent.complaint_taxonomy_validator.stats_aggregation.get_engine', lambda: engine)

    summary = refresh_statistics(stat_date='2026-04-10')

    assert summary == {
        'stat_date': '2026-04-10',
        'category_stats': 3,
        'tag_stats': 3,
        'category_tag_relations': 3,
        'category_keyword_stats': 2,
        'tag_keyword_stats': 4,
    }

    with engine.connect() as conn:
        category_101 = conn.execute(
            text(
                """
                select total_predicted_count, total_final_count, total_manual_confirmed_count,
                       total_correct_count, total_wrong_count, avg_confidence_score, hit_rate, accuracy_rate
                from complaint_category_stats
                where category_id = 101 and stat_date = '2026-04-10'
                """
            )
        ).mappings().one()
        relation_101_201 = conn.execute(
            text(
                """
                select sample_count, cooccurrence_count, cooccurrence_rate, confidence_score, relation_strength
                from complaint_category_tag_stat_relation
                where category_id = 101 and tag_id = 201
                """
            )
        ).mappings().one()
        category_keyword = conn.execute(
            text(
                """
                select sample_count, hit_count, confidence_score, source
                from complaint_category_keyword_stat
                where category_id = 101 and keyword = '过户'
                """
            )
        ).mappings().one()
        tag_keyword = conn.execute(
            text(
                """
                select sample_count, hit_count, confidence_score, source
                from complaint_tag_keyword_stat
                where tag_id = 201 and keyword = '移动号码'
                """
            )
        ).mappings().one()

    assert category_101['total_predicted_count'] == 2
    assert category_101['total_final_count'] == 2
    assert category_101['total_manual_confirmed_count'] == 1
    assert category_101['total_correct_count'] == 1
    assert category_101['total_wrong_count'] == 1
    assert float(category_101['avg_confidence_score']) == pytest.approx(0.85)
    assert float(category_101['hit_rate']) == pytest.approx(1.0)
    assert float(category_101['accuracy_rate']) == pytest.approx(0.5)

    assert relation_101_201['sample_count'] == 2
    assert relation_101_201['cooccurrence_count'] == 2
    assert float(relation_101_201['cooccurrence_rate']) == pytest.approx(1.0)
    assert float(relation_101_201['confidence_score']) == pytest.approx(1.0)
    assert float(relation_101_201['relation_strength']) == pytest.approx(1.0)

    assert category_keyword['sample_count'] == 2
    assert category_keyword['hit_count'] == 2
    assert float(category_keyword['confidence_score']) == pytest.approx(1.0)
    assert category_keyword['source'] == 'mining'

    assert tag_keyword['sample_count'] == 2
    assert tag_keyword['hit_count'] == 1
    assert float(tag_keyword['confidence_score']) == pytest.approx(0.5)
    assert tag_keyword['source'] == 'mining'


def test_refresh_statistics_replaces_existing_rows_for_same_stat_date(monkeypatch) -> None:
    engine = _build_stats_engine()
    _seed_stats_source_data(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                insert into complaint_category_stats (
                    category_id, stat_date, total_predicted_count, total_final_count, total_manual_confirmed_count,
                    total_correct_count, total_wrong_count, avg_confidence_score, hit_rate, accuracy_rate
                ) values (
                    101, '2026-04-10', 99, 99, 99, 99, 99, 0.1, 0.1, 0.1
                )
                """
            )
        )

    monkeypatch.setattr('voc_agent.complaint_taxonomy_validator.stats_aggregation.get_engine', lambda: engine)

    refresh_statistics(stat_date='2026-04-10')

    with engine.connect() as conn:
        values = conn.execute(
            text(
                """
                select total_predicted_count, total_final_count
                from complaint_category_stats
                where category_id = 101 and stat_date = '2026-04-10'
                """
            )
        ).mappings().one()

    assert values['total_predicted_count'] == 2
    assert values['total_final_count'] == 2
