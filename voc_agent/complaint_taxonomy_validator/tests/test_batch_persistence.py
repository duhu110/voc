from __future__ import annotations

from pathlib import Path

from voc_agent.complaint_taxonomy_validator.batch_persistence import run_persistence_batch
from voc_agent.complaint_taxonomy_validator.tools.fetch_pending_ticket_ids import PENDING_TICKET_QUERY


def test_pending_ticket_query_only_selects_unprocessed_rows() -> None:
    query = str(PENDING_TICKET_QUERY).lower()

    assert 'from raw_complaint_tickets' in query
    assert 'where process_status = false' in query


def test_run_persistence_batch_records_success_and_failure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        'voc_agent.complaint_taxonomy_validator.batch_persistence.fetch_pending_ticket_ids',
        lambda limit=20: ['T1', 'T2', 'T3'],
    )

    def fake_run_validator_and_persist(ticket_id: str) -> dict:
        if ticket_id == 'T2':
            raise RuntimeError('boom')
        return {
            'ticket_id': ticket_id,
            'result': {'summary': f'result-{ticket_id}'},
            'write_summary': {
                'category_results': 2,
                'tag_results': 3,
                'keyword_results': 4,
                'match_details': 5,
            },
        }

    monkeypatch.setattr(
        'voc_agent.complaint_taxonomy_validator.batch_persistence.run_validator_and_persist',
        fake_run_validator_and_persist,
    )

    summary = run_persistence_batch(sample_size=3, output_dir=tmp_path)

    assert summary['sample_size'] == 3
    assert summary['success_count'] == 2
    assert summary['failure_count'] == 1
    assert summary['success_rate'] == 2 / 3
    assert summary['failures_by_stage'] == {'persistence': 1}
    assert Path(summary['summary_path']).exists()
    assert Path(summary['report_path']).exists()
    assert summary['results'][0]['write_summary']['category_results'] == 2
    assert summary['results'][1]['status'] == 'failed'
