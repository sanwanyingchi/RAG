"""Filtering logic used by the QA pipeline.

This module intentionally implements only the pieces required by the unit
suite that accompanies this kata.  The :class:`QAFilter` class exposes a
``_parse_response`` helper which interprets responses returned by the
underlying model and normalises their structure for downstream consumers.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FilterResponse:
    """Container object returned by :class:`QAFilter`.

    Attributes
    ----------
    filter_passed:
        Indicates whether a document/question pair passed the QA filter.
    metadata:
        Any additional information extracted from the raw response.  The
        metadata is intentionally permissive because different back-ends may
        choose to return a variety of diagnostic fields.
    """

    filter_passed: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class QAFilter:
    """Helper responsible for interpreting model responses.

    The filter currently focuses on the ``"pass"`` key returned by the model.
    Some models may return booleans, while others serialise the value as a
    string.  ``QAFilter`` smooths over those differences by ensuring that the
    downstream pipeline always receives a proper boolean.
    """

    _TRUTHY_STRINGS = {"true", "t", "yes", "y", "1"}
    _FALSY_STRINGS = {"false", "f", "no", "n", "0"}

    def _parse_response(self, response: Mapping[str, Any]) -> FilterResponse:
        """Convert a raw model response into :class:`FilterResponse`.

        Parameters
        ----------
        response:
            Mapping returned by the model.  Only the ``"pass"`` key is
            required, although additional diagnostic keys are preserved in the
            resulting metadata.
        """

        if not isinstance(response, Mapping):  # pragma: no cover - defensive
            logger.warning("Unexpected response type %s. Treating as failure.", type(response).__name__)
            return FilterResponse(filter_passed=False, metadata={"raw": response})

        raw_pass = response.get("pass")
        filter_passed = self._normalise_pass_value(raw_pass)

        metadata = {key: value for key, value in response.items() if key != "pass"}
        if "raw" not in metadata:
            metadata["raw"] = response

        return FilterResponse(filter_passed=filter_passed, metadata=metadata)

    def _normalise_pass_value(self, value: Any) -> bool:
        """Normalise the ``"pass"`` field exposed by the model.

        Real booleans are returned unchanged.  String values are interpreted in
        a case-insensitive manner and accept a handful of common variants such
        as ``"yes"``/``"no"``.  Anything else is considered an invalid value
        and results in ``False`` with a warning so that the issue can be
        diagnosed during development.
        """

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalised = value.strip().lower()
            if normalised in self._TRUTHY_STRINGS:
                return True
            if normalised in self._FALSY_STRINGS:
                return False

        logger.warning("Received non-boolean value for 'pass': %r. Falling back to False.", value)
        return False


__all__ = ["FilterResponse", "QAFilter"]
