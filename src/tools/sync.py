import os
import subprocess
from colorama import Fore
from catfood.constant import YES
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置
from catfood.functions.terminal import runCommand
from function.constant.general import RETRY_INTERVAL

def main() -> int:
    try:
        winget_pkgs目录 = 读取配置("paths.winget-pkgs")
        if not isinstance(winget_pkgs目录, str):
            return 1

        os.chdir(winget_pkgs目录)

        # 签出 master
        try:
            subprocess.run(["git", "checkout", "master"], check=True)
            print(f"{消息头.信息} 已签出到 master 分支")
        except subprocess.CalledProcessError as e:
            print(f"{消息头.错误} 签出到 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1

        # 获取上游
        if e := runCommand(["git", "fetch", "upstream"], retry=RETRY_INTERVAL):
            print(f"{消息头.错误} 获取上游修改失败: Git 返回退出代码 {e}")
            return e
        else:
            print(f"{消息头.信息} 已获取上游修改")

        # 获取远程
        if e := runCommand(["git", "fetch", "origin"], retry=RETRY_INTERVAL):
            print(f"{消息头.错误} 获取远程修改失败: Git 返回退出代码 {e}")
            return e
        else:
            print(f"{消息头.信息} 已获取远程修改")

        try:
            subprocess.run(["git", "rebase", "upstream/master"], check=True) # 变基合并上游修改
            print(f"{消息头.信息} 已变基上游修改")
        except subprocess.CalledProcessError as e:
            print(f"{消息头.错误} 变基上游修改失败:\n{Fore.RED}{e}{Fore.RESET}")
            if input(f"{消息头.问题} 是否尝试替换 master 分支？(默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
                try:
                    subprocess.run(["git", "checkout", "upstream/master"], check=True) # 签出到上游 master 分支
                    print(f"{消息头.信息} 已签出到上游 master 分支")
                    subprocess.run(["git", "branch", "-D", "master"], check=True) # 移除旧的 master 分支
                    print(f"{消息头.信息} 已移除旧 master 分支")
                    subprocess.run(["git", "switch", "-c", "master"], check=True) # 创建并签出到 master 分支
                    print(f"{消息头.信息} 已创建并签出到 master 分支")
                except subprocess.CalledProcessError as e:
                    print(f"{消息头.错误} 替换 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
                    return 1
            else:
                raise KeyboardInterrupt

        # 推送到远程
        if e := runCommand(["git", "push", "origin", "master"], retry=RETRY_INTERVAL):
            print(f"{消息头.错误} 推送到远程失败: Git 返回退出代码 {e}")
            return e
        else:
            print(f"{消息头.信息} 已推送到远程")

        print(f"{消息头.成功} 同步完成")
    except KeyboardInterrupt:
        print(f"{消息头.错误} 用户已取消操作")
        return 1
    except Exception as e:
        print(f"{消息头.错误} 同步失败:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    return 0
