import os
import json
import requests
from typing import Any
from colorama import Fore
from catfood.functions.print import 消息头
from catfood.exceptions.operation import TryOtherMethods, OperationFailed

class 配置信息:
    默认配置: dict[str, Any] = {
        "$schema": "https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/1.2.json",
        "version": "1.2",
        "debug": False,
        "paths": {
            "winget-pkgs": "",
            "winget-tools": ""
        },
        "repos": {
            "winget-pkgs": "",
            "winget-tools": ""
        },
        "git": {
            "signature": False
        },
        "github": {
            "pr": {
                "maintainer_can_modify": False,
                "mention_self_when_reviewer": False
            }
        },
        "tools": {
            "prune": {
                "remote": {
                    "prune_merged_branches": False,
                    "prune_closed_branches": False
                }
            },
            "verify": {
                "show_warning_on_non-clean_windows": False
            }
        },
        "cache": {
            "validate": {
                "schema": True
            }
        },
        "i18n": {
            "lang": "zh-cn"
        }
    }

    布尔值项: list[str] = [
        "debug",
        "git.signature",
        "github.pr.maintainer_can_modify", "github.pr.mention_self_when_reviewer",
        "tools.prune.remote.prune_merged_branches", "tools.prune.remote.prune_closed_branches",
        "tools.verify.show_warning_on_non-clean_windows",
        "cache.validate.schema"
    ]

    必填项: list[str] = [
        "paths.winget-pkgs",
        "paths.winget-tools",
        "repos.winget-pkgs",
        "repos.winget-tools"
    ]

    最新版本: str = "1.2"

    所在位置: str = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

def 验证配置(配置项: str, 配置值: str | bool) -> str | None:
    """
    [验证配置]
    验证指定的配置项和配置值的配对是否有效，返回为什么无效。  
    有效返回 None，无效返回 str 原因。  
    配置项 = 键路径
    """

    if not 配置项:
        return "未指定配置项"
    if isinstance(配置值, str) and (not 配置值):
        return "未指定配置值"

    if 配置项.startswith("paths.") and isinstance(配置值, str):
        配置值 = os.path.normpath(配置值)
        if (not os.path.exists(配置值)):
            return f"配置文件中的目录 {Fore.BLUE}{配置值}{Fore.RESET} 不存在"
        return None

    elif 配置项.startswith("repos.") and isinstance(配置值, str):
        while True:
            parts = 配置值.split("/")
            if len(parts) == 2:
                owner, repo = parts
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                try:
                    response = requests.head(api_url)
                    if response.status_code < 400:
                        return None
                    elif response.status_code == 404:
                        return f"仓库 {Fore.BLUE}{配置值}{Fore.RESET} 不存在或没有权限访问"
                    else:
                        return f"无法验证仓库，GitHub API 响应 {Fore.BLUE}{response.status_code}{Fore.RESET}"
                except Exception:
                    return None # NOTE 避免网络问题导致的假性配置错误
            else:
                return "仓库格式不正确，应为 owner/repo 的格式"

    elif (配置项 in 配置信息.布尔值项) and (not isinstance(配置值, bool)):
        return f"应是布尔值，但实际是 {Fore.BLUE}{type(配置值)}{Fore.RESET}"

    elif (配置项 == "i18n.lang") and (配置值 not in ["zh-cn", "en-us"]):
        return f"不支持的语言 {Fore.BLUE}{配置值}{Fore.RESET}"

    else:
        return None

def 读取配置(配置项: str, 静默: bool = False) -> None | str | tuple[str, str] | bool:
    """
    [验证/转换后的配置值]
    读取 Sundry 配置文件的指定配置项，并返回配置值。
    如果读取失败则返回 None。
    """

    try:
        配置值: str | bool | None = 读取配置项(配置项, 静默)

        if 配置值 is None:
            return None
        
        # 验证前就要转换
        if 配置项.startswith("paths."):
            if isinstance(配置值, str):
                配置值 = os.path.normpath(配置值)
            else:
                if not 静默:
                    raise OperationFailed(f"配置值的类型不是 str (实际是{type(配置值)})")

        if 验证结果 := 验证配置(配置项, 配置值):
            if not 静默:
                raise OperationFailed(f"验证配置值失败: {Fore.RED}{验证结果}{Fore.RESET}")
            return None

        if 配置项.startswith("repos.") and isinstance(配置值, str):
            # 分隔 owner 和 repo
            try:
                owner, repo = 配置值.split("/")
                return owner, repo
            except Exception as e:
                if not 静默:
                    raise OperationFailed(f"分割 owner 和 repo 失败\n{e}")
                return None
        else:
            # 直接返回
            return 配置值
    except OperationFailed as e:
        if not 静默:
            print(f"{消息头.错误} 读取配置 {配置项} 失败: {Fore.RED}{e}{Fore.RESET}")
        return None

def 读取配置项(配置项: str, 静默: bool = False) -> str | bool | None:
    """
    [原始字符串]
    读取指定配置项的值，并返回配置项值。
    预期返回非空 str 或 bool，读取失败返回 None。
    """

    if os.path.exists(配置信息.所在位置):
        try:
            键路径 = 配置项.split(".")
            with open(配置信息.所在位置, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            当前字典 = 配置数据
            for 键 in 键路径[:-1]:
                当前字典 = 当前字典[键]
            最后键 = 键路径[-1]
            if 当前字典[最后键] is not None:
                return 当前字典[最后键]
            else:
                if not 静默:
                    print(f"{消息头.错误} 读取配置文件失败:\n{Fore.RED}值 \"{配置项}\" 为空{Fore.RESET}")
                    print(f"{消息头.消息} 运行 sundry config {配置项} <值> 来修改配置文件中的值")
                return None
        except KeyError as e:
            if not 静默:
                print(f"{消息头.错误} 读取配置文件失败:\n{Fore.RED}键 {e} 不存在{Fore.RESET}")
            return None
    else:
        if not 静默:
            print(f"{消息头.错误} 配置文件不存在")
            print(f"{消息头.消息} 运行 sundry config init 来初始化配置文件")
        return None
    
def 获取当前配置版本() -> float:
    """
    尝试从配置文件中的 version 字段获取当前配置文件的版本，失败返回 `None`。

    该函数不会输出错误，但会抛出 `ValueError`。
    """

    配置版本 = 读取配置("version", 静默=True)
    if not isinstance(配置版本, str):
        raise ValueError("未能获取当前配置文件版本")

    try:
        配置版本 = float(配置版本)
    except ValueError as e:
        raise ValueError(f"获取到的当前配置文件版本无效: ({e})")

    if not (1.1 <= 配置版本):
        raise ValueError(f"获取到的当前配置文件版本无效 ({配置版本})")
    
    return 配置版本
    
def 获取配置schema(版本: str | float) -> dict[str, Any] | None:
    """
    尝试从 GitHub 仓库和网站上获取指定版本的配置文件的 json schema，获取失败返回 `None`。

    此函数会输出错误。
    """

    try:
        # NOTE 这里的导入不要放顶级，会出现循环导入
        from function.github.token import read_token
        from catfood.functions.github.api import 获取GitHub文件内容

        print(f"{消息头.信息} 尝试从 GitHub API 获取配置文件 schema ...")
        schema文件 = 获取GitHub文件内容("DuckDuckStudio/yazicbs.github.io", f"Tools/Sundry/config/schema/{版本}.json", read_token(silent=True))
        if not schema文件:
            raise TryOtherMethods("未获取到内容")
        print(f"{消息头.信息} 获取配置文件 schema 成功")
        return json.loads(schema文件)
    except Exception as e:
        try:
            print(f"{消息头.警告} 获取配置文件 schema 失败 ({e})，通过 https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/{版本}.json 重试...")
            响应 = requests.get(f"https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/{版本}.json")
            响应.raise_for_status()
            print(f"{消息头.信息} 获取配置文件 schema 成功")
            return 响应.json()
        except Exception:
            return None
