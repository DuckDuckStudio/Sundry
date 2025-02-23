import os
import sys
import json
import requests
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer
from colorama import init, Fore

init(autoreset=True)

# 配置文件路径
配置文件 = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "config.json")

# 初始化配置文件
def 初始化配置文件():
    if not os.path.exists(配置文件) or (input(f"{Fore.YELLOW}⚠{Fore.RESET} 已经存在了一份配置文件，要覆盖它吗[Y/N]: ").lower() in ["y", "yes", "要", "覆盖", "force"]):
        默认配置 = '''{
    "version": "1.0.2",
    "winget-pkgs": "",
    "winget-tools": "",
    "fork": "",
    "signature": false
}
'''
        默认配置 = json.loads(默认配置)
        while True:
            默认配置["winget-pkgs"] = input(f"{Fore.BLUE}?{Fore.RESET} 您的本地 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库在哪里: ")
            # 清除可能的多余反斜杠 (\\ 或 \ -> /)
            默认配置["winget-pkgs"] = 默认配置["winget-pkgs"].replace("\\\\", "/").replace("\\", "/")
            if os.path.exists(默认配置["winget-pkgs"]):
                break
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 指定的路径不存在")
        while True:
            默认配置["winget-tools"] = input(f"{Fore.BLUE}?{Fore.RESET} 您的本地 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库在哪里: ")
            # 清除可能的多余反斜杠 (\\ 或 \ -> /)
            默认配置["winget-tools"] = 默认配置["winget-tools"].replace("\\\\", "/").replace("\\", "/")
            if os.path.exists(默认配置["winget-tools"]):
                break
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 指定的路径不存在")
        # 初始化 fork 配置项的逻辑
        # 支持这几种格式
        # owner/repo
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        while True:
            fork = input(f"{Fore.BLUE}?{Fore.RESET} 您的 winget-pkgs 仓库的 fork 仓库是什么: ")
            # 统一为 owner/repo 格式
            if fork.startswith("https://github.com/"):
                fork = fork.replace("https://github.com/", "").replace(".git", "")
            parts = fork.split("/")
            if len(parts) == 2:
                owner, repo = parts
                # GitHub API url
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                try:
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        默认配置["fork"] = fork
                        break
                    elif response.status_code == 404:
                        print(f"{Fore.RED}✕{Fore.RESET} 指定的 fork 仓库不存在或没有权限访问")
                    else:
                        print(f"{Fore.RED}✕{Fore.RESET} 检查 fork 仓库失败，状态码: {Fore.YELLOW}{response.status_code}{Fore.RESET}")
                except Exception as e:
                    print(f"{Fore.RED}✕{Fore.RESET} 检查 fork 仓库失败:\n{Fore.RED}{e}{Fore.RESET}")
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 请输入正确的 fork 仓库格式，例如: owner/repo")
        signature = input(f"{Fore.BLUE}?{Fore.RESET} 是否要为 Git 提交签名: (默认为{Fore.YELLOW}否{Fore.RESET}): ")
        if signature.lower() in ["y", "yes", "要", "是", "true"]:
            默认配置["signature"] = True
        else:
            默认配置["signature"] = False
        with open(配置文件, "w", encoding="utf-8") as f:
            json.dump(默认配置, f, indent=4, ensure_ascii=False)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功初始化配置文件")

# 展示现有配置
def 展示配置文件():
    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            print(highlight(json.dumps(配置数据, indent=4, ensure_ascii=False), JsonLexer(), TerminalFormatter()))
        except json.decoder.JSONDecodeError as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")

# 修改配置文件中的某一项
def 修改配置项(条目, 值):
    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            配置数据[条目] = 值
            
            with open(配置文件, "w", encoding="utf-8") as f:
                json.dump(配置数据, f, indent=4, ensure_ascii=False)
            
            print(f"{Fore.GREEN}✓{Fore.RESET} 成功更新 {条目} 为 {值}")
        except json.decoder.JSONDecodeError as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 更新条目失败:\n{Fore.RED}{e}{Fore.RESET}")
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")

# 主程序
def main():
    try:
        if len(sys.argv) < 2:
            print(f"{Fore.RED}✕{Fore.RESET} 缺少参数")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry --help 来获取命令帮助")
            return 2

        if sys.argv[1] == "init":
            初始化配置文件()
        elif sys.argv[1] == "show":
            展示配置文件()
        elif len(sys.argv) == 3:
            条目 = sys.argv[1]
            值 = sys.argv[2]
            修改配置项(条目, 值)
        else:
            print(f"{Fore.RED}✕{Fore.RESET} 无效的操作: {sys.argv[1]}")
            print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry --help 来获取命令帮助")
            return 2
        return 0
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}✕{Fore.RESET} 操作取消")
        return 2

if __name__ == "__main__":
    sys.exit(main())
