import os
import json
from typing import Any
from colorama import init, Fore
from function.print.print import 消息头
from function.maintain.config import 验证配置
from pygments import highlight # type: ignore
from pygments.lexers import JsonLexer # type: ignore
from pygments.formatters import TerminalFormatter

# 获取用户输入
def 获取用户输入(键路径: str) -> str | bool:
    提示消息映射: dict[str, str] = {
        "paths.winget-pkgs": f"{消息头.问题} 您的本地 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库在哪里: ",
        "paths.winget-tools": f"{消息头.问题} 您的本地 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库在哪里: ",
        "repos.winget-pkgs": f"{消息头.问题} 您的远程 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库是什么 (owner/winget-pkgs): ",
        "repos.winget-tools": f"{消息头.问题} 您的远程 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库是什么 (owner/winget-tools): ",
        "git.signature": f"{消息头.问题} 是否要为 Git 提交签名? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "github.pr.maintainer_can_modify": f"{消息头.问题} 是否允许维护者修改您的 PR 内容? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "tools.verify.check_url": f"{消息头.问题} verify 时验证清单中的 URL 是否有效? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "tools.verify.show_warning_on_non-clean_windows": f"{消息头.问题} 在非干净的 Windows 上验证时显示警告? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "tools.prune.remote.prune_merged_branches": f"{消息头.问题} prune 时清理远程中{Fore.YELLOW}已合并{Fore.RESET}的 PR 的分支? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "tools.prune.remote.prune_closed_branches": f"{消息头.问题} prune 时清理远程中{Fore.YELLOW}已关闭{Fore.RESET}的 PR 的分支? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "i18n.lang": f"{消息头.问题} 你希望 Sundry 使用哪种语言运行? [{Fore.GREEN}zh-CN(默认){Fore.RESET}, en-US]: "
    }

    if 键路径 in 提示消息映射:
        提示消息 = 提示消息映射[键路径]
    else:
        提示消息 = f"{消息头.问题} 请输入 {键路径} 的值: "

    while True:
        # 这个 while 用 return 而不是 break

        值 = input(提示消息).strip()

        if 键路径.startswith("paths."):
            路径 = os.path.abspath(os.path.normpath(值.replace("~", os.path.expanduser("~"))))
            验证结果 = 验证配置(键路径, 路径)
            if not 验证结果:
                return 路径
            else:
                print(f"{消息头.错误} {验证结果}")
        elif 键路径.startswith("repos."):
            if 值.startswith("https://github.com/"):
                值 = 值.replace("https://github.com/", "").replace(".git", "")
            验证结果 = 验证配置(键路径, 值)
            if not 验证结果:
                return 值
            else:
                print(f"{消息头.错误} {验证结果}")
        # 布尔值的配置项
        elif 键路径 in [
            "git.signature", "github.pr.maintainer_can_modify", "tools.verify.check_url",
            "tools.verify.show_warning_on_non-clean_windows",
            "tools.prune.remote.prune_merged_branches", "tools.prune.remote.prune_closed_branches"
        ]:
            if 值.lower() in ["y", "yes", "要", "是", "true"]:
                return True
            else:
                return False
        elif 键路径 == "i18n.lang":
            if not 值:
                值 = "zh-cn"
            值 = 值.lower()
            验证结果 = 验证配置(键路径, 值)
            if not 验证结果:
                return 值
            else:
                print(f"{消息头.错误} {验证结果}")
        else:
            return input(提示消息)

# 初始化配置文件
def 初始化配置文件(配置文件: str):
    if not os.path.exists(配置文件) or (input(f"{消息头.警告} 已经存在了一份配置文件，要覆盖它吗[{Fore.GREEN}Y{Fore.RESET}/n]: ").lower() not in ["n", "no", "不要"]):
        默认配置: dict[str, str | dict[str, str | bool | dict[str, bool | dict[str, bool]]]] = json.loads("""{
    "$schema": "https://duckduckstudio.github.io/yazicbs.github.io/Tools/Sundry/config/schema/1.1.json",
    "version": "1.1",
    "paths": {
        "winget-pkgs": "",
        "winget-tools": ""
    },
    "repos": {
        "winget-pkgs": "",
        "winget-tools": ""
    },
    "git": {
        "signature": false
    },
    "github": {
        "pr": {
            "maintainer_can_modify": false
        }
    },
    "tools": {
        "verify": {
            "check_url": false,
            "show_warning_on_non-clean_windows": false
        },
        "prune": {
            "remote": {
                "prune_merged_branches": false,
                "prune_closed_branches": false
            }
        }
    },
    "i18n": {
        "lang": "zh-cn"
    }
}
""")

        # 递归函数用于获取嵌套配置输入
        # NOTE 我知道配置字典是 dict[str, Any]，但不用 Any 的话 isinstance() 后面的值过不了类型检查
        def 递归获取输入(配置字典: Any, 当前路径: str="") -> None:
            for 键, 值 in 配置字典.items():
                新路径 = 当前路径 + "." + 键 if 当前路径 else 键
                if isinstance(值, dict):
                    递归获取输入(值, 新路径)
                else:
                    配置字典[键] = 获取用户输入(新路径)

        for 键 in ["paths", "repos"]:
            # 必须要用户给的配置项
            递归获取输入(默认配置[键], 键)

        if input(f"{消息头.可选问题} 继续设置其他配置项? [y/{Fore.YELLOW}N{Fore.RESET}] : ").lower() in ["y", "yes", "要", "是", "true"]:
            for 键 in list(默认配置.keys()):
                if 键 in (["version", "$schema"] + ["paths", "repos"]):
                    continue
                递归获取输入(默认配置[键], 键)

        if not os.path.exists(os.path.dirname(配置文件)):
            os.makedirs(os.path.dirname(配置文件), exist_ok=True)

        with open(配置文件, "w", encoding="utf-8") as f:
            json.dump(默认配置, f, indent=4, ensure_ascii=False)

        print(f"{消息头.成功} 成功初始化配置文件")
        return 0
    else:
        print(f"\n{消息头.错误} 操作取消")
        return 1

# 展示现有配置
def 展示配置文件(配置文件: str):
    if os.path.exists(配置文件):
        try:
            print(f"{消息头.提示} 前往 https://github.com/DuckDuckStudio/Sundry/tree/main/docs/config/1.1 了解配置项的含义")
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            print(highlight(json.dumps(配置数据, indent=4, ensure_ascii=False), JsonLexer(), TerminalFormatter())) # pyright: ignore[reportUnknownArgumentType]
            return 0
        except json.decoder.JSONDecodeError as e:
            print(f"{消息头.错误} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{消息头.提示} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
            return 1
        except Exception as e:
            print(f"{消息头.错误} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{消息头.错误} 配置文件不存在")
        print(f"{消息头.提示} 运行 sundry config init 来初始化配置文件")
        return 1

# 修改配置文件中的某一项
def 修改配置项(条目: str, 值: str, 配置文件: str):
    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            # 解析嵌套键路径
            键路径列表 = 条目.split(".")
            当前字典 = 配置数据
            # NOTE 我对这里的操作不太理解，这似乎是同一个引用?
            # NOTE 反正现在这里这样写是可以的，改当前字典会影响配置数据。
            for 键 in 键路径列表[:-1]:
                当前字典 = 当前字典[键]
            最后键 = 键路径列表[-1]

            # 根据键路径类型转换值
            布尔键路径列表 = [
                "git.signature", "github.pr.maintainer_can_modify", "tools.verify.check_url",
                "tools.verify.show_warning_on_non-clean_windows",
                "tools.prune.remote.prune_merged_branches", "tools.prune.remote.prune_closed_branches"
            ]
            if 条目 in 布尔键路径列表:
                if 值.lower() in ["true", "yes", "y", "是", "要"]:
                    配置值 = True
                else:
                    配置值 = False
            elif 条目 == "i18n.lang":
                if 值.lower() not in ["zh-cn", "en-us"]:
                    print(f"{消息头.错误} 不支持的语言")
                    return 1
                配置值 = 值
            else:
                配置值 = 值

            当前字典[最后键] = 配置值

            with open(配置文件, "w", encoding="utf-8") as f:
                json.dump(配置数据, f, indent=4, ensure_ascii=False)
            
            print(f"{消息头.成功} 成功更新 {Fore.BLUE}{条目}{Fore.RESET} 为 {Fore.BLUE}{值}{Fore.RESET}")
            return 0
        except json.decoder.JSONDecodeError as e:
            print(f"{消息头.错误} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{消息头.提示} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
            return 1
        except Exception as e:
            print(f"{消息头.错误} 更新条目失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{消息头.错误} 配置文件不存在")
        print(f"{消息头.提示} 运行 sundry config init 来初始化配置文件")
        return 1

# 主程序
def main(args: list[str]):
    init(autoreset=True)

    # 配置文件路径
    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

    try:
        if not args:
            print(f"{消息头.错误} 缺少参数")
            print(f"{消息头.提示} 运行 sundry --help 来获取命令帮助")
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
            print(f"{消息头.错误} 无效的操作: {args[0]}")
            print(f"{消息头.提示} 运行 sundry --help 来获取命令帮助")
            return 1
    except KeyboardInterrupt:
        print(f"\n{消息头.错误} 操作取消")
        return 1
