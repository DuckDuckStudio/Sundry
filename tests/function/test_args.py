from pathlib import Path
from unittest.mock import Mock

import pytest

from function import args


class TestGetManifestDirFromArgs:
    """
    对 `function.args` 模块中的 `get_manifest_dir_from_args` 函数的测试。
    """

    def test_get_manifest_dir_from_args_returns_resolved_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `get_manifest_dir_from_args` 函数应优先返回存在的现有目录。
        """

        mock_issue_number = Mock()
        monkeypatch.setattr(args, "IssueNumber", mock_issue_number)

        assert args.get_manifest_dir_from_args([str(tmp_path)]) == tmp_path.resolve()
        mock_issue_number.assert_not_called()

    @pytest.mark.parametrize("debug", (True, False))
    def test_get_manifest_dir_from_args_returns_pr_manifest_directory(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], debug: bool) -> None:
        """
        `get_manifest_dir_from_args` 函数应在获取 PR 清单成功时返回 PR 清单目录。
        """

        monkeypatch.setattr(args, "IssueNumber", Mock(return_value="123"))
        mock_read_config = Mock(return_value=debug)
        monkeypatch.setattr(args, "读取配置", mock_read_config)
        mock_get_pr_manifest = Mock(return_value=0)
        monkeypatch.setattr(args, "获取PR清单", mock_get_pr_manifest)
        mock_read_token = Mock(return_value="token")
        monkeypatch.setattr(args, "read_token", mock_read_token)

        result = args.get_manifest_dir_from_args(["https://github.com/example/repo/pull/123"])

        assert result == Path(args.VERIFY_TEMP_DIR) / "PRManifest" / "123"
        mock_get_pr_manifest.assert_called_once_with("123", str(result), "token")
        mock_read_token.assert_called_once_with(silent=True)
        mock_read_config.assert_called_once_with("debug")
        if debug:
            assert "也许这是一个 GitHub PR 链接" in capsys.readouterr().out
        else:
            assert not capsys.readouterr().out

    def test_get_manifest_dir_from_args_returns_none_when_get_pr_manifest_fails(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `get_manifest_dir_from_args` 函数应在获取 PR 清单失败时返回 `None`。
        """

        monkeypatch.setattr(args, "IssueNumber", Mock(return_value="123"))
        monkeypatch.setattr(args, "获取PR清单", Mock(return_value=1))
        monkeypatch.setattr(args, "read_token", Mock(return_value="token"))

        assert args.get_manifest_dir_from_args(["123"]) is None

    def test_get_manifest_dir_from_args_returns_none_for_invalid_argument(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `get_manifest_dir_from_args` 函数应在指定的参数既不是目录也不是 PR 链接或编号时返回 `None`。
        """

        monkeypatch.setattr(args, "IssueNumber", Mock(return_value=None))

        assert args.get_manifest_dir_from_args(["invalid"]) is None
        assert "给定的参数既不是一个存在的文件夹路径，也不是一个 GitHub PR 链接或编号" in capsys.readouterr().out

    def test_get_manifest_dir_from_args_returns_manifest_directory_for_identifier_and_version(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `get_manifest_dir_from_args` 函数应根据包标识符和版本返回清单目录。
        """

        mock_get_manifest_dir = Mock(return_value=str(tmp_path))
        monkeypatch.setattr(args, "获取清单目录", mock_get_manifest_dir)

        assert args.get_manifest_dir_from_args(["Example.Package", "1.2.3"]) == tmp_path
        mock_get_manifest_dir.assert_called_once_with("Example.Package", "1.2.3")

    def test_get_manifest_dir_from_args_returns_none_when_get_manifest_directory_fails(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `get_manifest_dir_from_args` 函数应在获取清单目录失败时返回 `None`。
        """

        monkeypatch.setattr(args, "获取清单目录", Mock(return_value=None))

        assert args.get_manifest_dir_from_args(["Example.Package", "1.2.3"]) is None
        assert "未能获取到仓库中的清单目录" in capsys.readouterr().out

    @pytest.mark.parametrize(
        ("parameters", "message"),
        [
            ([], "请提供参数"),
            (["one", "two", "three"], "参数太多"),
        ],
        ids=["no-arguments", "too-many-arguments"],
    )
    def test_get_manifest_dir_from_args_returns_none_for_wrong_argument_count(
        self,
        parameters: list[str],
        message: str,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `get_manifest_dir_from_args` 函数应在参数数量不正确时返回 `None` 并输出错误信息。
        """

        assert args.get_manifest_dir_from_args(parameters) is None
        assert message in capsys.readouterr().out
