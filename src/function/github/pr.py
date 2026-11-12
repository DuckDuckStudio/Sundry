import subprocess


def 检查重复拉取请求(包标识符: str, 包版本: str) -> bool:
    """
    检查上游仓库中是否有相同修改^1且打开的^2拉取请求。

    - ^1 相同修改: 指标题包含 `f"{包标识符} {包版本}"` 的拉取请求。
    - ^2 打开的: 包括草稿。

    Args:
        包标识符: 包的标识符。
        包版本: 包的版本。

    Returns:
        bool: 是否有重复的拉取请求。
    """

    result = subprocess.run(
        ["gh", "pr", "list", "-S", f"{包标识符} {包版本}", "--repo", "microsoft/winget-pkgs"],
        capture_output=True, text=True, check=True
    )
    return bool(result.stdout)
