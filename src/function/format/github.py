"""
将传入的字符统一为某种 GitHub 上的格式。
"""

def IssueNumber(input: str) -> str | None:
    """
    从输入中获取 Issue 或 PR 的 Number，并返回 str 的 Number。
    """

    if input.isdigit():
        return input
    elif input.startswith("#") and input[1:].isdigit():
        return input[1:]
    elif input.startswith("https://"):
        for path in input.split("/"):
            if path.isdigit():
                return path

    return None

def ResolvesIssue(input: str) -> str | None:
    """
    将输入格式化为 GitHub PR 的 Resolves Issue 格式。

    GitHub Docs: https://docs.github.com/zh/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword
    """

    num = IssueNumber(input)

    if num:
        return f"- Resolves {num}"
    else:
        return None
