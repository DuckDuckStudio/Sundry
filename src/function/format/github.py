"""
将传入的字符统一为某种 GitHub 上的格式。
"""

def IssueNumber(输入: str | int | None) -> str | None:
    """
    从输入中获取 Issue 或 PR 的 Number，并返回 str 的 Number。
    """

    if not 输入:
        return None
    elif isinstance(输入, int):
        # 妈的懒到家了
        return str(输入)
    # ===============
    elif 输入.isdigit():
        return 输入
    elif 输入.startswith("#") and 输入[1:].isdigit():
        return 输入[1:]
    elif 输入.startswith("https://"):
        for path in 输入.split("/"):
            if path.isdigit():
                return path

    return None

def ResolvesIssue(输入: str) -> str | None:
    """
    将输入格式化为 GitHub PR 的 Resolves Issue 格式。

    GitHub Docs: https://docs.github.com/zh/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword
    """

    num = IssueNumber(输入)

    if num:
        return f"- Resolves {num}"
    else:
        return None
