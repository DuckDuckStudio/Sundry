import os
import re
import io
import csv
import json
import shutil
import zipfile
import requests
from typing import Any
from colorama import Fore
import tools.maintain.cleanup as cleanup
from catfood.functions.print import 消息头
from urllib.parse import urlparse, parse_qs
from function.github.token import read_token
from function.maintain.config import 读取配置
from catfood.functions.files import open_file
from function.constant.paths import AZP_LOGS_DIR
from catfood.functions.format.github import IssueNumber
from catfood.exceptions.operation import TryOtherMethods
from function.constant.logsAnalyse import EXE_LIST_LIMIT
from catfood.functions.github.api import 获取GitHub文件内容

def main(args: list[str]) -> int:
    """`sundry logs-analyse <Url> [是否保留日志文件] [是否显示一般错误/异常]`"""

    # 获取 Azure Pipeline 运行链接
    if len(args) < 1:
        print(f"{消息头.错误} 请提供 GitHub PR 或 Azure Pipeline Run 的链接")
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
    
    print(f"{Fore.GREEN}✓{Fore.RESET} 成功验证提供的链接。")

    # ===========================================================================================

    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在获取管道运行 ({build_id}) 的日志...")

    logs_dir = os.path.join(AZP_LOGS_DIR, build_id)

    for i in ["InstallationVerificationLogs", "ValidationResult"]:
        if os.path.exists(os.path.join(logs_dir, i)):
            if input(f"{消息头.问题} 解压位置下{Fore.YELLOW}已存在同名目录{Fore.RESET} {Fore.BLUE}{os.path.join(logs_dir, i)}{Fore.RESET}，我应该移除它吗? [Y/n]: ").lower() in ["n", "no", "不", "不要", "否"]:
                print(f"{消息头.错误} 解压位置下存在同名目录")
                return 1
            else:
                try:
                    # 移除它
                    shutil.rmtree(os.path.join(logs_dir, i))
                except Exception as e:
                    print(f"{消息头.错误} 移除同名目录时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
                    return 1
        os.makedirs(os.path.join(logs_dir, i), exist_ok=True)

        # ========================================================================

        try:
            print(f"{消息头.信息} 正在下载 {i}.zip ...")
            response = requests.get(f"https://dev.azure.com/shine-oss/winget-pkgs/_apis/build/builds/{build_id}/artifacts?artifactName={i}&api-version=7.1&%24format=zip")
            response.raise_for_status()
            with open(os.path.join(logs_dir, i, f"{i}.zip"), "wb") as f:
                f.write(response.content)
            print(f"{消息头.成功} {i}.zip 下载完成")
        except requests.HTTPError as e:
            print(f"{消息头.错误} 下载 {i}.zip 失败: {Fore.RED}{e}{Fore.RESET}")
            shutil.rmtree(os.path.join(logs_dir, i))
            continue
        
        try:
            with zipfile.ZipFile(os.path.join(logs_dir, i, f"{i}.zip"), "r") as zip_ref:
                zip_ref.extractall(os.path.join(logs_dir, i))
            os.remove(os.path.join(logs_dir, i, f"{i}.zip"))
            print(f"{消息头.成功} {i}.zip 解压完成")
        except Exception as e:
            print(f"{消息头.错误} 解压 {i}.zip 失败: {Fore.RED}{e}{Fore.RESET}")
            shutil.rmtree(os.path.join(logs_dir, i))
            continue

    if not os.listdir(logs_dir):
        print(f"{消息头.错误} 未能获取到任何日志")
        return 1

    print() # 换行

    # =============================================

    found = False
    detailed = ((len(args) == 3) and (args[2].lower() in ["true", "yes", "y", "是"]))

    if os.path.exists(os.path.join(logs_dir, "InstallationVerificationLogs")):
        found = 分析InstallationVerificationLogs(os.path.join(logs_dir, "InstallationVerificationLogs"), detailed)

    if os.path.exists(os.path.join(logs_dir, "ValidationResult")):
        found = 分析ValidationResult(os.path.join(logs_dir, "ValidationResult"), detailed) or found

    if not found:
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

def 分析ValidationResult(dir_path: str, detailed: bool = False) -> bool:
    """
    在 ValidationResult 中查找错误信息，并输出找到的信息。

    :param dir_path: 结果文件目录
    :type dir_path: str
    :return: 返回是否找到错误信息
    :rtype: bool
    """

    found = False

    result_dict: dict[str, list[str]] = {
        # "退出代码": ["exe1", "exe2", ...]
    }

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file == "InstallationVerification_Result.json":
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    data: dict[str, Any] = json.load(f)
                    if data.get("OverallResult") == "Success":
                        return False
                    for result in data.get("AnalysisResults", []):
                        if result.get("AnalysisType") == "ExeRunInfo":
                            for exe_path, diag_info in result.get("Diagnostics", {}).items():
                                if diag_info.get("ExecutionStatusResult", "Pass") != "Pass":
                                    if (exit_code := diag_info.get("ExitCode")) != 0:
                                        found = True
                                        try:
                                            result_dict[exit_code].append(exe_path)
                                        except KeyError:
                                            result_dict[exit_code] = [exe_path]

                                        output = ""
                                        if diag_info.get("ErrorStream", ""):
                                            output = f"{Fore.RED}{diag_info.get("ErrorStream", "")}{Fore.RESET}"
                                        if diag_info.get("OutputStream", ""):
                                            output += diag_info.get("OutputStream", "")
                                        if output:
                                            print(f"{Fore.CYAN}ExeRunInfo{Fore.RESET} {Fore.BLUE}{exe_path}{Fore.RESET} 输出: {output}")
                                            print()

    if result_dict:
        for exit_code, exe_list in result_dict.items():
            print(f"{Fore.CYAN}ExeRunInfo{Fore.RESET} 以下可执行文件以退出代码 {Fore.RED}{exit_code}{Fore.RESET} 退出:")
            count = len(exe_list)
            if detailed or count <= EXE_LIST_LIMIT:
                for exe in exe_list:
                    print(f" - {Fore.BLUE}{exe}{Fore.RESET}")
            else:
                for exe in exe_list[:EXE_LIST_LIMIT]:
                    print(f" - {Fore.BLUE}{exe}{Fore.RESET}")
                print(f"   ... 等总共 {count} 个")
            查找错误代码解释(exit_code)
            print()
    return found

def 分析InstallationVerificationLogs(dir_path: str, detailed: bool = False) -> bool:
    """
    在 InstallationVerificationLogs 中查找错误截图和错误信息，并输出找到的信息。

    :param dir_path: 日志文件目录
    :type dir_path: str
    :param detailed: 是否显示一般错误/异常
    :type detailed: bool
    :return: 返回是否找到错误截图或错误信息
    :rtype: bool
    """

    # 将日志文件夹下的 .txt 替换为 .log
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".txt"):
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file[:-4] + ".log")
                os.rename(old_path, new_path)
                # print(f"已将 {old_path} 重命名为 {new_path}")

    found = False

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".png") and ("ErrorScreenshot" in file):
                found = True
                print(f"{Fore.CYAN}Screenshot{Fore.RESET} 日志目录下存在错误截图: {Fore.BLUE}{os.path.join(root, file)}{Fore.RESET}")

    # 查看日志中是否有带有以下关键词的行
    keyword_map = {
        "[FAIL] Installer failed security check": ("安装程序未通过安全检查", Fore.YELLOW),
        "No suitable installer found": ("未找到合适的安装程序", Fore.YELLOW),
        "ShellExecute installer failed": ("Shell 执行安装程序失败", Fore.YELLOW),
        "Installation failed with exit code": ("以非正常退出代码退出", Fore.RED),
        "Package failed updates, dependency or conflict validation.": ("安装依赖错误", Fore.YELLOW),
    }

    if detailed:
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

    for root, _, files in os.walk(dir_path):
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
                                found = True
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
                                        if 匹配.group(1) == "-2147467260":
                                            print(f"{消息头.提示} 这可能是{Fore.YELLOW}验证管道的一个已知问题{Fore.RESET}导致的: https://github.com/microsoft/winget-pkgs/issues/323120")
                                    else:
                                        print(f"{消息头.提示} 您可以尝试在 https://github.com/microsoft/winget-cli/blob/master/doc/windows/package-manager/winget/returnCodes.md 上查找对应退出代码的解释。")
                                        print(f"{消息头.提示} 也可以尝试在 https://github.com/microsoft/winget-pkgs/blob/master/Tools/ManualValidation/ExitCodes.csv 上查找对应退出代码的解释。")
                                elif keyword in ["ShellExecute installer failed", "MSIX installer failed"]:
                                    匹配 = re.search(f"{keyword}:\\s*(-?\\d+)", line, re.IGNORECASE)
                                    if 匹配:
                                        查找错误代码解释(匹配.group(1))
                                elif keyword == "No suitable installer found":
                                    print(f"{消息头.提示} 这可能是因为您提交的包的安装程序定义和依赖中的安装程序定义不匹配。")
                                    print(f"{消息头.提示} 如果你想了解更多信息，建议阅读: https://duckduckstudio.github.io/Articles/#/信息速查/终端/WinGet/参考信息?id=no-suitable-installer-found")
                                    print(f"{消息头.提示} TL;DR 这大概率不是你的问题（除非是架构不一致）。")
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
    return found

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
    给定当前已知的 URL (GitHub PR 或 Azure Pipeline Run)，返回 *PR 最新的 / 指定的* Azure Pipeline 运行的 id (buildId)。

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
        print(f"{消息头.错误} 未能从 Azure Pipeline 运行链接中获取 buildId 参数的值")
        return None

    return buildId

def 查找错误代码解释(ExitCode: str | int):
    """尝试从 ExitCodes.csv 中找 exit_code 的解释"""

    # ExitCodes.csv 示例
    # "Hex","Dec","InvDec","Symbol","Description"
    # "00000000","0","-4294967296","ERROR_SUCCESS","The operation completed successfully."
    # "00000001","1","-4294967295","ERROR_INVALID_FUNCTION","Incorrect function."
    # "00000002","2","-4294967294","ERROR_FILE_NOT_FOUND","The system cannot find the file specified."
    # "00000003","3","-4294967293","ERROR_PATH_NOT_FOUND","The system cannot find the path specified."
    # ...

    ExitCode = str(ExitCode) # 有些时候会被当做 int 传递

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
        csvStr = 获取GitHub文件内容("microsoft/winget-pkgs", "Tools/ManualValidation/ExitCodes.csv", github_token)
        if csvStr:
            ExitCodes = io.StringIO(csvStr)

    if ExitCodes:
        reader = csv.DictReader(ExitCodes)
        for row in reader:
            if ExitCode in [row["Hex"], row["Dec"], row["InvDec"], row["Symbol"]]:
                print(f"{消息头.提示} 此错误代码或许代表:")
                print(f"{消息头.提示} {" | ".join([f"Hex: {Fore.BLUE}{row['Hex']}{Fore.RESET}", f"Dec: {Fore.BLUE}{row['Dec']}{Fore.RESET}", f"InvDec: {Fore.BLUE}{row['InvDec']}{Fore.RESET}", f"Symbol: {Fore.BLUE}{row['Symbol']}{Fore.RESET}", f"Description: {Fore.BLUE}{row['Description']}{Fore.RESET}"]).replace(f"{Fore.BLUE}{ExitCode}{Fore.RESET}", f"{Fore.MAGENTA}{ExitCode}{Fore.RESET}")}")
