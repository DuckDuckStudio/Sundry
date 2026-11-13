# pyright: reportPrivateUsage=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false
# pylint: disable=protected-access / W0212

import csv
import json
from pathlib import Path

import pytest

from function.files import manifest


class TestFindReviewers:
    """
    对 `function.files.manifest` 模块中的 `find_reviewers` 函数的测试。
    """

    @pytest.fixture(name="winget_pkgs_repository")
    def _create_winget_pkgs_repository(self, tmp_path: Path) -> Path:
        """
        创建一个临时的 winget-pkgs 仓库结构。

        仓库结构：

        ```
        winget-pkgs/
            manifests/
                m/
                    Microsoft/
                        DotNet/
                            SDK/
                                Preview/
            Tools/
                ManualValidation/
                    ManualValidationPipeline.csv
        ```

        Returns:
            Path: 临时 winget-pkgs 仓库的根目录路径。
        """

        root: Path = tmp_path / "winget-pkgs"
        package_directory = root / "manifests" / "m" / "Microsoft" / "DotNet" / "SDK" / "Preview"
        package_directory.mkdir(parents=True)

        manual_validation_directory = root / "Tools" / "ManualValidation"
        manual_validation_directory.mkdir(parents=True)
        with (manual_validation_directory / "ManualValidationPipeline.csv").open("w", encoding="utf-8", newline="") as file:
            writer: csv.DictWriter[str] = csv.DictWriter(file, fieldnames=["PackageIdentifier", "gitHubUserName"])
            writer.writeheader()
            writer.writerow({"PackageIdentifier": "Microsoft.DotNet.*", "gitHubUserName": "csv-owner/csv-bot"})

        return root

    def _write_package_file(self, directory: Path, logins: list[str]) -> None:
        """
        在指定目录中创建一个 `.package` 文件，并写入给定的 GitHub 用户名列表。

        Args:
            directory: 要创建 `.package` 文件的目录。
            logins: 要写入 `.package` 文件的 GitHub 用户名列表。
        """

        directory.mkdir(parents=True, exist_ok=True)
        (directory / ".package").write_text(json.dumps({"schemaVersion": "0.1", "owners": [{"login": login} for login in logins]}), encoding="utf-8")

    def test_find_reviewers_from_dot_package_file_reports_non_object_json(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        """
        `_find_reviewers_from_dot_package_file` 函数应在 `.package` 文件顶层不是对象时输出错误信息。
        """

        package_file: Path = tmp_path / ".package"
        package_file.write_text("[]", encoding="utf-8")

        assert manifest._find_reviewers_from_dot_package_file(package_file) is None
        assert "理应包含 JSON 对象（dict），但读取到的数据类型是 list。" in capsys.readouterr().out

    def test_find_reviewers_from_dot_package_file_reports_invalid_owners(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `_find_reviewers_from_dot_package_file` 函数应在 `owners` 不是数组时输出错误信息。
        """

        package_file: Path = tmp_path / ".package"
        package_file.write_text(json.dumps({"owners": "invalid"}), encoding="utf-8")

        assert manifest._find_reviewers_from_dot_package_file(package_file) is None

        output = capsys.readouterr().out
        assert "中的 owners 理应是数组（list），但读取到的数据类型是 str。" in output

    def test_find_reviewers_from_dot_package_file_reports_invalid_owner_objects(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `_find_reviewers_from_dot_package_file` 函数应在 `owners` 中的条目不是对象时输出错误信息。
        """

        package_file: Path = tmp_path / ".package"
        package_file.write_text(json.dumps({"owners": ["invalid"]}), encoding="utf-8")

        assert manifest._find_reviewers_from_dot_package_file(package_file) is None
        assert "中的 owners 中的每个 owner 理应都是对象（dict），但第 1 个 owner 读取到的数据类型是 str。" in capsys.readouterr().out

    def test_find_reviewers_from_dot_package_file_handles_logins(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `_find_reviewers_from_dot_package_file` 函数应
        - 对非字符串 `login` 输出错误信息；
        - 跳过空白 `login`；
        - 对 `login` 去除首尾空白。
        """

        package_file: Path = tmp_path / ".package"
        package_file.write_text(
            json.dumps({"owners": [{}, {"login": 1}, {"login": "  "}, {"login": " owner "}]}),
            encoding="utf-8",
        )

        assert manifest._find_reviewers_from_dot_package_file(package_file) == ["owner"]
        assert "中的 owners 中的每个 owner 的 login 理应是字符串（str），但第 2 个 owner 中的 login 读取到的数据类型是 int。" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "csv_rows",
        [
            [],
            [{"PackageIdentifier": "Microsoft.DotNet.*", "gitHubUserName": ""}],
            [{"PackageIdentifier": "Microsoft.DotNet.*", "gitHubUserName": " / "}],
        ],
        ids=["no-matching-row", "empty-usernames", "blank-usernames"],
    )
    def test_find_reviewers_from_ManualValidationPipeline_csv_returns_none_without_usernames(
        self,
        winget_pkgs_repository: Path,
        csv_rows: list[dict[str, str]],
    ) -> None:
        """
        `_find_reviewers_from_ManualValidationPipeline_csv` 函数应在 CSV 中没有匹配条目或匹配条目没有有效用户名时返回 None。
        """

        csv_path: Path = winget_pkgs_repository / "Tools" / "ManualValidation" / "ManualValidationPipeline.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer: csv.DictWriter[str] = csv.DictWriter(file, fieldnames=["PackageIdentifier", "gitHubUserName"])
            writer.writeheader()
            writer.writerows(csv_rows)

        assert (
            manifest._find_reviewers_from_ManualValidationPipeline_csv(
                "Microsoft.DotNet.SDK.Preview",
                winget_pkgs_repository,
            )
            is None
        )

    def test_find_reviewers_from_ManualValidationPipeline_csv_missing_csv_file(
        self,
        winget_pkgs_repository: Path,
    ) -> None:
        """
        `_find_reviewers_from_ManualValidationPipeline_csv` 函数应在缺失 csv 文件时返回 `None`。
        """

        (winget_pkgs_repository / "Tools" / "ManualValidation" / "ManualValidationPipeline.csv").unlink()
        assert manifest._find_reviewers_from_ManualValidationPipeline_csv("Package.Id", winget_pkgs_repository) is None

    def test_find_reviewers_reads_nearest_package_file(self, winget_pkgs_repository: Path) -> None:
        """
        `find_reviewers` 函数应从最近的 `.package` 文件读取审查者，而不是从上级目录或 CSV 文件继承。
        """

        parent_directory: Path = winget_pkgs_repository / "manifests" / "m" / "Microsoft" / "DotNet"
        sdk_directory: Path = parent_directory / "SDK"
        self._write_package_file(parent_directory, ["inherited-owner"])
        self._write_package_file(sdk_directory, ["nearest-owner", "nearest-bot"])

        assert manifest.find_reviewers("Microsoft.DotNet.SDK.Preview", winget_pkgs_repository) == [
            "nearest-owner",
            "nearest-bot",
        ]

    def test_find_reviewers_inherits_from_parent_package_file(self, winget_pkgs_repository: Path) -> None:
        """
        `find_reviewers` 函数应从上级 `.package` 文件继承审查者。
        """

        parent_directory: Path = winget_pkgs_repository / "manifests" / "m" / "Microsoft" / "DotNet"
        self._write_package_file(parent_directory, ["inherited-owner"])

        assert manifest.find_reviewers("Microsoft.DotNet.SDK.Preview", winget_pkgs_repository) == ["inherited-owner"]

    def test_find_reviewers_falls_back_to_csv_without_package_logins(self, winget_pkgs_repository: Path) -> None:
        """
        `find_reviewers` 函数应在 `.package` 文件中没有用户名时回退到 CSV 文件。
        """

        parent_directory = winget_pkgs_repository / "manifests" / "m" / "Microsoft" / "DotNet"
        self._write_package_file(parent_directory, [])

        assert manifest.find_reviewers("Microsoft.DotNet.SDK.Preview", winget_pkgs_repository) == ["csv-owner", "csv-bot"]

    def test_find_reviewers_prefers_exact_csv_match(self, winget_pkgs_repository: Path) -> None:
        """
        `find_reviewers` 函数应优先使用精确匹配的 CSV 条目，而不是通配符匹配。
        """

        csv_path: Path = winget_pkgs_repository / "Tools" / "ManualValidation" / "ManualValidationPipeline.csv"
        with csv_path.open("a", encoding="utf-8", newline="") as file:
            writer: csv.DictWriter[str] = csv.DictWriter(file, fieldnames=["PackageIdentifier", "gitHubUserName"])
            writer.writerow({"PackageIdentifier": "Microsoft.DotNet.SDK.Preview", "gitHubUserName": "exact-owner"})

        assert manifest.find_reviewers("Microsoft.DotNet.SDK.Preview", winget_pkgs_repository) == ["exact-owner"]

    def test_find_reviewers_uses_configured_repository_path(self, monkeypatch: pytest.MonkeyPatch, winget_pkgs_repository: Path) -> None:
        """
        `find_reviewers` 函数应在未传入仓库路径时使用配置中的仓库路径查找审查者。
        """

        def fake_读取配置(配置项: str) -> str:
            """
            模拟 `function.maintain.config` 模块中的 `读取配置` 函数，
            返回临时 winget-pkgs 仓库的路径。

            Args:
                配置项: 配置项，应为 "paths.winget-pkgs"。

            Returns:
                str: 临时 winget-pkgs 仓库的路径。
            """

            assert 配置项 == "paths.winget-pkgs"
            return str(winget_pkgs_repository)

        monkeypatch.setattr(manifest, "读取配置", fake_读取配置)

        assert manifest.find_reviewers("Microsoft.DotNet.SDK.Preview") == ["csv-owner", "csv-bot"]

    def test_find_reviewers_returns_none_when_configured_path_is_not_string(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """
        `find_reviewers` 函数应在配置中的仓库路径不是字符串时返回 None。
        """

        monkeypatch.setattr(manifest, "读取配置", lambda 配置项: None)

        assert manifest.find_reviewers("Microsoft.DotNet.SDK.Preview") is None

    def test_find_reviewers_stops_ancestor_search_at_manifest_root(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """
        `find_reviewers` 函数不应在 manifests 根目录之外继续查找 `.package` 文件，并应回退到 CSV。
        """

        package_directory: Path = tmp_path / "manifests" / "e" / "Example" / "Package"
        package_directory.mkdir(parents=True)
        (tmp_path / ".package").write_text(json.dumps({"owners": [{"login": "owner1"}]}), encoding="utf-8")

        def _fake_获取清单目录(包标识符: str, winget_pkgs目录: str | None = None) -> str:
            """
            模拟 `function.files.manifest` 模块中的 `获取清单目录` 函数，
            返回临时包目录的路径。

            Args:
                包标识符: 包标识符。
                winget_pkgs目录: winget-pkgs 仓库的路径。

            Returns:
                str: 临时包目录的路径。
            """

            del 包标识符, winget_pkgs目录
            return str(package_directory)

        def _fake_find_reviewers_from_ManualValidationPipeline_csv(包标识符: str, winget_pkgs目录: Path) -> list[str]:
            """
            模拟 `function.files.manifest` 模块中的 `_find_reviewers_from_ManualValidationPipeline_csv` 函数，
            返回一个固定的审查者列表（`["reviewers-in-csv"]`）。

            Args:
                包标识符: 包标识符。
                winget_pkgs目录: winget-pkgs 仓库的路径。

            Returns:
                list[str]: 固定的审查者列表 `["reviewers-in-csv"]`。
            """

            del 包标识符, winget_pkgs目录
            return ["reviewers-in-csv"]

        monkeypatch.setattr(manifest, "获取清单目录", _fake_获取清单目录)
        monkeypatch.setattr(manifest, "_find_reviewers_from_ManualValidationPipeline_csv", _fake_find_reviewers_from_ManualValidationPipeline_csv)

        assert manifest.find_reviewers("Example.Package", tmp_path) == ["reviewers-in-csv"]
