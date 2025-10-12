import os
import re
import io
import csv
import shutil
import zipfile
import tempfile
import requests
from typing import Any
from colorama import Fore, init
from function.print.print import 消息头
import tools.maintain.cleanup as cleanup
from function.files.open import open_file
from urllib.parse import urlparse, parse_qs
from function.github.token import read_token
from function.maintain.config import 读取配置
from exception.request import RequestException
from function.format.github import IssueNumber
from exception.operation import TryOtherMethods

def main(args: list[str]) -> int:
    """sundry logs-analyse <Azure Pipline Url> [是否保留日志文件] [是否显示一般错误/异常]"""

    init(autoreset=True)

    # 获取 Azure Pipline 运行链接
    if len(args) < 1:
        print(f"{消息头.错误} 请提供 Azure Pipline Url")
        return 1

    if args[0].lower() in ["cleanup", "清理", "清理日志"]:
        return cleanup.main("logsAnalyse")
    else:
        print(f"{Fore.BLUE}INFO{Fore.RESET} 正在验证提供的参数...")
        build_id = 获取azp运行id(args[0])
        if not build_id:
            return 1
    
    # 获取该运行的信息（权限公开）
    api_url = f"https://dev.azure.com/shine-oss/winget-pkgs/_apis/build/builds/{build_id}?api-version=7.1"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"{消息头.错误} 无法获取运行信息: {api_url} 响应 {Fore.RED}{response.status_code}{Fore.RESET}")
        return 1
    
    build_info = response.json()
    # 获取管道名称
    pipeline_name = build_info.get("definition", {}).get("name")

    if not pipeline_name:
        print(f"{消息头.错误} 无法确定这是不是验证管道运行")
        return 1
    elif pipeline_name != "WinGetSvc-Validation":
        print(f"{消息头.错误} 这似乎不是验证管道的运行: {pipeline_name}")
        return 1
    
    print(f"{Fore.GREEN}✓{Fore.RESET} 成功验证提供的 Azure Pipline Url。")

    # ===========================================================================================

    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在获取管道运行 ({build_id}) 的日志...")

    # 获取日志下载链接，并将其下载到 %Temp%/Sundry/AzurePiplines/Logs/{build_id}/ 下，没有则创建文件夹
    logs_url = f"https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_apis/build/builds/{build_id}/artifacts?artifactName=InstallationVerificationLogs&api-version=7.1&%24format=zip"
    logs_dir = os.path.join(tempfile.gettempdir(), "Sundry", "AzurePiplines", "Logs", build_id)
    logs_zip_path = os.path.join(logs_dir, "logs.zip")

    # 如果原先存在同名zip文件
    if os.path.exists(logs_zip_path):
        if input(f"{消息头.问题} 下载位置下{Fore.YELLOW}已存在同名日志文件{Fore.RESET} {Fore.BLUE}{logs_zip_path}{Fore.RESET}，我应该移除它吗? [Y/n]: ").lower() not in ["y", "yes", "是", ""]:
            print(f"{消息头.错误} 下载位置下存在同名文件")
            return 1
        else:
            try:
                # 移除它
                os.remove(logs_zip_path)
            except Exception as e:
                print(f"{消息头.错误} 移除同名日志文件时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
                return 1
        
    # 如果解压后的位置存在同名目录
    if os.path.exists(logs_dir):
        if input(f"{消息头.问题} 解压位置下{Fore.YELLOW}已存在同名日志目录{Fore.RESET} {Fore.BLUE}{logs_dir}{Fore.RESET}，我应该移除它吗? [Y/n]: ").lower() not in ["y", "yes", "是", ""]:
            print(f"{消息头.错误} 解压位置下存在同名日志目录")
            return 1
        else:
            try:
                # 移除它
                shutil.rmtree(logs_dir)
            except Exception as e:
                print(f"{消息头.错误} 移除同名日志目录时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
                return 1
    os.makedirs(logs_dir, exist_ok=True)
        
    # 下载日志文件
    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在下载日志文件到 {logs_zip_path}...")
    response = requests.get(logs_url)
    if response.status_code != 200:
        print(f"{消息头.错误} 无法下载日志文件: {logs_url} 响应 {Fore.RED}{response.status_code}{Fore.RESET}")
        return 1
    with open(logs_zip_path, "wb") as f:
        f.write(response.content)
    print(f"{Fore.GREEN}✓{Fore.RESET} 日志文件下载完成。")
    # 解压日志文件
    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在解压日志文件到 {logs_dir}...")
    with zipfile.ZipFile(logs_zip_path, "r") as zip_ref:
        zip_ref.extractall(logs_dir)
    print(f"{Fore.GREEN}✓{Fore.RESET} 日志文件解压完成。")
    # 删除zip日志文件
    os.remove(logs_zip_path)
    print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件压缩包。")

    print(f"{Fore.GREEN}✓{Fore.RESET} 成功获取管道运行 ({build_id}) 的日志。")

    print() # 换行

    # =============================================

    # 看看解压后的日志文件夹中有没有 *.png 文件，有则输出位置
    png_files: list[str] = []
    for root, _, files in os.walk(logs_dir):
        for file in files:
            if file.endswith(".png") and ("ErrorScreenshot" in file):
                png_files.append(os.path.join(root, file))
    if png_files:
        for png_file in png_files:
            print(f"{Fore.CYAN}Screenshot{Fore.RESET} 日志目录下存在错误截图: {Fore.BLUE}{png_file}{Fore.RESET}")

    # 将日志文件夹下的 .txt 替换为 .log
    for root, _, files in os.walk(logs_dir):
        for file in files:
            if file.endswith(".txt"):
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file[:-4] + ".log")
                os.rename(old_path, new_path)
                # print(f"已将 {old_path} 重命名为 {new_path}")

    # 查看日志中是否有带有以下关键词的行
    keyword_map = {
        "[FAIL] Installer failed security check": ("安装程序未通过安全检查", Fore.YELLOW),
        "No suitable installer found": ("未找到合适的安装程序", Fore.YELLOW),
        "ShellExecute installer failed": ("Shell 执行安装程序失败", Fore.YELLOW),
        "Installation failed with exit code": ("以非正常退出代码退出", Fore.RED),
        "Package failed updates, dependency or conflict validation.": ("安装依赖错误", Fore.YELLOW),
    }

    if (len(args) == 3) and (args[2].lower() in ["true", "yes", "y", "是"]):
        # 追加这些关键词
        keyword_map.update({
            "InternetOpenUrl() failed.": ("遇到了网络错误", Fore.RED),
            "MSIX installer failed": ("MSIX 安装程序失败", Fore.RED),
            "fail": ("一般错误", ""),
            "error": ("一般错误", ""),
            "Exception": ("异常", ""),
        })

    # 为特定关键词设置排除子串
    exclude_map = {
        "error": [
            # 无关错误
            "Standard error:", 
            "The FileSystemWatcher has detected an error",
            "error.exe", # 不是错误，只是名字带 error 的可执行文件。例如 Git.Git 的 C:\Program Files\Git\usr\bin\gpg-error.exe
        ],
        "fail": [
            "Failed to open available source: msstore", # msstore 的问题
        ],
    }

    找到可能的问题了吗 = False

    for root, _, files in os.walk(logs_dir):
        for file in files:
            if file.endswith(".log"):
                with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        for keyword, (result, color) in keyword_map.items():
                            exclude_substrings = exclude_map.get(keyword, [])
                            if (
                                (keyword.lower() in line.lower()) # 全部转为小写来不区分大小写
                                and (not any(exclude in line for exclude in exclude_substrings))
                            ):
                                找到可能的问题了吗 = True
                                result_str = f"{color}{result}{Fore.RESET}" if color else result
                                highlighted_line = re.sub(
                                    re.escape(keyword),
                                    lambda m: f"{Fore.RED}{m.group(0)}{Fore.RESET}",
                                    line.strip(),
                                    flags=re.IGNORECASE
                                )
                                print(f"{Fore.CYAN}Analysis{Fore.RESET} {result_str}\n{highlighted_line} {Fore.BLUE}in{Fore.RESET} {file}")
                                if keyword == "Installation failed with exit code":
                                    # Installation failed with exit code 123
                                    匹配 = re.search(r"exit code (-?\d+)", line, re.IGNORECASE)
                                    if 匹配:
                                        查找错误代码解释(匹配.group(1))
                                    else:
                                        print(f"{消息头.提示} 您可以尝试在 https://github.com/microsoft/winget-cli/blob/master/doc/windows/package-manager/winget/returnCodes.md 上查找对应退出代码的解释。")
                                        print(f"{消息头.提示} 也可以尝试在 https://github.com/microsoft/winget-pkgs/edit/master/Tools/ManualValidation/ExitCodes.csv 上查找对应退出代码的解释。")
                                elif keyword in ["ShellExecute installer failed", "MSIX installer failed"]:
                                    # keyword: 123
                                    匹配 = re.search(f"{keyword}:\\s*(-?\\d+)", line, re.IGNORECASE)
                                    if 匹配:
                                        查找错误代码解释(匹配.group(1))
                                elif keyword == "No suitable installer found":
                                    print(f"{消息头.提示} 这可能是因为您提交的软件包的安装程序定义和依赖中的安装程序定义不匹配。")
                                    print(f"{消息头.提示} 举个例子，当上游依赖只支持 x64 架构，而您提交的清单中的安装程序还支持 x86 架构时，WinGet 会因为找不到 x86 的依赖安装程序而失败。")
                                    print(f"{消息头.提示} 具体需要如何处理此错误尚不确定: https://github.com/microsoft/winget-pkgs/issues/152555")
                                elif keyword == "Package failed updates, dependency or conflict validation.":
                                    print(f"{消息头.提示} 这可能是因为你在清单中指定的包依赖在 winget 源中并不存在，请检查并提交依赖清单。")
                                    查找错误代码解释("80073CF3")
                                elif "0x" in line:
                                    # 0x00000000 (Hex, 0x + 8个字符)
                                    # 不是每个错误代码都能找到解释的，没找到解释就没显示
                                    匹配 = re.search(r"0x[0-9A-Fa-f]{8}", line)
                                    if 匹配:
                                        查找错误代码解释(匹配.group(0))
                                print() # 换行
                                break

    if not 找到可能的问题了吗:
        print(f"{消息头.警告} 未找到可能的问题")
        if not ((len(args) == 3) and (args[2].lower() in ["true", "yes", "y", "是"])):
            if (len(args) == 2):
                print(f"{消息头.提示} 请尝试使用 {Fore.BLUE}sundry logs-analyse \"{args[0]}\" \"{args[1]}\" y{Fore.RESET} 来查看一般错误/异常")
            else:
                print(f"{消息头.提示} 请尝试使用 {Fore.BLUE}sundry logs-analyse \"{args[0]}\" \"[是否保留日志文件]\" y{Fore.RESET} 来查看一般错误/异常")

    if (len(args) >= 2):
        if (args[1].lower() in ["true", "yes", "y", "是"]):
            return open_file(logs_dir)
        elif (args[1].lower() in ["false", "no", "n", "否"]):
            # 移除它
            shutil.rmtree(logs_dir)
            print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件目录。")
        else:
            print(f"{消息头.警告} 指定的参数 1 无效，{Fore.BLUE}{args[1]}{Fore.RESET} 不能表达是否要保留日志文件")
            if (input(f"{消息头.问题} 你想要保留日志文件吗? [Y/n]: ").lower() in ["y", "yes", "是", ""]):
                return open_file(logs_dir)
            else:
                # 移除它
                shutil.rmtree(logs_dir)
                print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件目录。")
    else:
        if (input(f"{消息头.问题} 你想要保留日志文件吗? [Y/n]: ").lower() in ["y", "yes", "是", ""]):
            return open_file(logs_dir)
        else:
            # 移除它
            shutil.rmtree(logs_dir)
            print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件目录。")

    return 0

def 获取最新的验证管道运行(api: str) -> str | None:
    """
    传入 PR Comments API，返回 Azp 验证管道运行链接。
    """

    try:
        响应 = requests.get(api)
        响应.raise_for_status()
        数据 = 响应.json()
        body = 获取最新的验证管道评论(数据)
        if not body:
            return None
        match = re.search(r"\((https?://[^)]+)\)", body)
        if match:
            return match.group(1)
        else:
            return None
    except requests.HTTPError as e:
        print(f"{消息头.错误} 请求 GitHub API 时出现异常: {Fore.RED}{type(e)} {e}{Fore.RESET}")
        return None
    
def 获取最新的验证管道评论(data: list[dict[str, Any]]) -> str | None:
    """
    传入 PR Comments API 响应数据，返回最新的验证管道运行评论 body。
    """

    验证评论: list[dict[str, Any]] = []
    
    for comment in data:
        user: dict[str, Any] = comment.get("user", {})
        login: str = user.get("login", "wingetbot")
        body: str = comment.get("body", "")
        if (login == "wingetbot" and "WinGetSvc-Validation" in body):
            验证评论.append(comment)
    
    if 验证评论:
        # 按创建时间排序，最新的在前
        验证评论.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return 验证评论[0]["body"]
    else:
        return None

def 获取azp运行id(已知URL: str) -> str | None:
    """
    给定当前已知的 URL (GitHub PR 或 Azure Pipline Run)，返回 *PR 最新的 / 指定的* Azure Pipline 运行的 id (buildId)。

    没有获取到则返回 None，错误输出函数内处理。
    """

    if 已知URL.startswith("https://github.com/") or 已知URL.isdigit():
        议题编号 = IssueNumber(已知URL)
        if not 议题编号:
            print(f"{消息头.错误} 未能获取 GitHub PR 编号")
            return None
        azpUrl = 获取最新的验证管道运行(f"https://api.github.com/repos/microsoft/winget-pkgs/issues/{议题编号}/comments")
        if not azpUrl:
            print(f"{消息头.错误} 未能获取到最新验证管道运行链接，请尝试直接指定 Azure 管道运行链接")
            print(f"{消息头.提示} 管道运行链接获取方法: https://duckduckstudio.github.io/Articles/#/信息速查/终端/WinGet/参考信息#验证管道日志在哪看？")
            return None
    elif 已知URL.startswith("https://dev.azure.com/"):
        azpUrl = 已知URL
    else:
        print(f"{消息头.错误} 指定的 Azure 管道运行或 GitHub PR 链接不是有效格式")
        return None

    # 从 URL 中提取 buildId
    buildId = parse_qs(urlparse(azpUrl).query).get("buildId", [None])[0]
    if not buildId:
        print(f"{消息头.错误} 未能从 Azure Pipline 运行链接中获取 buildId 参数的值")
        return None

    return buildId

def 查找错误代码解释(ExitCode: str):
    """尝试从 ExitCodes.csv 中找 exit_code 的解释"""

    # ExitCodes.csv 示例
    # "Hex","Dec","InvDec","Symbol","Description"
    # "00000000","0","-4294967296","ERROR_SUCCESS","The operation completed successfully."
    # "00000001","1","-4294967295","ERROR_INVALID_FUNCTION","Incorrect function."
    # "00000002","2","-4294967294","ERROR_FILE_NOT_FOUND","The system cannot find the file specified."
    # "00000003","3","-4294967293","ERROR_PATH_NOT_FOUND","The system cannot find the path specified."
    # ...

    ExitCodes = None

    try:
        winget_pkgs仓库 = 读取配置("paths.winget-pkgs", 静默=True)
        if isinstance(winget_pkgs仓库, str):
            ExitCodesFile = os.path.join(winget_pkgs仓库, "Tools", "ManualValidation", "ExitCodes.csv")
            if os.path.exists(ExitCodesFile):
                try:
                    with open(ExitCodesFile, "r", encoding="utf-8") as csvFile:
                        ExitCodes = io.StringIO(csvFile.read())
                except PermissionError:
                    raise TryOtherMethods
            else:
                raise TryOtherMethods
        else:
            raise TryOtherMethods
    except TryOtherMethods:
        # 既然用户本地无法读取这个文件，就从 GitHub 上获取
        # https://github.com/microsoft/winget-pkgs/blob/master/Tools/ManualValidation/ExitCodes.csv
        github_token = read_token()
        csvStr = 获取GitHub文件内容(github_token, "microsoft/winget-pkgs", "Tools/ManualValidation/ExitCodes.csv")
        if csvStr:
            ExitCodes = io.StringIO(csvStr)

    if ExitCodes:
        reader = csv.DictReader(ExitCodes)
        for row in reader:
            if ExitCode in [row["Hex"], row["Dec"], row["InvDec"], row["Symbol"]]:
                print(f"{消息头.提示} 此错误代码或许代表:")
                print(f"{消息头.提示} {" | ".join([f"Hex: {Fore.BLUE}{row['Hex']}{Fore.RESET}", f"Dec: {Fore.BLUE}{row['Dec']}{Fore.RESET}", f"InvDec: {Fore.BLUE}{row['InvDec']}{Fore.RESET}", f"Symbol: {Fore.BLUE}{row['Symbol']}{Fore.RESET}", f"Description: {Fore.BLUE}{row['Description']}{Fore.RESET}"]).replace(f"{Fore.BLUE}{ExitCode}{Fore.RESET}", f"{Fore.MAGENTA}{ExitCode}{Fore.RESET}")}")

def 请求GitHubAPI(apiUrl: str, github_token: str | int):
    请求头 = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    if not github_token:
        # 移除 Authorization 头
        请求头.pop("Authorization", None)
    try:
        响应 = requests.get(apiUrl, headers=请求头)
        
        if 响应.status_code == 404:
            raise RequestException("PR 不存在或对应分支已被删除")
        elif 响应.status_code >= 400:
            raise RequestException(响应)
        else:
            return 响应.json()
    except RequestException:
        return

def 获取GitHub文件内容(github_token: str | int, 仓库: str, 文件路径: str):
    try:
        # 由于政府政策，在中国大陆不允许使用 raw.githubusercontent.com
        # 127.0.0.1 欢迎你 XD
        # raw_url = f"https://raw.githubusercontent.com/{仓库}/refs/heads/{分支}/{文件路径}"

        api = f"https://api.github.com/repos/{仓库}/contents/{文件路径}"
        响应 = 请求GitHubAPI(api, github_token)
        if not 响应:
            raise RequestException(f"响应为空: {响应}")

        import base64
        return base64.b64decode(响应["content"]).decode("utf-8")
    except Exception:
        return
