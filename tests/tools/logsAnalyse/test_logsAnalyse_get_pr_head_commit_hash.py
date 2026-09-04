from typing import Literal

import pytest

from tools.logsAnalyse import get_pr_head_commit_hash


@pytest.mark.parametrize("pr_number", [None, 0])
def test_get_pr_head_commit_hash_returns_none_for_missing_pr_number(pr_number: None | Literal[0]):
    assert get_pr_head_commit_hash(pr_number) is None


def test_get_pr_head_commit_hash_returns_sha(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: {"head": {"sha": "abc123def456"}},  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_pr_head_commit_hash(123) == "abc123def456"


def test_get_pr_head_commit_hash_returns_none_when_api_response_missing_head(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: {"message": "Not Found"},  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_pr_head_commit_hash(123) is None


def test_get_pr_head_commit_hash_returns_none_when_api_returns_none(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "tools.logsAnalyse.请求GitHubAPI",
        lambda *args, **kwargs: None,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr("tools.logsAnalyse.read_token", lambda: None)

    assert get_pr_head_commit_hash(123) is None
