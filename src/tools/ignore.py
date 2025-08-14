import os
import re
import time
import requests
import subprocess
from colorama import init, Fore
from function.files.open import open_file
from function.github.token import read_token
from function.maintain.config import 读取配置

def 追加忽略字段(检测程序路径: str, 忽略字段: str, 理由: str) -> bool | str:
    with open(检测程序路径, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 找到 HashSet<string> excludedDomains = 的行
    start_index = next(i for i, line in enumerate(lines) if 'HashSet<string> excludedDomains =' in line)
    end_index = next(i for i, line in enumerate(lines[start_index:]) if '];' in line) + start_index

    # 确保没有重复
    if 忽略字段 in "".join(lines[start_index:end_index]):
        print(f"{Fore.YELLOW}⚠ 该忽略字段已存在{Fore.RESET}")
        return "skip"

    # 查找是否已有相同理由的行
    found = False
    for i in range(start_index, end_index):
        if 理由 in lines[i]:
            # 如果有相同理由的行，则同行追加
            lines[i] = lines[i].replace(f"// {理由}", f"\"{忽略字段}\", // {理由}")
            found = True
            break

    if not found:
        # 如果没有相同理由的行，则新开一行
        lines.insert(end_index, f"                \"{忽略字段}\", // {理由}\n")

    with open(检测程序路径, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    return found

def 移除忽略字段(检测程序路径: str, 忽略字段: str, 新分支名: str):
    with open(检测程序路径, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 找到 HashSet<string> excludedDomains = 的行
    start_index = next(i for i, line in enumerate(lines) if 'HashSet<string> excludedDomains =' in line)
    end_index = next(i for i, line in enumerate(lines[start_index:]) if '];' in line) + start_index

    # 查找是否存在忽略字段
    方式 = None
    for i in range(start_index, end_index):
        line = lines[i].strip()
        match = re.match(r'^\s*"{}"\s*(,?\s*//.*)?\s*$'.format(re.escape(忽略字段)), line)
        if match:
            # 该行仅包含需要移除的忽略字段 - 整行移除
            del lines[i]
            方式 = "移除整行"
            break
        elif (忽略字段 in line):
            # 该行包含需要移除的忽略字段，但该行还有其他忽略字段 - 仅移除该忽略字段
            lines[i] = lines[i].replace(f"\"{忽略字段}\", ", "")
            方式 = "移除字段"
            
    if (not 方式):
        print(f"{Fore.RED}✕ 未找到对应忽略字段{Fore.RESET}")
        subprocess.run(["git", "checkout", "main"], check=True) # 签回
        subprocess.run(["git", "branch", "-D", 新分支名], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 工作区清理完毕")
        return 0

    with open(检测程序路径, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    return 方式

def 列出忽略字段(检测程序路径: str) -> None:
    with open(检测程序路径, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 找到 HashSet<string> excludedDomains = 的行
    start_index = next(i for i, line in enumerate(lines) if 'HashSet<string> excludedDomains =' in line)
    end_index = next(i for i, line in enumerate(lines[start_index:]) if '];' in line) + start_index + 1 # 包含结束行

    # 列出所有忽略字段
    for i in range(start_index, end_index):
        line = lines[i].strip()
        print(line)

def 编辑忽略字段(检测程序路径: str) -> None:
    print(f"{Fore.BLUE}INFO{Fore.RESET} 检测脚本位于 {检测程序路径}")
    print(f"{Fore.BLUE}INFO{Fore.RESET} 在默认程序中打开检测脚本...")
    # 使用默认程序打开检测程序并等待文件关闭
    open_file(检测程序路径)
    input(f"{Fore.BLUE}[!]{Fore.RESET} 请在编辑完成后按 Enter 继续...")


# 创建拉取请求
def 创建拉取请求(分支名: str, owner: str, 忽略字段: str | None = None, 格式化忽略字段: str | None = None, 理由: str | None = None) -> str | int:
    github_token = read_token()
    if not github_token:
        print(f"{Fore.RED}✕{Fore.RESET} 拉取请求创建失败: Token 读取失败")
        return 0
    api = f"https://api.github.com/repos/{owner}/winget-tools/pulls"
    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # =======================
    if owner == "DuckDuckStudio":
        # 对于源仓库 owner 不能添加前缀，否则返回 422
        owner = ""
    else:
        owner = f"{owner}:"

    if not 理由:
        # 追加创建的 PR 不会带理由，因为理由已写入检测脚本
        数据 = {
            "title": f"[Auto] 自动忽略追加 - {格式化忽略字段}",
            "head": f"{owner}{分支名}",
            "base": f"{owner}main",
            "body": f"### 此 PR 由 [Sundry](https://github.com/DuckDuckStudio/Sundry/) 创建，用于向检查代码**添加**忽略字段 `{忽略字段}`"
        }
    elif (理由 == "edit"):
        # sundry ignore edit 的 PR
        数据 = {
            "title": "chore(checker): 更新忽略字段",
            "head": f"{owner}{分支名}",
            "base": f"{owner}main",
            "body": f"### 此 PR 由 [Sundry](https://github.com/DuckDuckStudio/Sundry/) 创建，用于向检查代码**更新**忽略字段"
        }
    else:
        # 移除创建的 PR 会带理由
        数据 = {
            "title": f"[Auto] 自动忽略移除 - {格式化忽略字段}",
            "head": f"{owner}{分支名}",
            "base": f"{owner}main",
            "body": f"### 此 PR 由 [Sundry](https://github.com/DuckDuckStudio/Sundry/) 创建，用于向检查代码**移除**忽略字段 `{忽略字段}`\n理由: {理由}"
        }
    # =======================
    response = requests.post(api, headers=请求头, json=数据)
    if response.status_code == 201:
        print(f"{Fore.GREEN}✓{Fore.RESET} 拉取请求创建成功: {response.json()["html_url"]}")
        subprocess.run(["gh", "pr", "edit", f"{response.json()["html_url"]}", "--add-label", "auto"], check=True)
        subprocess.run(["gh", "pr", "merge", f"{response.json()["html_url"]}", "--auto", "--squash"], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 拉取请求标记成功: {response.json()["html_url"]}")
        return response.json()["html_url"]
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 拉取请求创建失败: {response.status_code} - {response.text}")
        return 0

def main(args: list[str]):
    init(autoreset=True)

    winget_tools目录 = 读取配置("winget-tools")
    if not isinstance(winget_tools目录, str):
        return 1
    
    tools仓库 = 读取配置("tools-repo")
    if not isinstance(tools仓库, tuple):
        return 1
    owner, _ = tools仓库

    os.chdir(winget_tools目录)
    检测程序 = os.path.normpath(os.path.join(winget_tools目录, "checker", "Program.cs"))

    # 使用时传入2个参数，即需要忽略的字段和理由
    if len(args) == 3:
        if (args[0] in ["add", "添加", "新增", "加", "新", "--add"]):
            操作 = "add"
        elif (args[0] in ["remove", "移除", "移", "除", "删", "删除", "--remove"]):
            操作 = "remove"
        else:
            print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
            return 1
        # ===========
        忽略字段 = args[1]
        理由 = args[2]
    elif (args[0] in ["list", "--list", "列", "列出", "现有", "now"]):
        操作 = "list"
    elif (args[0] in ["edit", "编辑", "修改", "编", "--edit"]):
        忽略字段 = "edit" # 签出分支时的占位符
        操作 = "edit"
    else:
        print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

    # 同步
    try:
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始同步...")
        subprocess.run(["git", "checkout", "main"], check=True)
        print(f"{Fore.BLUE}INFO{Fore.RESET}     已签出到 main 分支")
        subprocess.run(["git", "pull"], check=True)
        print(f"{Fore.BLUE}INFO{Fore.RESET}     已拉取远程修改")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}✕{Fore.RESET} 同步失败:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 签出新分支
    # 将忽略字段格式化为git分支接受的字符
    # 1. 只保留字母数字字符和 -、_ 符号
    # 2. 将空格替换为 _
    if (操作 != "list"):
        格式化忽略字段 = ''.join(e for e in 忽略字段 if e.isalnum() or e in ['-', '_']).replace(' ', '_')
        新分支名 = f"Ignore-{格式化忽略字段}-{int(time.time())}"
        subprocess.run(["git", "checkout", "-b", 新分支名], check=True)
        print(f"{Fore.BLUE}INFO{Fore.RESET}     已签出新分支 - {新分支名}")
    print(f"{Fore.GREEN}✓{Fore.RESET} 同步完成")

    # ============ 操作入口 ============
    失败 = False
    if (操作 == "add"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始追加...")

        方式 = 追加忽略字段(检测程序, 忽略字段, 理由)

        if 方式 == "skip":
            # 签回
            subprocess.run(["git", "checkout", "main"], check=True)
            subprocess.run(["git", "branch", "-D", 新分支名], check=True)
            # 直接 return
            return 0
        elif 方式:
            方式 = "同行追加"
        else:
            方式 = "新行追加"

        print(f"{Fore.GREEN}✓{Fore.RESET} 已将忽略字段 {Fore.BLUE}{忽略字段}{Fore.RESET} 和理由 {Fore.BLUE}{理由}{Fore.RESET} 追加到检测程序的忽略列表中 ({Fore.YELLOW}{方式}{Fore.RESET})")

        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始提交和推送...")
        subprocess.run(["git", "add", 检测程序], check=True)
        subprocess.run(["git", "commit", "-m", f"[Auto] 自动忽略追加 - {格式化忽略字段}"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", 新分支名], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功推送到远程")
        if not 创建拉取请求(新分支名, owner, 忽略字段, 格式化忽略字段):
            失败 = True
    elif (操作 == "remove"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始移除...")
        方式 = 移除忽略字段(检测程序, 忽略字段, 新分支名)

        if not 方式:
            return 1
        
        print(f"{Fore.GREEN}✓{Fore.RESET} 已将忽略字段 {Fore.BLUE}{忽略字段}{Fore.RESET} 从检测程序的忽略列表中移除 ({Fore.YELLOW}{方式}{Fore.RESET})")

        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始提交和推送...")
        subprocess.run(["git", "add", 检测程序], check=True)
        subprocess.run(["git", "commit", "-m", f"[Auto] 自动忽略移除 - {格式化忽略字段}"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", 新分支名], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功推送到远程")
        if not 创建拉取请求(新分支名, owner, 忽略字段, 格式化忽略字段, 理由):
            失败 = True
    elif (操作 == "list"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 现有忽略条目:")
        列出忽略字段(检测程序)
    elif (操作 == "edit"):
        编辑忽略字段(检测程序)

        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始提交和推送...")
        subprocess.run(["git", "add", 检测程序], check=True)
        subprocess.run(["git", "commit", "-m", "chore(checker): 更新忽略字段"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", 新分支名], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功推送到远程")
        if not 创建拉取请求(新分支名, owner, 理由="edit"):
            失败 = True

    # ============ 清理工作区 ============
    if (操作 != "list"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始清理工作区...")
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "branch", "-D", 新分支名], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 工作区清理完毕")

    # 汇报结果
    if 失败:
        return 1
    else:
        return 0
