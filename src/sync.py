import os
import sys
import json
import subprocess
from colorama import init, Fore

init(autoreset=True)

# 不计划添加推送到远程功能，因为我有个 GitHub Action 正在帮我做此事
# 如果您想要推送到远程，运行结束后自己 git push (--force) 一下

try:
    # 配置文件路径
    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            if 配置数据["winget-pkgs"]:
                winget_pkgs目录 = 配置数据["winget-pkgs"]
                if (not os.path.exists(winget_pkgs目录)):
                    print(f"{Fore.RED}✕{Fore.RESET} 配置文件中的目录 {Fore.BLUE}{winget_pkgs目录}{Fore.RESET} 不存在")
                    print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                    sys.exit(3)
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"winget-pkgs\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                sys.exit(3)
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            sys.exit(3)
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        sys.exit(3)

    # NOTE: 前面已经判断过 winget_pkgs目录 是否存在了

    # 入口
    os.chdir(winget_pkgs目录)
    try:
        subprocess.run(["git", "checkout", "master"], check=True) # 确保从 master 分支开始
        print(f"{Fore.BLUE}  已签出到 master 分支")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 签出到 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
        sys.exit(1)

    try:
        subprocess.run(["git", "fetch", "upstream"], check=True) # 拉取上游修改
        print(f"{Fore.BLUE}  已获取上游修改")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 获取上游修改失败:\n{Fore.RED}{e}{Fore.RESET}")
        if input(f"{Fore.BLUE}[!]{Fore.RESET} 是否尝试替换 master 分支？(默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
            try:
                subprocess.run(["git", "fetch", "upstream"], check=True) # 拉取上游修改
                print(f"{Fore.BLUE}  已获取上游修改")
                subprocess.run(["git", "checkout", "upstream/master"], check=True) # 签出到上游 master 分支
                print(f"{Fore.BLUE}  已签出到上游 master 分支")
                subprocess.run(["git", "branch", "-D", "master"], check=True) # 移除旧的 master 分支
                print(f"{Fore.BLUE}  已移除旧 master 分支")
                subprocess.run(["git", "switch", "-c", "master"], check=True) # 创建并签出到 master 分支
                print(f"{Fore.BLUE}  已创建并签出到 master 分支")
            except subprocess.CalledProcessError as e:
                print(f"{Fore.RED}✕{Fore.RESET} 替换 master 分支失败:\n{Fore.RED}{e}{Fore.RESET}")
                sys.exit(3)
        else:
            print(f"{Fore.BLUE}[!]{Fore.RESET} 已取消操作")
            sys.exit(3)

    try:
        subprocess.run(["git", "fetch", "origin"], check=True) # 拉取远程修改
        print(f"{Fore.BLUE}  已获取远程修改")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.YELLOW}⚠{Fore.RESET} 拉取远程修改失败:\n{Fore.YELLOW}{e}{Fore.RESET}")
        # 不影响...不影响

    try:
        subprocess.run(["git", "rebase", "upstream/master"], check=True) # 变基合并上游修改
        print(f"{Fore.BLUE}  已变基上游修改")
    except subprocess.CalledProcessError as e:
        if input(f"{Fore.BLUE}[!]{Fore.RESET} 变基合并上游修改失败:\n{Fore.RED}{e}{Fore.RESET}\n{Fore.BLUE}[!]{Fore.RESET} 是否重试？(默认为{Fore.YELLOW}是{Fore.RESET}): ").lower() not in ["n", "no", "不要", "否", "false"]:
            try:
                subprocess.run(["git", "rebase", "upstream/master"], check=True) # 重试变基合并上游修改
                print(f"{Fore.BLUE}  重试变基上游修改成功")
            except subprocess.CalledProcessError as e:
                if input(f"{Fore.BLUE}[!]{Fore.RESET} 重试变基合并上游修改失败:\n{Fore.RED}{e}{Fore.RESET}\n{Fore.BLUE}[!]{Fore.RESET} 是否尝试强制合并？(默认为{Fore.YELLOW}否{Fore.RESET}): ").lower() in ["y", "yes", "要", "是", "true"]:
                    try:
                        subprocess.run(["git", "rebase", "--force", "upstream/master"], check=True) # 强制变基合并上游修改
                        print(f"{Fore.BLUE}  已强制变基上游修改")
                    except subprocess.CalledProcessError as e:
                        print(f"{Fore.RED}✕{Fore.RESET} 强制变基合并上游修改失败:\n{Fore.RED}{e}{Fore.RESET}")
                        sys.exit(3)
                else:
                    print(f"{Fore.BLUE}[!]{Fore.RESET} 已取消操作")
                    sys.exit(3)
        else:
            print(f"{Fore.BLUE}[!]{Fore.RESET} 已取消操作")
            sys.exit(3)

    print(f"{Fore.GREEN}✓{Fore.RESET} 同步完成")
except KeyboardInterrupt:
    print(f"{Fore.RED}✕{Fore.RESET} 用户已取消操作")
    sys.exit(2)
except Exception as e:
    print(f"{Fore.RED}✕{Fore.RESET} 同步失败:\n{Fore.RED}{e}{Fore.RESET}")
    sys.exit(3)
sys.exit(0)
