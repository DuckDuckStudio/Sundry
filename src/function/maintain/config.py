import os
import json
import requests
from colorama import Fore
from function.print.print import 消息头

class 配置项信息:
    布尔值项: list[str] = [
        "debug",
        "git.signature",
        "github.pr.maintainer_can_modify", "github.pr.mention_self_when_reviewer",
        "tools.prune.remote.prune_merged_branches", "tools.prune.remote.prune_closed_branches",
        "tools.verify.show_warning_on_non-clean_windows",
        "cache.validate.schema"
    ]

def 验证配置(配置项: str, 配置值: str | bool) -> str | None:
    """
    [验证配置]
    验证指定的配置项和配置值的配对是否有效，返回为什么无效。  
    有效返回 None，无效返回 str 原因。  
    配置项 = 键路径
    """

    # 有一个人前来买瓜(调用)。  
    # ...  
    # 你这瓜(配置值)要熟(有效)我肯定要(return None)啊。  
    # 那它要是不熟(无效)怎么办啊？  
    # 要是不熟，我自己吃了它(return str)，满意了吧。

    if not 配置项:
        return "未指定配置项"
    if isinstance(配置值, str) and (not 配置值):
        return "未指定配置值"

    if 配置项.startswith("paths.") and isinstance(配置值, str):
        配置值 = os.path.normpath(配置值)
        if (not os.path.exists(配置值)):
            return f"{Fore.BLUE}{配置值}{Fore.RESET} 不存在"
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
                print(f"{消息头.错误} 仓库格式不正确，应为 owner/repo 的格式")
    # 布尔值的配置项
    elif 配置项 in 配置项信息.布尔值项:
        if isinstance(配置值, bool):
            return None
        return f"应是布尔值，但实际是 {Fore.BLUE}{type(配置值)}{Fore.RESET}"
    elif 配置项 == "i18n.lang":
        if 配置值 not in ["zh-cn", "en-us"]:
            return f"不支持的语言 {Fore.BLUE}{配置值}{Fore.RESET}"
        else:
            return None

def 读取配置(配置项: str, 静默: bool = False) -> None | str | tuple[str, str] | bool:
    """
    [验证/转换后的配置值]
    读取 Sundry 配置文件的指定配置项，并返回配置值。
    如果读取失败则返回 None。
    """

    if 配置项 == "debug":
        静默 = True

    配置值 = 读取配置项(配置项, 静默)

    if 配置值 is None:
        return None

    if 配置项.startswith("paths.") and isinstance(配置值, str):
        验证结果 = 验证配置(配置项, 配置值)
        if 验证结果:
            if not 静默:
                print(f"{消息头.错误} 配置文件中的目录 {验证结果}")
                print(f"{消息头.消息} 运行 sundry config {配置项} <路径> 来修改配置文件中的值")
            return None
        return 配置值
    elif 配置项.startswith("repos.") and isinstance(配置值, str):
        # 分隔 owner 和 repo
        try:
            owner, repo = 配置值.split("/")
            return owner, repo
        except Exception as e:
            if not 静默:
                print(f"{消息头.错误} 读取配置文件失败: {Fore.RED}分割 owner 和 repo 失败{Fore.RESET}\n{Fore.RED}{e}{Fore.RESET}")
            return None
    else:
        # 直接返回
        return 配置值

def 读取配置项(配置项: str, 静默: bool = False) -> str | bool | None:
    """
    [原始字符串]
    读取指定配置项的值，并返回配置项值。
    预期返回非空 str 或 bool，读取失败返回 None。
    """

    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

    if os.path.exists(配置文件):
        try:
            键路径 = 配置项.split(".")
            with open(配置文件, "r", encoding="utf-8") as f:
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
