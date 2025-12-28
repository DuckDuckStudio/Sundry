import os
import json
import jsonschema
from typing import Any
from colorama import Fore
from function.maintain.config import (
    配置信息,
    转换配置值,
    读取配置项, 读取配置,
    获取当前配置版本, 获取配置schema
)
from catfood.functions.print import 消息头
from catfood.functions.files import open_file
from pygments import highlight # type: ignore
from pygments.lexers import JsonLexer # type: ignore
from pygments.formatters import TerminalFormatter
from catfood.exceptions.operation import OperationFailed

def 获取用户输入(配置项: str) -> str | bool:
    提示消息映射: dict[str, str] = {
        # paths.*
        "paths.winget-pkgs": f"{消息头.问题} 您的本地 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库在哪里: ",
        "paths.winget-tools": f"{消息头.问题} 您的本地 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库在哪里: ",
        # repos.*
        "repos.winget-pkgs": f"{消息头.问题} 您的远程 winget-{Fore.YELLOW}pkgs{Fore.RESET} 仓库是什么 (owner/winget-pkgs): ",
        "repos.winget-tools": f"{消息头.问题} 您的远程 winget-{Fore.YELLOW}tools{Fore.RESET} 仓库是什么 (owner/winget-tools): ",
        # git.*
        "git.signature": f"{消息头.问题} 是否要为 Git 提交签名? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        # github.pr.*
        "github.pr.maintainer_can_modify": f"{消息头.问题} 是否允许维护者修改您的 PR 内容? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "github.pr.mention_self_when_reviewer": f"{消息头.问题} 创建 PR 时，如果自己在 Auth.csv 中作为包修改的审查者时，是否在 PR 中请求自己审查? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        # github.token
        "github.token": f"{消息头.问题} 我该从哪里读取 GitHub Token? [{Fore.GREEN}glm(默认){Fore.RESET}, 环境变量 GITHUB_TOKEN (env), komac]: ",
        # tools.autoremove.*
        "tools.autoremove.open_in_browser": f"{消息头.问题} 在自动移除 (autoremove) 时，是否要在浏览器中打开清单中的安装程序链接 (InstallerUrl) 以供检查? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        # tools.prune.*
        "tools.prune.remote.prune_merged_branches": f"{消息头.问题} prune 时清理远程中{Fore.YELLOW}已合并{Fore.RESET}的 PR 的分支? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        "tools.prune.remote.prune_closed_branches": f"{消息头.问题} prune 时清理远程中{Fore.YELLOW}已关闭{Fore.RESET}的 PR 的分支? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        # tools.verify.*
        "tools.verify.show_warning_on_non-clean_windows": f"{消息头.问题} 在非干净的 Windows 上验证时显示警告? (默认为{Fore.YELLOW}否{Fore.RESET}): ",
        # i18n.*
        "i18n.lang": f"{消息头.问题} 你希望 Sundry 使用哪种语言运行? [{Fore.GREEN}zh-CN(默认){Fore.RESET}, en-US]: ",
        # cache.*
        "cache.validate.schema": f"{消息头.问题} 在 sundry validate 时是否缓存下载的清单架构 (schema)? (默认为{Fore.GREEN}是{Fore.RESET}): "
    }

    if 配置项 in 提示消息映射:
        提示消息 = 提示消息映射[配置项]
    else:
        提示消息 = f"{消息头.问题} 请输入 {配置项} 的值: "

    # 给自己的兜底
    if not 提示消息.endswith(" "):
        if 读取配置("debug", 静默=True):
            print(f"{消息头.内部警告} 配置项 {Fore.BLUE}{配置项}{Fore.RESET} 的提示消息未以空格结尾")
        提示消息 += " "

    while True:
        配置值 = input(提示消息).strip()
        try:
            return 转换配置值(配置项, 配置值)
        except OperationFailed as e:
            print(f"{消息头.错误} 无法转换配置值: {Fore.RED}{e}{Fore.RESET}")

def 初始化配置文件() -> int:
    if not os.path.exists(配置信息.所在位置) or (input(f"{消息头.警告} 已经存在了一份配置文件，要覆盖它吗? (默认为{Fore.GREEN}是{Fore.RESET}): ").lower() not in ["n", "no", "不要"]):
        默认配置: dict[str, Any] = 配置信息.默认配置

        # 递归函数用于获取嵌套配置输入
        def 递归获取输入(配置字典: dict[str, Any], 当前路径: str="") -> None:
            for k, v in 配置字典.items():
                新路径: str = 当前路径 + "." + k if 当前路径 else k
                v: dict[str, Any] | str | bool
                if isinstance(v, dict):
                    递归获取输入(v, 新路径)
                else:
                    配置字典[k] = 获取用户输入(新路径)

        for 键 in ("paths", "repos"):
            # 必须要用户给的配置项
            递归获取输入(默认配置[键], 键)

        if input(f"{消息头.可选问题} 继续设置其他配置项? (默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
            for 键 in list(默认配置.keys()):
                if 键 in (
                    # NOTE: 这里只能跳过顶级键，如 debug, version 等
                    "$schema", "version", "debug", # 不需要询问用户，直接用默认值
                    "paths", "repos", "cache", # 别的地方问过了
                    # 暂未实现
                    "i18n"
                ):
                    continue
                递归获取输入(默认配置[键], 键)

            if input(f"{消息头.问题} 是否修改缓存配置? (默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
                递归获取输入(默认配置["cache"], "cache")

        if not os.path.exists(os.path.dirname(配置信息.所在位置)):
            os.makedirs(os.path.dirname(配置信息.所在位置), exist_ok=True)

        with open(配置信息.所在位置, "w", encoding="utf-8") as f:
            json.dump(默认配置, f, indent=4, ensure_ascii=False)

        print(f"{消息头.成功} 成功初始化配置文件")
        return 0
    else:
        print(f"\n{消息头.错误} 操作取消")
        return 1

def 展示配置文件() -> int:
    if os.path.exists(配置信息.所在位置):
        try:
            print(f"{消息头.提示} 前往 https://github.com/DuckDuckStudio/Sundry/tree/main/docs/config 了解配置项的含义")
            with open(配置信息.所在位置, "r", encoding="utf-8") as f:
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

def 修改配置项(配置项: str, 值: str) -> int:
    if os.path.exists(配置信息.所在位置):
        try:
            配置值 = 转换配置值(配置项, 值)

            with open(配置信息.所在位置, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            # 解析嵌套键路径
            键路径列表 = 配置项.split(".")
            当前字典 = 配置数据
            # NOTE 我对这里的操作不太理解，这似乎是同一个引用?
            # NOTE 反正现在这里这样写是可以的，改当前字典会影响配置数据。
            for 键 in 键路径列表[:-1]:
                当前字典 = 当前字典[键]
            最后键 = 键路径列表[-1]

            当前字典[最后键] = 配置值

            with open(配置信息.所在位置, "w", encoding="utf-8") as f:
                json.dump(配置数据, f, indent=4, ensure_ascii=False)
            
            print(f"{消息头.成功} 成功更新 {Fore.BLUE}{配置项}{Fore.RESET} 为 {Fore.BLUE}{配置值}{Fore.RESET}")
            return 0
        except json.decoder.JSONDecodeError as e:
            print(f"{消息头.错误} 读取配置文件失败，配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
            print(f"{消息头.提示} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
            return 1
        except Exception as e:
            print(f"{消息头.错误} 更新配置失败: {Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{消息头.错误} 配置文件不存在")
        print(f"{消息头.提示} 运行 sundry config init 来初始化配置文件")
        return 1
    
def 更新配置文件() -> int:
    """
    尝试将旧的配置文件更新至最新版本的格式，旧配置缺失的键的值使用默认值。
    """

    if not os.path.exists(配置信息.所在位置):
        print(f"{消息头.错误} 配置文件不存在")
        print(f"{消息头.提示} 运行 sundry config init 来初始化配置文件")
        return 1

    try:
        当前配置版本 = 获取当前配置版本()

        schema = 获取配置schema(当前配置版本)
        if schema:
            with open(配置信息.所在位置, "r") as f:
                jsonschema.validate(json.load(f), schema)
        else:
            print(f"{消息头.警告} 未能获取到当前配置版本的 schema，跳过验证")
    except Exception as e:
        print(f"{消息头.错误} 当前的配置文件似乎无效: {Fore.RED}{e}{Fore.RESET}")
        print(f"{消息头.提示} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
        return 1

    if 当前配置版本 < float(配置信息.最新版本):
        print(f"{消息头.信息} 看起来当前的配置文件需要更新，正在尝试自动更新...")
    else:
        print(f"{消息头.消息} 看起来当前的配置文件已经是最新的了")
        return 0

    try:
        新配置数据 = 配置信息.默认配置

        def 递归获取配置值(配置字典: dict[str, Any], 当前路径: str="") -> None:
            for 键, 值 in 配置字典.items():
                新路径: str = 当前路径 + "." + 键 if 当前路径 else 键
                值: dict[str, Any] | str | bool
                if isinstance(值, dict):
                    递归获取配置值(值, 新路径)
                else:
                    if not any(新路径.startswith(跳过键) for 跳过键 in {
                        "$schema", "version", # 不需要从旧配置同步，直接用默认值
                    }):
                        配置值 = 读取配置项(新路径, 静默=True)
                        if (配置值 is None):
                            if (新路径 in 配置信息.必填项):
                                from tools.maintain.config import 获取用户输入
                                配置字典[键] = 获取用户输入(新路径)
                        else:
                            配置字典[键] = 配置值

        递归获取配置值(新配置数据)

        with open(配置信息.所在位置, "w", encoding="utf-8") as f:
            json.dump(新配置数据, f, indent=4, ensure_ascii=False)

        print(f"{消息头.成功} 成功更新配置文件 {Fore.RED}{当前配置版本}{Fore.RESET} -> {Fore.GREEN}{配置信息.最新版本}{Fore.RESET}")
        return 0
    except json.decoder.JSONDecodeError as e:
        print(f"{消息头.错误} 更新配置文件失败，现有配置文件不是有效的 json 字段:\n{Fore.RED}{e}{Fore.RESET}")
        print(f"{消息头.提示} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
        return 1
    except Exception as e:
        print(f"{消息头.错误} 更新配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
        print(f"{消息头.提示} 请{Fore.YELLOW}考虑{Fore.RESET}运行 sundry config init 来覆盖现有的配置文件")
        return 1

def main(args: list[str]) -> int:
    try:
        if not args:
            print(f"{消息头.错误} 缺少参数")
            print(f"{消息头.提示} 运行 sundry --help 来获取命令帮助")
            return 1

        if args[0] == "init":
            return 初始化配置文件()
        elif args[0] == "show":
            return 展示配置文件()
        elif args[0] in ["update", "更新", "upgrade"]:
            return 更新配置文件()
        elif args[0] in ["编辑", "edit", "打开", "open"]:
            print(f"{消息头.信息} 配置文件 config.json 位于 {配置信息.所在位置}")
            print(f"{消息头.信息} 尝试打开配置文件 config.json ...")
            return open_file(配置信息.所在位置)
        elif len(args) == 2:
            return 修改配置项(args[0], args[1])
        else:
            print(f"{消息头.错误} 无效的操作: {args[0]}")
            print(f"{消息头.提示} 运行 sundry --help 来获取命令帮助")
            return 1
    except KeyboardInterrupt:
        print(f"\n{消息头.错误} 操作取消")
        return 1
