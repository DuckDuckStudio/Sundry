import os
import yaml
import requests
import subprocess
from typing import Any
import tools.remove as remove
from colorama import Fore, init
from function.constant import Response
from function.print.print import 消息头
from exception.request import RequestException
from function.files.manifest import 获取现有包版本, 获取清单目录

def main(args: list[str]) -> int:
    try:
        init(autoreset=True)
        if not args:
            print(f"{消息头.错误} 请传递参数")
            raise KeyboardInterrupt

        if len(args) == 1:
            args.append("")
        elif len(args) > 2:
            print(f"{消息头.提示} 多余的参数，我们最多只需要 2 个参数")
            args = args[:2]

        版本列表: list[str] | None = 获取现有包版本(args[0])
        if not 版本列表:
            print(f"{消息头.错误} 未能获取到版本列表")
            raise KeyboardInterrupt
        检查软件包版本(args[0], 版本列表, (args[1].lower() in ["y", "yes", "skip", "skip-check"]))
        print(f"{消息头.成功} 成功检查 {Fore.BLUE}{args[0]}{Fore.RESET} 的所有版本")
        return 0
    except KeyboardInterrupt:
        print(f"{消息头.错误} 操作中止")
        return 1

def 检查软件包版本(软件包标识符: str, 版本列表: list[str], 跳过检查: bool) -> None:
    for 版本 in 版本列表:
        移除理由 = "Attempt to download using WinGet failed."
        # TODO: 在参数中指定这个理由

        print(f"\n{Fore.BLUE}INFO{Fore.RESET} 正在检查 {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} ({版本列表.index(版本)+1}/{len(版本列表)}) ...")
        if not 跳过检查:
            验证结果 = remove.使用WinGet验证(软件包标识符, 版本, AutoRemove=True)
            if not 验证结果:
                print(f"{消息头.成功} 验证 {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} 通过！")
                continue
            else:
                InstallerUrls验证结果 = 检查所有安装程序URL(软件包标识符, 版本) # 验证所有 InstallerUrl
                if InstallerUrls验证结果[0] in {1, 2}:
                    print(f"{消息头.警告} 似乎有几个安装程序链接仍然有效，请检查它们。")
                    if 是否中止(input(f"{消息头.问题} 要移除此版本吗? [y/N]: ")):
                        return
                else:
                    验证结果.append(InstallerUrls验证结果[1])
                print(f"{消息头.错误} {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} 下载失败！将移除此版本...")
                移除理由 = f"{移除理由}\n\n```logs\n{"\n".join(验证结果)}\n```"
        else:
            print(f"{消息头.警告} 参数指定跳过检查，直接开始移除。")

        移除软件包版本(软件包标识符, 版本, 移除理由)

def 使用GitHubAPI检查安装程序URL(InstallerUrl: str) -> str:
    """
    > 呵呵... 你把我 GitHub 127.0.0.1/Connect reset 了，我用 GitHub API 你还能拿我怎样？

    本函数使用 GitHub API 来检查指定的工件是否存在对应 tag 上。

    请求 GitHub API 获取 Release 信息 (包含工件列表) → 检查工件名 (name) 是否在列表中。
    """

    # https://github.com/owner/repo/releases/download/1.0.0/Installer.exe

    try:
        api = InstallerUrl.replace("https://github.com/", "https://api.github.com/repos/", 1).rsplit("/", 1)[0].rsplit("/", 2)
        api[1] = "tags"
        api = "/".join(api)

        # I am too lazy so I don't use token, just send request.
        响应 = requests.get(api)

        if 响应.status_code == 404:
            return f"{Fore.YELLOW}失效{Fore.RESET} (Tag 不存在)"
        elif 响应.status_code >= 400:
            return f"{Fore.RED}错误 (GitHub API 响应 {响应.status_code} {响应.content}){Fore.RESET}"

        # 你可以自己 GET 下这个 json 看看是什么样的
        # https://api.github.com/repos/DuckDuckStudio/Sundry/releases/tags/1.4.1
        响应json: dict[str, str | int | dict[str, str | int | bool] | bool | list[dict[str, str | int | dict[str, str | int | bool] | None]]] = 响应.json()
        工件数据: list[dict[str, str | int | None | dict[str, str | int | bool]]] = 响应json["assets"] # pyright: ignore[reportAssignmentType]
        for 工件 in 工件数据:
            if 工件["name"] == InstallerUrl.split("/")[-1]:
                return f"{Fore.GREEN}通过 (工件名在 GitHub API 响应的工件列表中){Fore.RESET}"
        else:
            return f"{Fore.YELLOW}不存在{Fore.RESET} (工件名不在 GitHub API 响应的工件列表中)"
    except ValueError as e:
        return f"{Fore.RED}错误 ({e}){Fore.RESET}"

def 检查所有安装程序URL(软件包标识符: str, 软件包版本: str) -> tuple[int, str]:
    """
    检查指定 软件包标识符 软件包版本 的安装程序清单中的所有 InstallerUrl 是否有失效的。

    返回: 状态, 状态信息

    状态:
    - 全部失效为 0
    - 部分失效为 1
    - 全部有效为 2
    - 检查失败为 3

    返回示例: 3, "失效 (404)"
    """
    清单目录 = 获取清单目录(软件包标识符, 软件包版本)
    if not 清单目录:
        raise KeyboardInterrupt
    try:
        # 获取安装程序清单中的所有 InstallerUrl 字段的值
        with open(os.path.join(清单目录, f"{软件包标识符}.installer.yaml"), "r", encoding="utf-8") as 清单文件:
            清单数据: dict[str, Any] = yaml.safe_load(清单文件)
            if not isinstance(清单数据, dict): # pyright: ignore[reportUnnecessaryIsInstance]
                raise ValueError(f"清单读取错误。预期读到 dict，实际读到 {type(清单数据)}")
        InstallerUrls: set[str] = set()
        for item in 清单数据.get("Installers", []):
            if "InstallerUrl" in item:
                InstallerUrls.add(item["InstallerUrl"])

        if not InstallerUrls:
            print(f"{消息头.错误} {Fore.BLUE}{软件包标识符} {软件包版本}{Fore.RESET} 的安装程序清单中未找到 InstallerUrl")
            return 3, ""
        
        # 检查所有 InstallerUrl 字段指向的 Url 是否有效
        失效数 = 0
        结果 = f"{Fore.GREEN}通过{Fore.RESET}"
        验证结果 = "========== 验证安装程序清单中的 InstallerUrl(s) =========="
        print("========== 验证安装程序清单中的 InstallerUrl(s) ==========")
        for InstallerUrl in InstallerUrls:
            print(f"正在检查 {InstallerUrl} ...", end="")
            try:
                try:
                    # 尝试 HEAD 下
                    响应 = requests.head(InstallerUrl, allow_redirects=True)
                    if 400 <= 响应.status_code:
                        raise RequestException
                    else:
                        检查响应类型(响应)
                except (requests.RequestException, ValueError):
                    raise RequestException
            except RequestException:
                try:
                    # 以 GET 方法重试
                    响应 = requests.get(InstallerUrl, allow_redirects=True)
                    if 响应.status_code < 400:
                        检查响应类型(响应)
                    elif 响应.status_code < 500: # 4xx 客户端错误
                        失效数 += 1
                        结果 = f"失效 ({响应.status_code})"
                        结果 = f"{Fore.YELLOW}{结果}{Fore.RESET}"
                    else:
                        结果 = f"服务端错误 ({响应.status_code})，不计失败"
                except requests.exceptions.SSLError:
                    # 这大概率是某个用证书加速的加速器干的。
                    结果 = 使用GitHubAPI检查安装程序URL(InstallerUrl)
                    if (Fore.YELLOW in 结果) or (Fore.RED in 结果):
                        失效数 += 1
                except (requests.RequestException, ValueError) as e:
                    失效数 += 1
                    结果 = f"{Fore.RED}错误 ({e}){Fore.RESET}"
            print(f"\r{InstallerUrl} | {结果}")
            验证结果 = f"{验证结果}\n{InstallerUrl} | {结果.replace(Fore.RED, "").replace(Fore.YELLOW, "").replace(Fore.RESET, "")}"
        if 失效数:
            if 失效数 == len(InstallerUrls):
                return 0, 验证结果
            else:
                return 1, 验证结果
        else:
            return 2, 验证结果
    except Exception as e:
        if isinstance(e, KeyboardInterrupt):
            raise e
        print(f"{消息头.错误} 检查安装程序清单中的 InstallerUrl(s) 失败:\n{Fore.RED}{e}{Fore.RESET}")
        return 3, ""
    
def 检查响应类型(response: requests.Response) -> None:
    """
    检查响应的类型是否是常见的意外类型

    如果是，则 `raise ValueError`
    """

    contentType = response.headers.get("Content-Type")

    if contentType and any(i in contentType for i in Response.unexpectedTypes):
        raise ValueError(f"意外的类型 ({contentType})")

def 检查重复拉取请求(软件包标识符: str, 软件包版本: str) -> bool:
    """
    检查上游仓库中是否有 相同 (软件包标识符、版本) 的且 打开的 拉取请求。
    如有，返回 True。否则返回 False。
    """

    result = subprocess.run(
        ["gh", "pr", "list", "-S", f"{软件包标识符} {软件包版本}", "--repo", "microsoft/winget-pkgs"],
        capture_output=True, text=True, check=True
    )
    return bool(result.stdout)

def 移除软件包版本(软件包标识符: str, 版本: str, 原因: str) -> None:
    if 检查重复拉取请求(软件包标识符, 版本):
        print(f"{消息头.警告} 找到重复的拉取请求，跳过后续处理")
        return
    if remove.main([软件包标识符, 版本, "True", 原因]):
        print(f"{消息头.错误} 尝试移除 {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} 失败！")
        raise KeyboardInterrupt

def 是否中止(输入: str, 默认: str = "n") -> bool:
    """
    依据输入确定是否中止后续操作。
    false 表示继续。
    true 表示中止。
    """
    if not 输入:
        输入 = 默认

    return 输入.lower() not in ["y", "yes", "是"]
