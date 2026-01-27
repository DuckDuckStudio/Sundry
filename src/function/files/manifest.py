import os
import shutil
import base64
import subprocess
from typing import Any
from colorama import Fore
from function.maintain.config import 读取配置
from catfood.functions.github.api import 请求GitHubAPI
from catfood.functions.print import 消息头, 多行带头输出
from catfood.exceptions.request import RequestException
from catfood.exceptions.operation import TryOtherMethods

class 清单信息:
    """有关包清单的一些信息"""

    版本列表: list[str]= ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0", "1.9.0", "1.10.0", "1.12.0"]
    """包清单的所有版本（包括已弃用版本）"""

    旧版本列表: list[str] = 版本列表[:-1]
    """非最新的包清单版本"""

    最新版本: str = 版本列表[-1]
    """最新的包清单版本"""

    类型列表: list[str] = [
        "installer", # 安装程序清单
        "defaultLocale", # 默认本地化清单
        "locale", # 本地化清单
        "version", # 版本清单
        "singleton", # 单例清单，已弃用
        "merged" # 合并后的清单，常见于验证管道
    ]
    """包清单的所有类型"""

def 获取清单目录(包标识符: str, 包版本: str | None = None, winget_pkgs目录: str | None = None) -> str | None:
    """
    依据指定的包标识符（和包版本）获取该包（版本）的清单目录。

    会验证获取到的清单目录是否存在，不存在则返回 `None`。

    此函数没有输出。
    
    :param 包标识符: 指定的包标识符
    :type 包标识符: str
    :param 包版本: 指定的包版本
    :type 包版本: str | None
    :param winget_pkgs目录: (可选) 如果在调用处已经有获取了 winget-pkgs 仓库的路径，则可传递此路径，避免重复读取。
    :type winget_pkgs目录: str | None
    :return: 获取到的清单目录，没获取到则返回 `None`
    :rtype: str | None
    """

    if not winget_pkgs目录:
        配置值 = 读取配置("paths.winget-pkgs")
        if isinstance(配置值, str):
            winget_pkgs目录 = 配置值
        else:
            return None

    可能的包类型 = ["manifests", "fonts"]

    for 包类型 in 可能的包类型:
        清单目录 = os.path.join(winget_pkgs目录, 包类型, 包标识符[0].lower(), *包标识符.split('.'))
        if 包版本:
            清单目录 = os.path.join(清单目录, 包版本)
        if os.path.exists(清单目录):
            return 清单目录

    return None
        
def 获取现有包版本(包标识符: str, winget_pkgs仓库: str | None = None) -> list[str] | None:
    """
    尝试获取指定的包的现有版本列表。

    会尝试输出错误信息

    :param 包标识符: 指定的包标识符
    :type 包标识符: str
    :param winget_pkgs仓库: (可选) 如果在调用处已经有获取了 winget-pkgs 仓库的路径，则可传递此路径，避免重复读取。
    :type winget_pkgs仓库: str | None
    :return: 获取到的版本列表，没获取到返回 `None`
    :rtype: list[str] | None
    """

    版本列表: list[str] = []

    try:
        # 从本地仓库获取版本号
        清单目录 = 获取清单目录(包标识符, winget_pkgs目录=winget_pkgs仓库)
        if not 清单目录:
            raise TryOtherMethods("未能获取清单目录")
        
        for 文件夹 in os.listdir(清单目录):
            if os.path.isdir(os.path.join(清单目录, 文件夹)):
                for 文件 in os.listdir(os.path.join(清单目录, 文件夹)):
                    if os.path.isdir(os.path.join(清单目录, 文件夹, 文件)):
                        # 如果这个版本文件夹下面还有目录，则代表这可能是类似 Nightly 版本的包的标识符的一部分
                        break
                else:
                    # 如果前面的 for 没有 break，则执行
                    版本列表.append(文件夹)

        if not 版本列表:
            raise TryOtherMethods("未能通过本地 winget-pkgs 仓库获取版本列表")
    except TryOtherMethods as e:
        print(f"{消息头.警告} {e}，尝试改用 WinGet...")

        # 从 WinGet 输出获取版本号
        try:
            结果 = subprocess.run(
                ["winget", "show", "--id", 包标识符, "-s", "winget", "-e", "--versions"],
                capture_output=True, text=True, check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"{消息头.警告} 在默认源 (winget) 中运行 WinGet 失败，尝试指定字体源 (winget-font) ...")
            if 读取配置("debug", 静默=True):
                print(f"{消息头.调试} WinGet 输出")
                print(f"{消息头.调试} stderr:")
                多行带头输出(e.stderr, 消息头.调试)
                print(f"{消息头.调试} stdout:")
                多行带头输出(e.stdout, 消息头.调试)

            try:
                结果 = subprocess.run(
                    ["winget", "show", "--id", 包标识符, "-s", "winget-font", "-e", "--versions"],
                    capture_output=True, text=True, check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"{消息头.错误} 未能获取现有包版本，WinGet 又失败了 (返回 {e.returncode})")
                if 读取配置("debug", 静默=True):
                    print(f"{消息头.调试} WinGet 输出")
                    print(f"{消息头.调试} stderr:")
                    多行带头输出(e.stderr, 消息头.调试)
                    print(f"{消息头.调试} stdout:")
                    多行带头输出(e.stdout, 消息头.调试)
                return None

        离开始还有几行 = 3
        for 行 in [line for line in 结果.stdout.splitlines() if line.strip()]:
            if (离开始还有几行 < 1):
                版本列表.append(行)
            if (包标识符 in 行) or (离开始还有几行 < 3):
                离开始还有几行 -= 1

    if 版本列表:
        return 版本列表
    else:
        print(f"{消息头.错误} 未能获取现有包版本列表")
        return None

def FormatManifest(Manifest: str, Comment: str = "# Created with Sundry-Locale") -> str:
    """
    格式化清单内容
    - 更新清单版本
    - 添加 schema
    - 添加工具注释
    - 去除末尾多余空行 / 添加末尾空行
    
    :param Manifest: 清单文件内容
    :type Manifest: str
    :param Comment: 工具注释内容
    :type Comment: str
    :return: 格式化后的清单文件内容
    :rtype: str
    """

    # 修改 ManifestVersion 和版本号
    for OldManifestVersion in 清单信息.旧版本列表:
        # 修改 ManifestVersion
        if f"ManifestVersion: {OldManifestVersion}" in Manifest:
            print(f"更新 ManifestVersion: {Fore.RED}{OldManifestVersion}{Fore.RESET} -> {Fore.GREEN}{清单信息.最新版本}{Fore.RESET}")
            Manifest = Manifest.replace(f"ManifestVersion: {OldManifestVersion}", f"ManifestVersion: {清单信息.最新版本}")

        # 修改 schema 引用，只替换版本号部分
        if f"{OldManifestVersion}.schema.json" in Manifest:
            print(f"更新 schema 引用: {Fore.RED}{OldManifestVersion}{Fore.RESET}.schema.json -> {Fore.GREEN}{清单信息.最新版本}{Fore.RESET}.schema.json")
            Manifest = Manifest.replace(f"{OldManifestVersion}.schema.json", f"{清单信息.最新版本}.schema.json")

    # 替换工具注释
    '''
    判断是否 `清单文件内容`为空 或 第一行以`#`开头
        如果是，在`清单文件内容`第一行前面追加三行工具注释与`# yaml-language-server: $schema=...`与一个空行。
    否则，`清单文件内容`有内容且第一行以`#`开头
        再判断`清单文件内容`第一行是否以`# yaml-language-server`开头
            如果是，在`清单文件内容`第一行前面追加一行工具注释
            如果不是，将`清单文件内容`第一行替换为工具注释
    '''

    # 按行分割文件内容
    lines: list[str] = Manifest.splitlines()

    if (not lines) or (not lines[0].startswith("#")): # https://github.com/DuckDuckStudio/Sundry/issues/28
        # 如果清单文件内容为空或第一行不是以#开头
        # 第一行前面追加三行
        lines.insert(0, "")
        if "\nManifestType: installer" in Manifest: # 安装程序清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.{清单信息.最新版本}.schema.json")
        elif "\nManifestType: defaultLocale" in Manifest: # 默认区域清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.{清单信息.最新版本}.schema.json")
        elif "\nManifestType: locale" in Manifest: # 一般区域清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.locale.{清单信息.最新版本}.schema.json")
        else: # 版本清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.{清单信息.最新版本}.schema.json")
        lines.insert(0, Comment)
    # 否则第一行是#开头
    else:
        # 判断第一行是否以# yaml-language-server开头
        if lines[0].startswith("# yaml-language-server"):
            # 如果是，追加一行
            lines.insert(0, Comment)
        else:
            # 否则，替换第一行
            lines[0] = Comment

    # 将修改后的内容重新合并为一个字符串并赋值回清单文件内容
    Manifest = "\n".join(lines)

    # 确保最后有且只有一行空行
    if not Manifest.endswith('\n'): # 如果最后没有换行符
        Manifest += '\n' # 添加一个换行符
    else: # 如果有了
        Manifest = Manifest.rstrip('\n') + '\n'
        # 管他几个先全移除 -> 添加一个换行符
        # .rstrip() 去除文本末尾的指定字符

    return Manifest

def 获取PR清单(PR编号: str, 清单目录: str, token: str | None = None) -> int:
    """
    尝试获取 PR 中修改的包版本的清单。

    :param PR编号: PR 的编号
    :type PR编号: str
    :param 清单目录: 清单文件保存的位置
    :type 清单目录: str
    :param token: 请求使用的 GitHub Token，`None` 为不带 Token 请求。
    :type token: str | None
    :return: 是否成功获取清单。成功为 `0`，失败为 `1`。
    :rtype: int
    """

    print(f"{消息头.信息} 尝试获取 PR #{PR编号} 中的清单...")
    if not (清单文件夹路径 := _获取PR清单文件夹路径(PR编号, token)):
        return 1

    if 结果 := _获取PR仓库和分支(PR编号, token):
        fork仓库, fork分支 = 结果
    else:
        return 1
    
    if os.path.exists(清单目录):
        print(f"{消息头.警告} 临时清单目录下{Fore.YELLOW}已存在同名清单目录{Fore.RESET}，Sundry 将覆盖掉它。")
        try:
            shutil.rmtree(清单目录)
        except Exception as e:
            print(f"{消息头.错误} 移除同名清单目录时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{消息头.提示} 清单目录位于: {清单目录}")
            return 1
    os.makedirs(清单目录, exist_ok=True)

    try:
        api = f"https://api.github.com/repos/{fork仓库}/contents/{清单文件夹路径}?ref={fork分支}" # NOTE: 这里不对 url 进行编码，因为包标识符不允许出现特殊字符/中文
        清单目录响应: list[dict[str, Any]] | None = 请求GitHubAPI(api, token=token)
        if not isinstance(清单目录响应, list):
            raise RequestException(f"未获取到清单文件夹信息: {清单目录响应}")

        for 清单文件 in 清单目录响应: # NOTE: 原来在 verify 中时这里写了个“这里要改”，但我完全不记得是要改什么 :(
            api = 清单文件.get("url")
            if not isinstance(api, str):
                raise ValueError(f"未能获取到清单文件 api (url 字段): {清单文件}")
            
            文件名 = 清单文件.get("name")
            if not isinstance(文件名, str):
                raise ValueError(f"未能获取到清单文件名: {清单文件}")
            
            清单文件响应: dict[str, str | int | dict[str, str]] | None = 请求GitHubAPI(api, token=token)
            if not 清单文件响应:
                raise RequestException(f"未获取到清单文件信息: {清单文件响应}")

            清单内容 = 清单文件响应.get("content")
            if not isinstance(清单内容, str):
                raise ValueError(f"未能获取到清单内容: {清单文件响应}")

            清单内容 = base64.b64decode(清单内容)

            with open(os.path.join(清单目录, 文件名), "wb") as 清单文件:
                清单文件.write(清单内容)
    except Exception as e:
        print(f"{消息头.错误} 下载清单文件失败:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

    print(f"{消息头.成功} 成功获取 PR #{PR编号} 中的清单")
    return 0

def _获取PR清单文件夹路径(PR编号: str, token: str | None = None) -> str | None:
    """
    尝试获取 PR 中修改的清单文件夹路径。

    :param PR编号: PR 的编号
    :type PR编号: str
    :param token: 请求使用的 GitHub Token，`None` 为不带 Token 请求。
    :type token: str | None
    :return: 获取到的路径，获取失败返回 `None`。
    :rtype: str | None
    """
    api = f"https://api.github.com/repos/microsoft/winget-pkgs/pulls/{PR编号}/files"
    非预期状态 = True # 如果文件状态全是移除或没有状态，则为非预期状态
    清单文件夹 = None
    清单文件路径: list[str] = []

    响应 = 请求GitHubAPI(api, token=token)
    if 响应:
        for 文件 in 响应:
            文件相对路径: str = 文件["filename"]
            # 文件是 .yaml 格式且在 manifests 目录下
            if 文件相对路径.endswith(".yaml") and 文件相对路径.startswith("manifests/"):
                清单文件路径.append(文件相对路径)
                if 清单文件夹 is None:
                    清单文件夹 = os.path.dirname(文件相对路径)
                elif 清单文件夹 != os.path.dirname(文件相对路径):
                    print(f"{消息头.错误} 此 PR 修改了多个文件夹下的文件")
                    return None
            else:
                print(f"{消息头.错误} 非预期的清单类型: {Fore.BLUE}{文件相对路径}{Fore.RESET}")
                print(f"{Fore.YELLOW}Hint{Fore.RESET} 请确定 PR 是对清单的修改，并确定修改的文件都是 .yaml 格式")
                return None
            if 文件["status"] != "removed":
                非预期状态 = False

        if 非预期状态:
            print(f"{消息头.错误} 这是个纯移除或没有修改的 PR")
            return None
        
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功获取清单文件夹相对路径")
        return 清单文件夹
    else:
        print(f"{消息头.错误} 未能获取清单文件夹相对路径，请求 {Fore.BLUE}{api}{Fore.RESET} 失败。")
        return None

def _获取PR仓库和分支(PR编号: str, token: str | None = None) -> tuple[str, str] | None:
    """
    尝试获取 PR HEAD 的仓库和分支

    :param PR编号: PR 的编号
    :type PR编号: str
    :param token: 请求使用的 GitHub Token，`None` 为不带 Token 请求。
    :type token: str | None
    :return: 包含仓库（owner/repo）和分支名的元组，获取失败返回 `None`。
    :rtype: tuple[str, str] | None
    """

    api = f"https://api.github.com/repos/microsoft/winget-pkgs/pulls/{PR编号}"

    响应 = 请求GitHubAPI(api, token=token)
    if 响应:
        try:
            fork仓库 = 响应["head"]["repo"]["full_name"]
            fork分支 = 响应["head"]["ref"]
            print(f"{Fore.GREEN}✓{Fore.RESET} 成功获取 PR HEAD 的仓库和分支")
            return fork仓库, fork分支
        except KeyError as e:
            print(f"{消息头.错误} 未能获取 PR HEAD 的仓库和分支: 响应中没有键 {Fore.BLUE}{e}{Fore.RESET}")
            return None
    else:
        return None
