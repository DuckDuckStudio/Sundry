import os
import re
import json
import keyring
import requests
import subprocess
from colorama import init, Fore

def main(args, Sundry版本号):
    init(autoreset=True)

    # 配置文件路径
    配置文件 = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")

    if os.path.exists(配置文件):
        try:
            with open(配置文件, "r", encoding="utf-8") as f:
                配置数据 = json.load(f)
            
            if 配置数据["winget-tools"]:
                winget_tools目录 = 配置数据["winget-tools"]
                if (not os.path.exists(winget_tools目录)):
                    print(f"{Fore.RED}✕{Fore.RESET} 配置文件中的目录 {Fore.BLUE}{winget_tools目录}{Fore.RESET} 不存在")
                    print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-tools [路径] 来修改配置文件中的值")
                    return 1
            else:
                print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}值 \"winget-tools\" 为空{Fore.RESET}")
                print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config winget-tools [路径] 来修改配置文件中的值")
                return 1
        except Exception as e:
            print(f"{Fore.RED}✕{Fore.RESET} 读取配置文件失败:\n{Fore.RED}{e}{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕{Fore.RESET} 配置文件不存在")
        print(f"{Fore.BLUE}[!]{Fore.RESET} 运行 sundry config init 来初始化配置文件")
        return 1

    os.chdir(winget_tools目录)
    检测程序 = os.path.join(winget_tools目录, "auto_script", "check", "checker", "Program.cs")

    # 使用时传入2个参数，即需要忽略的字段和理由
    if len(args) == 3:
        if (args[0] in ["add", "添加", "新增", "加", "新"]):
            操作 = "add"
        elif (args[0] in ["remove", "移除", "移", "除", "删", "删除"]):
            操作 = "remove"
        else:
            print(f"{Fore.RED}✕ 请按照以下格式传入参数:{Fore.RESET}")
            print(f"{Fore.BLUE}    sundry ignore [add/remove] [忽略字段] [理由]{Fore.RESET}")
            return 1
        # ===========
        忽略字段 = args[1]
        理由 = args[2]
    elif (args[0] in ["list", "--list", "列", "列出", "现有", "now"]):
        操作 = "list"
    else:
        print(f"{Fore.RED}✕ 请按照以下格式传入参数:")
        print(f"{Fore.BLUE}sundry ignore [add/remove/list] [忽略字段] [理由]")
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
        subprocess.run(["git", "checkout", "-b", f"Ignore-{格式化忽略字段}"], check=True)
        print(f"{Fore.BLUE}INFO{Fore.RESET}     已签出新分支 - Ignore-{格式化忽略字段}")
    print(f"{Fore.GREEN}✓{Fore.RESET} 同步完成")

    # ============ 操作入口 ============
    if (操作 == "add"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始追加...")

        方式 = 追加忽略字段(检测程序, 忽略字段, 理由)
        if 方式:
            方式 = "同行追加"
        else:
            方式 = "新行追加"

        print(f"{Fore.GREEN}✓{Fore.RESET} 已将忽略字段 {Fore.BLUE}{忽略字段}{Fore.RESET} 和理由 {Fore.BLUE}{理由}{Fore.RESET} 追加到检测程序的忽略列表中 ({Fore.YELLOW}{方式}{Fore.RESET})")

        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始提交和推送...")
        subprocess.run(["git", "add", 检测程序], check=True)
        subprocess.run(["git", "commit", "-m", f"[Auto] 自动忽略追加 - {格式化忽略字段}"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", f"Ignore-{格式化忽略字段}"], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功推送到远程")
        创建拉取请求(忽略字段, 格式化忽略字段, Sundry版本号)
    elif (操作 == "remove"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始移除...")
        方式 = 移除忽略字段(检测程序, 忽略字段, 格式化忽略字段)
        
        print(f"{Fore.GREEN}✓{Fore.RESET} 已将忽略字段 {Fore.BLUE}{忽略字段}{Fore.RESET} 从检测程序的忽略列表中移除 ({Fore.YELLOW}{方式}{Fore.RESET})")

        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始提交和推送...")
        subprocess.run(["git", "add", 检测程序], check=True)
        subprocess.run(["git", "commit", "-m", f"[Auto] 自动忽略移除 - {格式化忽略字段}"], check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", f"Ignore-{格式化忽略字段}"], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 成功推送到远程")
        创建拉取请求(忽略字段, 格式化忽略字段, Sundry版本号, 理由)
    elif (操作 == "list"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 现有忽略条目:")
        列出忽略字段(检测程序)

    # ============ 清理工作区 ============
    if (操作 != "list"):
        print(f"{Fore.BLUE}INFO{Fore.RESET} 开始清理工作区...")
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "branch", "-D", f"Ignore-{格式化忽略字段}"], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 工作区清理完毕")

def 追加忽略字段(检测程序路径, 忽略字段, 理由):
    with open(检测程序路径, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 找到 HashSet<string> excludedDomains = 的行
    start_index = next(i for i, line in enumerate(lines) if 'HashSet<string> excludedDomains =' in line)
    end_index = next(i for i, line in enumerate(lines[start_index:]) if '];' in line) + start_index

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

def 移除忽略字段(检测程序路径, 忽略字段, 格式化忽略字段):
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
        subprocess.run(["git", "branch", "-D", f"Ignore-{格式化忽略字段}"], check=True)
        print(f"{Fore.GREEN}✓{Fore.RESET} 工作区清理完毕")
        return 1

    with open(检测程序路径, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    return 方式

def 列出忽略字段(检测程序路径):
    # 暂不做单理由查找
    with open(检测程序路径, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 找到 HashSet<string> excludedDomains = 的行
    start_index = next(i for i, line in enumerate(lines) if 'HashSet<string> excludedDomains =' in line)
    end_index = next(i for i, line in enumerate(lines[start_index:]) if '];' in line) + start_index

    # 列出所有忽略字段
    for i in range(start_index, end_index):
        line = lines[i].strip()
        print(line)
    return

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

# 创建拉取请求
def 创建拉取请求(忽略字段, 格式化忽略字段, Sundry版本号, 理由=None):
    github_token = read_token()
    api = "https://api.github.com/repos/DuckDuckStudio/winget-tools/pulls"
    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # =======================
    if not 理由:
        # 追加创建的 PR 不会带理由，因为理由已写入检测脚本
        数据 = {
            "title": f"[Auto] 自动忽略追加 - {格式化忽略字段}",
            "head": f"DuckDuckStudio:Ignore-{格式化忽略字段}",
            "base": "main",
            "body": f"### 此 PR 由 [Sundry](https://github.com/DuckDuckStudio/Sundry/) {Sundry版本号} 创建，用于向检查代码**添加**忽略字段 `{忽略字段}`"
        }
    else:
        # 移除创建的 PR 会带理由
        数据 = {
            "title": f"[Auto] 自动忽略移除 - {格式化忽略字段}",
            "head": f"DuckDuckStudio:Ignore-{格式化忽略字段}",
            "base": "main",
            "body": f"### 此 PR 由 [Sundry](https://github.com/DuckDuckStudio/Sundry/) {Sundry版本号} 创建，用于向检查代码**移除**忽略字段 `{忽略字段}`\n理由: {理由}"
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
        input(f"{Fore.RED}✕{Fore.RESET} 拉取请求创建失败: {response.status_code} - {response.text}")
