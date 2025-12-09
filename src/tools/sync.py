import os
import subprocess
from colorama import init, Fore
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置

def main():
    init(autoreset=True)

    try:
        winget_pkgs目录 = 读取配置("paths.winget-pkgs")
        if not isinstance(winget_pkgs目录, str):
            return 1

        # 入口
        os.chdir(winget_pkgs目录)
        try:
            subprocess.run(["git", "checkout", "master"], check=True) # 确保从 master 分支开始
            print(f"{Fore.BLUE}  已签出到 master 分支")
        except subprocess.CalledProcessError as e:
            print(f"{消息头.错误} 签出到 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1

        while True:
            try:
                subprocess.run(["git", "fetch", "upstream"], check=True) # 拉取上游修改
                print(f"{Fore.BLUE}  已获取上游修改")
                break
            except subprocess.CalledProcessError as e:
                print(f"{消息头.错误} 获取上游修改失败:\n{Fore.RED}{e}{Fore.RESET}")
                if input(f"{消息头.问题} 是否重试？(默认为{Fore.GREEN}是{Fore.RESET}): ").lower() not in ["y", "yes", "要", "是", "true", ""]:
                    print(f"{消息头.消息} 已取消操作")
                    return 1

        try:
            subprocess.run(["git", "fetch", "origin"], check=True) # 拉取远程修改
            print(f"{Fore.BLUE}  已获取远程修改")
        except subprocess.CalledProcessError as e:
            print(f"{消息头.警告} 拉取远程修改失败:\n{Fore.YELLOW}{e}{Fore.RESET}")
            # 不影响...不影响

        try:
            subprocess.run(["git", "rebase", "upstream/master"], check=True) # 变基合并上游修改
            print(f"{Fore.BLUE}  已变基上游修改")
        except subprocess.CalledProcessError as e:
            print(f"{消息头.错误} 变基上游修改失败:\n{Fore.RED}{e}{Fore.RESET}")
            if input(f"{消息头.问题} 是否尝试替换 master 分支？(默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
                try:
                    subprocess.run(["git", "checkout", "upstream/master"], check=True) # 签出到上游 master 分支
                    print(f"{Fore.BLUE}  已签出到上游 master 分支")
                    subprocess.run(["git", "branch", "-D", "master"], check=True) # 移除旧的 master 分支
                    print(f"{Fore.BLUE}  已移除旧 master 分支")
                    subprocess.run(["git", "switch", "-c", "master"], check=True) # 创建并签出到 master 分支
                    print(f"{Fore.BLUE}  已创建并签出到 master 分支")
                except subprocess.CalledProcessError as e:
                    print(f"{消息头.错误} 替换 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
                    return 1
            else:
                print(f"{消息头.消息} 已取消操作")
                return 1

        try:
            # 推送 master
            subprocess.run(["git", "push", "origin", "master"], check=True)
            print(f"{Fore.BLUE}  已推送 master 分支")
        except subprocess.CalledProcessError as e:
            print(f"{消息头.错误} 推送 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1

        print(f"{Fore.GREEN}✓{Fore.RESET} 同步完成")
    except KeyboardInterrupt:
        print(f"{消息头.错误} 用户已取消操作")
        return 1
    except Exception as e:
        print(f"{消息头.错误} 同步失败:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    return 0
