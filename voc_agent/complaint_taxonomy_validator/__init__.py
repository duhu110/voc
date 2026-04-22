from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ['graph', 'run_validator', 'save_validator_result', 'run_validator_and_persist', 'refresh_statistics']


def __getattr__(name: str) -> Any:
    if name in {'graph', 'run_validator'}:
        module = import_module('voc_agent.complaint_taxonomy_validator.chain')
        return getattr(module, name)
    if name in {'save_validator_result', 'run_validator_and_persist'}:
        module = import_module('voc_agent.complaint_taxonomy_validator.persistence')
        return getattr(module, name)
    if name == 'refresh_statistics':
        module = import_module('voc_agent.complaint_taxonomy_validator.stats_aggregation')
        return getattr(module, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
