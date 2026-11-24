# pyright: reportUnknownLambdaType=false, reportUnknownArgumentType=false

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal
from unittest.mock import Mock

import pytest
from catfood.exceptions.operation import OperationFailed

from tools.maintain import config
from tools.maintain.config import (
    修改配置项,
    初始化配置文件,
    展示配置文件,
    更新配置文件,
    获取用户输入,
)


class Test获取用户输入:
    """
    对 `tools.maintain.config` 模块中的 `获取用户输入` 函数的测试。
    """

    def test_获取用户输入_retries_after_invalid_value(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `获取用户输入` 函数应重新询问无法转换配置值的无效值。
        """

        answers: Iterator[str] = iter(["maybe", " yes "])
        prompts: list[str] = []
        monkeypatch.setattr(
            "builtins.input", lambda prompt: prompts.append(prompt) or next(answers)
        )

        def _fake_转换配置值(item: str, value: str) -> Literal[True]:
            """
            模拟 `function.maintain.config` 中的 `转换配置值` 函数。

            除了配置值为 `yes` 时，都抛出 :class:`OperationFailed` 异常。

            Raises:
                OperationFailed: 传入非 `yes` 的无效配置值时。

            Returns:
                True: 传入 `yes` 时。
            """

            del item
            if value != "yes":
                raise OperationFailed(f"无效的配置值 {value}")
            return True

        monkeypatch.setattr(config, "转换配置值", _fake_转换配置值)

        assert 获取用户输入("git.signature") is True
        assert len(prompts) == 2  # 调用了两次 input()
        assert "无法转换配置值" in capsys.readouterr().out

    def test_获取用户输入_retries_after_setting_keyring_token_failed(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        `获取用户输入` 函数应在设置 keyring 失败后重新询问。
        """

        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)

        answers: Iterator[str] = iter(["keyring", "env"])

        def _fake_input_func(prompt: str) -> str:
            assert "我该从哪里读取 GitHub Token" in prompt
            return next(answers)

        _fake_input = Mock(side_effect=_fake_input_func)
        _fake_read_token_from = Mock(return_value=None)
        _fake_set_token = Mock(return_value=1)
        monkeypatch.setattr("builtins.input", _fake_input)
        monkeypatch.setattr(
            config.tools.maintain.token, "read_token_from", _fake_read_token_from
        )
        monkeypatch.setattr(config.tools.maintain.token, "set_token", _fake_set_token)

        assert config.获取用户输入("github.token") == "env"
        assert _fake_input.call_count == 2
        _fake_read_token_from.assert_called_once_with(source="keyring")
        _fake_set_token.assert_called_once_with()  # 第二次输入 env，不需要设置


class Test初始化配置文件:
    """
    对 `tools.maintain.config` 模块中的 `初始化配置文件` 函数的测试。
    """

    def test_初始化配置文件_writes_defaults_and_required_values(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `初始化配置文件` 函数应写入必须值和默认值。
        """

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        default_configuration_snapshot = (
            config.配置信息.get_a_copy_of_the_default_config()
        )

        def _fake_input(prompt: str) -> Literal["n"]:
            """
            模拟 `input` 函数。

            因为我们需要测试他是否会写入默认值，所以我们不继续设置其他配置项。

            Returns:
                Literal["n"]: 不继续设置其他配置项。
            """

            assert "继续设置其他配置项" in prompt
            return "n"

        monkeypatch.setattr("builtins.input", _fake_input)
        asked: list[str] = []

        def _fake_获取用户输入(key: str) -> str:
            asked.append(key)
            return "/pkgs" if key == "paths.winget-pkgs" else "owner/winget-pkgs"

        monkeypatch.setattr(config, "获取用户输入", _fake_获取用户输入)

        assert 初始化配置文件() == 0
        written = json.loads(config_path.read_text(encoding="utf-8"))
        assert written["paths"]["winget-pkgs"] == "/pkgs"
        assert written["repos"]["winget-pkgs"] == "owner/winget-pkgs"
        assert written["github"]["token"] == "keyring"  # 默认值
        assert asked == ["paths.winget-pkgs", "repos.winget-pkgs"]
        assert (
            config.配置信息.默认配置 == default_configuration_snapshot
        )  # 没有改变配置信息类中的默认配置

    def test_初始化配置文件_does_not_ask_for_unimplemented_items(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `初始化配置文件` 函数应跳过未实现的配置项，不询问用户。
        """

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        def _fake_input(prompt: str) -> Literal["y", "n"]:
            """
            模拟 `input` 函数。

            Returns:
                input_str: 是否覆盖现有配置文件。
            """

            if "继续设置其他配置项" in prompt:
                return "y"
            elif any(x in prompt for x in ("是否修改缓存配置", "sundry ignore")):
                return "n"
            else:
                pytest.fail(f'没有为 input(prompt="{prompt}") 预设回答。')

        monkeypatch.setattr("builtins.input", _fake_input)

        asked: list[str] = []
        unimplemented_items = set(config.配置信息.未实现项)

        def _fake_获取用户输入(item: str) -> Literal["fake_config_value"]:
            """
            记录初始化配置时询问了的配置项。

            Returns:
                str: 固定的占位配置值。
            """

            asked.append(item)
            return "fake_config_value"

        monkeypatch.setattr(config, "获取用户输入", _fake_获取用户输入)

        assert 初始化配置文件() == 0
        assert unimplemented_items.isdisjoint(asked)

    @pytest.mark.parametrize("input_str", ("y", "n"))
    def test_初始化配置文件_overwrite(
        self,
        input_str: Literal["y", "n"],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `初始化配置文件` 函数应能依照用户指示覆盖现有配置文件。
        """

        config_path: Path = tmp_path / "config.json"
        config_path.write_text('{"existing": true}', encoding="utf-8")
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        def _fake_input(prompt: str) -> Literal["y", "n"]:
            """
            模拟 `input` 函数。

            Returns:
                input_str: 是否覆盖现有配置文件。
            """

            del prompt

            return input_str

        monkeypatch.setattr("builtins.input", _fake_input)

        def _fake_获取用户输入(item: str) -> Literal["fake_config_value"]:
            """
            模拟 `tools.maintain.config` 模块中的 `获取用户输入` 函数。

            Returns:
                Literal["fake_config_value"]: 固定的占位配置值
            """

            del item

            assert (
                input_str != "n"
            ), "用户表示不覆盖现有配置文件时，不应调用 `获取用户输入` 函数，询问用户配置项的设置值。"
            return "fake_config_value"

        monkeypatch.setattr(config, "获取用户输入", _fake_获取用户输入)

        result = config.初始化配置文件()
        final_config = json.loads(config_path.read_text(encoding="utf-8"))
        if input_str == "n":
            assert result == 1
            assert final_config == {"existing": True}
        else:
            assert result == 0
            assert final_config != {"existing": True}

    def test_初始化配置文件_no_winget_tools(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `初始化配置文件` 函数应能不设置 winget-tools 相关配置。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))

        def _fake_获取用户输入(item: str) -> Literal["fake_config_value"]:
            """
            模拟 `tools.maintain.config` 模块中的 `获取用户输入` 函数。

            Returns:
                Literal["fake_config_value"]: 固定的占位配置值
            """

            assert "winget-tools" not in item
            return "fake_config_value"

        monkeypatch.setattr(config, "获取用户输入", _fake_获取用户输入)

        def _fake_input(prompt: str) -> Literal["y", "n"]:
            """
            模拟 `input` 函数。

            Returns:
                input_str: 是否覆盖现有配置文件。
            """

            from colorama import Fore

            if (
                f"是否使用 ({Fore.YELLOW}将在未来弃用的{Fore.RESET}) sundry ignore?"
                in prompt
            ):
                return "n"

            return "y"

        monkeypatch.setattr("builtins.input", _fake_input)

        assert 初始化配置文件() == 0
        final_config = json.loads(config_path.read_text(encoding="utf-8"))
        assert final_config["paths"]["winget-tools"] is None
        assert final_config["repos"]["winget-tools"] is None


class Test展示配置文件:
    """
    对 `tools.maintain.config` 模块中的 `展示配置文件` 函数的测试。
    """

    def test_展示配置文件_successful(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `展示配置文件` 函数应正常输出有效的当前配置。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(
            json.dumps({"fake_item": "fake_value"}), encoding="utf-8"
        )

        assert 展示配置文件() == 0
        output: str = capsys.readouterr().out
        assert "fake_item" in output
        assert "fake_value" in output

    def test_展示配置文件_missing_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `展示配置文件` 函数应对没有配置文件的情况输出错误提示。
        """

        monkeypatch.setattr(config.配置信息, "所在位置", str(tmp_path / "missing.json"))

        assert 展示配置文件() == 1
        output = capsys.readouterr().out
        assert "配置文件不存在" in output
        assert "运行 sundry config init 来初始化配置文件" in output

    def test_展示配置文件_invalid(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `展示配置文件` 函数应对无效的配置文件内容输出错误提示。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text("not a json", encoding="utf-8")

        assert 展示配置文件() == 1
        output = capsys.readouterr().out
        assert "读取配置文件失败，配置文件不是有效的 json 字段" in output
        assert "运行 sundry config init 来覆盖现有的配置文件" in output


class Test修改配置项:
    """
    对 `tools.maintain.config` 模块中的 `修改配置项` 函数的测试。
    """

    def test_修改配置项_successful(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `修改配置项` 函数应正确修改已知配置项的值。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(
            json.dumps(
                {
                    "debug": False,
                    "git": {"signature": False, "retry_interval": 50},
                }
            ),
            encoding="utf-8",
        )

        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)

        assert 修改配置项("debug", "modified1") == 0
        assert json.loads(config_path.read_text(encoding="utf-8")) == {
            "debug": "modified1",
            "git": {"signature": False, "retry_interval": 50},
        }

        assert 修改配置项("git.signature", "modified2") == 0
        assert json.loads(config_path.read_text(encoding="utf-8")) == {
            "debug": "modified1",
            "git": {"signature": "modified2", "retry_interval": 50},
        }

    def test_修改配置项_output_a_warning_when_modifying_unexpected_configurations(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `修改配置项` 函数应在修改意外的配置项时显示警告。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(
            json.dumps(
                {
                    "$schema": "https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/1.4.json",
                    "version": "1.4",
                    "debug": False,
                }
            ),
            encoding="utf-8",
        )

        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)

        assert 修改配置项("$schema", "X X XXX") == 0
        assert json.loads(config_path.read_text(encoding="utf-8")) == {
            "$schema": "X X XXX",
            "version": "1.4",
            "debug": False,
        }
        assert "理论上你不应该修改配置项 $schema 的值" in capsys.readouterr().out

        assert 修改配置项("version", "x x xxx") == 0
        assert json.loads(config_path.read_text(encoding="utf-8")) == {
            "$schema": "X X XXX",
            "version": "x x xxx",
            "debug": False,
        }
        assert "理论上你不应该修改配置项 version 的值" in capsys.readouterr().out

    def test_修改配置项_invalid(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `修改配置项` 函数应对无效的配置文件内容输出错误提示。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text("not a json", encoding="utf-8")

        assert 修改配置项("无关", "无关") == 1
        output = capsys.readouterr().out
        assert "读取配置文件失败，配置文件不是有效的 json 字段" in output
        assert "运行 sundry config init 来覆盖现有的配置文件" in output
        assert config_path.read_text(encoding="utf-8") == "not a json"

    @pytest.mark.parametrize(
        "item",
        (
            # 不存在于配置文件
            "xxx",
            "yyy.zzz",
            # 存在于配置文件
            "aaa",
            "bbb.ccc",
        ),
    )
    def test_修改配置项_reject_unknown_config_item(
        self,
        item: str,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `修改配置项` 函数应拒绝修改未知配置项。
        """

        config_file = tmp_path / "config.json"
        original_config = {"aaa": "value", "bbb": {"ccc": "value2"}}
        config_file.write_text(json.dumps(original_config), encoding="utf-8")
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_file))
        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)

        assert 修改配置项(item, "无关") == 1
        assert "未知的配置项" in capsys.readouterr().out
        assert json.loads(config_file.read_text(encoding="utf-8")) == original_config

    def test_修改配置项_add_missing_known_config_item(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `修改配置项` 函数应添加配置文件中缺失的已知配置项。
        """

        配置文件 = tmp_path / "config.json"
        配置文件.write_text("{}", encoding="utf-8")
        monkeypatch.setattr(config.配置信息, "所在位置", str(配置文件))

        assert 修改配置项("git.signature", "y") == 0
        assert json.loads(配置文件.read_text(encoding="utf-8")) == {
            "git": {"signature": True}
        }

    def test_修改配置项_not_a_config_item(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `修改配置项` 函数应在找到已知的和需要修改的配置项同名的键，但该键不是配置项时，输出错误信息。

        仅判断是否在 `配置信息.默认配置` 中，而不是判断是否在配置文件中。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(
            json.dumps({"git": "无关"}),
            encoding="utf-8",
        )

        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)

        assert 修改配置项("git", "无关") == 1
        assert "是一个分类，而不是一个配置项。" in capsys.readouterr().out
        assert json.loads(config_path.read_text(encoding="utf-8")) == {"git": "无关"}

    def test_修改配置项_missing_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `修改配置项` 函数应对没有配置文件的情况输出错误提示。
        """

        monkeypatch.setattr(config.配置信息, "所在位置", str(tmp_path / "missing.json"))

        assert 修改配置项("无关", "无关") == 1
        output = capsys.readouterr().out
        assert "配置文件不存在" in output
        assert "运行 sundry config init 来初始化配置文件" in output


class Test更新配置文件:
    """
    对 `tools.maintain.config` 模块中的 `更新配置文件` 函数的测试。
    """

    def test_更新配置文件_reports_missing_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `更新配置文件` 函数应对配置文件不存在的情况输出错误提示。
        """

        monkeypatch.setattr(config.配置信息, "所在位置", str(tmp_path / "missing.json"))

        assert config.更新配置文件() == 1
        output = capsys.readouterr().out
        assert "配置文件不存在" in output
        assert "运行 sundry config init 来初始化配置文件" in output

    def test_更新配置文件_alreday_updated(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `更新配置文件` 函数应在配置文件已经是最新版本时，输出提示信息。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(
            json.dumps(
                {
                    "$schema": f"https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/{config.配置信息.最新版本}.json",
                    "version": config.配置信息.最新版本,
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(config, "获取配置schema", lambda version: None)

        assert 更新配置文件() == 0
        assert "看起来当前的配置文件已经是最新的了" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "migration_case",
        [
            pytest.param(
                (
                    "1.1",
                    {
                        "version": "1.1",
                        "paths": {
                            "winget-pkgs": "old-pkgs",
                            "winget-tools": "old-tools",
                        },
                        "repos": {
                            "winget-pkgs": "owner/pkgs",
                            "winget-tools": "owner/tools",
                        },
                        "git": {"signature": True},
                        "github": {"pr": {"maintainer_can_modify": True}},
                        "tools": {"verify": {"check_url": True}},
                    },
                    "keyring",
                    False,
                    True,
                ),
                id="1.1",
            ),
            pytest.param(
                (
                    "1.2",
                    {
                        "version": "1.2",
                        "debug": True,
                        "paths": {
                            "winget-pkgs": "old-pkgs",
                            "winget-tools": "old-tools",
                        },
                        "repos": {
                            "winget-pkgs": "owner/pkgs",
                            "winget-tools": "owner/tools",
                        },
                        "git": {"signature": True},
                        "github": {
                            "pr": {
                                "maintainer_can_modify": True,
                                "mention_self_when_reviewer": True,
                            }
                        },
                        "cache": {"validate": {"schema": False}},
                    },
                    "keyring",
                    False,
                    False,
                ),
                id="1.2",
            ),
            pytest.param(
                (
                    "1.3",
                    {
                        "version": "1.3",
                        "debug": True,
                        "paths": {
                            "winget-pkgs": "old-pkgs",
                            "winget-tools": "old-tools",
                        },
                        "repos": {
                            "winget-pkgs": "owner/pkgs",
                            "winget-tools": "owner/tools",
                        },
                        "git": {"signature": True},
                        "github": {
                            "pr": {
                                "maintainer_can_modify": True,
                                "mention_self_when_reviewer": True,
                            },
                            "token": "glm",
                        },
                        "tools": {"autoremove": {"open_in_browser": True}},
                        "cache": {"validate": {"schema": False}},
                    },
                    "glm",
                    True,
                    False,
                ),
                id="1.3",
            ),
        ],
    )
    def test_更新配置文件_migrates_supported_historical_versions(
        self,
        migration_case: tuple[str, dict[str, Any], str, bool, bool],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `更新配置文件` 函数应迁移受支持的历史版本，保留已有值并补齐新默认值。
        """

        version, old_config, expected_token, expected_browser, expected_cache = (
            migration_case
        )
        config_path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(json.dumps(old_config), encoding="utf-8")
        monkeypatch.setattr(
            config,
            "获取配置schema",
            lambda schema_version: {
                "type": "object",
                "properties": {"version": {"const": schema_version}},
            },
        )

        assert 更新配置文件() == 0

        migrated_config = json.loads(config_path.read_text(encoding="utf-8"))

        expected_config = config.配置信息.get_a_copy_of_the_default_config()
        expected_config["debug"] = version != "1.1"
        expected_config["paths"]["winget-pkgs"] = "old-pkgs"
        expected_config["paths"]["winget-tools"] = "old-tools"
        expected_config["repos"]["winget-pkgs"] = "owner/pkgs"
        expected_config["repos"]["winget-tools"] = "owner/tools"
        expected_config["git"]["signature"] = True
        expected_config["github"]["pr"]["maintainer_can_modify"] = True
        expected_config["github"]["pr"]["mention_self_when_reviewer"] = version != "1.1"
        expected_config["github"]["token"] = expected_token
        expected_config["tools"]["autoremove"]["open_in_browser"] = expected_browser
        expected_config["cache"]["validate"]["schema"] = expected_cache

        assert migrated_config == expected_config

    def test_更新配置文件_does_not_mutate_default_config(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `更新配置文件` 函数应保留类级默认配置不变。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(json.dumps({"version": "1.3"}), encoding="utf-8")
        monkeypatch.setattr(config, "获取配置schema", lambda version: None)
        monkeypatch.setattr(config, "获取用户输入", lambda item: "fake_config_value")
        default_configuration_snapshot = (
            config.配置信息.get_a_copy_of_the_default_config()
        )

        assert 更新配置文件() == 0
        assert config.配置信息.默认配置 == default_configuration_snapshot
