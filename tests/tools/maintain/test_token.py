from typing import NoReturn

import keyring
import pytest

from tools.maintain.token import read_token


def test_read_token_returns_token_from_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: "env")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setenv("GITHUB_TOKEN", "environment-token")

    assert read_token() == "environment-token"


def test_read_token_returns_none_when_environment_token_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: "env")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert read_token() is None
    assert "未能从环境变量 GITHUB_TOKEN 中读取 GitHub Token" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("source", "service_name", "username"),
    [
        ("keyring", "DuckStudio.Sundry-GitHubToken", "GitHubToken"),
        ("glm", "github-access-token.glm", "github-access-token"),
        ("komac", "github-access-token.komac", "github-access-token"),
    ],
)
def test_read_token_returns_token_from_keyring_source(
    source: str,
    service_name: str,
    username: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: source)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    calls: list[tuple[str, str]] = []

    def get_password(service: str, username: str) -> str:
        calls.append((service, username))
        return "keyring-token"

    monkeypatch.setattr(keyring, "get_password", get_password)

    assert read_token() == "keyring-token"
    assert calls == [(service_name, username)]


def test_read_token_returns_none_for_invalid_source(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: "unknown")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert read_token() is None
    assert "未知的 GitHub Token 读取源: unknown" in capsys.readouterr().out


def test_read_token_returns_none_for_no_configed_source(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: None)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert read_token() is None
    assert "未能从配置文件中获取 GitHub Token 读取源" in capsys.readouterr().out


def test_read_token_returns_none_when_keyring_token_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: "komac")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setattr(keyring, "get_password", lambda service, username: None)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert read_token() is None
    assert "未能从 komac 源中读取 GitHub Token" in capsys.readouterr().out


def test_read_token_return_none_when_keyring_raise_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    def raise_keyring_error(service_name: str, username: str) -> NoReturn:
        del service_name, username
        from keyring.errors import KeyringError

        raise KeyringError("123456")

    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: "komac")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setattr(keyring, "get_password", raise_keyring_error)

    assert read_token() is None

    output = capsys.readouterr().out
    assert "读取 GitHub Token 失败:" in output
    assert "123456" in output


def test_read_token_silent_failure_does_not_print(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("tools.maintain.token.读取配置", lambda name: "env")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert read_token(silent=True) is None
    assert capsys.readouterr().out == ""
