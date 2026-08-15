"""Tests for verdict parsing in research-eval.py.

Regression tests for #2: substring-matching the whole judge output scored
REQUIREMENTS_NOT_MET verdicts as passes whenever the step-by-step analysis
mentioned REQUIREMENTS_MET, and a "Generation failed" placeholder as a clean
fail. Run with pytest; no network or API keys needed. The provider SDKs the
script imports at module level are stubbed since none of the tested code
touches them.
"""

import importlib.util
import sys
import types
from pathlib import Path

for _mod in ("mistralai",):
    if _mod not in sys.modules:
        sys.modules[_mod] = types.ModuleType(_mod)

_spec = importlib.util.spec_from_file_location(
    "research_eval", Path(__file__).parent / "research-eval.py"
)
_re = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_re)
parse_verdict = _re.parse_verdict


def test_plain_pass():
    assert parse_verdict("Final answer: REQUIREMENTS_MET") is True


def test_plain_fail():
    assert parse_verdict("Final answer: REQUIREMENTS_NOT_MET") is False


def test_analysis_mentioning_pass_token_does_not_flip_a_fail():
    out = (
        "Requirement 2 is violated, which rules out REQUIREMENTS_MET.\n"
        "Final answer: REQUIREMENTS_NOT_MET"
    )
    assert parse_verdict(out) is False


def test_analysis_mentioning_both_tokens_keeps_a_pass():
    out = (
        "I must choose between REQUIREMENTS_MET and REQUIREMENTS_NOT_MET.\n"
        "All requirements hold.\nFinal answer: REQUIREMENTS_MET"
    )
    assert parse_verdict(out) is True


def test_failed_generation_placeholder_is_unparseable_not_a_fail():
    assert parse_verdict("Generation failed after 3 trials") is None


def test_empty_output_is_unparseable():
    assert parse_verdict("") is None
