import os
from colorama import Fore
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置
from catfood.functions.terminal import runCommand
from function.constant.general import RETRY_INTERVAL

def main() -> int:
    try:
        for 仓库 in ["winget-pkgs", "winget-tools"]:
            仓库路径 = 读取配置(f"paths.{仓库}")
            if isinstance(仓库路径, str):
                os.chdir(仓库路径)
                print(f"清理 {Fore.BLUE}{仓库}{Fore.RESET} 仓库的远程已删除分支...")
                if e := runCommand(["git", "remote", "prune", "origin"], retry=RETRY_INTERVAL):
                    print(f"{消息头.错误} 清理 {Fore.BLUE}{仓库}{Fore.RESET} 的远程已删除分支时出错: Git 返回退出代码 {e}")
                    return e
                else:
                    print(f"{Fore.GREEN}✓{Fore.RESET} 清理完毕")
            else:
                raise ValueError
    except KeyboardInterrupt:
        print(f"{消息头.错误} 已取消操作")
        return 1
    except ValueError:
        return 1
    return 0
