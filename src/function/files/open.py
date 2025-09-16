import os
import sys
from colorama import Fore
from function.print.print import 消息头

def open_file(file: str) -> int:
    try:
        if not os.path.exists(file):
            raise FileNotFoundError(f"未找到 {file}")

        if (sys.platform != "win32") and os.path.isdir(file):
            raise Exception("只能在 Windows 上打开目录")

        if sys.platform == "win32":
            os.startfile(file)
        elif sys.platform == "linux":
            import subprocess
            try:
                subprocess.run(["xdg-open", file], check=True)
            except FileNotFoundError:
                try:
                    subprocess.run(["nano", file], check=True)
                except FileNotFoundError:
                    subprocess.run(["vim", file], check=True)
                    raise Exception("我实在不知道该用什么来打开它...")
        else:
            raise OSError(f"很抱歉，作者见识太少，不清楚如何在 {sys.platform} 上打开文件...")
        return 0
    except Exception as e:
        print(f"{消息头.错误} 打开文件时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
