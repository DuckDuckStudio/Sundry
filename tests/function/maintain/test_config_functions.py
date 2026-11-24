# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

import json
import os.path
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import catfood.functions.github.api
import pytest
import requests
from catfood.exceptions.operation import OperationFailed
from colorama import Fore

import tools.maintain.token
from function.maintain import config
from function.maintain.config import (
    获取配置schema,
    读取配置,
    读取配置项,
    转换配置值,
    验证配置,
)


@dataclass
class FakeResponse:
    """假的 requests.Response"""

    status_code: int


class Test配置信息:
    """
    对 `function.maintain.config` 模块中的 `配置信息` 类的测试。
    """

    def test_默认配置_should_be_immutable_at_every_level(self) -> None:
        """
        `配置信息.默认配置` 应在所有嵌套层级不可修改。
        """

        with pytest.raises(TypeError):
            config.配置信息.默认配置["debug"] = True  # pyright: ignore[reportIndexIssue]  # ty: ignore[invalid-assignment]

        with pytest.raises(TypeError):
            config.配置信息.默认配置["github"]["pr"]["maintainer_can_modify"] = True

    def test_get_a_copy_of_the_default_config_should_be_independently_mutable(
        self,
    ) -> None:
        """
        `get_a_copy_of_the_default_config` 函数应返回与默认配置相互独立的可变副本。
        """

        default_config_copy = config.配置信息.get_a_copy_of_the_default_config()
        default_config_copy["github"]["pr"]["maintainer_can_modify"] = True
        assert (
            config.配置信息.默认配置["github"]["pr"]["maintainer_can_modify"] is False
        )


class Test验证配置:
    """
    对 `function.maintain.config` 模块中的 `验证配置` 函数的测试。
    """

    @pytest.mark.parametrize(
        ("config_item", "config_value"),
        (
            ("paths.test", "/this/is/a/path/"),
            ("repos.test", "owner/repo"),
            ("debug", True),
            ("i18n.lang", "zh-cn"),
            ("github.token", "keyring"),
            ("git.retry_interval", 30),
            ("version", "1.4"),
            ("unknown.config.item", None),
        ),
    )
    def test_验证配置_accepts_valid_values(
        self,
        config_item: str,
        config_value: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        验证配置函数应接受有效的配置项和配置值组合。
        """

        def _fake_head(url: str, timeout: int) -> FakeResponse:
            """
            模拟 `requests.head()` 函数，返回状态码为 `200` 的假响应。
            """

            del url, timeout
            return FakeResponse(status_code=200)

        monkeypatch.setattr(os.path, "exists", lambda _: True)
        monkeypatch.setattr(requests, "head", _fake_head)

        assert 验证配置(config_item, config_value) is None

    @pytest.mark.parametrize(
        ("config_item", "config_value", "error_message"),
        (
            ("", "", "未指定配置项"),
            ("", "value", "未指定配置项"),
            ("item", "", "未指定配置值"),
            (
                "paths.test",
                "/not/exists/",
                f"目录 {Fore.BLUE}/not/exists/{Fore.RESET} 不存在",
            ),
            # ("repos.test", "owner/repo", "xxx"), - 多个状态码分支，另外测试
            (
                "debug",
                "not-a-bool-value",
                f"应是布尔值，但实际是 {Fore.BLUE}<class 'str'>{Fore.RESET}",
            ),
            (
                "i18n.lang",
                "unsupported-language",
                f"不支持的语言 {Fore.BLUE}unsupported-language{Fore.RESET}",
            ),
            ("github.token", "unknown-source", "未知的 Token 读取源"),
            (
                "git.retry_interval",
                "not-an-int-value",
                f"应是整数，但实际是 {Fore.BLUE}<class 'str'>{Fore.RESET}",
            ),
            (
                "version",
                1.4,
                f"应是字符串，但实际是 {Fore.BLUE}<class 'float'>{Fore.RESET}",
            ),
            (
                "version",
                "1.2.3",
                "格式不正确，应是 x.y 的格式（其中 x、y 为一位非负整数）",
            ),
            ("version", "0.9", "弃用的配置文件版本"),
            ("version", "1.0", "弃用的配置文件版本"),
        ),
    )
    def test_验证配置_return_error_message_for_invalid_values(
        self,
        config_item: str,
        config_value: Any,
        error_message: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        验证配置函数应对无效的配置项和配置值组合返回错误消息。
        """

        def _fake_head(url: str, timeout: int) -> NoReturn:
            """
            模拟 `requests.head()` 函数，但没有实现。

            因为该测试没有测试仓库配置，所以函数不应该发起请求。

            Raises:
                NotImplementedError: 此函数没有实现。
            """

            raise NotImplementedError(
                f"该测试没有测试仓库配置，函数不应该发起请求，但函数调用了 requests.head(url={url}, timeout={timeout})。"
            )

        monkeypatch.setattr(os.path, "exists", lambda _: False)
        monkeypatch.setattr(requests, "head", _fake_head)
        monkeypatch.setattr(os.path, "normpath", lambda x: x)

        assert 验证配置(config_item, config_value) == error_message

    @pytest.mark.parametrize(
        ("status_code", "error_message"),
        (
            # (200, None), - 和有效值的测试重复
            (
                404,
                f"仓库 {Fore.BLUE}owner/repo{Fore.RESET} 不存在或没有权限访问",
            ),
            (888, f"无法验证仓库，GitHub API 响应 {Fore.BLUE}888{Fore.RESET}"),
        ),
    )
    def test_验证配置_checks_repo_status(
        self,
        status_code: int,
        error_message: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        验证配置函数应依照 GitHub API 响应状态码返回不同的错误消息。
        """

        def _fake_head(url: str, timeout: int) -> FakeResponse:
            """
            模拟 `requests.head()` 函数，返回指定状态码的假响应。
            """

            del url, timeout
            return FakeResponse(status_code=status_code)

        monkeypatch.setattr(requests, "head", _fake_head)
        assert 验证配置("repos.winget-pkgs", "owner/repo") == error_message

    def test_验证配置_checks_repo_failed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        验证配置函数应在请求 GitHub API 出现异常时捕获并跳过检查。

        这在原先代码中注释为“避免网络问题导致的假性配置错误”，
        在后续可能有变化：https://github.com/DuckDuckStudio/Sundry/issues/456
        """

        def _fake_head(url: str, timeout: int) -> NoReturn:
            """
            模拟抛出异常的 `requests.head()` 函数。

            Raises:
                requests.RequestException: 抛出的异常。
            """

            raise requests.RequestException

        monkeypatch.setattr(requests, "head", _fake_head)

        assert 验证配置("repos.winget-pkgs", "owner/repo") is None


class Test转换配置值:
    """
    对 `function.maintain.config` 模块中的 `转换配置值` 函数的测试。
    """

    @pytest.mark.parametrize(
        ("config_item", "config_value", "expected"),
        [
            # 默认 True 的
            ("cache.validate.schema", "y", True),
            ("cache.validate.schema", "n", False),
            ("cache.validate.schema", "", True),
            # 默认 False 的
            ("debug", "y", True),
            ("debug", "n", False),
            ("debug", "", False),
            # git.retry_interval
            ("git.retry_interval", "", 50),
            ("git.retry_interval", "30", 30),
            # 统一为小写
            ("github.token", "KeYrInG", "keyring"),
            ("i18n.lang", "zH-Cn", "zh-cn"),
            ("github.token", "", "keyring"),
            ("i18n.lang", "", "zh-cn"),
            # 转换为 owner/repo 的格式
            ("repos.test", "https://github.com/owner/repo", "owner/repo"),
            ("repos.test", "https://github.com/owner/repo.git", "owner/repo"),
            ("repos.test", "owner", "owner/test"),
            # null
            ("github.token", "null", None),
            ("github.token", "None", None),
        ],
    )
    def test_转换配置值_convert_valid_value(
        self,
        config_item: str,
        config_value: str,
        expected: Any,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        转换配置值函数应正确转换有效输入。
        """

        monkeypatch.setattr(config, "验证配置", lambda item, value: None)

        assert 转换配置值(config_item, config_value) == expected

    @pytest.mark.parametrize(
        ("config_item", "config_value", "error_message"),
        (
            (
                "cache.validate.schema",
                "not-no-or-yes",
                f"{Fore.BLUE}not-no-or-yes{Fore.RED} 不能代表是或否，请使用 y / n",
            ),
            (
                "debug",
                "not-no-or-yes",
                f"{Fore.BLUE}not-no-or-yes{Fore.RED} 不能代表是或否，请使用 y / n",
            ),
            ("git.retry_interval", "NaN", "指定的配置值不是整数"),
            ("no-default-value", "", "指定的配置值为空，但该配置项没有默认值"),
        ),
    )
    def test_转换配置值_raises_for_invalid_input(
        self, config_item: str, config_value: str, error_message: str
    ) -> None:
        """
        转换配置值函数应对无效输入抛出 `OperationFailed` 异常，并附带对应错误消息。
        """

        with pytest.raises(OperationFailed) as ex:
            转换配置值(config_item, config_value)

        assert str(ex.value) == error_message

    def test_转换配置值_raises_for_value_that_failed_validation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        转换配置值函数应对验证失败的值抛出 `OperationFailed` 异常，并附带对应错误消息。
        """

        monkeypatch.setattr(config, "验证配置", lambda item, value: "X X XXX")

        with pytest.raises(OperationFailed) as ex:
            转换配置值("config_item", "config_value")

        assert str(ex.value) == "验证配置值失败: X X XXX"


class Test读取配置项:
    """
    对 `function.maintain.config` 模块中的 `读取配置项` 函数的测试。
    """

    def test_读取配置项_reads_nested_value(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        读取配置项函数应能读取嵌套字段值。
        """

        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps({"a": {"b": "x x xxx"}, "c": "hhh"}),
            encoding="utf-8",
        )
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        assert 读取配置项("a.b") == "x x xxx"
        assert 读取配置项("c") == "hhh"

    def test_读取配置项_handles_empty_value(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        读取配置项函数应原样读取空值，并对 null 值输出错误消息。
        """

        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps({"a": None, "b": "", "c": False, "d": 0}))
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        assert 读取配置项("a") is None
        assert "值为空" in capsys.readouterr().out

        assert 读取配置项("b") == ""
        assert 读取配置项("c") is False

        _result = 读取配置项("d")
        assert _result == 0
        assert type(_result) is int  # pylint: disable=unidiomatic-typecheck / C0123
        del _result
        assert not capsys.readouterr().out

    def test_读取配置项_handles_missing_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        读取配置项函数应对配置文件不存在的情况输出错误消息。
        """

        config_path = tmp_path / "x_x_xxx.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        assert 读取配置项("X X XXX") is None
        assert "配置文件不存在" in capsys.readouterr().out

    def test_读取配置项_handles_missing_key(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        读取配置项函数应对配置项不存在的情况输出错误消息。
        """

        config_path = tmp_path / "x_x_xxx.json"
        config_path.write_text(json.dumps({"x": "y"}), encoding="utf-8")
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        assert 读取配置项("X X XXX") is None
        assert "键 'X X XXX' 不存在" in capsys.readouterr().out


class Test读取配置:
    """
    对 `function.maintain.config` 模块中的 `读取配置` 函数的测试。
    """

    def test_读取配置_silently_read_config_item_debug(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """
        读取配置函数应静默读取配置项 `debug`。
        """

        # 验证配置值失败
        monkeypatch.setattr(config, "读取配置项", lambda itme, value: True)
        monkeypatch.setattr(config, "验证配置", lambda item, value: "错误消息")

        assert 读取配置("debug") is None
        assert not capsys.readouterr().out
        assert 读取配置("debug", False) is None
        assert not capsys.readouterr().out

        # 没有读取到配置值
        monkeypatch.setattr(config, "读取配置项", lambda itme, value: None)

        assert 读取配置("debug") is None
        assert not capsys.readouterr().out
        assert 读取配置("debug", False) is None
        assert not capsys.readouterr().out

        # try 中抛出 OperationFailed 异常
        def _raise_exc(item: str, value: str) -> NoReturn:
            """
            模拟抛出 `OperationFailed` 异常。

            Raises:
                OperationFailed: 抛出的异常。
            """

            raise OperationFailed("由测试触发的异常")

        monkeypatch.setattr(config, "读取配置项", _raise_exc)

        assert 读取配置("debug") is None
        assert not capsys.readouterr().out
        assert 读取配置("debug", False) is None
        assert not capsys.readouterr().out


class Test获取配置schema:
    """
    对 `function.maintain.config` 模块中的 `获取配置schema` 函数的测试。
    """

    def test_获取配置schema_returns_github_api_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        获取配置schema函数返回成功获取的 GitHub API 响应。
        """

        monkeypatch.setattr(tools.maintain.token, "read_token", lambda silent: None)
        monkeypatch.setattr(
            catfood.functions.github.api,
            "get_github_file_content",
            lambda repo, path, token: json.dumps({"x": "y"}),
        )

        def _fake_get(url: str, timeout: int) -> NoReturn:
            """
            模拟 `requests.get()` 函数，但没有实现。

            预期如果 `get_github_file_content` 函数有返回有效内容，则不再需要再调用此函数。

            Raises:
                NotImplementedError: 此函数没有实现。
            """

            raise NotImplementedError(
                f"预期如果 `get_github_file_content` 函数有返回有效内容，则不再需要再调用此函数。但函数调用了 requests.get(url={url}, timeout={timeout})。"
            )

        monkeypatch.setattr(requests, "get", _fake_get)

        assert 获取配置schema("1.1") == {"x": "y"}

    def test_获取配置schema_fallback_to_github_io(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        获取配置schema函数在通过 GitHub API 获取失败后回退到通过 github.io 获取。

        https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/{版本}.json
        """

        monkeypatch.setattr(tools.maintain.token, "read_token", lambda silent: None)
        monkeypatch.setattr(
            catfood.functions.github.api,
            "get_github_file_content",
            lambda repo, path, token: None,
        )

        class FakeResponse2(FakeResponse):
            "带有 `raise_for_status` 和 `json` 方法的 :class:`FakeResponse`。"

            def raise_for_status(self) -> None:
                pass

            def json(self) -> dict[str, str]:
                return {"x": "y"}

        def _fake_get(url: str, timeout: int) -> FakeResponse2:
            """
            模拟 `requests.get()` 函数，返回状态码为 `200` 的假响应。
            """

            del url, timeout
            return FakeResponse2(status_code=200)

        monkeypatch.setattr(requests, "get", _fake_get)

        assert 获取配置schema("1.1") == {"x": "y"}

    def test_获取配置schema_returns_none_when_both_sources_fail(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(tools.maintain.token, "read_token", lambda silent: None)
        monkeypatch.setattr(
            catfood.functions.github.api,
            "get_github_file_content",
            lambda repo, path, token: None,
        )

        class FakeResponse2(FakeResponse):
            "带有 `raise_for_status` 方法的 :class:`FakeResponse`。"

            def raise_for_status(self) -> None:
                raise requests.exceptions.HTTPError

        def _fake_get(url: str, timeout: int) -> FakeResponse2:
            """
            模拟返回请求失败响应的 `requests.get()` 函数。
            """

            del url, timeout
            return FakeResponse2(status_code=888)

        monkeypatch.setattr(requests, "get", _fake_get)

        assert config.获取配置schema("1.4") is None
