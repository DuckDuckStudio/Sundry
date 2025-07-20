import re
import os
import csv
import json
import yaml
import ctypes
import winreg
import base64
import shutil
import requests
import subprocess
import exception.request
from colorama import Fore, init
from function.github.token import read_token
from pygments import highlight # type: ignore
from pygments.lexers import YamlLexer # type: ignore
from pygments.formatters import TerminalFormatter

def main(args: list[str]) -> int:
    init(autoreset=True)

    # 初始化
    软件包标识符: str = ""
    软件包版本: str = ""
    PR编号: str = ""
    github_token = 0

    # 解析参数
    if (len(args) == 2): # 符合参数个数要求
        软件包标识符 = args[0]
        软件包版本 = args[1]
    elif (len(args) == 1):
        匹配 = re.match("https://github.com/microsoft/winget-pkgs/pull/(\\d+)", args[0])
        if 匹配:
            PR编号 = 匹配.group(1)
            github_token = read_token()
            # 这里不做用户询问，测试时放 Token 确实有点...
            # 但为了速率，这里有读到 Token 就带 Token，没有就没有
            print(f"{Fore.YELLOW}⚠{Fore.RESET} 没有读到 Token，请求时不带 Token")
        else:
            print(f"{Fore.RED}✕{Fore.RESET} 无效的 PR 链接")
            return 1
    else: # 不符合
        print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")
    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            if 配置数据["winget-pkgs"]:
                winget_pkgs目录 = os.path.normpath(配置数据["winget-pkgs"])
                if (not os.path.exists(winget_pkgs目录)):
                    print(f"{Fore.RED}✕{Fore.RESET} 配置文件中的目录 {Fore.BLUE}{winget_pkgs目录}{Fore.RESET} 不存在")
                    print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                    return 1
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"winget-pkgs\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                return 1
            # ========================================
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        return 1
    
    # ============================================================

    if PR编号:
        清单目录 = os.path.join(os.environ["TEMP"], "Sundry", "Verify", "PRManifest", PR编号)
        if 获取PR清单(PR编号, github_token, 清单目录):
            return 1
    else:
        清单目录 = os.path.join(winget_pkgs目录, "manifests", 软件包标识符[0].lower(), *软件包标识符.split("."), 软件包版本)

        # 如果该软件包在 Auth.csv 中，则警告用户
        with open(os.path.join(winget_pkgs目录, "Tools", "Auth.csv"), mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            # 遍历 CSV 文件中的每一行
            found = False # 标记是否找到了包标识符
            for row in csv_reader:
                if row["PackageIdentifier"] == 软件包标识符:
                    found = row["Account"]
                    print(f"{Fore.YELLOW}⚠ 看起来此软件包在 Auth.csv 中被要求所有者({found})审查{Fore.RESET}")
                    break # 找到后退出循环

    # 如果有任何一步失败了，就 return 1
    if 验证清单(清单目录):
        return 1
    elif 软件包标识符 in ["DuckStudio.Sundry"]:
        print(f"{Fore.YELLOW}⚠{Fore.RESET} 此软件包是 Sundry verify 的依赖项，再次安装它将导致冲突，故取消后续验证。")
        return 0
    安装前ARP = 读取ARP字段()
    if 测试安装与卸载(清单目录, "安装"):
        return 1
    else:
        安装后ARP = 读取ARP字段()
        # 对比 ARP 字段，并找出具体不同
        不同条目: list[dict[str, str | int]] = []
        for 条目 in 安装后ARP:
            if 条目 not in 安装前ARP:
                不同条目.append(条目)
        if 不同条目:
            print(f"{Fore.BLUE}[!]{Fore.RESET} ARP 条目变更:")
            for 条目 in 不同条目:
                print(highlight(yaml.dump(转换ARP条目为YAML(条目), sort_keys=False, allow_unicode=True, default_flow_style=False), YamlLexer(), TerminalFormatter())) # type: ignore - 依赖问题
        else:
            print(f"{Fore.YELLOW}⚠{Fore.RESET} ARP 条目没有变化")

        try:
            input("按 ENTER 继续测试卸载，按 CTRL + C 结束...")
            if 测试安装与卸载(清单目录, "卸载"):
                return 1
            raise KeyboardInterrupt # 和下面 except 相同的处理
        except KeyboardInterrupt:
            if PR编号:
                print(f"{Fore.GREEN}✓{Fore.RESET} 成功验证 #{PR编号} 的清单")
            else:
                print(f"{Fore.GREEN}✓{Fore.RESET} 成功验证 {软件包标识符} {软件包版本} 的本地清单")
            return 0

def 请求GitHubAPI(apiUrl: str, github_token: str | int):
    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    if not github_token:
        # 移除 Authorization 头
        请求头.pop("Authorization", None)
    try:
        响应 = requests.get(apiUrl, headers=请求头)
        
        if 响应.status_code == 404:
            raise exception.request.RequestException("PR 不存在或对应分支已被删除")
        elif 响应.status_code >= 400:
            raise exception.request.RequestException(响应)
        else:
            return 响应.json()
    except exception.request.RequestException as e:
        print(f"{Fore.RED}✕{Fore.RESET} 请求 GitHub API 失败:\n{e}")
        return

def 获取PR清单(PR编号: str, github_token: str | int, 清单目录: str) -> int:
    print(f"尝试获取 PR #{PR编号} 中的清单...")
    清单文件路径 = 获取PR清单文件路径(PR编号, github_token)
    if not 清单文件路径:
        return 1
    结果 = 获取PR仓库和分支(PR编号, github_token)
    if not 结果:
        return 1
    fork仓库, fork分支 = 结果

    if os.path.exists(清单目录):
        if input(f"{Fore.BLUE}?{Fore.RESET} 临时清单目录下{Fore.YELLOW}已存在同名清单目录{Fore.RESET} {Fore.BLUE}{清单目录}{Fore.RESET}，我应该移除它吗? [Y/n]: ").lower() not in ["y", "yes", "是", ""]:
            print(f"{Fore.RED}✕{Fore.RESET} 临时清单目录下存在同名清单目录")
            return 1
        else:
            try:
                # 移除它
                shutil.rmtree(清单目录)
            except Exception as e:
                print(f"{Fore.RED}✕{Fore.RESET} 移除同名清单目录时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
                return 1
    os.makedirs(清单目录, exist_ok=True)

    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    if not github_token:
        # 移除 Authorization 头
        请求头.pop("Authorization", None)

    for 文件路径 in 清单文件路径:
        try:
            # 由于政府政策，在中国大陆不允许使用 raw.githubusercontent.com
            # 127.0.0.1 欢迎你 XD
            # raw_url = f"https://raw.githubusercontent.com/{fork仓库}/refs/heads/{fork分支}/{文件路径}"

            api = f"https://api.github.com/repos/{fork仓库}/contents/{文件路径}?ref={fork分支}" # NOTE: 这里不对 url 进行编码，因为软件包标识符不允许出现特殊字符/中文
            响应 = 请求GitHubAPI(api, github_token)
            if not 响应:
                raise exception.request.RequestException(f"响应为空: {响应}")

            清单内容 = base64.b64decode(响应["content"])

            with open(os.path.join(清单目录, os.path.basename(文件路径)), "wb") as 清单文件:
                清单文件.write(清单内容)
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 下载清单文件失败:\n{e}")
            return 1

    print(f"成功获取 PR #{PR编号} 中的清单")
    return 0

def 获取PR仓库和分支(PR编号: str, github_token: str | int) -> None | tuple[str, str]:
    api = f"https://api.github.com/repos/microsoft/winget-pkgs/pulls/{PR编号}"

    响应 = 请求GitHubAPI(api, github_token)
    if 响应:
        fork仓库 = 响应["head"]["repo"]["full_name"]
        fork分支 = 响应["head"]["ref"]
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功获取 PR HEAD 的仓库和分支")
        return fork仓库, fork分支
    else:
        return

def 获取PR清单文件路径(PR编号: str, github_token: str | int) -> None | list[str]:
    api = f"https://api.github.com/repos/microsoft/winget-pkgs/pulls/{PR编号}/files"
    非预期状态 = True # 如果文件状态全是移除或没有状态，则为非预期状态
    清单文件夹 = None
    清单文件路径: list[str] = []

    响应 = 请求GitHubAPI(api, github_token)
    if 响应:
        for 文件 in 响应:
            文件相对路径: str = 文件["filename"]
            # 文件是 .yaml 格式且在 manifests 目录下
            if 文件相对路径.endswith(".yaml") and 文件相对路径.startswith("manifests/"):
                清单文件路径.append(文件相对路径)
                if 清单文件夹 is None:
                    清单文件夹 = os.path.normpath(os.path.dirname(文件相对路径))
                elif 清单文件夹 != os.path.normpath(os.path.dirname(文件相对路径)):
                    print(f"{Fore.RED}✕{Fore.RESET} 此 PR 修改了多个文件夹下的文件")
                    return
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 非预期的清单类型: {Fore.BLUE}{文件相对路径}{Fore.RESET}")
                print(f"{Fore.YELLOW}Hint{Fore.RESET} 请确定 PR 是对清单的修改，并确定修改的文件都是 .yaml 格式")
                return
            if 文件["status"] != "removed":
                非预期状态 = False

        if 非预期状态:
            print(f"{Fore.RED}✕{Fore.RESET} 这是个纯移除或没有修改的 PR")
            return
        
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功获取清单文件相对路径")
        return 清单文件路径
    else:
        return

def 验证清单(清单目录: str) -> int:
    # 使用 winget validate 验证清单文件，并返回 winget 退出代码
    try:
        print("正在验证清单修改...")
        subprocess.run(["winget", "validate", "--manifest", 清单目录], check=True)
        # WinGet 会输出清单验证成功
        return 0
    except subprocess.CalledProcessError as e:
        return e.returncode

def 测试安装与卸载(清单目录: str, 操作: str) -> int:
    # 使用 winget install/uninstall --manifest 尝试安装与卸载清单中的程序，并返回 winget 退出代码

    if 操作 == "卸载":
        命令 = "uninstall"
    else:
        命令 = "install"

    # 运行 winget settings export 并获取 LocalManifestFiles 是否为 true
    # 输出示例
    # {"$schema":"https://aka.ms/winget-settings-export.schema.json","adminSettings":{"BypassCertificatePinningForMicrosoftStore":false,"InstallerHashOverride":false,"LocalArchiveMalwareScanOverride":false,"LocalManifestFiles":true,"ProxyCommandLineOptions":false},"userSettingsFile":"C:\\Users\\xxx\\AppData\\Local\\Packages\\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\\LocalState\\settings.json"}
    try:
        settings_output = subprocess.check_output(["winget", "settings", "export"], text=True)
        settings = json.loads(settings_output)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 获取 winget 设置失败: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 解析 winget 设置失败: {e}")
        return 1

    if not settings.get("adminSettings", {}).get("LocalManifestFiles", False): # 如果没有启用本地清单
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            # 启用本地清单需要管理员权限
            print(f"{Fore.RED}✕{Fore.RESET} 允许{操作}本地清单中的程序需要管理员权限")
            print(f"{Fore.YELLOW}Hint{Fore.RESET} 请在管理员权限的终端运行: winget settings --enable LocalManifestFiles")
            return 1
        else:
            try:
                临时启用 = True
                subprocess.run(["winget", "settings", "--enable", "LocalManifestFiles"], check=True)
                print(f"{Fore.BLUE}[!]{Fore.RESET} 临时启用 LocalManifestFiles")
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}✕{Fore.RESET} 启用 LocalManifestFiles 失败: {e}")
                return 1
    else:
        临时启用 = False

    # 尝试运行 WinGet 操作
    try:
        print(f"尝试{操作}软件包...")
        完整命令 = ["winget", 命令, "--manifest", 清单目录, "--accept-source-agreements"]
        if 命令 == "install":
            完整命令.append("--accept-package-agreements")
        subprocess.run(完整命令, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 尝试{操作}软件包失败: WinGet 返回 {e.returncode}")
        return 1

    try:
        if 临时启用:
            print(f"{Fore.BLUE}[!]{Fore.RESET} 还原 LocalManifestFiles 设置")
            subprocess.run(["winget", "settings", "--disable", "LocalManifestFiles"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 还原 LocalManifestFiles 设置失败: {e}")
        return 1
    
    return 0

def 读取ARP字段():
    # 机器范围 ARP: 计算机\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\<ProductCode>
    # 用户范围 ARP: 计算机\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall\<ProductCode>
    # 此函数皆在实现获取机器/用户范围的 ARP，并返回获取到的结果
    # 对应清单中的 AppsAndFeaturesEntries

    # 定义关心的字段列表
    关心的字段 = [
        "DisplayName", "DisplayVersion", "Publisher", "UninstallString", "HelpLink",
        "InstallLocation", "SystemComponent", "WindowsInstaller", "NoRemove", "NoModify",
        "InstallSource", "EstimatedSize", "URLInfoAbout", "Comments"
    ]

    def _读取注册表值(键: winreg.HKEYType, 值名: str):
        try:
            值, 注册类型 = winreg.QueryValueEx(键, 值名)
            if 注册类型 == winreg.REG_EXPAND_SZ:
                # 展开环境变量
                return os.path.expandvars(值)
            elif 注册类型 in (winreg.REG_SZ, winreg.REG_MULTI_SZ):
                return 值
            elif 注册类型 == winreg.REG_DWORD:
                return 值
            else:
                # 其他类型转换为字符串
                return str(值)
        except FileNotFoundError:
            return None

    def _读取注册表条目(hive: int, subkey: str, access: int=0):
        entries: list[dict[str, str | int]] = []
        try:
            with winreg.ConnectRegistry(None, hive) as reg:
                with winreg.OpenKey(reg, subkey, 0, winreg.KEY_READ | access) as key:
                    index = 0
                    while True:
                        try:
                            子键名称 = winreg.EnumKey(key, index)
                            index += 1
                            with winreg.OpenKey(key, 子键名称) as 子键句柄:
                                entry: dict[str, str | int] = {}
                                # 添加ProductCode（子键名称）
                                entry["ProductCode"] = 子键名称
                                # 读取所有关心的字段
                                for 字段 in 关心的字段:
                                    值 = _读取注册表值(子键句柄, 字段)
                                    if 值 is not None:
                                        entry[字段] = 值
                                # 添加范围标识
                                entry["Scope"] = "Machine" if hive == winreg.HKEY_LOCAL_MACHINE else "User"
                                entries.append(entry)
                        except PermissionError:
                            continue
                        except OSError as e:
                            if e.winerror == 259: # 没有更多项目
                                break
        except FileNotFoundError:
            pass
        return entries

    所有条目: list[dict[str, str | int]] = []
    
    # 读取机器范围 (64位和32位) - WOW
    所有条目.extend(_读取注册表条目(
        winreg.HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
        winreg.KEY_WOW64_64KEY
    ))
    
    所有条目.extend(_读取注册表条目(
        winreg.HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
        winreg.KEY_WOW64_32KEY
    ))
    
    # 读取用户范围
    所有条目.extend(_读取注册表条目(
        winreg.HKEY_CURRENT_USER,
        "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    ))
    
    return 所有条目

def 转换ARP条目为YAML(ARP条目: dict[str, str | int]):
    # 顶层字段
    YAML条目: dict[str, str | list[dict[str, str]]] = {}
    if "Scope" in ARP条目:
        YAML条目["Scope"] = str(ARP条目["Scope"])
    if "HelpLink" in ARP条目:
        YAML条目["PublisherSupportUrl"] = str(ARP条目["HelpLink"])
    
    # AppsAndFeaturesEntries
    程序与功能条目: dict[str, str] = {}
    for 字段 in ["DisplayName", "DisplayVersion", "Publisher", "ProductCode"]:
        if 字段 in ARP条目:
            程序与功能条目[字段] = str(ARP条目[字段])
    
    if 程序与功能条目:
        YAML条目["AppsAndFeaturesEntries"] = [程序与功能条目]
    else:
        YAML条目["AppsAndFeaturesEntries"] = []
    
    # 其他字段
    用过的字段 = ["Scope", "HelpLink", "DisplayName", "DisplayVersion", "Publisher", "ProductCode"]
    其他条目: dict[str, str] = {}
    for 键, 值 in ARP条目.items():
        if 键 not in 用过的字段:
            其他条目[键] = str(值)
    
    if 其他条目:
        YAML条目["OtherEntries"] = [其他条目]
    else:
        YAML条目["OtherEntries"] = []
    
    return YAML条目
