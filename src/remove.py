import os
import csv
import json
import shutil
import keyring
import tempfile
import requests
import subprocess
import webbrowser
from colorama import init, Fore
from translate import Translator

# 创建拉取请求
def 创建拉取请求(分支名, 版本文件夹, 理由, Sundry版本号):
    global github_token, owner, 手动验证结果, 软件包标识符
    api = "https://api.github.com/repos/microsoft/winget-pkgs/pulls"
    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    if (手动验证结果):
        数据 = {
            "title": f"Remove version: {软件包标识符} version {版本文件夹} (Auto)",
            "head": f"{owner}:{分支名}",
            "base": "master",
            "body": f"### This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/) {Sundry版本号}, please apply any changes requests directly🙏.\n{理由}\n{手动验证结果}\n\n---\n"
        }
    else:
        数据 = {
            "title": f"Remove version: {软件包标识符} version {版本文件夹} (Auto)",
            "head": f"{owner}:{分支名}",
            "base": "master",
            "body": f"### This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/) {Sundry版本号}, please apply any changes requests directly🙏.\n{理由}\n\n---\n"
        }
    response = requests.post(api, headers=请求头, json=数据)
    if response.status_code == 201:
        print(f"  {Fore.GREEN}成功创建拉取请求：{response.json()["html_url"]}")
    else:
        input(f"  {Fore.RED}拉取请求创建失败：{response.status_code} - {response.text}")

# GitHub 访问令牌
def read_token():
    # 凭据 github-access-token.glm
    try:
        token = keyring.get_password("github-access-token.glm", "github-access-token")
        if token is None:
            print(f"你可能还没设置glm的Token, 请尝试使用以下命令设置Token:\n    glm config --token <YOUR-TOKEN>\n")
            return "error"
        # else:
        return token
    except Exception as e:
        print(f"✕ 读取Token时出错:\n{e}")
        return "error"

def main(args, Sundry版本号):
    global 软件包标识符, 手动验证结果, github_token, owner

    init(autoreset=True)

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
                    return 1
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"winget-pkgs\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                return 1
            # ========================================
            if 配置数据["fork"]:
                try:
                    owner, repo = 配置数据["fork"].split("/")
                except Exception as e:
                    print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败: {Fore.RED}解析 fork 配置项失败{Fore.RESET}\n{Fore.RED}{e}{Fore.RESET}")
                    return 1
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"fork\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config fork [所有者/仓库名] 来修改配置文件中的值")
                return 1
            # ========================================
            if 配置数据["signature"]:
                是否签名 = 配置数据["signature"]
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"signature\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config signature [true/false] 来修改配置文件中的值")
                return 1
            # ========================================
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        return 1

    跳过检查 = False
    理由 = "It returns a 404 status code in GitHub Action and has been automatically verified."
    手动验证结果 = None

    # 尝试从参数中获取软件包标识符和版本
    if (2 <= len(args) <= 4):
        软件包标识符 = args[0]
        软件包版本 = args[1]
        if (3 <= len(args) <= 4):
            if ((isinstance(args[2], bool)) or (args[2].lower() in ["true"])):
                # bool 值视为是否跳过检查开关
                跳过检查 = True # 不接受传 False
                if (len(args) == 4):
                    # 如果需同时传递开关和新理由，则使用
                    # sundry remove [标识符] [版本] True [新理由]
                    理由 = args[3]
            else:
                # 其他值视为理由
                理由 = args[2]
    else:
        print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

    清单目录 = os.path.join(winget_pkgs目录, "manifests", 软件包标识符[0].lower(), *软件包标识符.split('.'))

    # 确保清单存在
    if not os.path.exists(清单目录):
        print(f"{Fore.RED}清单目录不存在: {清单目录}")
        return 1

    github_token = read_token()

    # 入口
    os.chdir(winget_pkgs目录)
    if not 跳过检查:
        try:
            print(f"{Fore.BLUE}开始预先检查")
            print("======= 此软件包现有的所有版本 =======")
            subprocess.run(["winget", "show", "--versions", 软件包标识符], check=True)
            print("======= 此软件包版本在 winget 上的信息 =======")
            subprocess.run(["winget", "show", "--id", 软件包标识符, "--version", 软件包版本, "--source", "winget", "--exact"], check=True)
            import cat
            cat.main([软件包标识符, 软件包版本, "installer"])
            print("======= 确认 =======")
            t = input("您手动访问过每个安装程序链接了吗?").lower()
            if (t in ["没", "否", "假", "f", "n", "open", "o", "打开"]):
                webbrowser.open(f"https://github.com/microsoft/winget-pkgs/tree/master/manifests/{软件包标识符[0].lower()}/{'/'.join(软件包标识符.split('.'))}/{软件包版本}/{软件包标识符}.installer.yaml")
            if (t in ["没", "否", "假", "f", "n", "open", "o", "打开"]) or (t in ["手动", "m", "manually"]):
                if not 手动验证结果:
                    手动验证结果 = input("手动验证结果: ")
                    if 手动验证结果:
                        # 自动将手动验证结果翻译为英文
                        手动验证结果 = Translator(from_lang='zh', to_lang='en').translate(手动验证结果)
                        if input(f"自动翻译结果: {Fore.BLUE}{手动验证结果}{Fore.RESET} 正确吗? ") in ["否", "n", "no", "不"]:
                            手动验证结果 = input("手动验证结果: ")
                        手动验证结果 = f"Manual Verification: {手动验证结果} (auto-translate)"

            with open(os.path.join(winget_pkgs目录, "Tools", "Auth.csv"), mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                # 遍历 CSV 文件中的每一行
                found = False # 标记是否找到了包标识符
                for row in csv_reader:
                    if row['PackageIdentifier'] == 软件包标识符:
                        found = row['Account']
                        break # 找到后退出循环

                if found:
                    input(f"{Fore.YELLOW}⚠ 看起来此软件包在 Auth.csv 中被要求所有者({found})审查，您还是想要移除此软件包版本吗(这将在移除PR中@审查者):")
                    审查者列表 = found.split('/')
                    格式化审查者 = ' , '.join([f"@{审查者}" for 审查者 in 审查者列表])
                    理由 = f"{理由}\n\n{格式化审查者} PTAL"

            print(f"{Fore.BLUE}使用 winget 验证...")
            结果 = subprocess.run(["winget", "download", "--accept-source-agreements", "--accept-package-agreements", "--source", "winget", "--id", 软件包标识符, "--version", 软件包版本, "--exact", "--download-directory", tempfile.gettempdir()], capture_output=True, check=False, text=True)
            if 结果.returncode == 0:
                input(f"{Fore.YELLOW}⚠ 看起来此软件包可以被 winget 正常下载，您还是想要移除此软件包版本吗:")
            else:
                print(f"{Fore.GREEN}使用 winget 验证证实确实存在问题 ({结果.returncode})")
                print(f"{Fore.BLUE}查重...")
                print("======= 打开的 =======")
                subprocess.run(["gh", "pr", "list", "-S", 软件包标识符, "--repo", "microsoft/winget-pkgs"], check=True) # 为什么不自己写请求？老子懒得再去处理它什么的分页什么的速率！
                print("======= 所有 =======")
                subprocess.run(["gh", "pr", "list", "-S", f"{软件包标识符} {软件包版本}", "--repo", "microsoft/winget-pkgs", "--state", "all"], check=True) # 为什么不自己写请求？老子懒得再去处理它什么的分页什么的速率！
                input("您确定没有重复的拉取请求?")
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}已取消操作，没有修改任何文件")
            return 0
    else:
        print(f"{Fore.YELLOW}⚠ 已跳过相关检查")
        理由 = 理由.replace(" and has been automatically verified", "")

    if 手动验证结果:
        理由 = 理由.replace("has been automatically verified.", "has been automatically verified and **manually confirmed**.")

    print(f"{Fore.BLUE}开始操作")
    subprocess.run(["git", "checkout", "master"], check=True) # 确保从 master 分支开始
    print(f"{Fore.BLUE}  已签出到 master 分支")
    subprocess.run(["git", "fetch", "upstream"], check=True) # 拉取上游修改
    subprocess.run(["git", "fetch", "origin"], check=True) # 拉取远程修改
    subprocess.run(["git", "rebase", "upstream/master"], check=True) # 变基合并上游修改
    print(f"{Fore.BLUE}  已拉取上游修改")
    subprocess.run(["git", "checkout", "-b", f"Remove-{软件包标识符}-{软件包版本}"], check=True) # 创建并切换到新的分支
    print(f"{Fore.BLUE}  已签出新分支 Remove-{软件包标识符}-{软件包版本}")

    shutil.rmtree(os.path.join(清单目录, 软件包版本))
    print(f"{Fore.BLUE}  已移除软件包 {软件包标识符} 版本 {软件包版本}")

    subprocess.run(["git", "add", 清单目录], check=True) # 暂存修改
    if 是否签名:
        subprocess.run(["git", "commit", "-S", "-m", f"Remove version: {软件包标识符} version {软件包版本}"], check=True)
    else:
        subprocess.run(["git", "commit", "-m", f"Remove version: {软件包标识符} version {软件包版本}"], check=True)
    print(f"{Fore.BLUE}  已提交修改")

    subprocess.run(["git", "push"], check=True)
    print(f"{Fore.BLUE}  已推送修改")

    while (not 理由):
        理由 = input("移除此软件包版本的理由: ")

    创建拉取请求(f"Remove-{软件包标识符}-{软件包版本}", 软件包版本, 理由, Sundry版本号)

    print(f"{Fore.GREEN} 成功移除 {软件包标识符} 版本 {软件包版本}")
    print(f"{Fore.BLUE}开始清理工作区")
    subprocess.run(["git", "checkout", "master"], check=True)

    # 获取所有本地分支
    branches = subprocess.check_output(["git", "branch"]).decode("utf-8").splitlines()

    # 过滤分支
    exclude_branches = ["master"] # 过滤掉啥这里设啥
    branches_to_delete = [branch.strip() for branch in branches if not any(exclude in branch for exclude in exclude_branches)]

    # 删除分支
    for branch in branches_to_delete:
        subprocess.run(["git", "branch", "-D", branch], check=True)
    print(f"{Fore.GREEN}工作区清理完成")
    return 0
