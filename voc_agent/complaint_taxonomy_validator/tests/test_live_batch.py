from __future__ import annotations

from voc_agent.complaint_taxonomy_validator.live_batch import run_live_batch


def test_run_live_batch_runs_without_artifacts(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        'voc_agent.complaint_taxonomy_validator.live_batch.fetch_pending_ticket_ids',
        lambda limit=500: ['T1', 'T2', 'T3'],
    )

    class FakeSettings:
        llm_model_name = 'test-model'

    monkeypatch.setattr(
        'voc_agent.complaint_taxonomy_validator.live_batch.get_settings',
        lambda: FakeSettings(),
    )

    def fake_run_validator_and_persist(ticket_id: str) -> dict:
        calls.append(ticket_id)
        if ticket_id == 'T2':
            raise RuntimeError('boom')
        return {
            'ticket_id': ticket_id,
            'result': {'summary': f'result-{ticket_id}'},
            'write_summary': {
                'category_results': 1,
                'tag_results': 2,
                'keyword_results': 3,
                'match_details': 4,
            },
        }

    monkeypatch.setattr(
        'voc_agent.complaint_taxonomy_validator.live_batch.run_validator_and_persist',
        fake_run_validator_and_persist,
    )

    summary = run_live_batch(sample_size=3)

    assert calls == ['T1', 'T2', 'T3']
    assert summary['sample_size'] == 3
    assert summary['success_count'] == 2
    assert summary['failure_count'] == 1
    assert summary['success_rate'] == 2 / 3
    assert summary['model_name'] == 'test-model'
    assert summary['results'][0]['status'] == 'success'
    assert summary['results'][1]['status'] == 'failed'
    assert 'summary_path' not in summary
    assert 'report_path' not in summary
    assert 'result_files' not in summary
