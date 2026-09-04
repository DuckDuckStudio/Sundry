from pathlib import Path
from typing import Any

import pytest

from tools.logsAnalyse import get_validation_log_zip_from_args


def test_get_validation_log_zip_from_args_returns_none_when_pr_number_is_missing(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("tools.logsAnalyse.IssueNumber", lambda arg: None)  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]

    assert get_validation_log_zip_from_args(["invalid"]) is None


def test_get_validation_log_zip_from_args_downloads_log_zip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    calls: list[tuple[str, Any]] = []
    expected_path = tmp_path / "validation.zip"

    monkeypatch.setattr(
        "tools.logsAnalyse.IssueNumber",
        lambda arg: calls.append(("IssueNumber", arg)) or "123",  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr(
        "tools.logsAnalyse.get_pr_head_commit_hash",
        lambda pr_number: calls.append(("get_pr_head_commit_hash", pr_number)) or "commit-sha",  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr(
        "tools.logsAnalyse.get_check_suite_id",
        lambda commit_hash: calls.append(("get_check_suite_id", commit_hash)) or 456,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr(
        "tools.logsAnalyse.get_validation_completed_check_text",
        lambda check_suite_id: calls.append(("get_validation_completed_check_text", check_suite_id)) or "check text",  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr(
        "tools.logsAnalyse.match_validation_log_download_url",
        lambda check_text: calls.append(("match_validation_log_download_url", check_text)) or "download URL",  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )
    monkeypatch.setattr(
        "tools.logsAnalyse.download_validation_log_zip",
        lambda download_url: calls.append(("download_validation_log_zip", download_url)) or expected_path,  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    )

    assert get_validation_log_zip_from_args(["https://github.com/microsoft/winget-pkgs/pull/123"]) == expected_path
    assert calls == [
        ("IssueNumber", "https://github.com/microsoft/winget-pkgs/pull/123"),
        ("get_pr_head_commit_hash", 123),
        ("get_check_suite_id", "commit-sha"),
        ("get_validation_completed_check_text", 456),
        ("match_validation_log_download_url", "check text"),
        ("download_validation_log_zip", "download URL"),
    ]


def test_get_validation_log_zip_from_args_returns_none_when_download_fails(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("tools.logsAnalyse.IssueNumber", lambda arg: "123")  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    monkeypatch.setattr("tools.logsAnalyse.get_pr_head_commit_hash", lambda pr_number: "commit-sha")  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    monkeypatch.setattr("tools.logsAnalyse.get_check_suite_id", lambda commit_hash: 456)  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    monkeypatch.setattr("tools.logsAnalyse.get_validation_completed_check_text", lambda check_suite_id: "check text")  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    monkeypatch.setattr("tools.logsAnalyse.match_validation_log_download_url", lambda check_text: "download URL")  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]
    monkeypatch.setattr("tools.logsAnalyse.download_validation_log_zip", lambda download_url: None)  # pyright: ignore[reportUnknownArgumentType,reportUnknownLambdaType]

    assert get_validation_log_zip_from_args(["123"]) is None
