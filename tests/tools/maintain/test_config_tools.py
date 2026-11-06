import json
from copy import deepcopy
from pathlib import Path
from typing import Literal

import pytest

from tools.maintain import config
from tools.maintain.config import 初始化配置文件


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

    def test_初始化配置文件_skips_unimplemented_items(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `初始化配置文件` 函数应跳过未实现项并保留默认值。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        asked: list[str] = []

        def _fake_input(prompt: str) -> Literal["y", "n"]:
            if "继续设置其他配置项" in prompt:
                return "y"
            return "n"

        def _fake_获取用户输入(key: str) -> str:
            asked.append(key)
            return "fake_config_value"

        monkeypatch.setattr("builtins.input", _fake_input)
        monkeypatch.setattr(config, "获取用户输入", _fake_获取用户输入)

        assert 初始化配置文件() == 0

        written = json.loads(config_path.read_text(encoding="utf-8"))
        for item in config.配置信息.未实现项:
            assert item not in asked
        assert written["tools"]["prune"]["remote"]["prune_merged_branches"] is False
        assert written["tools"]["prune"]["remote"]["prune_closed_branches"] is False
        assert written["tools"]["verify"]["show_warning_on_non-clean_windows"] is False
        assert written["i18n"]["lang"] == "zh-cn"

    def test_初始化配置文件_skips_keys_that_do_not_require_user_input(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `初始化配置文件` 函数应跳过无需询问用户的顶级配置键。
        """

        config_path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        defaults = deepcopy(config.配置信息.默认配置)
        asked: list[str] = []

        def _fake_input(prompt: str) -> Literal["y", "n"]:
            if "继续设置其他配置项" in prompt:
                return "y"
            return "n"

        def _fake_获取用户输入(key: str) -> str:
            asked.append(key)
            return "fake_config_value"

        monkeypatch.setattr("builtins.input", _fake_input)
        monkeypatch.setattr(config, "获取用户输入", _fake_获取用户输入)

        assert 初始化配置文件() == 0

        written = json.loads(config_path.read_text(encoding="utf-8"))
        for key in ("$schema", "version", "debug"):
            assert key not in asked
            assert written[key] == defaults[key]
