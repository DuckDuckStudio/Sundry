# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

from typing import NoReturn
from unittest.mock import Mock

import keyring.errors
import pytest

from tools.maintain import token


class TestMain:
    """
    对 `tools.maintain.token` 模块中的 `main` 函数的测试。
    """

    @pytest.mark.parametrize(("operation", "function_name"), (("set", "set_token"), ("remove", "remove_token")))
    def test_main_dispatches_supported_operations(self, operation: str, function_name: str, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `main` 函数应将支持的操作分发给对应的函数。
        """

        fake_function = Mock(return_value=0)
        monkeypatch.setattr(token, function_name, fake_function)

        assert token.main(operation) == 0
        fake_function.assert_called_once_with()

    @pytest.mark.parametrize(("operation", "message"), (("", "请告诉我你要做什么"), ("other", "未知的操作")))
    def test_main_rejects_unsupported_operations(self, operation: str, message: str, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `main` 函数应拒绝空操作和未知操作并输出提示。
        """

        assert token.main(operation) == 1
        assert message in capsys.readouterr().out


class TestRemoveToken:
    """
    对 `tools.maintain.token` 模块中的 `remove_token` 函数的测试。
    """

    def test_remove_token_deletes_saved_token(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `remove_token` 函数应删除已保存的 Token 并返回成功。
        """

        fake_delete_password = Mock()
        monkeypatch.setattr(token.keyring, "delete_password", fake_delete_password)

        assert token.remove_token() == 0
        fake_delete_password.assert_called_once_with(service_name="DuckStudio.Sundry-GitHubToken", username="GitHubToken")
        assert "成功移除设置的 Token" in capsys.readouterr().out

    def test_remove_token_handles_missing_saved_token(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `remove_token` 函数应在没有已保存 Token 时提示用户并返回成功。
        """

        def _fake_delete_password(service_name: str, username: str) -> NoReturn:
            """
            模拟 `keyring` 模块中的 `delete_password` 函数。

            Raises:
                keyring.errors.PasswordDeleteError: 模拟没有已保存的 Token。
            """

            del service_name, username
            raise keyring.errors.PasswordDeleteError

        monkeypatch.setattr(token.keyring, "delete_password", _fake_delete_password)

        assert token.remove_token() == 0
        assert "没有找到已设置的 Token" in capsys.readouterr().out

    @pytest.mark.xfail
    def test_remove_token_reports_keyring_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `remove_token` 函数应在密钥环操作失败时输出错误并返回失败。
        """

        def _fake_delete_password(service_name: str, username: str) -> None:
            """
            模拟 `keyring` 模块中的 `delete_password` 函数。

            Raises:
                keyring.errors.KeyringError: 测试异常。
            """

            del service_name, username
            raise keyring.errors.KeyringError("测试异常")

        monkeypatch.setattr(token.keyring, "delete_password", _fake_delete_password)

        assert token.remove_token() == 1
        assert "移除 Token 时发生异常：(keyring.errors.KeyringError) 测试异常" in capsys.readouterr().out


class TestSetToken:
    """
    对 `tools.maintain.token` 模块中的 `set_token` 函数的测试。
    """

    @pytest.mark.parametrize("secret", ("ghp_test-token", "github_pat_test-token"))
    def test_set_token_saves_supported_token(self, secret: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `set_token` 函数应接受支持的 Token 前缀并保存 Token。
        """

        monkeypatch.setattr(token, "getpass", lambda prompt: secret)
        fake_set_password = Mock()
        monkeypatch.setattr(token.keyring, "set_password", fake_set_password)

        assert token.set_token() == 0
        fake_set_password.assert_called_once_with(service_name="DuckStudio.Sundry-GitHubToken", username="GitHubToken", password=secret)
        assert "成功设置 Token" in capsys.readouterr().out

    def test_set_token_rejects_unsupported_token(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `set_token` 函数应拒绝不符合支持前缀的 Token，且不写入密钥环。
        """

        monkeypatch.setattr(token, "getpass", lambda prompt: "invalid-token")
        fake_set_password = Mock()
        monkeypatch.setattr(token.keyring, "set_password", fake_set_password)

        assert token.set_token() == 1
        fake_set_password.assert_not_called()
        assert "格式不正确" in capsys.readouterr().out

    @pytest.mark.xfail
    def test_set_token_reports_keyring_error(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `set_token` 函数应在密钥环操作失败时输出错误并返回失败。
        """

        monkeypatch.setattr(token, "getpass", lambda prompt: "ghp_test-token")

        def _fake_set_password(service_name: str, username: str, password: str) -> NoReturn:
            """
            模拟 `keyring` 模块中的 `set_password` 函数。

            Raises:
                keyring.errors.KeyringError: 测试异常。
            """

            del service_name, username, password
            raise keyring.errors.KeyringError("测试异常")

        monkeypatch.setattr(token.keyring, "set_password", _fake_set_password)

        assert token.set_token() == 1
        assert "设置 Token 时发生异常：(keyring.errors.KeyringError) 测试异常" in capsys.readouterr().out


class TestReadTokenFrom:
    """
    对 `tools.maintain.token` 模块中的 `read_token_from` 函数的测试。
    """

    def test_read_token_from_rejects_unknown_source(self) -> None:
        """
        `read_token_from` 函数应对未知来源抛出 `ValueError`。
        """

        with pytest.raises(ValueError, match="未知的 GitHub Token 读取源"):
            token.read_token_from("unknown")


class TestReadToken:
    """
    对 `tools.maintain.token` 模块中的 `read_token` 函数的测试。
    """

    @pytest.mark.parametrize("silent", (False, True))
    def test_read_token_honors_do_not_use_config(self, silent: bool, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `read_token` 函数应遵循不使用 Token 的配置及静默选项。
        """

        monkeypatch.setattr(token, "读取配置", lambda item: token.DO_NOT_USE)
        should_print = not silent

        assert token.read_token(silent=silent) is None
        output = capsys.readouterr().out
        assert bool(output) == should_print

    @pytest.mark.parametrize(
        ("source", "expected_message"),
        (
            (None, "未能从配置文件中获取 GitHub Token 读取源"),
            ("env", "环境变量 GITHUB_TOKEN"),
            ("keyring", "未能从 keyring 读取 GitHub Token"),
        ),
    )
    def test_read_token_reports_invalid_config_or_missing_token(self, source: str | None, expected_message: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `read_token` 函数应在配置来源无效或来源中没有 Token 时返回空值并报告错误。
        """

        monkeypatch.setattr(token, "读取配置", lambda item: source)
        monkeypatch.setattr(token, "read_token_from", lambda configured_source: None)

        assert token.read_token() is None
        assert expected_message in capsys.readouterr().out

    @pytest.mark.parametrize("silent", (False, True))
    def test_read_token_handles_source_errors(self, silent: bool, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `read_token` 函数应捕获来源读取错误，并遵循静默选项。
        """

        def _fake_read_token_from(source: str) -> None:
            """
            模拟 `tools.maintain.token` 模块中的 `read_token_from` 函数，抛出未知来源错误。
            """

            del source
            raise ValueError("test error")

        monkeypatch.setattr(token, "读取配置", lambda item: "unknown")
        monkeypatch.setattr(token, "read_token_from", _fake_read_token_from)

        assert token.read_token(silent=silent) is None
        output = capsys.readouterr().out
        assert ("读取 GitHub Token 失败" in output) is not silent
