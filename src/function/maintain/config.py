import os
import json
from colorama import Fore
from function.print.print import 消息头

def 读取配置(配置项: str, 静默: bool = False) -> None | str | tuple[str, str] | bool:
    """
    [验证/转换后的配置值]  
    读取 Sundry 配置文件的指定配置项，并返回配置值。  
    如果读取失败则返回 0。
    """

    # {
    #     "version": "1.3.4", -> str
    #     "winget-pkgs": "D:\\...\\winget-pkgs", -> exists? -> str
    #     "winget-tools": "D:\\...\\winget-tools", -> exists? -> str
    #     "pkgs-repo": "owner/winget-pkgs", -> split -> owner, repo
    #     "tools-repo": "owner/winget-tools", -> split -> owner, repo
    #     "signature": "yes", -> conversion -> bool
    #     "fork": "owner/winget-pkgs", -> split -> owner, repo
    #     "lang": "zh-CN" -> str
    # }

    配置值 = 读取配置项(配置项, 静默)

    if not 配置值:
        return None

    if 配置项 in ["winget-pkgs", "winget-tools"]:
        # 验证配置的路径是否存在
        配置值 = os.path.normpath(配置值)
        if (not os.path.exists(配置值)):
            if not 静默:
                print(f"{消息头.错误} 配置文件中的目录 {Fore.BLUE}{配置值}{Fore.RESET} 不存在")
                print(f"{消息头.消息} 运行 sundry config {配置项} <路径> 来修改配置文件中的值")
            return None
        return 配置值
    elif 配置项 in ["pkgs-repo", "tools-repo", "fork"]:
        # 分隔 owner 和 repo
        try:
            owner, repo = 配置值.split("/")
            return owner, repo
        except Exception as e:
            if not 静默:
                print(f"{消息头.错误} 读取配置文件失败: {Fore.RED}解析 pkgs-repo 配置项失败{Fore.RESET}\n{Fore.RED}{e}{Fore.RESET}")
            return None
    elif 配置项 in ["signature"]:
        # yes 反 Ture，否则反 False
        if 配置值.lower() == "yes":
            return True
        else:
            return False
    else:
        # 直接返回
        return 配置值


def 读取配置项(配置项: str, 静默: bool = False) -> str | None:
    """
    [原始字符串]  
    读取指定配置项的值，并返回配置项值。  
    预期返回非空 str，读取失败返回 None。
    """

    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
                if 配置数据[配置项]:
                    return 配置数据[配置项]
                else:
                    if not 静默:
                        print(f"{消息头.错误} 读取配置文件失败:\n{Fore.RED}值 \"{配置项}\" 为空{Fore.RESET}")
                        print(f"{消息头.消息} 运行 sundry config {配置项} <值> 来修改配置文件中的值")
                    return None
        except Exception as e:
            if not 静默:
                print(f"{消息头.错误} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return None
    else:
        if not 静默:
            print(f"{消息头.错误} 配置文件不存在")
            print(f"{消息头.消息} 运行 sundry config init 来初始化配置文件")
        return None
