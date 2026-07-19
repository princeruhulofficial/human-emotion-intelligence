import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: marks tests that call real LLMs (deselect with '-m "not integration"')"
    )
