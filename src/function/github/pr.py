from colorama import Fore
from requests import HTTPError
from catfood.functions.print import 消息头
from function.github.token import read_token
from function.maintain.config import 读取配置
from function.constant.general import PR_TOOL_NOTE
from catfood.functions.github.api import 请求GitHubAPI
from catfood.exceptions.operation import OperationFailed
from catfood.functions.format.github import ResolvesIssue

def submitChanges(
    branch: str,
    packageIdentifier: str,
    packageVersion: str,
    doWhat: str,
    resolves: str | None = None,
    information: str | None = None,
    token: str | None = None
) -> bool:
    """
    向上游仓库（microsoft/winget-pkgs）提交修改拉取请求。

    :param branch: 修改位于的分支名
    :type branch: str
    :param packageIdentifier: 修改的包的标识符
    :type packageIdentifier: str
    :param packageVersion: 修改的包的版本
    :type packageVersion: str
    :param doWhat: 做什么修改，该内容作为拉取请求标题开头
    :type doWhat: str
    :param resolves: 解决了什么议题
    :type resolves: str | None
    :param information: 要在拉取请求正文中添加的内容
    :type information: str | None
    :param token: 创建拉取请求时使用的 GitHub Token
    :type token: str | None
    :return: 是否成功创建拉取请求
    :rtype: bool
    """

    pkgs仓库 = 读取配置("repos.winget-pkgs")
    if not isinstance(pkgs仓库, tuple):
        print(f"{消息头.错误} 未能获取配置文件中的 repos.winget-pkgs")
        return False
    owner: str = pkgs仓库[0]

    if not token:
        token = read_token()
        if not token:
            print(f"{消息头.错误} 未能读取到 Token")

    jsonData: dict[str, str | bool] = {
        "title": f"{doWhat}: {packageIdentifier} version {packageVersion}",
        "head": f"{owner}:{branch}",
        "base": "master",
        "body": PR_TOOL_NOTE
    }

    if resolves:
        if resolvesStr := ResolvesIssue(resolves):
            jsonData["body"] = f"{jsonData['body']}\n\n{resolvesStr}"
        else:
            print(f"{消息头.警告} 未能格式化解决议题字符串，拉取请求正文中不会链接议题")

    if information:
        jsonData["body"] = f"{jsonData['body']}\n\n{information}"

    if 读取配置("github.pr.maintainer_can_modify") == False:
        jsonData["maintainer_can_modify"] = False

    try:
        try:
            response = 请求GitHubAPI(
                api="https://api.github.com/repos/microsoft/winget-pkgs/pulls",
                json=jsonData,
                token=token,
                method="POST",
                raiseException=True
            )
            if not response:
                raise ValueError(f"catfood 的 请求GitHubAPI 函数没有返回有效的预期值，实际返回 {repr(response)}")
            print(f"{消息头.成功} 拉取请求创建成功: {response.get("html_url", f"{Fore.YELLOW}未能获取到拉取请求链接{Fore.RESET}")}")
            return True
        except HTTPError as e:
            raise OperationFailed(f"GitHub API 响应 {e.response.status_code} 错误: {e.response.text}") from e
    except Exception as e:
        print(f"{消息头.错误} 创建拉取请求失败: {Fore.RED}{e}{Fore.RESET}")
        return False
