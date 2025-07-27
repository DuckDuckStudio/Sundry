import os
import sys
import csv
import json
import time
import random
import requests
import subprocess
from typing import Union
from datetime import datetime
from colorama import init, Fore
from function.files.open import open_file
from function.github.token import read_token

def main(args: list[str]):
    global 软件包标识符, 软件包版本, 日志文件路径, 解决, 清单目录, 首个_PR, 格式化审查者
    global 配置文件, 程序所在目录, 旧清单版本号, 新清单版本号
    global owner

    init(autoreset=True)

    # 目录路径
    # 尝试从参数中获取软件包标识符和版本
    if (2 <= len(args) <= 3):
        软件包标识符 = args[0]
        软件包版本 = args[1]
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
        print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1
    
    # 路径
    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")
    程序所在目录 = os.path.dirname(os.path.abspath(sys.argv[0]))
    日志文件路径 = os.path.join("logs", datetime.today().strftime('%Y\\%m\\%d'), f"{软件包标识符}-{软件包版本}.log") # 相对路径

    # 需要替换的版本号
    旧清单版本号 = ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0", "1.9.0"]
    新清单版本号 = "1.10.0"

    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            if 配置数据["winget-pkgs"]:
                winget_pkgs目录 = os.path.normpath(配置数据["winget-pkgs"])
                if (not os.path.exists(winget_pkgs目录)):
                    print(f"{Fore.RED}✕{Fore.RESET} 配置文件中的目录 {Fore.BLUE}{winget_pkgs目录}{Fore.RESET} 不存在")
                    print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                    return 1
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"winget-pkgs\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-pkgs [路径] 来修改配置文件中的值")
                return 1
            # ========================================
            if 配置数据["pkgs-repo"]:
                try:
                    owner, _ = 配置数据["pkgs-repo"].split("/")
                except Exception as e:
                    print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败: {Fore.RED}解析 pkgs-repo 配置项失败{Fore.RESET}\n{Fore.RED}{e}{Fore.RESET}")
                    return 1
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"pkgs-repo\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config pkgs-repo [所有者/仓库名] 来修改配置文件中的值")
                return 1
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        return 1

    清单目录 = os.path.join(winget_pkgs目录, "manifests", 软件包标识符[0].lower(), *软件包标识符.split('.'))

    # 预先检查
    格式化审查者 = ""
    with open(os.path.join(winget_pkgs目录, "Tools", "Auth.csv"), mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        # 遍历 CSV 文件中的每一行
        found = False # 标记是否找到了包标识符
        for row in csv_reader:
            if row['PackageIdentifier'] == 软件包标识符:
                found = row['Account']
                break # 找到后退出循环

        if found:
            input(f"{Fore.YELLOW}⚠ 看起来此软件包在 Auth.csv 中被要求所有者({found})审查，您还是想要更新此软件包吗(这将在首个PR中@审查者，并在后续PR中提及首个PR):{Fore.RESET}")
            审查者列表 = found.split('/')
            格式化审查者 = ' , '.join([f"@{审查者}" for 审查者 in 审查者列表])
            首个_PR = "是"

    # ========= 日志 配置 开始 =========
    os.chdir(程序所在目录)
    os.makedirs(os.path.join(程序所在目录, "logs", datetime.today().strftime('%Y\\%m\\%d')), exist_ok=True) # 创建今日日志文件夹
    with open(os.path.join(程序所在目录, 日志文件路径), 'w') as 日志文件:
        日志文件.write('~~ Start logging ~~\n') # 初始化日志文件

    # 打开文件并读取所有行 - FUN
    with open(os.path.join(程序所在目录, "fun.txt"), 'r', encoding='utf-8') as file:
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
                            # 如果这个版本文件夹下面还有目录，则代表这可能是类似 Nightly 版本的软件包的标识符的一部分
                            break
                    else:
                        # 如果前面的 for 没有 break，则执行
                        版本文件夹s.append(文件夹)
            print(f"找到以下版本文件夹: {版本文件夹s}")
            写入日志(f"Found the following version folder: {版本文件夹s}")
            break
        except FileNotFoundError as e:
            print(f"{Fore.RED}✕{Fore.RESET} {Fore.RED}{e}{Fore.RESET}")
            写入日志(f"Error getting package version number folder: {e}")
            try:
                input("是否重新查找? [ENTER/CTRL+C]")
                写入日志("Trying to re-find...")
            except KeyboardInterrupt:
                print(f"\n{Fore.BLUE}[INFO]{Fore.RESET} 了解，正在关闭日志...")
                写入日志("User interrupted the process, exiting...")
                with open(os.path.join(程序所在目录, 日志文件路径), 'a') as 日志文件: # 追加写入
                    日志文件.write("~~ End of logging ~~\n")
                print(f"{Fore.BLUE}[INFO]{Fore.RESET} 日志已关闭，正在退出...")
                return 1

    # 确保有获取到至少一个版本文件夹
    if not 版本文件夹s:
        print(f"{Fore.RED}✕{Fore.RESET} 没有找到任何版本文件夹，请检查参数是否正确。")
        写入日志("No version folder found.", "ERROR")
        with open(os.path.join(程序所在目录, 日志文件路径), 'a') as 日志文件: # 追加写入
            日志文件.write("~~ End of logging ~~\n")
        print(f"{Fore.BLUE}[INFO]{Fore.RESET} 日志已关闭，正在退出...")
        return 1

    # 遍历所有版本并进行处理
    for 版本文件夹 in 版本文件夹s:
        if 版本文件夹 != 软件包版本:
            print(f"跳过版本文件夹: {版本文件夹}")
            写入日志(f"Skip version {版本文件夹}, because it's not in the list of versions to be modified.")
            continue
        if 修改版本(版本文件夹) == 1:
            with open(os.path.join(程序所在目录, 日志文件路径), 'a') as 日志文件:
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
    with open(os.path.join(程序所在目录, 日志文件路径), 'a') as 日志文件: # 追加写入
        日志文件.write('~~ End of logging ~~\n')
    print(f"{Fore.GREEN}✓{Fore.RESET} 成功修改 {Fore.BLUE}{软件包标识符}{Fore.RESET} 版本 {Fore.BLUE}{软件包版本}{Fore.RESET} 的清单。")
    # ========= 日志关闭 结束 =========

    return 0

def 写入日志(消息: str, 等级: str="INFO"):
    global 程序所在目录, 日志文件路径
    现在时间 = datetime.now()
    写入时间 = 现在时间.strftime('%Y-%m-%d %H:%M:%S.') + str(现在时间.microsecond)[:3] # 格式化日志时间 YYYY-MM-DD HH:MM:SS.ms
    with open(os.path.join(程序所在目录, 日志文件路径), 'a') as 日志文件: # 追加写入
        for 行 in 消息.split("\n"):
            日志文件.write(f"{写入时间} {等级} {行}\n")

# 创建拉取请求
def 创建拉取请求(分支名: str, 版本文件夹: str, 审查: str="") -> Union[str, int]:
    # 审查:
    # False -> 不请求审查
    # 带 @ 的字符串 -> 在 PR body 中 @ 审查者
    # 不带 @ 的字符串 -> 在 PR body 中引用首个拉取请求
    global 解决
    github_token = read_token()
    if not github_token:
        print(f"{Fore.RED}✕{Fore.RESET} 拉取请求创建失败: Token 读取失败")
        return 1
    api = "https://api.github.com/repos/microsoft/winget-pkgs/pulls"
    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    数据 = {
        "title": f"Modify: {软件包标识符} version {版本文件夹} (Auto)",
        "head": f"{owner}:{分支名}",
        "base": "master",
        "body": f"### This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/)🚀.\n\n{审查}\n{解决}\n\n---\n"
    }

    while (True):
        response = requests.post(api, headers=请求头, json=数据)
        if response.status_code == 201:
            print(f"    {Fore.GREEN}拉取请求创建成功: {response.json()["html_url"]}")
            写入日志(f"    Pull request created successfully: {response.json()["html_url"]}")
            break
        else:
            print(f"    {Fore.RED}拉取请求创建失败: {response.status_code} - {response.text}")
            写入日志(f"    Failed to create pull request: {response.status_code} - {response.text}", "ERROR")
            try:
                if input(f"{Fore.BLUE}?{Fore.RESET} 我应该重试吗[Y/N]: ").lower() not in ["y", "yes", "应该", "要", "重试", "retry"]:
                    return 1
                print("正在重试...")
                写入日志("    Retrying to create a pull request...")
            except KeyboardInterrupt:
                return 1

    return response.json()["html_url"]

# Git 操作部分
def 修改版本(版本文件夹: str):
    global 首个_PR
    print(f"\n正在处理版本文件夹: {版本文件夹}")
    写入日志(f"Processing version folder: {版本文件夹}")
    版本文件夹路径 = os.path.join(清单目录, 版本文件夹)

    # 创建并切换到新的分支
    新分支 = f"Modify-S-{软件包标识符}-{版本文件夹}-{int(time.time())}"
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

                # =========================== 必经修改 =========================
                # 修改 ManifestVersion 和版本号
                for 清单中的旧清单版本号 in 旧清单版本号:
                    # 修改 ManifestVersion
                    if f"ManifestVersion: {清单中的旧清单版本号}" in 清单文件内容:
                        print(f"    替换 ManifestVersion: {清单中的旧清单版本号} -> {新清单版本号}")
                        写入日志(f"    Replace ManifestVersion: {清单中的旧清单版本号} -> {新清单版本号}")
                        清单文件内容 = 清单文件内容.replace(f"ManifestVersion: {清单中的旧清单版本号}", f"ManifestVersion: {新清单版本号}")

                    # 修改 schema 引用，只替换版本号部分
                    schema_line = f"{清单中的旧清单版本号}.schema.json"
                    if schema_line in 清单文件内容:
                        print(f"    替换 schema 引用: {清单中的旧清单版本号}.schema.json -> {新清单版本号}.schema.json")
                        写入日志(f"    Replace schema references: {清单中的旧清单版本号}.schema.json -> {新清单版本号}.schema.json")
                        清单文件内容 = 清单文件内容.replace(f"{清单中的旧清单版本号}.schema.json", f"{新清单版本号}.schema.json")

                # 替换工具注释
                '''
                判断是否 `清单文件内容`为空 或 第一行以`#`开头
                    如果是，在`清单文件内容`第一行前面追加三行`# Modified with Sundry.`与`# yaml-language-server: $schema=...`与一个空行。
                否则，`清单文件内容`有内容且第一行以`#`开头
                    再判断`清单文件内容`第一行是否以`# yaml-language-server`开头
                        如果是，在`清单文件内容`第一行前面追加一行`# Modified with Sundry.`
                        如果不是，将`清单文件内容`第一行替换为`# Modified with Sundry.`
                '''

                # 按行分割文件内容
                lines = 清单文件内容.splitlines()

                if (not lines) or (not lines[0].startswith("#")): # DuckDuckStudio/Sundry#28
                    # 如果清单文件内容为空或第一行不是以#开头
                    # 第一行前面追加三行
                    lines.insert(0, "")
                    if 'installer' in file: # 安装程序清单
                        lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.{新清单版本号}.schema.json")
                    elif 'locale' in file: # 区域清单
                        if 'defaultLocale' in 清单文件内容: # 默认区域清单
                            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.{新清单版本号}.schema.json")
                        else: # 一般区域清单
                            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.locale.{新清单版本号}.schema.json")
                    else: # 版本清单
                        lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.{新清单版本号}.schema.json")
                    lines.insert(0, "# Modified with Sundry.")
                # 否则第一行是#开头
                else:
                    # 判断第一行是否以# yaml-language-server开头
                    if lines[0].startswith("# yaml-language-server"):
                        # 如果是，追加一行
                        lines.insert(0, "# Modified with Sundry.")
                    else:
                        # 否则，替换第一行
                        lines[0] = "# Modified with Sundry."

                # 将修改后的内容重新合并为一个字符串并赋值回清单文件内容
                清单文件内容 = "\n".join(lines)

                # 确保最后有且只有一行空行
                if not 清单文件内容.endswith('\n'): # 如果最后没有换行符
                    清单文件内容 += '\n' # 添加一个换行符
                else: # 如果有了
                    清单文件内容 = 清单文件内容.rstrip('\n') + '\n'
                    # 管他几个先全移除 -> 添加一个换行符
                    # .rstrip() 去除文本末尾的指定字符

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
        print(f"{Fore.GREEN}  清单验证成功")

    # 暂存、提交并推送
    print("  暂存并提交更改到 Git")
    写入日志("  Staging and Committing Changes to Git")
    subprocess.run(["git", "add", 版本文件夹路径], check=True)
    提交消息 = f"Modify: {软件包标识符} version {版本文件夹} (Auto)"
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
    if 格式化审查者:
        if 首个_PR == "是":
            首个_PR = 创建拉取请求(新分支, 版本文件夹, f"{格式化审查者} PTAL")
            if 首个_PR == 1:
                return 1 # 创建拉取请求时出错
        else:
            if 创建拉取请求(新分支, 版本文件夹, f"Review has been requested in {首个_PR}") == 1:
                return 1 # 创建拉取请求时出错
    else:
        if 创建拉取请求(新分支, 版本文件夹) == 1:
            return 1 # 创建拉取请求时出错

    return 0 # 成功处理版本文件夹
