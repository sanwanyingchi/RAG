import logging

import pytest

from filtering.filter import QAFilter


@pytest.mark.parametrize(
    "value, expected",
    [
        (True, True),
        (False, False),
        ("true", True),
        ("TRUE", True),
        ("yes", True),
        ("no", False),
        ("false", False),
        ("FALSE", False),
    ],
)
def test_parse_response_supported_values(value, expected):
    qa_filter = QAFilter()
    qa_filter._parse_response({"pass": value})
    assert qa_filter.filter_passed is expected


def test_parse_response_invalid_string_logs_warning(caplog):
    qa_filter = QAFilter()
    caplog.set_level(logging.WARNING)

    qa_filter._parse_response({"pass": "maybe"})

    assert qa_filter.filter_passed is False
    assert "Unrecognized string" in caplog.text


@pytest.mark.parametrize("value", [None, 1, 0.0, [], {}])
def test_parse_response_unexpected_types_default_to_false(caplog, value):
    qa_filter = QAFilter()
    caplog.set_level(logging.WARNING)

    qa_filter._parse_response({"pass": value})

    assert qa_filter.filter_passed is False
    assert "defaulting to failure" in caplog.text


def test_parse_response_missing_key(caplog):
    qa_filter = QAFilter()
    caplog.set_level(logging.WARNING)

    qa_filter._parse_response({})

    assert qa_filter.filter_passed is False
    assert "missing 'pass' value" in caplog.text
