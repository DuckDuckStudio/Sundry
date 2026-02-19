import os
import sys
import csv
import time
import random
import subprocess
from colorama import Fore
from typing import Literal
from datetime import datetime
from catfood.functions.print import 消息头
from function.git.format import branchName
from function.github.pr import submitChanges
from function.maintain.config import 读取配置
from catfood.functions.files import open_file
from function.files.manifest import 获取清单目录
from function.files.manifest import FormatManifest
from function.github.token import read_token, 这是谁的Token

def main(args: list[str]) -> Literal[1, 0]:
    global 包标识符, 包版本, 日志文件路径
    global 解决, 清单目录, 格式化审查者, 程序所在目录
    global owner

    # 目录路径
    # 尝试从参数中获取包标识符和版本
    if (2 <= len(args) <= 3):
        包标识符 = args[0]
        包版本 = args[1]
        if (len(args) == 3):
            解决 = args[2]
            # 如果 args[2] 是 Issue 格式 （#数字、纯数字、纯 https://github.com/microsoft/winget-pkgs/issues/数字）
            if (解决.startswith("#") or 解决.isdigit() or 解决.startswith("https://github.com/microsoft/winget-pkgs/issues/")):
                if args[2].isdigit():
                    解决 = f"#{解决}"
                解决 = f"- Resolves {解决}"
        else:
            解决 = ""
    else:
        print(f"{消息头.错误} {Fore.RED}参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1
    
    # 路径
    程序所在目录 = os.path.dirname(os.path.abspath(sys.argv[0]))
    日志文件路径 = os.path.join("logs", datetime.today().strftime('%Y\\%m\\%d'), f"{包标识符}-{包版本}.log") # 相对路径

    winget_pkgs目录 = ""
    winget_pkgs目录 = 读取配置("paths.winget-pkgs")
    if not isinstance(winget_pkgs目录, str):
        return 1
    
    pkgs仓库 = 读取配置("repos.winget-pkgs")
    if not isinstance(pkgs仓库, tuple):
        return 1
    owner, _ = pkgs仓库

    可能是清单目录 = 获取清单目录(包标识符, winget_pkgs目录=winget_pkgs目录)
    # 这里用 可能是清单目录 而不是直接用 清单目录 是因为
    # 直接用的话 None 会 global 到其他函数。
    # 不懂的话改改看就知道了。
    if not 可能是清单目录:
        print(f"{消息头.错误} 获取清单目录失败")
        return 1
    清单目录 = 可能是清单目录

    # 预先检查
    格式化审查者 = ""
    with open(os.path.join(winget_pkgs目录, "Tools", "ManualValidation", "Auth.csv"), mode='r', encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        # 遍历 CSV 文件中的每一行
        found = False # 标记是否找到了包标识符
        for row in csv_reader:
            if row['PackageIdentifier'] == 包标识符:
                found = row['Account']
                break # 找到后退出循环

        if found:
            审查者列表 = found.split('/')
            我是谁 = 这是谁的Token(read_token(silent=True))
            if not (我是谁 in 审查者列表) and (not 读取配置("github.pr.mention_self_when_reviewer")):
                if 我是谁 not in 审查者列表:
                    try:
                        input(f"{Fore.YELLOW}⚠ 看起来此包在 Auth.csv 中被要求所有者({", ".join(审查者列表)})审查，您还是想要修改此包吗 (这将在 PR 中 @审查者): [ENTER/CTRL+C]{Fore.RESET}")
                    except KeyboardInterrupt:
                        return 1

                格式化审查者 = ' , '.join([f"@{审查者}" for 审查者 in 审查者列表])

    # ========= 日志 配置 开始 =========
    os.chdir(程序所在目录)
    os.makedirs(os.path.join(程序所在目录, "logs", datetime.today().strftime('%Y\\%m\\%d')), exist_ok=True) # 创建今日日志文件夹
    with open(os.path.join(程序所在目录, 日志文件路径), 'w', encoding="utf-8") as 日志文件:
        日志文件.write('~~ Start logging ~~\n') # 初始化日志文件

    # 打开文件并读取所有行 - FUN
    with open(os.path.join(程序所在目录, "fun.txt"), 'r', encoding="utf-8") as file:
        随机句子 = None
        while (not 随机句子): # 避免空行
            随机句子 = random.choice(file.readlines()).strip().replace("\\n", "\n") # 多行好玩的
    写入日志(随机句子, "FUN")
    # ========= 日志 配置 结束 =========

    # CD 到仓库目录
    os.chdir(winget_pkgs目录)

    # 获取所有版本号文件夹
    while True:
        try:
            版本文件夹s: list[str] = []
            for 文件夹 in os.listdir(清单目录):
                if os.path.isdir(os.path.join(清单目录, 文件夹)):
                    for 文件 in os.listdir(os.path.join(清单目录, 文件夹)):
                        if os.path.isdir(文件):
                            # 如果这个版本文件夹下面还有目录，则代表这可能是类似 Nightly 版本的包的标识符的一部分
                            break
                    else:
                        # 如果前面的 for 没有 break，则执行
                        版本文件夹s.append(文件夹)
            print(f"找到以下版本文件夹: {版本文件夹s}")
            写入日志(f"Found the following version folder: {版本文件夹s}")
            break
        except FileNotFoundError as e:
            print(f"{消息头.错误} {Fore.RED}{e}{Fore.RESET}")
            写入日志(f"Error getting package version number folder: {e}")
            try:
                input("是否重新查找? [ENTER/CTRL+C]")
                写入日志("Trying to re-find...")
            except KeyboardInterrupt:
                print(f"\n{Fore.BLUE}[INFO]{Fore.RESET} 了解，正在关闭日志...")
                写入日志("User interrupted the process, exiting...")
                with open(os.path.join(程序所在目录, 日志文件路径), 'a', encoding="utf-8") as 日志文件: # 追加写入
                    日志文件.write("~~ End of logging ~~\n")
                print(f"{Fore.BLUE}[INFO]{Fore.RESET} 日志已关闭，正在退出...")
                return 1

    # 确保有获取到至少一个版本文件夹
    if not 版本文件夹s:
        print(f"{消息头.错误} 没有找到任何版本文件夹，请检查参数是否正确。")
        写入日志("No version folder found.", "ERROR")
        with open(os.path.join(程序所在目录, 日志文件路径), 'a', encoding="utf-8") as 日志文件: # 追加写入
            日志文件.write("~~ End of logging ~~\n")
        print(f"{Fore.BLUE}[INFO]{Fore.RESET} 日志已关闭，正在退出...")
        return 1

    # 遍历所有版本并进行处理
    for 版本文件夹 in 版本文件夹s:
        if 版本文件夹 != 包版本:
            print(f"跳过版本文件夹: {版本文件夹}")
            写入日志(f"Skip version {版本文件夹}, because it's not in the list of versions to be modified.")
            continue
        if 修改版本(版本文件夹) == 1:
            with open(os.path.join(程序所在目录, 日志文件路径), 'a', encoding="utf-8") as 日志文件:
                日志文件.write("~~ End of logging ~~\n")
            return 1 # 如果修改版本时出错，退出程序

    print(f"\n{Fore.GREEN}所有版本清单已修改并推送完成。")
    写入日志("All manifests have been modified and pushed through.")

    subprocess.run(["git", "checkout", "master"], check=True)

    # 获取所有本地分支
    branches = subprocess.check_output(["git", "branch"]).decode("utf-8").splitlines()

    # 过滤分支
    exclude_branches = ["master"]
    branches_to_delete = [branch.strip() for branch in branches if not any(exclude in branch for exclude in exclude_branches)]

    # 删除分支
    for branch in branches_to_delete:
        subprocess.run(["git", "branch", "-D", branch], check=True)
    print("工作区清理完成。")
    写入日志("Workspace clean-up completed.")

    # ========= 日志关闭 开始 =========
    with open(os.path.join(程序所在目录, 日志文件路径), 'a', encoding="utf-8") as 日志文件: # 追加写入
        日志文件.write('~~ End of logging ~~\n')
    print(f"{Fore.GREEN}✓{Fore.RESET} 成功修改 {Fore.BLUE}{包标识符}{Fore.RESET} 版本 {Fore.BLUE}{包版本}{Fore.RESET} 的清单。")
    # ========= 日志关闭 结束 =========

    return 0

def 写入日志(消息: str, 等级: str="INFO"):
    global 程序所在目录, 日志文件路径
    现在时间 = datetime.now()
    写入时间 = 现在时间.strftime('%Y-%m-%d %H:%M:%S.') + str(现在时间.microsecond)[:3] # 格式化日志时间 YYYY-MM-DD HH:MM:SS.ms
    with open(os.path.join(程序所在目录, 日志文件路径), 'a', encoding="utf-8") as 日志文件: # 追加写入
        for 行 in 消息.split("\n"):
            日志文件.write(f"{写入时间} {等级} {行}\n")

# Git 操作部分
def 修改版本(版本文件夹: str) -> Literal[1, 0]:
    print(f"\n正在处理版本文件夹: {版本文件夹}")
    写入日志(f"Processing version folder: {版本文件夹}")
    版本文件夹路径 = os.path.join(清单目录, 版本文件夹)

    # 创建并切换到新的分支
    新分支 = branchName(f"Modify-S-{包标识符}-{版本文件夹}-{int(time.time())}")
    print(f"  创建并切换到新分支: {新分支}")
    写入日志(f"  Create and checkout to a new branch: {新分支}")
    subprocess.run(["git", "checkout", "master"], check=True) # 确保从 master 分支开始
    subprocess.run(["git", "fetch", "upstream"], check=True) # 拉取上游修改
    subprocess.run(["git", "rebase", "upstream/master"], check=True) # 变基上游修改
    subprocess.run(["git", "checkout", "-b", 新分支], check=True) # 创建并切换到新的分支

    # 遍历该版本文件夹中的所有文件
    for root, _, files in os.walk(版本文件夹路径):
        for file in files:
            清单文件路径 = os.path.join(root, file)
            
            # 只处理 YAML 文件
            if file.endswith(".yaml"):
                print(f"  正在处理文件: {清单文件路径}")
                写入日志(f"  Processing of manifest: {清单文件路径}")
                with open(清单文件路径, "r", encoding="utf-8") as f:
                    清单文件内容 = f.read()

                清单文件内容 = FormatManifest(清单文件内容, "# Modified with Sundry.")

                # 写回修改后的文件内容
                with open(清单文件路径, "w", encoding="utf-8") as f:
                    f.write(清单文件内容)
                    print(f"  修改后的文件已保存: {清单文件路径}")
                    写入日志(f"    The manifest file has been saved as: {清单文件路径}")
                open_file(清单文件路径)

    input(f"  {Fore.BLUE}修改完后按 Enter 键继续...{Fore.RESET}")

    # 验证清单修改
    print("  验证清单修改")
    验证结果 = subprocess.Popen(
        ["winget", "validate", "--manifest", 版本文件夹路径],
        stdout=subprocess.PIPE, # 捕获标准输出
        stderr=subprocess.PIPE, # 捕获标准错误
        text=True # 输出为字符串
    )

    # 逐行读取并处理输出
    for line in 验证结果.stdout or []:
        if line.endswith("\n"):
            line = line.rstrip('\n') # 去除空行
        # 处理警告
        if ("Manifest Warning" in line) or ("警告" in line):
            写入日志(f"    {line}", "WARNING")
            print(f"{Fore.YELLOW}{line}{Fore.RESET}")
        else:
            写入日志(f"    {line}")
            if ("清单验证成功" not in line): # 避免和下面的输出重复
                print(f"{Fore.BLUE}{line}{Fore.RESET}")

    # 逐行读取并处理错误输出
    for line in 验证结果.stderr or []:
        if line.endswith("\n"):
            line = line.rstrip('\n') # 去除空行
        写入日志(f"    {line}", "ERROR")
        print(f"{Fore.RED}{line}{Fore.RESET}")

    # 等待进程结束并获取返回码
    验证结果.wait()

    if (验证结果.returncode != 0):
        input(f"{Fore.RED}清单验证出现错误，请检查您的清单{Fore.RESET}")
        写入日志("Manifest Error Fixed.")
    else:
        print(f"{Fore.GREEN}  清单验证成功{Fore.RESET}")

    # 暂存、提交并推送
    print("  暂存并提交更改到 Git")
    写入日志("  Staging and Committing Changes to Git")
    subprocess.run(["git", "add", 版本文件夹路径], check=True)
    提交消息 = f"Modify: {包标识符} version {版本文件夹} (Auto)"
    subprocess.run(["git", "commit", "-m", 提交消息], check=True)
    print(f"    提交信息: {提交消息}")
    写入日志(f"    Commit message: {提交消息}")

    # 推送更改到远程仓库
    print("  推送更改到远程仓库")
    写入日志("  Pushing changes to remote (origin) repository")
    subprocess.run(["git", "push", "origin", 新分支], check=True)
    print(f"    {Fore.GREEN}推送到远程成功: {新分支}")
    写入日志(f"    Successfully pushed to remote (origin): {新分支}")

    # 创建拉取请求
    if submitChanges(
        branch=新分支,
        packageIdentifier=包标识符,
        packageVersion=包版本,
        doWhat="Modify",
        information=(f"\n\n{格式化审查者} PTAL" if 格式化审查者 else "") + (f"\n\n{解决}" if 解决 else "")
    ):
        return 0
    else:
        return 1
