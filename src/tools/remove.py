import re
import os
import csv
import time
import shutil
import tempfile
import requests
import subprocess
import webbrowser
import tools.cat as cat
import tools.sync as sync
from colorama import Fore
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置
from function.files.manifest import 获取清单目录
from translate import Translator # type: ignore
from catfood.functions.github.token import read_token, 这是谁的Token

# 创建拉取请求
def 创建拉取请求(软件包标识符: str, 分支名: str, 版本文件夹: str, 理由: str):
    global owner, 手动验证结果
    while True: # 不 break 直接 return
        github_token = read_token()
        if not github_token:
            print(f"{消息头.错误} 拉取请求创建失败: Token 读取失败")
            return 1

        api = "https://api.github.com/repos/microsoft/winget-pkgs/pulls"
        请求头 = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        数据: dict[str, str | bool]
        if (手动验证结果):
            数据 = {
                "title": f"Remove version: {软件包标识符} version {版本文件夹} (Auto)",
                "head": f"{owner}:{分支名}",
                "base": "master",
                "body": f"### This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/)🚀.\n{理由}\n{手动验证结果}\n\n---\n"
            }
        else:
            数据 = {
                "title": f"Remove version: {软件包标识符} version {版本文件夹} (Auto)",
                "head": f"{owner}:{分支名}",
                "base": "master",
                "body": f"### This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/)🚀.\n{理由}\n\n---\n"
            }

        if 读取配置("github.pr.maintainer_can_modify") == False:
            数据["maintainer_can_modify"] = False

        response = requests.post(api, headers=请求头, json=数据)
        if response.status_code == 201:
            print(f"    {Fore.GREEN}拉取请求创建成功: {response.json()["html_url"]}")
            return response.json()["html_url"]
        else:
            print(f"    {Fore.RED}拉取请求创建失败: {response.status_code} - {response.text}")
            try:
                if input(f"{消息头.问题} 我应该重试吗[Y/N]: ").lower() not in ["y", "yes", "应该", "要", "重试", "retry"]:
                    return 1
                print("正在重试...")
            except KeyboardInterrupt:
                return 1

def main(args: list[str]) -> int:
    global 手动验证结果, owner

    winget_pkgs目录 = 读取配置("paths.winget-pkgs")
    if not isinstance(winget_pkgs目录, str):
        return 1
    pkgs仓库 = 读取配置("repos.winget-pkgs")
    if not isinstance(pkgs仓库, tuple):
        return 1
    owner, _ = pkgs仓库
    是否签名 = 读取配置("git.signature")
    if not isinstance(是否签名, bool):
        return 1

    # 尝试从参数中获取软件包标识符和版本
    跳过检查 = False
    理由 = "It returns a 404 status code in GitHub Action and has been automatically verified."
    手动验证结果 = None
    if (2 <= len(args) <= 4):
        软件包标识符 = args[0]
        软件包版本 = args[1]
        if (3 <= len(args) <= 4):
            if (args[2].lower() == "true"):
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
        print(f"{消息头.错误} {Fore.RED}参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

    清单目录 = 获取清单目录(软件包标识符, winget_pkgs目录=winget_pkgs目录)
    if not 清单目录:
        print(f"{Fore.RED}未能找到该标识符的清单目录: {软件包标识符}")
        return 1

    if not os.path.exists(os.path.join(清单目录, 软件包版本)):
        print(f"{Fore.RED}包版本清单目录不存在: {os.path.join(清单目录, 软件包版本)}")
        return 1

    if any(os.path.isdir(os.path.join(os.path.join(清单目录, 软件包版本), item)) for item in os.listdir(os.path.join(清单目录, 软件包版本))):
        # 如果软件包版本清单目录下存在其他文件夹
        print(f"{消息头.错误} 包版本清单目录下存在其他文件夹")
        print(f"{消息头.提示} 这可能是因为你 {Fore.YELLOW}错误的将包标识符的一部分当作包版本{Fore.RESET} 导致的。")
        print(f"{消息头.提示} 例如软件包 DuckStudio.GitHubView.Nightly 被错误的认为是软件包 DuckStudio.GitHubView 的一个版本号为 Nightly 的版本。")
        return 1

    # 入口
    os.chdir(winget_pkgs目录)
    if not 跳过检查:
        try:
            print(f"{Fore.BLUE}开始预先检查")
            try:
                print("======= 此包现有的所有版本 =======")
                subprocess.run(["winget", "show", "--versions", 软件包标识符], check=True)
                print("======= 此包版本在 winget 上的信息 =======")
                subprocess.run(["winget", "show", "--id", 软件包标识符, "--version", 软件包版本, "--source", "winget", "--exact"], check=True)
            except subprocess.CalledProcessError as e:
                print(f"{消息头.错误} 获取包信息失败: {Fore.RED}{e}{Fore.RESET}")
                return 1
            cat.main([软件包标识符, 软件包版本, "installer"])
            print("======= 确认 =======")
            t = input("您手动访问过每个安装程序链接了吗?").lower()
            if (t in ["没", "否", "假", "f", "n", "open", "o", "打开"]):
                if os.path.join(winget_pkgs目录, "manifests") in 清单目录:
                    webbrowser.open(f"https://github.com/microsoft/winget-pkgs/tree/master/manifests/{软件包标识符[0].lower()}/{'/'.join(软件包标识符.split('.'))}/{软件包版本}/{软件包标识符}.installer.yaml")
                else:
                    webbrowser.open(f"https://github.com/microsoft/winget-pkgs/tree/master/fonts/{软件包标识符[0].lower()}/{'/'.join(软件包标识符.split('.'))}/{软件包版本}/{软件包标识符}.installer.yaml")
            if (t in ["没", "否", "假", "f", "n", "open", "o", "打开"]) or (t in ["手动", "m", "manually"]):
                if not 手动验证结果:
                    手动验证结果 = input("手动验证结果: ").replace("\\n", "\n")
                    if 手动验证结果:
                        # 自动将手动验证结果翻译为英文
                        手动验证结果 = Translator(from_lang='zh', to_lang='en').translate(手动验证结果) # type: ignore
                        手动验证结果 = f"{手动验证结果} (auto-translate)"
                        if input(f"自动翻译结果: {Fore.BLUE}{手动验证结果}{Fore.RESET} 正确吗? ").lower() not in ["正确", "对", "y", "对的", "yes", ""]: # 空字符串代表直接 Enter
                            手动验证结果 = input("手动验证结果: ").replace("\\n", "\n")
                        手动验证结果 = f"Manual Verification:\n{手动验证结果}"

            with open(os.path.join(winget_pkgs目录, "Tools", "ManualValidation", "Auth.csv"), mode='r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                # 遍历 CSV 文件中的每一行
                found = False # 标记是否找到了包标识符
                for row in csv_reader:
                    if row['PackageIdentifier'] == 软件包标识符:
                        found = row['Account']
                        break # 找到后退出循环

                if found:
                    审查者列表 = found.split('/')
                    我是谁 = 这是谁的Token(read_token(silent=True))
                    if not (我是谁 in 审查者列表) and (not 读取配置("github.pr.mention_self_when_reviewer")):
                        if 我是谁 not in 审查者列表:
                            try:
                                input(f"{Fore.YELLOW}⚠ 看起来此包在 Auth.csv 中被要求所有者({", ".join(审查者列表)})审查，您还是想要移除此包版本吗 (这将在 PR 中 @审查者): [ENTER/CTRL+C]{Fore.RESET}")
                            except KeyboardInterrupt:
                                return 1

                        格式化审查者 = ' , '.join([f"@{审查者}" for 审查者 in 审查者列表])
                        理由 = f"{理由}\n\n{格式化审查者} PTAL"

            验证结果日志 = 使用WinGet验证(软件包标识符, 软件包版本)
            if 验证结果日志:
                理由 = f"{理由}\n\n```logs\n{"\n".join(验证结果日志)}\n```"

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
    if sync.main():
        return 1
    新分支名 = f"Remove-{软件包标识符}-{软件包版本}-{int(time.time())}"
    subprocess.run(["git", "checkout", "-b", 新分支名], check=True) # 创建并切换到新的分支
    print(f"{Fore.BLUE}  已签出新分支 {新分支名}")

    shutil.rmtree(os.path.join(清单目录, 软件包版本))
    print(f"{Fore.BLUE}  已移除软件包 {软件包标识符} 版本 {软件包版本}")

    subprocess.run(["git", "add", 清单目录], check=True) # 暂存修改
    if 是否签名:
        subprocess.run(["git", "commit", "-S", "-m", f"Remove version: {软件包标识符} version {软件包版本} (Auto)"], check=True)
    else:
        subprocess.run(["git", "commit", "-m", f"Remove version: {软件包标识符} version {软件包版本} (Auto)"], check=True)
    print(f"{Fore.BLUE}  已提交修改")

    subprocess.run(["git", "push"], check=True)
    print(f"{Fore.BLUE}  已推送修改")

    while (not 理由):
        理由 = input("移除此软件包版本的理由: ")

    if 创建拉取请求(软件包标识符, 新分支名, 软件包版本, 理由) == 1:
        return 1 # 拉取请求创建失败

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


def 使用WinGet验证(软件包标识符: str, 软件包版本: str, AutoRemove: bool=False) -> list[str] | None:
    # 使用 WinGet 尝试下载
    print(f"{Fore.BLUE}使用 winget 验证...{Fore.RESET}")
    验证结果 = subprocess.Popen(
        [
            "winget", "download", "--accept-source-agreements",
            "--accept-package-agreements", "--skip-dependencies",
            "--source", "winget", "--id", 软件包标识符, "--version", 软件包版本,
            "--exact", "--download-directory", os.path.join(tempfile.gettempdir(), "Sundry", "RemoveAndAutoRemove", "DownloadInstallers")
        ],
        stdout=subprocess.PIPE, # 捕获标准输出
        stderr=subprocess.PIPE, # 捕获标准错误
        text=True # 输出为字符串
    )

    # 逐行读取并处理输出
    同行: str = "正常"
    验证结果日志: list[str] = []
    for line in 验证结果.stdout or []: # 标准输出
        if line.endswith("\n"):
            line = line.rstrip("\n") # 去除空行

        if re.match(r"^\s*[-\\|/]", line): # 加载动画，使用 \r 输出
            # ^ 匹配字符串开头
            # \s* 匹配 0 - n 个空格
            # [-\\|/] 匹配 - \ | /
            # {1} 表示仅匹配 1 个动画字符
            # $ 匹配字符串结尾
            同行 = "加载动画"
            print(f"\r{Fore.BLUE}{line.strip()}{Fore.RESET}", end="")
        elif any(进度条 in line for 进度条 in ["█", "▒"]):
            # 不属于同行，自身 \r 完后要留着
            同行 = "进度条"
            print(f"\r{line}", end="")
            if "▒" not in line: # 跑完进度了
                验证结果日志.append(line.replace("\r", "")) # 进度条也算日志
        elif line.strip():
            if 同行 == "加载动画":
                line = f"\r{line}"
            elif 同行 == "进度条":
                line = f"\n{line}"

            同行 = "正常"
            验证结果日志.append(line.replace("\r", "").replace("\n", ""))

            if any(msg in line for msg in ["执行此命令时发生意外错误", "Download request status is not success.", "404", "403", "安装程序哈希不匹配"]) and (not any(msg in line for msg in ["已找到", "正在下载"])):
                print(f"{Fore.RED}{line}{Fore.RESET}")
            elif "正在下载" in line:
                line = f"{line.replace("正在下载", f"正在下载{Fore.LIGHTBLUE_EX}")}{Fore.RESET}"
                print(line)
            elif "已找到" in line:
                # 为包名和标识符上 CYAN，[]原色
                # 正则逐部分解释
                # 1. `已找到``
                # 字面量，匹配字符串“已找到”。
                # 2. `\s+`
                # 匹配一个或多个空白字符（如空格、Tab），用于分隔“已找到”和包名。
                # 3. `([^\[]+)`
                # 这是第一个捕获组，用于匹配包名。
                # `[^\[]+`` 的意思是“匹配一个或多个不是左方括号 `[` 的字符”。
                # 这样可以让包名中包含空格，但不会匹配到左方括号（即包名遇到 `[` 就停止匹配）。
                # 例如：`calibre portable` 等都能被完整捕获。
                # 4. `\s+`
                # 再次匹配一个或多个空白字符，分隔包名和方括号。
                # 5. `\[(\S+)\]`
                # 匹配左方括号 `[`
                # `(\S+)` 是第二个捕获组，匹配一个或多个非空白字符（即包标识符，不能有空格）。
                # 匹配右方括号 `]`
                # 例如：`[calibre.calibre.portable]`，捕获到 `calibre.calibre.portable`。
                # `\\1`和`\\2`分别引用正则表达式中的第1和第2个捕获组（即包名和包标识符）。
                line = re.sub(r"已找到\s+([^\[]+)\s+\[(\S+)\]", f"已找到 {Fore.CYAN}\\1{Fore.RESET} [{Fore.CYAN}\\2{Fore.RESET}]", line)
                print(line)
            else:
                print(line)

    # 逐行读取并处理错误输出
    for line in 验证结果.stderr or []: # 错误输出
        if line.endswith("\n"):
            line = line.rstrip('\n') # 去除空行
        验证结果日志.append(line)
        print(f"{Fore.RED}{line}{Fore.RESET}")

    # 等待进程结束并获取返回码
    验证结果.wait()

    if (验证结果.returncode == 0):
        if not AutoRemove:
            input(f"{Fore.YELLOW}⚠ 看起来此软件包可以被 winget 正常下载，您还是想要移除此软件包版本吗:{Fore.RESET}")
        return None
    else:
        验证结果日志.append(f"WinGet returned exit code: {验证结果.returncode}")
        if not AutoRemove:
            print(f"{Fore.GREEN}使用 winget 验证证实确实存在问题 ({验证结果.returncode}){Fore.RESET}")
        # elif 验证结果.returncode != 2149122452:
        #     input(f"{Fore.YELLOW}WinGet 返回了非预期的退出代码 {验证结果.returncode}{Fore.RESET}")
        return 验证结果日志
