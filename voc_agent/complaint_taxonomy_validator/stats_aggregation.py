from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from sqlalchemy import text

from voc_agent.core.db import get_engine

CATEGORY_RESULT_QUERY = text(
    """
    select ticket_id, category_id, confidence_score, is_final, is_manual_confirmed, evaluation_status, created_at
    from complaint_ticket_category_result
    where result_source = 'ai' and date(created_at) = :stat_date
    """
)

TAG_RESULT_QUERY = text(
    """
    select ticket_id, tag_id, confidence_score, is_final, is_manual_confirmed, evaluation_status, created_at
    from complaint_ticket_tag_result
    where result_source = 'ai' and date(created_at) = :stat_date
    """
)

FINAL_CATEGORY_RESULT_QUERY = text(
    """
    select ticket_id, category_id
    from complaint_ticket_category_result
    where result_source = 'ai' and is_final = true
    """
)

FINAL_TAG_RESULT_QUERY = text(
    """
    select ticket_id, tag_id
    from complaint_ticket_tag_result
    where result_source = 'ai' and is_final = true
    """
)

CATEGORY_KEYWORD_QUERY = text(
    """
    select ticket_id, keyword, weight
    from complaint_ticket_keyword_result
    where source = 'ai' and keyword_type = 'category'
    """
)

TAG_KEYWORD_QUERY = text(
    """
    select ticket_id, keyword, weight
    from complaint_ticket_keyword_result
    where source = 'ai' and keyword_type = 'tag'
    """
)

DELETE_CATEGORY_STATS_SQL = text(
    """
    delete from complaint_category_stats
    where stat_date = :stat_date
    """
)

DELETE_TAG_STATS_SQL = text(
    """
    delete from complaint_tag_stats
    where stat_date = :stat_date
    """
)

DELETE_CATEGORY_TAG_RELATION_SQL = text("delete from complaint_category_tag_stat_relation")
DELETE_CATEGORY_KEYWORD_SQL = text("delete from complaint_category_keyword_stat")
DELETE_TAG_KEYWORD_SQL = text("delete from complaint_tag_keyword_stat")

CATEGORY_STATS_INSERT_SQL = text(
    """
    insert into complaint_category_stats (
        category_id, stat_date, total_predicted_count, total_final_count,
        total_manual_confirmed_count, total_correct_count, total_wrong_count,
        avg_confidence_score, hit_rate, accuracy_rate
    ) values (
        :category_id, :stat_date, :total_predicted_count, :total_final_count,
        :total_manual_confirmed_count, :total_correct_count, :total_wrong_count,
        :avg_confidence_score, :hit_rate, :accuracy_rate
    )
    """
)

TAG_STATS_INSERT_SQL = text(
    """
    insert into complaint_tag_stats (
        tag_id, stat_date, total_predicted_count, total_final_count,
        total_manual_confirmed_count, total_correct_count, total_wrong_count,
        avg_confidence_score, hit_rate, accuracy_rate
    ) values (
        :tag_id, :stat_date, :total_predicted_count, :total_final_count,
        :total_manual_confirmed_count, :total_correct_count, :total_wrong_count,
        :avg_confidence_score, :hit_rate, :accuracy_rate
    )
    """
)

CATEGORY_TAG_RELATION_INSERT_SQL = text(
    """
    insert into complaint_category_tag_stat_relation (
        category_id, tag_id, sample_count, cooccurrence_count,
        cooccurrence_rate, confidence_score, relation_strength, last_calculated_at
    ) values (
        :category_id, :tag_id, :sample_count, :cooccurrence_count,
        :cooccurrence_rate, :confidence_score, :relation_strength, :last_calculated_at
    )
    """
)

CATEGORY_KEYWORD_INSERT_SQL = text(
    """
    insert into complaint_category_keyword_stat (
        category_id, keyword, sample_count, hit_count, confidence_score, source, last_calculated_at
    ) values (
        :category_id, :keyword, :sample_count, :hit_count, :confidence_score, :source, :last_calculated_at
    )
    """
)

TAG_KEYWORD_INSERT_SQL = text(
    """
    insert into complaint_tag_keyword_stat (
        tag_id, keyword, sample_count, hit_count, confidence_score, source, last_calculated_at
    ) values (
        :tag_id, :keyword, :sample_count, :hit_count, :confidence_score, :source, :last_calculated_at
    )
    """
)


def _normalize_stat_date(stat_date: str | None) -> str:
    if stat_date:
        return stat_date
    return date.today().isoformat()


def _fetch_rows(statement: Any, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    with get_engine().connect() as conn:
        rows = conn.execute(statement, params or {}).mappings().all()
    return [dict(row) for row in rows]


def _safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return float(numerator) / float(denominator)


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _build_category_stats_rows(category_rows: list[dict[str, Any]], stat_date: str) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in category_rows:
        grouped[int(row['category_id'])].append(row)

    results: list[dict[str, Any]] = []
    for category_id, rows in grouped.items():
        total_predicted_count = len(rows)
        total_final_count = sum(1 for row in rows if bool(row['is_final']))
        total_manual_confirmed_count = sum(1 for row in rows if bool(row['is_manual_confirmed']))
        total_correct_count = sum(1 for row in rows if row.get('evaluation_status') == 'correct')
        total_wrong_count = sum(1 for row in rows if row.get('evaluation_status') == 'wrong')
        avg_confidence_score = _average([float(row['confidence_score']) for row in rows if row.get('confidence_score') is not None])
        results.append(
            {
                'category_id': category_id,
                'stat_date': stat_date,
                'total_predicted_count': total_predicted_count,
                'total_final_count': total_final_count,
                'total_manual_confirmed_count': total_manual_confirmed_count,
                'total_correct_count': total_correct_count,
                'total_wrong_count': total_wrong_count,
                'avg_confidence_score': avg_confidence_score,
                'hit_rate': _safe_ratio(total_final_count, total_predicted_count),
                'accuracy_rate': _safe_ratio(total_correct_count, total_correct_count + total_wrong_count),
            }
        )
    return results


def _build_tag_stats_rows(tag_rows: list[dict[str, Any]], stat_date: str) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in tag_rows:
        grouped[int(row['tag_id'])].append(row)

    results: list[dict[str, Any]] = []
    for tag_id, rows in grouped.items():
        total_predicted_count = len(rows)
        total_final_count = sum(1 for row in rows if bool(row['is_final']))
        total_manual_confirmed_count = sum(1 for row in rows if bool(row['is_manual_confirmed']))
        total_correct_count = sum(1 for row in rows if row.get('evaluation_status') == 'correct')
        total_wrong_count = sum(1 for row in rows if row.get('evaluation_status') == 'wrong')
        avg_confidence_score = _average([float(row['confidence_score']) for row in rows if row.get('confidence_score') is not None])
        results.append(
            {
                'tag_id': tag_id,
                'stat_date': stat_date,
                'total_predicted_count': total_predicted_count,
                'total_final_count': total_final_count,
                'total_manual_confirmed_count': total_manual_confirmed_count,
                'total_correct_count': total_correct_count,
                'total_wrong_count': total_wrong_count,
                'avg_confidence_score': avg_confidence_score,
                'hit_rate': _safe_ratio(total_final_count, total_predicted_count),
                'accuracy_rate': _safe_ratio(total_correct_count, total_correct_count + total_wrong_count),
            }
        )
    return results


def _build_category_tag_relation_rows(
    final_category_rows: list[dict[str, Any]],
    final_tag_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    categories_by_ticket: dict[str, set[int]] = defaultdict(set)
    tags_by_ticket: dict[str, set[int]] = defaultdict(set)
    category_sample_counts: dict[int, int] = defaultdict(int)
    tag_sample_counts: dict[int, int] = defaultdict(int)
    pair_counts: dict[tuple[int, int], int] = defaultdict(int)
    now = datetime.now().isoformat(sep=' ', timespec='seconds')

    for row in final_category_rows:
        ticket_id = str(row['ticket_id'])
        category_id = int(row['category_id'])
        if category_id not in categories_by_ticket[ticket_id]:
            category_sample_counts[category_id] += 1
        categories_by_ticket[ticket_id].add(category_id)

    for row in final_tag_rows:
        ticket_id = str(row['ticket_id'])
        tag_id = int(row['tag_id'])
        if tag_id not in tags_by_ticket[ticket_id]:
            tag_sample_counts[tag_id] += 1
        tags_by_ticket[ticket_id].add(tag_id)

    for ticket_id, category_ids in categories_by_ticket.items():
        tag_ids = tags_by_ticket.get(ticket_id, set())
        for category_id in category_ids:
            for tag_id in tag_ids:
                pair_counts[(category_id, tag_id)] += 1

    results: list[dict[str, Any]] = []
    for (category_id, tag_id), cooccurrence_count in pair_counts.items():
        category_rate = _safe_ratio(cooccurrence_count, category_sample_counts[category_id])
        tag_rate = _safe_ratio(cooccurrence_count, tag_sample_counts[tag_id])
        relation_strength = None
        if category_rate is not None and tag_rate is not None:
            relation_strength = (category_rate + tag_rate) / 2
        results.append(
            {
                'category_id': category_id,
                'tag_id': tag_id,
                'sample_count': category_sample_counts[category_id],
                'cooccurrence_count': cooccurrence_count,
                'cooccurrence_rate': category_rate,
                'confidence_score': category_rate,
                'relation_strength': relation_strength,
                'last_calculated_at': now,
            }
        )
    return results


def _build_category_keyword_rows(
    final_category_rows: list[dict[str, Any]],
    category_keyword_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    categories_by_ticket: dict[str, set[int]] = defaultdict(set)
    keywords_by_ticket: dict[str, set[str]] = defaultdict(set)
    category_sample_counts: dict[int, int] = defaultdict(int)
    pair_counts: dict[tuple[int, str], int] = defaultdict(int)
    now = datetime.now().isoformat(sep=' ', timespec='seconds')

    for row in final_category_rows:
        ticket_id = str(row['ticket_id'])
        category_id = int(row['category_id'])
        if category_id not in categories_by_ticket[ticket_id]:
            category_sample_counts[category_id] += 1
        categories_by_ticket[ticket_id].add(category_id)

    for row in category_keyword_rows:
        keywords_by_ticket[str(row['ticket_id'])].add(str(row['keyword']))

    for ticket_id, category_ids in categories_by_ticket.items():
        for category_id in category_ids:
            for keyword in keywords_by_ticket.get(ticket_id, set()):
                pair_counts[(category_id, keyword)] += 1

    results: list[dict[str, Any]] = []
    for (category_id, keyword), hit_count in pair_counts.items():
        sample_count = category_sample_counts[category_id]
        results.append(
            {
                'category_id': category_id,
                'keyword': keyword,
                'sample_count': sample_count,
                'hit_count': hit_count,
                'confidence_score': _safe_ratio(hit_count, sample_count),
                'source': 'mining',
                'last_calculated_at': now,
            }
        )
    return results


def _build_tag_keyword_rows(
    final_tag_rows: list[dict[str, Any]],
    tag_keyword_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    tags_by_ticket: dict[str, set[int]] = defaultdict(set)
    keywords_by_ticket: dict[str, set[str]] = defaultdict(set)
    tag_sample_counts: dict[int, int] = defaultdict(int)
    pair_counts: dict[tuple[int, str], int] = defaultdict(int)
    now = datetime.now().isoformat(sep=' ', timespec='seconds')

    for row in final_tag_rows:
        ticket_id = str(row['ticket_id'])
        tag_id = int(row['tag_id'])
        if tag_id not in tags_by_ticket[ticket_id]:
            tag_sample_counts[tag_id] += 1
        tags_by_ticket[ticket_id].add(tag_id)

    for row in tag_keyword_rows:
        keywords_by_ticket[str(row['ticket_id'])].add(str(row['keyword']))

    for ticket_id, tag_ids in tags_by_ticket.items():
        for tag_id in tag_ids:
            for keyword in keywords_by_ticket.get(ticket_id, set()):
                pair_counts[(tag_id, keyword)] += 1

    results: list[dict[str, Any]] = []
    for (tag_id, keyword), hit_count in pair_counts.items():
        sample_count = tag_sample_counts[tag_id]
        results.append(
            {
                'tag_id': tag_id,
                'keyword': keyword,
                'sample_count': sample_count,
                'hit_count': hit_count,
                'confidence_score': _safe_ratio(hit_count, sample_count),
                'source': 'mining',
                'last_calculated_at': now,
            }
        )
    return results


def _execute_many(conn: Any, statement: Any, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    conn.execute(statement, rows)
    return len(rows)


def refresh_statistics(stat_date: str | None = None) -> dict[str, Any]:
    """Refresh statistics and relation tables from persisted AI result tables."""
    normalized_stat_date = _normalize_stat_date(stat_date)
    category_rows = _fetch_rows(CATEGORY_RESULT_QUERY, {'stat_date': normalized_stat_date})
    tag_rows = _fetch_rows(TAG_RESULT_QUERY, {'stat_date': normalized_stat_date})
    final_category_rows = _fetch_rows(FINAL_CATEGORY_RESULT_QUERY)
    final_tag_rows = _fetch_rows(FINAL_TAG_RESULT_QUERY)
    category_keyword_rows = _fetch_rows(CATEGORY_KEYWORD_QUERY)
    tag_keyword_rows = _fetch_rows(TAG_KEYWORD_QUERY)

    category_stats_rows = _build_category_stats_rows(category_rows, normalized_stat_date)
    tag_stats_rows = _build_tag_stats_rows(tag_rows, normalized_stat_date)
    relation_rows = _build_category_tag_relation_rows(final_category_rows, final_tag_rows)
    category_keyword_stat_rows = _build_category_keyword_rows(final_category_rows, category_keyword_rows)
    tag_keyword_stat_rows = _build_tag_keyword_rows(final_tag_rows, tag_keyword_rows)

    with get_engine().begin() as conn:
        conn.execute(DELETE_CATEGORY_STATS_SQL, {'stat_date': normalized_stat_date})
        conn.execute(DELETE_TAG_STATS_SQL, {'stat_date': normalized_stat_date})
        conn.execute(DELETE_CATEGORY_TAG_RELATION_SQL)
        conn.execute(DELETE_CATEGORY_KEYWORD_SQL)
        conn.execute(DELETE_TAG_KEYWORD_SQL)

        category_stats_count = _execute_many(conn, CATEGORY_STATS_INSERT_SQL, category_stats_rows)
        tag_stats_count = _execute_many(conn, TAG_STATS_INSERT_SQL, tag_stats_rows)
        relation_count = _execute_many(conn, CATEGORY_TAG_RELATION_INSERT_SQL, relation_rows)
        category_keyword_count = _execute_many(conn, CATEGORY_KEYWORD_INSERT_SQL, category_keyword_stat_rows)
        tag_keyword_count = _execute_many(conn, TAG_KEYWORD_INSERT_SQL, tag_keyword_stat_rows)

    return {
        'stat_date': normalized_stat_date,
        'category_stats': category_stats_count,
        'tag_stats': tag_stats_count,
        'category_tag_relations': relation_count,
        'category_keyword_stats': category_keyword_count,
        'tag_keyword_stats': tag_keyword_count,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Refresh complaint taxonomy statistics tables.')
    parser.add_argument('--stat-date', help='Stat date in YYYY-MM-DD. Category/tag stats will refresh this date.')
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = refresh_statistics(stat_date=args.stat_date)
    print(summary)


if __name__ == '__main__':
    main()
