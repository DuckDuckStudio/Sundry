import os
import subprocess
from colorama import Fore, init
from function.maintain.config import 读取配置

def main(args: list[str]):
    init(autoreset=True)

    winget_pkgs目录 = 读取配置("winget-pkgs")
    winget_tools目录 = 读取配置("winget-tools")
    if not (isinstance(winget_pkgs目录, str) and isinstance(winget_tools目录, str)):
        return 1
    
    # 格式化输入
    if (len(args) < 3):
        print(f"{Fore.RED}✕{Fore.RESET} 参数不够")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry help 查看帮助")
        return 1

    # 第 1 个参数 - 需要还原的仓库
    if args[0].lower() in ["both", "all", "双仓库", "所有"]:
        需要还原的仓库 = "all"
    elif args[0].lower() in ["pkgs", "winget-pkgs", "清单仓库", "软件包仓库"]:
        需要还原的仓库 = "pkgs"
    elif args[0].lower() in ["tools", "winget-tools", "工具仓库", "日志仓库"]:
        需要还原的仓库 = "tools"
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 需要还原的仓库 (参数1) 不是有效值。")
        return 1

    # 第 2 个参数 - 是否已提交
    if args[1].lower() in ["是", "y", "yes", "已提交", "true"]:
        是否已提交 = True
    elif args[1].lower() in ["否", "n", "no", "未提交", "false"]:
        是否已提交 = False
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 是否已提交 (参数2) 不是有效值。")
        return 1

    # 第 3 个参数 - 是否丢弃
    if args[2].lower() in ["是", "y", "yes", "丢弃", "true"]:
        是否丢弃 = True
    elif args[2].lower() in ["否", "n", "no", "不丢弃", "false"]:
        是否丢弃 = False
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 是否丢弃 (参数3) 不是有效值。")
        return 1

    # 判断操作
    if (需要还原的仓库 == "all"):
        # 双仓库
        if not 还原("pkgs", winget_pkgs目录, 是否已提交, 是否丢弃):
            if not 还原("tools", winget_tools目录, 是否已提交, 是否丢弃):
                return 0
        return 1
    else:
        # 单仓库
        if (需要还原的仓库 == "pkgs"):
            if not 还原("pkgs", winget_pkgs目录, 是否已提交, 是否丢弃):
                return 0
        elif (需要还原的仓库 == "tools"):
            if not 还原("tools", winget_tools目录, 是否已提交, 是否丢弃):
                return 0
        return 1

def 还原(哪个仓库: str, 仓库路径: str, 是否已提交: bool, 是否丢弃: bool):
    try:
        os.chdir(仓库路径)
        # 获取当前所在分支
        当前分支 = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
        if ((当前分支 == "master") and (哪个仓库 == "pkgs")) or ((当前分支 == "main") and (哪个仓库 == "tools")):
            print(f"{Fore.RED}✕{Fore.RESET} [{哪个仓库}仓库] 你不能丢弃主分支")
            return 1
        
        if ((not 是否已提交) and 是否丢弃):
            # 提交丢弃内容
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "--no-gpg-sign", "-m", "丢弃"], check=True)

        # 签回主分支
        主分支 = "master" if 哪个仓库 == "pkgs" else "main"
        subprocess.run(["git", "checkout", 主分支], check=True)

        if 当前分支:
            # 丢弃分支
            subprocess.run(["git", "branch", "-D", 当前分支], check=True)
        else:
            print(f"{Fore.YELLOW}WARN{Fore.RESET} [{哪个仓库}仓库] 未获取到需要丢弃的分支名称")
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 尝试还原 {哪个仓库} 仓库时出现异常: {Fore.RED}{e}{Fore.RESET}")
        return 1
    print(f"{Fore.GREEN}✓{Fore.RESET} 已还原 {哪个仓库} 仓库")
    return 0
