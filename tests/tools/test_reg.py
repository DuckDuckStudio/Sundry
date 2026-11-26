"""
测试 `tools.reg` 模块。
"""

import sys

import pytest

if sys.platform != "win32":
    pytest.skip("只有 Windows 有 winreg 库", allow_module_level=True)

# pylint: disable=wrong-import-position / C0413, wrong-import-order / C0411

from typing import Any, Final

import function.constant.registry
import tools.reg
from function.constant.registry import REGISTRY_ENTRY
from tools.reg import _matches_registry_entry, find_installer_registry_entries, main  # pyright: ignore[reportPrivateUsage]

_fake_entry: Final = REGISTRY_ENTRY(
    RegistryPath="HKEY_LOCAL_MACHINE\\SOFTWARE\\Example\\Product",
    ProductCode="Example.Product",
    Scope="machine",
    DisplayName="Sample App",
    DisplayVersion="1.2.3",
    Publisher="Example Publisher",
    InstallLocation="C:\\Program Files\\Example",
)


def _fake_read_installer_registry_entries() -> list[REGISTRY_ENTRY]:
    """
    模拟 `function.registry` 模块中的 `read_installer_registry_entries` 函数，返回测试条目。
    """

    return [_fake_entry]


class TestMain:
    """
    对 `tools.reg` 模块中的 `main` 函数的测试。
    """

    def test_main_should_print_yaml_for_matching_entries(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `main` 函数应输出匹配条目的注册表路径和 YAML。
        """

        def _fake_highlight(code: str, *args: Any) -> str:
            """
            模拟 `pygments` 的 `highlight` 函数，原样返回代码文本。
            """

            del args
            return code

        monkeypatch.setattr(tools.reg, "read_installer_registry_entries", _fake_read_installer_registry_entries)
        monkeypatch.setattr(function.constant.registry, "highlight", _fake_highlight)

        assert main(["sample", "app"]) == 0

        output = capsys.readouterr().out
        assert "HKEY_LOCAL_MACHINE\\SOFTWARE\\Example\\Product" in output
        assert "DisplayName: Sample App" in output
        assert "ProductCode: Example.Product" in output

    def test_main_should_report_when_no_entries_match(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `main` 函数应在没有匹配条目时输出提示。
        """

        monkeypatch.setattr(tools.reg, "read_installer_registry_entries", _fake_read_installer_registry_entries)

        assert main(["mismatch"]) == 0

        assert "没有找到匹配的注册表条目" in capsys.readouterr().out

    def test_main_should_output_an_error_message_and_exit_with_the_exit_code_1_when_no_arguments_are_passed(self, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `main` 函数应在没有传递参数时输出错误信息并以退出代码 `1` 退出。
        """

        assert main([]) == 1

        assert "请提供注册表条目搜索关键词" in capsys.readouterr().out


class TestMatchesRegistryEntry:
    """
    对 `tools.reg` 模块中的 `_matches_registry_entry` 函数的测试。
    """

    @pytest.mark.parametrize(
        "keyword",
        ["AMPLE APP", "Example.Product", "1.2.3", "Example Publisher"],
    )
    def test_matches_registry_entry_should_match_apps_and_features_fields(self, keyword: str) -> None:
        """
        `_matches_registry_entry` 函数应匹配 `AppsAndFeaturesEntries` 中的关键词。
        """

        assert _matches_registry_entry(_fake_entry, keyword)

    @pytest.mark.parametrize(
        "keyword",
        ["Software\\Example", "machine", "Program Files"],
    )
    def test_matches_registry_entry_should_ignore_other_fields(self, keyword: str) -> None:
        """
        `_matches_registry_entry` 函数应忽略 `AppsAndFeaturesEntries` 以外的字段。
        """

        assert not _matches_registry_entry(_fake_entry, keyword)

    def test_matches_registry_entry_should_return_false_when_there_is_no_match(self) -> None:
        """
        `_matches_registry_entry` 函数应在不匹配时返回 `False`。
        """

        assert not _matches_registry_entry(_fake_entry, "mismatch")


class TestFindInstallerRegistryEntries:
    """
    对 `tools.reg` 模块中的 `find_installer_registry_entries` 函数的测试。
    """

    def test_find_installer_registry_entries_should_return_matching_entries(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `find_installer_registry_entries` 函数应返回匹配的注册表条目列表。
        """

        monkeypatch.setattr(tools.reg, "read_installer_registry_entries", _fake_read_installer_registry_entries)

        assert find_installer_registry_entries("SAMPLE") == [_fake_entry]

    def test_find_installer_registry_entries_should_return_empty_list_when_no_entries_match(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `find_installer_registry_entries` 函数应在没有匹配条目时返回空列表。
        """

        monkeypatch.setattr(tools.reg, "read_installer_registry_entries", _fake_read_installer_registry_entries)

        assert find_installer_registry_entries("mismatch") == []
