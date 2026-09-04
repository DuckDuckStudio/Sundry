from typing import Any

import pytest

from tools.logsAnalyse import get_check_suite_id


@pytest.mark.parametrize("commit_hash", [None, ""])
def test_get_check_suite_id_returns_none_for_missing_commit_hash(commit_hash: None | str):
    assert get_check_suite_id(commit_hash) is None


def test_get_check_suite_id_returns_none_when_api_returns_none(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: None,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_check_suite_id("abc123") is None


@pytest.mark.parametrize("response", [{}, {"abc": {}}, {"check_suites": {}}, {"check_suites": ["invalid"]}, {"check_suites": [{"1": None}]}])
def test_get_check_suite_id_returns_none_for_invalid_check_suites_response(
    monkeypatch: pytest.MonkeyPatch,
    response: dict[str, Any],
):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: response,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_check_suite_id("abc123") is None


def test_get_check_suite_id_returns_validator_suite_id(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: {  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
            "check_suites": [
                {"app": {"name": "Other App"}, "id": 111},
                "invalid",
                {"app": {"name": "WinGetValidator-Prod"}, "id": 222},
            ]
        },
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_check_suite_id("abc123") == 222


def test_get_check_suite_id_returns_none_when_validator_suite_id_is_not_int(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: {  # pyright: ignore[reportUnknownLambdaType,reportUnknownArgumentType]
            "check_suites": [
                {"app": {"name": "WinGetValidator-Prod"}, "id": "not int"},
            ]
        },
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_check_suite_id("abc123") is None
