import json
from pathlib import Path

import pytest

from tools.maintain import config
from tools.maintain.config import 修改配置项


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
