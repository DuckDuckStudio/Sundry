import os
import sys
from 修改版本号 import 替换文件内容

def main():
    源码路径 = os.path.normpath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "src", "tools", "verify.py"))

    if (
        替换文件内容(
            源码路径,
            "if input(f\"{Fore.BLUE}?{Fore.RESET} 临时清单目录下{Fore.YELLOW}已存在同名清单目录{Fore.RESET} {Fore.BLUE}{清单目录}{Fore.RESET}，我应该移除它吗? [Y/n]: \").lower()",
            "if \"y\""
        )
        or 替换文件内容(
            源码路径,
            "input(\"按 ENTER 继续测试卸载，按 CTRL + C 结束...\")",
            "print(\"继续测试卸载...\")"
        )
    ):
        return 1

    print("🎉 成功修改 verify 的源码来假装它可以静默执行")
    return 0

if __name__ == "__main__":
    sys.exit(main())
