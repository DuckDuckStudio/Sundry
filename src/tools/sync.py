import os
import subprocess

from catfood.constant import YES
from catfood.functions.print import MSHead
from catfood.functions.terminal import runCommand
from colorama import Fore

from function.constant.general import RETRY_INTERVAL
from function.maintain.config import 读取配置


def main() -> int:
    try:
        winget_pkgs目录 = 读取配置("paths.winget-pkgs")
        if not isinstance(winget_pkgs目录, str):
            return 1

        os.chdir(winget_pkgs目录)

        # 签出 master
        try:
            subprocess.run(["git", "checkout", "master"], check=True)
            print(f"{MSHead.Information} 已签出到 master 分支")
        except subprocess.CalledProcessError as e:
            print(f"{MSHead.Error} 签出到 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1

        # 获取上游
        if e := runCommand(["git", "fetch", "upstream"], retry=RETRY_INTERVAL):
            print(f"{MSHead.Error} 获取上游修改失败: Git 返回退出代码 {e}")
            return e
        else:
            print(f"{MSHead.Information} 已获取上游修改")

        # 获取远程
        if e := runCommand(["git", "fetch", "origin"], retry=RETRY_INTERVAL):
            print(f"{MSHead.Error} 获取远程修改失败: Git 返回退出代码 {e}")
            return e
        else:
            print(f"{MSHead.Information} 已获取远程修改")

        try:
            subprocess.run(
                ["git", "rebase", "upstream/master"], check=True
            )  # 变基合并上游修改
            print(f"{MSHead.Information} 已变基上游修改")
        except subprocess.CalledProcessError as e:
            print(f"{MSHead.Error} 变基上游修改失败:\n{Fore.RED}{e}{Fore.RESET}")
            if (
                input(
                    f"{MSHead.Question} 是否尝试替换 master 分支？(默认为{Fore.YELLOW}否{Fore.RESET}): "
                ).lower()
                in YES
            ):
                try:
                    subprocess.run(
                        ["git", "checkout", "upstream/master"], check=True
                    )  # 签出到上游 master 分支
                    print(f"{MSHead.Information} 已签出到上游 master 分支")
                    subprocess.run(
                        ["git", "branch", "-D", "master"], check=True
                    )  # 移除旧的 master 分支
                    print(f"{MSHead.Information} 已移除旧 master 分支")
                    subprocess.run(
                        ["git", "switch", "-c", "master"], check=True
                    )  # 创建并签出到 master 分支
                    print(f"{MSHead.Information} 已创建并签出到 master 分支")
                except subprocess.CalledProcessError as e1:
                    print(
                        f"{MSHead.Error} 替换 master 分支失败:\n{Fore.RED}{e1}{Fore.RESET}"
                    )
                    return 1
            else:
                raise KeyboardInterrupt from e

        # 推送到远程
        if e := runCommand(["git", "push", "origin", "master"], retry=RETRY_INTERVAL):
            print(f"{MSHead.Error} 推送到远程失败: Git 返回退出代码 {e}")
            return e
        else:
            print(f"{MSHead.Information} 已推送到远程")

        print(f"{MSHead.Success} 同步完成")
    except KeyboardInterrupt:
        print(f"{MSHead.Error} 用户已取消操作")
        return 1
    except Exception as e:
        print(f"{MSHead.Error} 同步失败:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    return 0
