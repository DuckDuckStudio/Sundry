import subprocess

from catfood.exceptions.operation import OperationFailed
from catfood.functions.github.api import request_github_api
from catfood.functions.print import MSHead
from colorama import Fore
from requests import HTTPError

from function.constant.general import PR_TOOL_NOTE
from function.github.token import read_token
from function.maintain.config import 读取配置


def submitPR(
    branch: str,
    packageIdentifier: str,
    packageVersion: str,
    doWhat: str,
    information: str | None = None,
    token: str | None = None
) -> bool:
    """
    向上游仓库（microsoft/winget-pkgs）提交修改拉取请求。

    Args:
        branch: 需要提交的分支名。
        packageIdentifier: 包的标识符。
        packageVersion: 包的版本。
        doWhat: 做什么修改，该内容作为拉取请求标题开头。
        information: 要在拉取请求正文中添加的内容。
        token: 创建拉取请求时使用的 GitHub Token。

    Returns:
        bool: 是否成功创建拉取请求。
    """

    pkgs_repo = 读取配置("repos.winget-pkgs")
    if not isinstance(pkgs_repo, tuple):
        print(f"{MSHead.Error} 未能获取配置文件中的 repos.winget-pkgs")
        return False
    owner: str = pkgs_repo[0]
    del pkgs_repo

    jsonData: dict[str, str | bool] = {
        "title": f"{doWhat}: {packageIdentifier} version {packageVersion}",
        "head": f"{owner}:{branch}",
        "base": "master",
        "body": PR_TOOL_NOTE
    }

    if information:
        jsonData["body"] = f"{jsonData['body']}\n\n{information}"

    # 保证 PR body 最后是分割线
    if isinstance(jsonData["body"], str) and (not jsonData["body"].rstrip('\n').endswith("---")):
        jsonData["body"] = f"{jsonData["body"].rstrip('\n')}\n\n---\n\n"

    maintainer_can_modify = 读取配置("github.pr.maintainer_can_modify")
    if isinstance(maintainer_can_modify, bool):
        jsonData["maintainer_can_modify"] = maintainer_can_modify
    del maintainer_can_modify

    try:
        try:
            response = request_github_api(
                api="https://api.github.com/repos/microsoft/winget-pkgs/pulls",
                json=jsonData,
                token=token or read_token(),
                method="POST",
                raiseException=True
            )
            if not response:
                raise ValueError(f"catfood 的 request_github_api 函数没有返回有效的预期值，实际返回 {response!r}")
            print(f"{MSHead.Success} 拉取请求创建成功: {response.get("html_url", f"{Fore.YELLOW}未能获取到拉取请求链接{Fore.RESET}")}")
            return True
        except HTTPError as e:
            response = e.response
            if response is None:
                raise OperationFailed(f"GitHub API 请求失败，未收到响应：{e}") from e
            raise OperationFailed(f"GitHub API 响应 {response.status_code} 错误：{response.text}") from e
    except Exception as e:
        print(f"{MSHead.Error} 创建拉取请求失败: {Fore.RED}{e}{Fore.RESET}")
        return False


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
