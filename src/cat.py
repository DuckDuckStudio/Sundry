import os
import sys
import json
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter
from colorama import init, Fore

init(autoreset=True)

# 配置文件路径
配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

if os.path.exists(配置文件):
    try:
        with open(配置文件, "r", encoding="utf-8") as f:
            配置数据 = json.load(f)
        
        if 配置数据["winget-pkgs"]:
            winget_pkgs目录 = 配置数据["winget-pkgs"]
            if (not os.path.exists(winget_pkgs目录)):
                print(f"{Fore.RED}✕{Fore.RESET} 配置文件中的目录 {Fore.BLUE}{winget_pkgs目录}{Fore.RESET} 不存在")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                sys.exit(3)
        else:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"winget-pkgs\" 为空{Fore.RESET}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
            sys.exit(3)
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
        sys.exit(3)
else:
    print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
    print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
    sys.exit(3)

# NOTE: 前面已经判断过 winget_pkgs目录 是否存在了

# 尝试从参数中获取软件包标识符和版本
if (4 <= len(sys.argv) <= 5):
    软件包标识符 = sys.argv[1]
    软件包版本 = sys.argv[2]
    清单类型 = sys.argv[3].lower()
    # 格式化 清单类型
    if (清单类型 in ["locale", "区域", "区域设置", "l"]):
        清单类型 = "locale"
    elif (清单类型 in ["installer", "安装程序", "安装", "i"]):
        清单类型 = "installer"
    elif (清单类型 in ["version", "ver", "v", "版本"]):
        清单类型 = "version"
    # 获取区域
    if (len(sys.argv) == 5):
        if (清单类型 == "locale"):
            区域设置 = sys.argv[4]
        else:
            print(f"{Fore.RED}✕{Fore.RESET} 清单类型为 {Fore.BLUE}{清单类型}{Fore.RESET} 时，不应传入第 4 参数")
            sys.exit(1)
else:
    print(f"{Fore.RED}✕ 请按照以下格式传入参数:")
    print(f"{Fore.BLUE}sundry cat [软件包标识符] [版本] [清单类型] [区域设置(如果是locale类型)]{Fore.RESET}")
    sys.exit(1)

清单目录 = os.path.join(winget_pkgs目录, "manifests", 软件包标识符[0].lower(), *软件包标识符.split('.'), 软件包版本)
if not os.path.exists(清单目录):
    print(f"{Fore.RED}✕{Fore.RESET} 清单目录不存在")
    sys.exit(3)

def 读取和输出(清单文件):
    if not os.path.exists(清单文件):
        print(f"{Fore.RED}✕{Fore.RESET} 清单文件不存在")
        sys.exit(3)
    try:
        # 读取清单文件
        with open(清单文件, 'r', encoding='utf-8') as file:
            清单内容 = file.read()
        
        # 使用 pygments 优化输出 YAML 文件
        高亮清单 = highlight(清单内容, YamlLexer(), TerminalFormatter())
        
        # 输出优化后的 YAML 内容
        print(高亮清单)
    except PermissionError:
        print(f"{Fore.RED}✕{Fore.RESET} 读取清单文件失败: {Fore.RED}没有权限{Fore.RESET}")
        sys.exit(3)
    except FileNotFoundError:
        print(f"{Fore.RED}✕{Fore.RESET} 读取清单文件失败: {Fore.RED}文件不存在{Fore.RESET}")
        sys.exit(3)

if (清单类型 == "installer"):
    清单文件 = os.path.join(清单目录, f"{软件包标识符}.installer.yaml")
    读取和输出(清单文件)
if (清单类型 == "locale"):
    清单文件 = os.path.join(清单目录, f"{软件包标识符}.locale.{区域设置}.yaml")
    读取和输出(清单文件)
if (清单类型 == "version"):
    清单文件 = os.path.join(清单目录, f"{软件包标识符}.yaml")
    读取和输出(清单文件)
