import os
import subprocess
from colorama import init, Fore
from function.maintain.config import 读取配置
from exception.operation import OperationFailed

def main():
    init(autoreset=True)

    try:
        winget_pkgs目录 = 读取配置("winget-pkgs")
        if not isinstance(winget_pkgs目录, str):
            return 1
        winget_tools目录 = 读取配置("winget-tools")
        if not isinstance(winget_tools目录, str):
            return 1
        
        对应 = {
            "winget-pkgs": winget_pkgs目录,
            "winget-tools": winget_tools目录
        }

        for 仓库 in 对应:
            仓库路径 = 对应.get(仓库)
            if 仓库路径:
                清理远程(仓库, 仓库路径)
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 仓库路径为假值")
                raise OperationFailed
    except KeyboardInterrupt:
        print(f"{Fore.RED}✕{Fore.RESET} 已取消操作")
        return 1
    except OperationFailed:
        return 1
    return 0


def 清理远程(仓库: str, 仓库路径: str):
    try:
        print(f"清理 {Fore.BLUE}{仓库}{Fore.RESET} 仓库的远程已删除分支...")
        os.chdir(仓库路径)
        subprocess.run(["git", "remote", "prune", "origin"], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 清理完毕")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 清理 {Fore.BLUE}{仓库}{Fore.RESET} 的远程已删除分支时出错，git 返回 {Fore.BLUE}{e.returncode}{Fore.RESET}")
        raise OperationFailed
