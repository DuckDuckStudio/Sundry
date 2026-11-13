import pytest

from function import interactions


class Testask_for_reviewers:
    """
    对 `function.interactions` 模块中的 `ask_for_reviewers` 函数的测试。
    """

    def test_ask_for_reviewers_returns_continue_without_mention_when_no_reviewers(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """
        `ask_for_reviewers` 函数应在没有审查者时返回不提及审查者并继续的状态（`continue_without_mention`），
        且不应读取 Token 或询问用户。
        """

        monkeypatch.setattr(interactions, "read_token", lambda: pytest.fail("不应读取 Token"))
        monkeypatch.setattr(interactions, "get_github_token_owner", lambda token: pytest.fail("不应获取 Token 所有者"))
        monkeypatch.setattr("builtins.input", lambda prompt: pytest.fail("不应询问用户"))

        assert interactions.ask_for_reviewers(None, "修改此包") == "continue_without_mention"
        assert interactions.ask_for_reviewers([], "修改此包") == "continue_without_mention"

    def test_ask_for_reviewers_asks_unlisted_user_to_continue(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `ask_for_reviewers` 函数应在当前用户不在审查者列表中时询问用户是否继续操作。
        """

        monkeypatch.setattr(interactions, "read_token", lambda: "token")
        monkeypatch.setattr(interactions, "get_github_token_owner", lambda token: "username")
        prompts: list[str] = []
        monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "y")

        assert interactions.ask_for_reviewers(["reviewer1", "reviewer2"], "更新此包") == "continue_with_mention"
        assert len(prompts) == 1
        assert capsys.readouterr().out == ""

    def test_ask_for_reviewers_stops_when_user_declines(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `ask_for_reviewers` 函数应在用户选择不继续操作时返回取消状态（`cancel`），并输出对应消息。
        """

        monkeypatch.setattr(interactions, "read_token", lambda: "token")
        monkeypatch.setattr(interactions, "get_github_token_owner", lambda token: None)
        monkeypatch.setattr("builtins.input", lambda prompt: "n")

        assert interactions.ask_for_reviewers(["reviewer"], "移除此包版本") == "cancel"
        assert "用户决定不再移除此包版本" in capsys.readouterr().out

    def test_ask_for_reviewers_stops_when_prompt_is_interrupted(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """
        `ask_for_reviewers` 函数应在用户中断输入时返回取消状态（`cancel`），并输出对应消息。
        """

        monkeypatch.setattr(interactions, "read_token", lambda: "token")
        monkeypatch.setattr(interactions, "get_github_token_owner", lambda token: None)

        def interrupt_prompt(prompt: str) -> str:
            raise KeyboardInterrupt

        monkeypatch.setattr("builtins.input", interrupt_prompt)

        assert interactions.ask_for_reviewers(["reviewer"], "更新此包") == "cancel"
        assert "用户取消了更新此包" in capsys.readouterr().out

    @pytest.mark.parametrize(
        ("mention_self", "expected"),
        [(False, "continue_without_mention"), (True, "continue_with_mention")],
    )
    def test_ask_for_reviewers_respects_mention_self_setting(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mention_self: bool,
        expected: str,
    ) -> None:
        """
        `ask_for_reviewers` 函数应根据配置设置 `github.pr.mention_self_when_reviewer` 的值来决定是否询问用户。
        """

        monkeypatch.setattr(interactions, "read_token", lambda: "token")
        monkeypatch.setattr(interactions, "get_github_token_owner", lambda token: "reviewer")
        monkeypatch.setattr(interactions, "读取配置", lambda 配置项: mention_self)
        monkeypatch.setattr("builtins.input", lambda prompt: pytest.fail("自己是审查者时不应询问"))

        assert interactions.ask_for_reviewers(["reviewer"], "更新此包") == expected
