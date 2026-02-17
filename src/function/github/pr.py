import subprocess

def 检查重复拉取请求(包标识符: str, 包版本: str) -> bool:
    """
    检查上游仓库中是否有相同修改^1且打开的^2拉取请求

    - ^1 相同修改: 指标题包含 `f"{包标识符} {包版本}"` 的拉取请求。
    - ^2 打开的: 包括草稿
    
    :param 包标识符: 修改的包的标识符
    :type 包标识符: str
    :param 包版本: 修改的包的版本
    :type 包版本: str
    :return: 是否有重复的拉取请求。有返回 `True`，没有返回 `False`。
    :rtype: bool
    """

    result = subprocess.run(
        ["gh", "pr", "list", "-S", f"{包标识符} {包版本}", "--repo", "microsoft/winget-pkgs"],
        capture_output=True, text=True, check=True
    )
    return bool(result.stdout)
