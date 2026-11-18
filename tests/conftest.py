from __future__ import annotations

import pytest
from src.backend.employers.registry import reset_registry


@pytest.fixture(autouse=True)
def clean_employer_registry_state():
    """
    Autouse fixture guaranteeing pure test environment isolation.
    Resets the in-memory employer registry singleton before and after every test,
    preventing state leakage between test modules.
    """
    reset_registry()
    yield
    reset_registry()
