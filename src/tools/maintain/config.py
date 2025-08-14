import os
import json
import requests
from colorama import init, Fore
from pygments import highlight # type: ignore
from pygments.lexers import JsonLexer # type: ignore
from pygments.formatters import TerminalFormatter

# 获取用户输入
def 获取用户输入(键: str):
    # 定义一个嵌套字典，按分类组织提示消息
    提示消息 = {
        "路径": {
            "winget-pkgs": f"{Fore.BLUE}?{Fore.RESET} 您的本地 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库在哪里: ",
            "winget-tools": f"{Fore.BLUE}?{Fore.RESET} 您的本地 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库在哪里: "
        },
        "仓库": {
            "pkgs-repo": f"{Fore.BLUE}?{Fore.RESET} 您的远程 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库是什么: ",
            "tools-repo": f"{Fore.BLUE}?{Fore.RESET} 您的远程 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库是什么: "
        },
        "签名": {
            "signature": f"{Fore.BLUE}?{Fore.RESET} 是否要为 Git 提交签名？(默认为{Fore.YELLOW}否{Fore.RESET}): "
        },
        "i18n": {
            "lang": f"{Fore.BLUE}?{Fore.RESET} 你希望 Sundry 使用哪种语言运行？[{Fore.GREEN}zh-CN(默认){Fore.RESET}, en-US]: "
        }
    }

    # 路径输入
    if 键 in 提示消息["路径"]:
        while True:
            路径 = os.path.abspath(os.path.normpath(input(提示消息["路径"][键]).replace("~", os.path.expanduser("~"))))
            if os.path.exists(路径):
                return 路径
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 指定的路径不存在")
    # 仓库输入
    elif 键 in 提示消息["仓库"]:
        # 支持这几种格式
        # owner/repo
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        while True:
            fork = input(提示消息["仓库"][键])
            if fork.startswith("https://github.com/"):
                fork = fork.replace("https://github.com/", "").replace(".git", "")
            parts = fork.split("/")
            if len(parts) == 2:
                owner, repo = parts
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                try:
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        return fork
                    elif response.status_code == 404:
                        print(f"{Fore.RED}✕{Fore.RESET} 指定的仓库不存在或没有权限访问")
                    else:
                        print(f"{Fore.RED}✕{Fore.RESET} 检查仓库失败，状态码: {Fore.YELLOW}{response.status_code}{Fore.RESET}")
                except Exception as e:
                    print(f"{Fore.RED}✕{Fore.RESET} 检查仓库失败:\n{Fore.RED}{e}{Fore.RESET}")
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 请输入正确的仓库格式，例如: owner/repo")
    # 签名输入
    elif 键 in 提示消息["签名"]:
        if input(提示消息["签名"][键]).lower() in ["y", "yes", "要", "是", "true"]:
            return "yes"
        else:
            return "no"
    # Sundry-Locale i18n 分支兼容
    # i18n输入
    elif 键 in 提示消息["i18n"]:
        while True:
            答案 = input(提示消息["i18n"][键]).lower()
            if 答案 not in ["", "zh-cn", "en-us"]:
                print(f"{Fore.RED}✕{Fore.RESET} 不支持的语言，请在 [] 中的语言中选择一种")
            else:
                语言映射 = {
                    "": "zh-CN",
                    "zh-cn": "zh-CN",
                    "en-us": "en-US",
                }
                return 语言映射.get(答案, "zh-CN")
    else:
        return input(f"{Fore.BLUE}?{Fore.RESET} 请输入 {键} 的值: ")

# 初始化配置文件
def 初始化配置文件(配置文件: str):
    if not os.path.exists(配置文件) or (input(f"{Fore.YELLOW}⚠{Fore.RESET} 已经存在了一份配置文件，要覆盖它吗[Y/N]: ").lower() in ["y", "yes", "要", "覆盖", "force"]):
        默认配置 = '''{
    "version": "develop",
    "winget-pkgs": "",
    "winget-tools": "",
    "pkgs-repo": "",
    "tools-repo": "",
    "signature": ""
}
'''
        默认配置 = json.loads(默认配置)

        for 键 in 默认配置.keys():
            if 键 == "version":
                continue
            默认配置[键] = 获取用户输入(键)

        if input(f"{Fore.BLUE}? (可选){Fore.RESET} 是否要让配置文件兼容 Sundry-old 和 Sundry-Locale (i18n 分支)？(默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
            # 往默认配置中添加 key "fork" 值同 "pkgs-repo"
            # Sundry-old 兼容
            默认配置["fork"] = 默认配置["pkgs-repo"]
            # 往默认配置中添加 key "lang" 值 问用户
            # Sundry-Locale i18n 分支兼容
            默认配置["lang"] = 获取用户输入("lang")

        # =========================================

        if not os.path.exists(os.path.dirname(配置文件)):
            os.makedirs(os.path.dirname(配置文件), exist_ok=True)

        with open(配置文件, "w", encoding="utf-8") as f:
            json.dump(默认配置, f, indent=4, ensure_ascii=False)

        print(f"{Fore.GREEN}✓{Fore.RESET} 成功初始化配置文件")
        return 0
    else:
        print(f"\n{Fore.RED}✕{Fore.RESET} 操作取消")
        return 1

# 展示现有配置
def 展示配置文件(配置文件: str):
    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            print(highlight(json.dumps(配置数据, indent=4, ensure_ascii=False), JsonLexer(), TerminalFormatter())) # pyright: ignore[reportUnknownArgumentType]
            return 0
        except json.decoder.JSONDecodeError as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
            return 1
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        return 1

# 修改配置文件中的某一项
def 修改配置项(条目: str, 值: str, 配置文件: str):
    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            配置数据[条目] = 值
            
            with open(配置文件, "w", encoding="utf-8") as f:
                json.dump(配置数据, f, indent=4, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✓{Fore.RESET} 成功更新 {Fore.BLUE}{条目}{Fore.RESET} 为 {Fore.BLUE}{值}{Fore.RESET}")
            return 0
        except json.decoder.JSONDecodeError as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
            return 1
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 更新条目失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        return 1

# 主程序
def main(args: list[str]):
    init(autoreset=True)

    # 配置文件路径
    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

    try:
        if not args:
            print(f"{Fore.RED}✕{Fore.RESET} 缺少参数")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry --help 来获取命令帮助")
            return 1

        if args[0] == "init":
            return 初始化配置文件(配置文件)
        elif args[0] == "show":
            return 展示配置文件(配置文件)
        elif len(args) == 2:
            条目 = args[0]
            值 = args[1]
            return 修改配置项(条目, 值, 配置文件)
        else:
            print(f"{Fore.RED}✕{Fore.RESET} 无效的操作: {args[0]}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry --help 来获取命令帮助")
            return 1
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}✕{Fore.RESET} 操作取消")
        return 1
