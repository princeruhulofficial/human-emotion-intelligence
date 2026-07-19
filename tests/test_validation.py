"""Unit tests for input validation (no LLM needed)"""

import pytest
from hei import HEI, HEIValidationError


@pytest.fixture
def hei():
    # No real API key needed for validation tests
    return HEI(api_key="sk-fake-key-for-validation-tests")


def test_empty_message_raises(hei):
    with pytest.raises(HEIValidationError, match="empty"):
        hei.analyze("")


def test_whitespace_only_raises(hei):
    with pytest.raises(HEIValidationError, match="empty"):
        hei.analyze("   \n\t  ")


def test_none_message_raises(hei):
    with pytest.raises(HEIValidationError):
        hei.analyze(None)  # type: ignore


def test_too_long_message_raises(hei):
    long_msg = "a" * 9000
    with pytest.raises(HEIValidationError, match="too long"):
        hei.analyze(long_msg)


def test_valid_message_passes_validation(hei):
    # Should not raise HEIValidationError (may raise HEIError later due to fake key)
    try:
        hei.analyze("Hello, I am feeling okay.")
    except HEIValidationError:
        pytest.fail("Valid message should not raise HEIValidationError")
    except Exception:
        # Expected because of fake API key
        pass
