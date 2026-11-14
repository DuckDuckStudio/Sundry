import json
from copy import deepcopy
from pathlib import Path
from typing import Literal

import pytest

from tools.maintain import config
from tools.maintain.config import 修改配置项, 初始化配置文件


class Test修改配置项:
    """
    对 `tools.maintain.config` 模块中的 `修改配置项` 函数的测试。
    """

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
        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)  # pyright: ignore[reportUnknownLambdaType, reportUnknownArgumentType]

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
        assert json.loads(配置文件.read_text(encoding="utf-8")) == {"git": {"signature": True}}

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

        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]

        assert 修改配置项("git", "无关") == 1
        assert "是一个分类，而不是一个配置项。" in capsys.readouterr().out
        assert json.loads(config_path.read_text(encoding="utf-8")) == {"git": "无关"}


class Test初始化配置文件:
    """
    对 `tools.maintain.config` 模块中的 `初始化配置文件` 函数的测试。
    """

    @pytest.fixture(autouse=True)
    def _isolate_默认配置(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `function.maintain.config` 中定义的 `配置信息` 中的 `默认配置` 是
        可变的 `dict`，前一个 `case` 修改后，下一个 `case` 会使用修改后的结果。

        所以，在测试前，需要先将该值 Mock 为一个 `deepcopy` 的值。
        """

        monkeypatch.setattr(
            config.配置信息,
            "默认配置",
            deepcopy(config.配置信息.默认配置),
        )

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
