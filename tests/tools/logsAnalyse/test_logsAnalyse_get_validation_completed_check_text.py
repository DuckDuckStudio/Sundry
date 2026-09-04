from typing import Any, Literal

import pytest

from tools.logsAnalyse import get_validation_completed_check_text


@pytest.mark.parametrize("check_suite_id", [None, 0])
def test_get_validation_completed_check_text_returns_none_for_missing_check_suite_id(check_suite_id: None | Literal[0]):
    assert get_validation_completed_check_text(check_suite_id) is None


def test_get_validation_completed_check_text_returns_none_when_api_returns_none(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: None,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_validation_completed_check_text(123) is None


@pytest.mark.parametrize(
    "response",
    [
        {},
        {"1": None},
        {"check_runs": {}},
        {"check_runs": ["invalid"]},
        {"check_runs": [{"name": "1"}]},
        {"check_runs": [{"name": "10. Validation Completed"}]},
        {"check_runs": [{"name": "10. Validation Completed", "output": "1"}]},
        {"check_runs": [{"name": "10. Validation Completed", "output": {"1": None}}]},
        {"check_runs": [{"name": "10. Validation Completed", "output": {"text": None}}]},
    ],
)
def test_get_validation_completed_check_text_returns_none_for_invalid_response(
    monkeypatch: pytest.MonkeyPatch,
    response: dict[str, Any],
):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: response,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_validation_completed_check_text(123) is None


def test_get_validation_completed_check_text_returns_validation_text(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: {  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
            "check_runs": [
                {"name": "9. Something Else", "output": {"text": "ignored"}},
                "invalid",
                {"name": "10. Validation Completed", "output": {"text": "validation details"}},
            ]
        },
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_validation_completed_check_text(123) == "validation details"
