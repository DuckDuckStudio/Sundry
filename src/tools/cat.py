import os
from colorama import init, Fore
from pygments import highlight # type: ignore
from pygments.lexers import YamlLexer # type: ignore
from function.maintain.config import 读取配置
from pygments.formatters import TerminalFormatter

def 读取和输出(清单文件: str):
    if not os.path.exists(清单文件):
        print(f"{Fore.RED}✕{Fore.RESET} 清单文件不存在")
        return 1

    try:
        print(f"{Fore.GREEN}✓{Fore.RESET} 清单文件位于 {Fore.BLUE}{清单文件}{Fore.RESET}\n")

        # 读取清单文件
        with open(清单文件, 'r', encoding='utf-8') as file:
            清单内容 = file.read()
        
        # 使用 pygments 优化输出 YAML 文件
        高亮清单: str = highlight(清单内容, YamlLexer(), TerminalFormatter()) # pyright: ignore[reportUnknownArgumentType]
        
        # 输出优化后的 YAML 内容
        print(高亮清单)

        return 0
    except PermissionError:
        print(f"{Fore.RED}✕{Fore.RESET} 读取清单文件失败: {Fore.RED}没有权限{Fore.RESET}")
        return 1
    except FileNotFoundError:
        print(f"{Fore.RED}✕{Fore.RESET} 读取清单文件失败: {Fore.RED}文件不存在{Fore.RESET}")
        return 1

def main(args: list[str]):
    init(autoreset=True)

    winget_pkgs目录 = 读取配置("winget-pkgs")
    if not isinstance(winget_pkgs目录, str):
        return 1

    # 尝试从参数中获取软件包标识符和版本
    if (2 <= len(args) <= 4):
        软件包标识符 = args[0]
        软件包版本 = args[1]
        清单类型 = args[2].lower() if len(args) > 2 else "all" # 不指定则为 all
        # 格式化 清单类型
        if (清单类型 in ["locale", "区域", "区域设置", "l"]):
            清单类型 = "locale"
        elif (清单类型 in ["installer", "安装程序", "安装", "i"]):
            清单类型 = "installer"
        elif (清单类型 in ["version", "ver", "v", "版本"]):
            清单类型 = "version"
        elif (清单类型 in ["all", "全部", "所有"]):
            清单类型 = "all"
        else:
            print(f"{Fore.RED}✕{Fore.RESET} 清单类型不正确")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 清单类型必须是 {Fore.BLUE}installer version locale all{Fore.RESET} 中的一种")
            return 1
        # 获取区域
        区域设置 = ""
        if (清单类型 == "locale"):
            if (len(args) != 4):
                print(f"{Fore.RED}✕{Fore.RESET} 请告诉我您需要查看哪个区域的清单")
                return 1
            区域设置 = args[3]
    else:
        print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

    清单目录 = os.path.join(winget_pkgs目录, "manifests", 软件包标识符[0].lower(), *软件包标识符.split('.'), 软件包版本)
    if not os.path.exists(清单目录):
        print(f"{Fore.RED}✕{Fore.RESET} 清单目录不存在")
        return 1

    if any(os.path.isdir(os.path.join(清单目录, item)) for item in os.listdir(清单目录)):
        # 如果清单目录下存在其他文件夹
        print(f"{Fore.RED}✕{Fore.RESET} 清单目录下存在其他文件夹")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 这可能是因为你 {Fore.YELLOW}错误的将软件包标识符的一部分当作软件包版本{Fore.RESET} 导致的。")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 例如软件包 DuckStudio.GitHubView.Nightly 被错误的认为是软件包 DuckStudio.GitHubView 的一个版本号为 Nightly 的版本。")
        return 1

    清单文件: list[str] | str
    if (清单类型 == "all"):
        # 设置清单文件为清单目录下的所有 yaml 文件
        清单文件 = []
        for 清单 in os.listdir(清单目录):
            if 清单.endswith(".yaml"):
                清单文件.append(os.path.join(清单目录, 清单))

        if not 清单文件:
            print(f"{Fore.RED}✕{Fore.RESET} 清单目录下没有 YAML 文件")
            return 1

        for 清单 in 清单文件:
            if 读取和输出(os.path.normpath(清单)): # 如果读取失败则返回 1
                return 1
            
        return 0
    else:
        清单文件 = ""
        if (清单类型 == "installer"):
            清单文件 = os.path.join(清单目录, f"{软件包标识符}.installer.yaml")
        if (清单类型 == "locale"):
            清单文件 = os.path.join(清单目录, f"{软件包标识符}.locale.{区域设置}.yaml")
        if (清单类型 == "version"):
            清单文件 = os.path.join(清单目录, f"{软件包标识符}.yaml")

        return 读取和输出(os.path.normpath(清单文件))
