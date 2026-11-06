import json
from pathlib import Path
from typing import Literal

import pytest

from tools.maintain import config
from tools.maintain.config import 修改配置项


class Test修改配置项:
    @pytest.mark.parametrize("config_item", ("xxx", "xxx.yyy"))
    def test_修改配置项_no_specified_configuration_items(
        self,
        config_item: Literal["xxx", "xxx.yyy"],
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `修改配置项` 函数应在配置文件中没有指定的配置项时输出错误信息。
        """

        config_path: Path = tmp_path / "config.json"
        monkeypatch.setattr(config.配置信息, "所在位置", str(config_path))
        config_path.write_text(
            json.dumps({"item": "value"}),
            encoding="utf-8",
        )

        monkeypatch.setattr(config, "转换配置值", lambda item, value: value)

        assert 修改配置项(config_item, "zzz") == 1
        assert "当前配置文件中没有键" in capsys.readouterr().out
