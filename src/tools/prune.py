import os
import subprocess
from colorama import init, Fore
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置
from catfood.exceptions.operation import OperationFailed

def main():
    init(autoreset=True)

    try:
        for 仓库 in ["winget-pkgs", "winget-tools"]:
            仓库路径 = 读取配置(f"paths.{仓库}")
            if isinstance(仓库路径, str):
                清理远程(仓库, 仓库路径)
            else:
                raise OperationFailed
    except KeyboardInterrupt:
        print(f"{消息头.错误} 已取消操作")
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
        print(f"{消息头.错误} 清理 {Fore.BLUE}{仓库}{Fore.RESET} 的远程已删除分支时出错，git 返回 {Fore.BLUE}{e.returncode}{Fore.RESET}")
        raise OperationFailed
