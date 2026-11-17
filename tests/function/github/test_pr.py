from io import BytesIO
from unittest.mock import Mock

import pytest
from requests import HTTPError, Response

from function.constant.general import PR_TOOL_NOTE
from function.github.pr import submitPR


class TestsubmitPR:
    """
    对 `function.github.pr` 模块中的 `submitPR` 函数的测试。
    """

    @pytest.fixture
    def submit_pr_mocks(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> tuple[Mock, Mock, Mock]:
        """
        模拟配置读取、GitHub API 请求和 Token 读取的函数。

        Returns:
            tuple[Mock, Mock, Mock]: 返回三个模拟对象：
                1. `config_reader`: 模拟 `读取配置` 函数。
                    - `repos.winget-pkgs` 返回元组 `("穗穗", "winget-pkgs")`；
                    - `github.pr.maintainer_can_modify` 返回 `True`。
                2. `github_request`: 模拟 `request_github_api` 函数，返回 `{"html_url": "https://github.com/example/pull/1"}`。
                3. `token_reader`: 模拟 `read_token` 函数，返回 `"mock-token"`。
        """

        config_values: dict[str, tuple[str, str] | bool] = {
            "repos.winget-pkgs": ("穗穗", "winget-pkgs"),
            "github.pr.maintainer_can_modify": True,
        }
        config_reader = Mock(side_effect=lambda name: config_values[name])
        github_request = Mock(return_value={"html_url": "https://github.com/example/pull/1"})
        token_reader = Mock(return_value="mock-token")

        monkeypatch.setattr("function.github.pr.读取配置", config_reader)
        monkeypatch.setattr("function.github.pr.request_github_api", github_request)
        monkeypatch.setattr("function.github.pr.read_token", token_reader)

        return config_reader, github_request, token_reader

    def test_submitPR_should_submit_pull_request_with_given_token_and_information(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应使用指定的 GitHub Token 和信息提交拉取请求。
        """

        _, github_request, token_reader = submit_pr_mocks

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            information="Additional details.",
            token="given-token",
        )

        assert result is True
        token_reader.assert_not_called()
        github_request.assert_called_once_with(
            api="https://api.github.com/repos/microsoft/winget-pkgs/pulls",
            json={
                "title": "Update: Example.Package version 1.2.3",
                "head": "穗穗:test-branch",
                "base": "master",
                "body": f"{PR_TOOL_NOTE}\n\nAdditional details.\n\n---\n\n",
                "maintainer_can_modify": True,
            },
            token="given-token",
            method="POST",
            raiseException=True,
        )
        assert "https://github.com/example/pull/1" in capsys.readouterr().out

    def test_submitPR_should_attempt_reading_the_token_when_no_token_was_given(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在未提供 GitHub Token 时尝试读取 GitHub Token。
        """

        _, github_request, token_reader = submit_pr_mocks

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
        )

        assert result is True
        token_reader.assert_called_once_with()
        github_request.assert_called_once_with(
            api="https://api.github.com/repos/microsoft/winget-pkgs/pulls",
            json={
                "title": "Update: Example.Package version 1.2.3",
                "head": "穗穗:test-branch",
                "base": "master",
                "body": f"{PR_TOOL_NOTE}\n\n---\n\n",
                "maintainer_can_modify": True,
            },
            token="mock-token",
            method="POST",
            raiseException=True,
        )
        assert "https://github.com/example/pull/1" in capsys.readouterr().out

    def test_submitPR_should_fail_when_token_is_unavailable(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在无法读取 GitHub Token 时失败。
        """

        _, github_request, token_reader = submit_pr_mocks
        token_reader.return_value = None

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
        )

        assert result is False
        github_request.assert_not_called()
        assert "未能获取 GitHub Token" in capsys.readouterr().out

    def test_submitPR_should_fail_when_repository_config_is_invalid(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在仓库配置格式无效时失败。
        """

        config_reader, github_request, token_reader = submit_pr_mocks
        config_reader.side_effect = lambda name: "无效配置" if name == "repos.winget-pkgs" else True

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            token="given-token",
        )

        assert result is False
        token_reader.assert_not_called()
        github_request.assert_not_called()
        assert "未能从配置文件获取你的 winget-pkgs 仓库（repos.winget-pkgs）" in capsys.readouterr().out

    def test_submitPR_should_not_specify_maintainer_can_modify_when_its_config_is_invalid(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在是否允许维护者修改 PR 的配置无效时不指定 `maintainer_can_modify`。
        """

        config_reader, github_request, token_reader = submit_pr_mocks
        config_reader.side_effect = lambda name: "无效配置" if name == "github.pr.maintainer_can_modify" else ("穗穗", "winget-pkgs")

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            information="正文内容",
            token="given-token",
        )

        assert result is True
        token_reader.assert_not_called()
        github_request.assert_called_once_with(
            api="https://api.github.com/repos/microsoft/winget-pkgs/pulls",
            json={
                "title": "Update: Example.Package version 1.2.3",
                "head": "穗穗:test-branch",
                "base": "master",
                "body": f"{PR_TOOL_NOTE}\n\n正文内容\n\n---\n\n",
                # "maintainer_can_modify": True, -- 应没有指定维护者是否可修改
            },
            token="given-token",
            method="POST",
            raiseException=True,
        )
        assert "https://github.com/example/pull/1" in capsys.readouterr().out

    def test_submitPR_should_fail_when_github_api_returns_no_response(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在 GitHub API 未返回有效响应时失败。
        """

        _, github_request, _ = submit_pr_mocks
        github_request.return_value = None

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            token="given-token",
        )

        assert result is False
        assert "GitHub API 没有返回有效的预期值，实际返回 None" in capsys.readouterr().out

    def test_submitPR_should_report_github_api_http_error(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在 GitHub API 返回 HTTP 错误时失败并报告响应状态和正文。
        """

        _, github_request, token_reader = submit_pr_mocks
        response = Response()
        response.status_code = 422
        response.raw = BytesIO(b"Request failed")
        github_request.side_effect = HTTPError("请求失败", response=response)

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            token="given-token",
        )

        assert result is False
        token_reader.assert_not_called()
        assert "GitHub API 响应 422 错误：Request failed" in capsys.readouterr().out

    def test_submitPR_should_fail_when_github_api_returns_http_error_with_no_response(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `submitPR` 函数应在 GitHub API 返回 HTTP 错误且没有响应时失败。
        """

        _, github_request, token_reader = submit_pr_mocks
        github_request.side_effect = HTTPError("请求失败", response=None)

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            token="given-token",
        )

        assert result is False
        token_reader.assert_not_called()
        assert "GitHub API 请求失败，未收到响应：请求失败" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "pr_body",
        (
            "正文内容",
            "正文内容\n",
            "正文内容\n\n",
            pytest.param("正文内容\n\n---", marks=pytest.mark.xfail),
            "正文内容\n\n---\n\n",
        ),
    )
    def test_submitPR_should_insert_a_divider_line_at_the_end_of_the_pull_request_body(
        self,
        submit_pr_mocks: tuple[Mock, Mock, Mock],
        capsys: pytest.CaptureFixture[str],
        pr_body: str,
    ) -> None:
        """
        `submitPR` 函数应在 PR 正文结尾插入分割线。
        """

        _, github_request, token_reader = submit_pr_mocks

        result = submitPR(
            branch="test-branch",
            packageIdentifier="Example.Package",
            packageVersion="1.2.3",
            doWhat="Update",
            information=pr_body,
            token="given-token",
        )

        assert result is True
        token_reader.assert_not_called()
        github_request.assert_called_once_with(
            api="https://api.github.com/repos/microsoft/winget-pkgs/pulls",
            json={
                "title": "Update: Example.Package version 1.2.3",
                "head": "穗穗:test-branch",
                "base": "master",
                "body": f"{PR_TOOL_NOTE}\n\n正文内容\n\n---\n\n",
                "maintainer_can_modify": True,
            },
            token="given-token",
            method="POST",
            raiseException=True,
        )
        assert "https://github.com/example/pull/1" in capsys.readouterr().out
