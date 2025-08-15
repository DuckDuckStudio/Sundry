import re
import os
import subprocess
import tools.remove as remove
from colorama import Fore, init
from function.maintain.config import 读取配置

def main(args: list[str]) -> int:
    try:
        init(autoreset=True)
        软件包标识符: str = 处理参数(args)
        版本列表: list[str] = 查找软件包版本(软件包标识符)
        检查软件包版本(软件包标识符, 版本列表)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功检查 {Fore.BLUE}{软件包标识符}{Fore.RESET} 的所有版本")
        return 0
    except KeyboardInterrupt:
        print(f"{Fore.RED}✕{Fore.RESET} 操作中止")
        return 1

def 检查软件包版本(软件包标识符: str, 版本列表: list[str]) -> None:
    for 版本 in 版本列表:
        print(f"\n{Fore.BLUE}INFO{Fore.RESET} 正在检查 {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} ...")
        验证结果 = remove.使用WinGet验证(软件包标识符, 版本, AutoRemove=True)
        if not 验证结果:
            print(f"{Fore.GREEN}✓{Fore.RESET} 验证 {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} 通过！")
        else:
            print(f"{Fore.RED}✕{Fore.RESET} {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} 下载失败！将移除此版本...")
            移除软件包版本(软件包标识符, 版本, f"Attempt to download using WinGet failed.\n\n```logs\n{"\n".join(验证结果)}\n```")

def 检查重复拉取请求(软件包标识符: str, 软件包版本: str) -> bool:
    '''
    检查上游仓库中是否有 相同 (软件包标识符、版本) 的且 打开的 拉取请求。
    如有，返回 True。否则返回 False。
    '''
    result = subprocess.run(
        ["gh", "pr", "list", "-S", f"{软件包标识符} {软件包版本}", "--repo", "microsoft/winget-pkgs"],
        capture_output=True, text=True, check=True
    )
    return not result.stdout

def 移除软件包版本(软件包标识符: str, 版本: str, 原因: str) -> None:
    if not 检查重复拉取请求(软件包标识符, 版本):
        print(f"{Fore.YELLOW}WARN{Fore.RESET} 找到重复的拉取请求，跳过后续处理")
        return
    if remove.main([软件包标识符, 版本, "True", 原因]):
        print(f"{Fore.RED}✕{Fore.RESET} 尝试移除 {Fore.BLUE}{软件包标识符} {版本}{Fore.RESET} 失败！")
        raise KeyboardInterrupt
    
def 获取winget_pkgs目录() -> str:
    winget_pkgs目录 = 读取配置("winget-pkgs")
    if not isinstance(winget_pkgs目录, str):
        raise KeyboardInterrupt
    return winget_pkgs目录

def 查找软件包版本(软件包标识符: str, 本地仓库: bool = False) -> list[str]:
    try:
        版本列表: list[str] = []
        if 本地仓库:
            # 获取所有版本号文件夹
            清单目录 = os.path.join(获取winget_pkgs目录(), "manifests", 软件包标识符[0].lower(), *软件包标识符.split('.'))
            while True:
                try:
                    for 文件夹 in os.listdir(清单目录):
                        if os.path.isdir(os.path.join(清单目录, 文件夹)):
                            for 文件 in os.listdir(os.path.join(清单目录, 文件夹)):
                                if os.path.isdir(文件):
                                    # 如果这个版本文件夹下面还有目录，则代表这可能是类似 Nightly 版本的软件包的标识符的一部分
                                    break
                            else:
                                # 如果前面的 for 没有 break，则执行
                                版本列表.append(文件夹)
                    break
                except FileNotFoundError as e:
                    print(f"{Fore.RED}✕{Fore.RESET} {Fore.RED}{e}{Fore.RESET}")
                    input("是否重新查找? [ENTER/CTRL+C]")
        else:
            结果 = subprocess.run(
                ["winget", "show", "--id", 软件包标识符, "-s", "winget", "-e", "--versions"],
                capture_output=True, text=True, check=True
            )
            版本列表 = []
            for 行 in [line for line in 结果.stdout.splitlines() if line.strip()]:
                匹配结果 = re.match(r"^[Vv]?\d+(?:\.\d+)*$", 行)
                # ^[Vv]?\d+(?:\.\d+)*$
                # ^...$      -> 匹配行的开头和结尾，确保这一整行都是版本号。
                # [Vv]?      -> 可选的 V 或 v，用于匹配像 "v1.2.3" 或 "V2.0" 这种带前缀的版本号。
                # \d+        -> 匹配一个或多个数字，版本号的主版本部分，如 "1"、"12"。
                # (?:\.\d+)* -> 非捕获分组，匹配零次或多次 ".数字"，用于次版本号和补丁号，如 ".2"、".3"。
                #
                # 这个正则的目的是:
                # - 匹配类似 "1.2.3"、"v2.0"、"V10.4.1" 这样的版本号字符串；
                # - 支持可选的 v 或 V 前缀；
                if 匹配结果:
                    版本列表.append(行)
        if not 版本列表:
            print(f"{Fore.RED}✕{Fore.RESET} 未找到 {Fore.BLUE}{软件包标识符}{Fore.RESET} 的任何版本")
            if 本地仓库 or 是否中止(input(f"{Fore.BLUE}?{Fore.RESET} 使用本地仓库中的信息吗? [Y/n]: "), "y"):
                raise KeyboardInterrupt
        print(f"{Fore.GREEN}✓{Fore.RESET} 找到 {Fore.BLUE}{软件包标识符}{Fore.RESET} 版本:\n{Fore.BLUE}{f"{Fore.RESET},{Fore.BLUE} ".join(版本列表)}{Fore.RESET}\n")
        return 版本列表
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 获取版本失败:\n{Fore.RED}{e}{Fore.RESET}")
        raise KeyboardInterrupt

def 是否中止(输入: str, 默认: str = "n") -> bool:
    '''
    依据输入确定是否中止后续操作。
    false 表示继续。
    true 表示中止。
    '''
    if not 输入:
        输入 = 默认

    return 输入.lower() not in ["y", "yes", "是"]

def 处理参数(args: list[str]) -> str:
    if not args:
        print(f"{Fore.RED}✕{Fore.RESET} 请传递参数")
        raise KeyboardInterrupt
    
    预期参数数量: int = 1
    if len(args) > 预期参数数量:
        print(f"{Fore.YELLOW}Hint{Fore.RESET} 多余的参数，我们只需要 {预期参数数量} 个参数")

    return args[0] # 包标识符
