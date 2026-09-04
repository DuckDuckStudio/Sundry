from typing import NoReturn

import keyring
import pytest

from function.github.token import read_token


def test_read_token_returns_token_from_environment(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: "env")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setenv("GITHUB_TOKEN", "environment-token")

    assert read_token() == "environment-token"


def test_read_token_returns_none_when_environment_token_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: "env")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert read_token() is None
    assert "没有读取到 Token" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("source", "service_name"),
    [
        ("glm", "github-access-token.glm"),
        ("komac", "github-access-token.komac"),
    ],
)
def test_read_token_returns_token_from_keyring_source(
    source: str,
    service_name: str,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: source)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    calls: list[tuple[str, str]] = []

    def get_password(service: str, username: str) -> str:
        calls.append((service, username))
        return "keyring-token"

    monkeypatch.setattr(keyring, "get_password", get_password)

    assert read_token() == "keyring-token"
    assert calls == [(service_name, "github-access-token")]


def test_read_token_returns_none_for_invalid_source(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: "unknown")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert read_token() is None
    assert "未知的读取源 unknown" in capsys.readouterr().out


def test_read_token_returns_none_for_no_configed_source(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: None)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert read_token() is None
    assert "未能从配置文件中获取读取源" in capsys.readouterr().out


def test_read_token_returns_none_when_keyring_token_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: "komac")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setattr(keyring, "get_password", lambda service, username: None)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

    assert read_token() is None
    assert "没有读取到 Token" in capsys.readouterr().out


def test_read_token_return_none_when_keyring_raise_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    def raise_keyring_error(service_name: str, username: str) -> NoReturn:
        del service_name, username
        from keyring.errors import KeyringError

        raise KeyringError("123456")

    monkeypatch.setattr("function.github.token.读取配置", lambda name: "komac")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.setattr(keyring, "get_password", raise_keyring_error)

    assert read_token() is None
    assert "123456" in capsys.readouterr().out


def test_read_token_silent_failure_does_not_print(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("function.github.token.读取配置", lambda name: "env")  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert read_token(silent=True) is None
    assert capsys.readouterr().out == ""
