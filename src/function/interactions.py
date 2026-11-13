"""
有关用户交互的函数
"""

from typing import Literal

from catfood.constant import NO
from catfood.functions.github.api import get_github_token_owner
from catfood.functions.print import MSHead
from colorama import Fore

from function.github.token import read_token
from function.maintain.config import 读取配置


def ask_for_reviewers(reviewers: list[str] | None, doWhat: str) -> Literal["cancel", "continue_without_mention", "continue_with_mention"]:
    """
    询问用户在包需要审查者审查时是否继续修改。

    Args:
        reviewers: 审查者信息。
        doWhat: 用户正在执行的操作，例如 "修改此包"。

    Returns:
        "cancel": 终止。
        "continue_without_mention": 不提及任何人，继续。
        "continue_with_mention": 提及审查者，继续。
    """

    if not reviewers:
        return "continue_without_mention"

    iAm: str | None = get_github_token_owner(read_token())
    if (not iAm) or (iAm not in reviewers):
        try:
            if input(f"{MSHead.Warning} 有关此包的修改需要 {Fore.BLUE}{f'{Fore.RESET}、{Fore.BLUE}'.join(reviewers)}{Fore.RESET} 审查，您还是想要{doWhat}吗（这将在 PR 正文中 @审查者）：[{Fore.GREEN}Y{Fore.RESET}/n]").lower() in NO:
                print(f"{MSHead.Error} 用户决定不再{doWhat}")
                return "cancel"
        except KeyboardInterrupt:
            print(f"{MSHead.Error} 用户取消了{doWhat}")
            return "cancel"
    elif not 读取配置("github.pr.mention_self_when_reviewer"):
        return "continue_without_mention"

    return "continue_with_mention"
