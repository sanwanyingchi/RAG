"""Filtering utilities for question-answering pipelines."""

from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class QAFilter:
    """Filter helper that parses model responses for pass/fail signals."""

    def __init__(self) -> None:
        self.filter_passed: bool = False

    def _parse_response(self, response: Mapping[str, Any] | None) -> None:
        """Parse a model response to determine whether the filter passed.

        The model is expected to return a mapping that includes a ``"pass"``
        key whose value indicates whether the filter should allow the sample to
        pass through. Historically the ``"pass"`` field was assumed to be a
        boolean. Some models instead return the value as a string (for example
        ``"true"`` or ``"false"``). This method understands both formats. Any
        other value is treated as a failure and results in a warning so that
        misconfigured prompts can be diagnosed quickly.
        """

        # Default to ``False`` unless a valid value is provided.
        parsed_value = False

        if response is None:
            logger.warning("QA filter received no response; defaulting to failure.")
            self.filter_passed = parsed_value
            return

        raw_value: Any
        try:
            raw_value = response.get("pass") if isinstance(response, Mapping) else None
        except Exception as exc:  # pragma: no cover - very defensive
            logger.warning(
                "Failed to read 'pass' value from QA filter response %r: %s", response, exc
            )
            self.filter_passed = parsed_value
            return

        if isinstance(raw_value, bool):
            self.filter_passed = raw_value
            return

        if isinstance(raw_value, str):
            normalized = raw_value.strip().lower()
            if normalized in {"true", "yes"}:
                self.filter_passed = True
                return
            if normalized in {"false", "no"}:
                self.filter_passed = False
                return
            logger.warning(
                "Unrecognized string for QA filter 'pass' value: %r; defaulting to failure.",
                raw_value,
            )
            self.filter_passed = parsed_value
            return

        if raw_value is None:
            logger.warning(
                "QA filter response missing 'pass' value; defaulting to failure."
            )
        else:
            logger.warning(
                "Unexpected type %s for QA filter 'pass' value %r; defaulting to failure.",
                type(raw_value).__name__,
                raw_value,
            )

        self.filter_passed = parsed_value


__all__ = ["QAFilter"]
