import logging

import pytest

from filtering.filter import QAFilter


@pytest.mark.parametrize(
    "value,expected",
    [
        (True, True),
        (False, False),
        ("true", True),
        ("FALSE", False),
        ("Yes", True),
        ("no", False),
        ("1", True),
        ("0", False),
    ],
)
def test_normalise_pass_value_handles_common_inputs(value, expected):
    qa_filter = QAFilter()
    assert qa_filter._normalise_pass_value(value) is expected


def test_parse_response_handles_string_false(caplog):
    qa_filter = QAFilter()
    response = {"pass": "false", "reason": "The answer was incorrect."}

    with caplog.at_level(logging.WARNING):
        result = qa_filter._parse_response(response)

    assert result.filter_passed is False
    assert result.metadata["reason"] == "The answer was incorrect."
    # No warning should be emitted for a recognised boolean string.
    assert not any(record.levelno >= logging.WARNING for record in caplog.records)


def test_parse_response_logs_warning_for_unexpected_value(caplog):
    qa_filter = QAFilter()

    with caplog.at_level(logging.WARNING):
        result = qa_filter._parse_response({"pass": 3.14})

    assert result.filter_passed is False
    assert any("Falling back to False" in record.getMessage() for record in caplog.records)
