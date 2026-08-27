import argparse
import csv
import io
import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any, Literal

import requests
from catfood.constant import NO
from catfood.exceptions.operation import TryOtherMethods
from catfood.functions.files import open_file
from catfood.functions.format.github import IssueNumber
from catfood.functions.github.api import 获取GitHub文件内容, 请求GitHubAPI
from catfood.functions.print import 消息头
from colorama import Fore

from function.constant.general import REQUEST_TIMEOUT
from function.constant.logsAnalyse import (
    DETAILED_KEYWORD_MAP,
    EXCLUDE_MAP,
    EXE_LIST_LIMIT,
    KEYWORD_MAP,
)
from function.constant.paths import VALIDATION_LOGS_DIR, VALIDATION_LOGS_ZIP_DIR
from function.constant.regexes import LOGS_ZIP_DOWNLOAD_URL
from function.github.token import read_token
from function.maintain.config import 读取配置


def main(args: list[str]) -> Literal[0, 1]:
    """
    `sundry logs-analyse` 命令的入口函数。

    Args:
        args: `sundry logs-analyse <PR 链接/PR 编号/检查链接> [--detailed]`

    Returns:
        退出代码
    """

    parser = argparse.ArgumentParser(
        prog="sundry logs-analyse",
        description="分析验证日志",
        allow_abbrev=False,
    )
    parser.add_argument("pr", help="PR 链接、PR 编号或检查链接")
    parser.add_argument("--detailed", action="store_true", help="启用详细模式，显示一般错误和异常")
    parser.add_argument(
        "--keep-logs",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="是否保留下载的日志文件；未指定时在分析结束后询问",
    )

    try:
        parsed_args = parser.parse_args(args)
    except SystemExit:
        return 1

    log_zip_file_path = get_validation_log_zip_from_args([parsed_args.pr])
    if not log_zip_file_path:
        return 1

    logs_dir_path = unzip_validation_log_zip(log_zip_file_path)
    del log_zip_file_path

    print()  # 获取验证日志的输出，和分析验证日志的输出之间，空一行

    found = analyze_validation_result((logs_dir_path / "ValidationResult"), parsed_args.detailed)
    found = analyze_installation_verification_logs((logs_dir_path / "InstallationVerificationLogs"), parsed_args.detailed) or found

    if not found:
        print(f"{消息头.警告} 未找到可能的问题")
        if not parsed_args.detailed:
            print(f'{消息头.提示} 请尝试使用 {Fore.BLUE}sundry logs-analyse "{parsed_args.pr}" --detailed{Fore.RESET} 来查看一般错误/异常')

    keep_logs = parsed_args.keep_logs
    if keep_logs is None:
        keep_logs = input(f"{消息头.问题} 是否保留日志文件? [{Fore.GREEN}Y{Fore.RESET}/n]: ").strip().lower() not in NO

    if keep_logs:
        print(f"{消息头.消息} 打开 {Fore.BLUE}{logs_dir_path}{Fore.RESET}")
        result = open_file(str(logs_dir_path))
        return (1 if found else 0) or result
    else:
        shutil.rmtree(logs_dir_path)
        print(f"{消息头.成功} 已删除日志文件目录")
        return 1 if found else 0


# =================== 获取验证日志 ===================


def get_pr_head_commit_hash(pr_number: int | None) -> str | None:
    """
    获取 PR 头提交的哈希值

    Args:
        pr_number: PR 编号

    Returns:
        str: 头提交哈希值
        None: 获取失败
    """

    if not pr_number:
        return None

    responsed_data = 请求GitHubAPI(
        f"https://api.github.com/repos/microsoft/winget-pkgs/pulls/{pr_number}",
        token=read_token()
    )
    if not responsed_data:
        return None

    try:
        return responsed_data["head"]["sha"]
    except KeyError:
        return None


def get_check_suite_id(commit_hash: str | None) -> int | None:
    """
    获取该提交中的 WinGetValidator-Prod 检查套件的 ID

    Args:
        commit_hash: 提交的哈希值

    Returns:
        int: 提交对应的 WinGetValidator-Prod 检查套件的 ID
        None: 获取失败
    """

    if not commit_hash:
        return None

    # NOTE: 当前 winget-pkgs 中一个提交的检查套件数还没超过 100，如果后续超过了需要处理分页。
    responsed_data = 请求GitHubAPI(
        f"https://api.github.com/repos/microsoft/winget-pkgs/commits/{commit_hash}/check-suites",
        params={
            "per_page": 100
        },
        token=read_token()
    )
    if not responsed_data:
        return None

    try:
        check_suites = responsed_data["check_suites"]
    except KeyError:
        return None

    if not isinstance(check_suites, list):
        return None

    for check_suite in check_suites:  # pyright: ignore[reportUnknownVariableType]
        if not isinstance(check_suite, dict):
            continue

        try:
            if check_suite["app"]["name"] == "WinGetValidator-Prod":
                check_suite_id = check_suite["id"]  # pyright: ignore[reportUnknownVariableType]
                if isinstance(check_suite_id, int):
                    return check_suite_id
        except KeyError:
            continue

    return None


def get_validation_completed_check_text(check_suite_id: int | None) -> str | None:
    """
    获取 WinGetValidator-Prod 检查套件中的 "10. Validation Completed" 检查的 ID

    Args:
        check_suite_id: WinGetValidator-Prod 检查套件的 ID

    Returns:
        str: "10. Validation Completed" 检查的 text
        None: 获取失败
    """

    if not check_suite_id:
        return None

    # NOTE: 当前 winget-pkgs 中 WinGetValidator-Prod 检查套件的检查只有 10 个，如果后续超过 30 个需要增加每页大小或处理分页。
    responsed_data = 请求GitHubAPI(
        f"https://api.github.com/repos/microsoft/winget-pkgs/check-suites/{check_suite_id}/check-runs",
        token=read_token()
    )
    if not responsed_data:
        return None

    try:
        check_runs = responsed_data["check_runs"]
    except KeyError:
        return None

    if not isinstance(check_runs, list):
        return None

    for check_run in check_runs:  # pyright: ignore[reportUnknownVariableType]
        if not isinstance(check_run, dict):
            continue

        try:
            if check_run["name"] == "10. Validation Completed":
                check_output = check_run["output"]  # pyright: ignore[reportUnknownVariableType]
                if not isinstance(check_output, dict):
                    continue

                check_text = check_output["text"]  # pyright: ignore[reportUnknownVariableType]
                if isinstance(check_text, str):
                    return check_text
        except KeyError:
            continue

    return None


def match_validation_log_download_url(check_text: str | None) -> str | None:
    """
    从验证详情中正则匹配日志下载链接

    Args:
        check_text: 验证详情

    Returns:
        str: 日志下载链接
        None: 未匹配
    """

    if not check_text:
        return None

    result = re.search(LOGS_ZIP_DOWNLOAD_URL, check_text)
    if result:
        return result.group()
    return None


def download_validation_log_zip(download_url: str | None) -> Path | None:
    """
    下载验证日志 zip 到 Sundry 临时目录

    Args:
        download_url: 验证日志 zip 下载链接

    Returns:
        Path: 验证日志 zip 文件所在路径对象
        None: 下载失败

    Raises:
        ValueError: 下载链接不在预期的路径上
    """

    if not download_url:
        return None

    if not re.match(LOGS_ZIP_DOWNLOAD_URL, download_url):
        raise ValueError("验证日志 zip 的下载链接不匹配预期正则")

    # 下载验证日志 zip 到 Sundry 临时目录
    VALIDATION_LOGS_ZIP_DIR.mkdir(parents=True, exist_ok=True)

    zip_file_name = download_url.split("/")[-1]
    zip_file_path = VALIDATION_LOGS_ZIP_DIR / zip_file_name

    try:
        if zip_file_path.exists():
            raise FileExistsError(f"验证日志 zip 文件下载位置 {Fore.BLUE}{zip_file_path}{Fore.RESET} {Fore.YELLOW}已存在同名 zip 文件{Fore.RESET}。")
    except FileExistsError as e:
        print(f"{消息头.警告} {e}")
        if input(f"{消息头.问题} 是否覆盖下载? [Y/n]: ").strip().lower() in NO:
            return None

        # 移除同名文件
        zip_file_path.unlink()

    try:
        print(f"{消息头.信息} 正在下载 {Fore.BLUE}{zip_file_name}{Fore.RESET} ...")
        response = requests.get(download_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"{消息头.错误} 下载 {Fore.BLUE}{download_url}{Fore.RESET} 失败: {Fore.RED}{e}{Fore.RESET}")
        return None

    try:
        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(response.content)
        print(f"{消息头.成功} {Fore.BLUE}{zip_file_name}{Fore.RESET} 下载成功")
        return zip_file_path
    except Exception as e:
        print(f"{消息头.错误} 将响应内容写入 {Fore.BLUE}{zip_file_path}{Fore.RESET} 时遇到异常: {Fore.RED}{e}{Fore.RESET}")
        return None


def get_validation_log_zip_from_args(args: list[str]) -> Path | None:
    """
    尝试通过传入的参数下载验证日志 zip，并返回 zip 文件所在路径。

    会输出错误信息

    Args:
        args:
            传入的参数列表
            - `... <PR 链接>`
            - `... <PR 编号>`
            - `... <检查链接>`

    Returns:
        Path: 验证日志 zip 文件所在路径
        None: 未能获取验证日志 zip 文件
    """

    pr_number = IssueNumber(args[0])
    if not pr_number:
        print(f"{消息头.错误} 未能从给定的参数中获取 PR 编号")
        return None

    result = download_validation_log_zip(
        match_validation_log_download_url(
            get_validation_completed_check_text(
                get_check_suite_id(
                    get_pr_head_commit_hash(
                        int(pr_number)
                    )
                )
            )
        )
    )

    if result is None:
        print(f"{消息头.错误} 未能获取到验证日志")

    return result


def unzip_validation_log_zip(file_path: Path) -> Path:
    """
    解压验证日志 zip 到 Sundry 临时目录，然后删除验证日志 zip 文件。

    解压失败的异常会直接抛出。

    Args:
        file_path: 验证日志 zip 文件的所在路径

    Returns:
        Path: 解压后的日志文件目录所在路径

    Raises:
        ValueError: 解压位置已存在，但解压位置既不是文件也不是目录，不知道怎么处理
    """

    dir_path = VALIDATION_LOGS_DIR / file_path.stem

    try:
        if dir_path.exists():
            raise FileExistsError(f"验证日志解压位置 {Fore.BLUE}{dir_path}{Fore.RESET} {Fore.YELLOW}已存在{Fore.RESET}。")
    except FileExistsError as e:
        print(f"{消息头.警告} {e}")
        if input(f"{消息头.问题} 是否覆盖? [Y/n]: ").strip().lower() in NO:
            raise

        if dir_path.is_file():
            dir_path.unlink()
        elif dir_path.is_dir():
            shutil.rmtree(dir_path)
        else:
            raise ValueError(f"验证日志解压位置 {Fore.BLUE}{dir_path}{Fore.RESET} {Fore.YELLOW}既不是文件也不是目录{Fore.RESET}")  # pylint: disable=raise-missing-from / W0707 - 这是在处理异常时出现的异常，而不是捕获的异常导致的异常

    with zipfile.ZipFile(file_path) as zip_ref:
        zip_ref.extractall(dir_path)
    file_path.unlink()
    print(f"{消息头.成功} {Fore.BLUE}{file_path.name}{Fore.RESET} 解压完成")
    return dir_path


# =================== 分析验证日志 ===================


def analyze_validation_result(validation_result_dir: Path, detailed: bool = False) -> bool:
    """
    在 ValidationResult 中查找错误信息，并输出找到的信息。

    Args:
        validation_result_dir: ValidationResult 日志目录
        detailed: 是否启用详细输出

    Returns:
        bool: 是否找到可能的错误
    """

    if not validation_result_dir.is_dir():
        return False

    found = False
    exit_code_result_dict: dict[int, list[str]] = {
        # "退出代码": ["exe1", "exe2", ...]
    }

    # 该目录下有一个 merged 的 yaml 清单，和验证结果 json 文件
    for json_file in validation_result_dir.rglob("*.json"):
        if json_file.name == "InstallationVerification_Result.json":
            with open(json_file, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            if data.get("OverallResult", "Success") == "Success":
                continue

            for result in data.get("AnalysisResults", []):
                if result.get("AnalysisType") == "ExeRunInfo":
                    for exe_path, diag_info in result.get("Diagnostics", {}).items():
                        diag_info: dict[str, str | int]

                        if diag_info.get("ExecutionStatusResult", "Pass") == "Pass":
                            continue

                        exit_code = diag_info.get("ExitCode", 0)
                        if not isinstance(exit_code, int):
                            continue

                        if exit_code != 0:
                            found = True

                            try:
                                exit_code_result_dict[exit_code].append(exe_path)
                            except KeyError:
                                exit_code_result_dict[exit_code] = [exe_path]

                            output = ""

                            ErrorStream = diag_info.get("ErrorStream", None)
                            if isinstance(ErrorStream, str) and ErrorStream:
                                output = f"{Fore.RED}{ErrorStream}{Fore.RESET}"
                            del ErrorStream

                            OutputStream = diag_info.get("OutputStream", None)
                            if isinstance(OutputStream, str) and OutputStream:
                                if output:
                                    output += "\n"
                                output += OutputStream
                            del OutputStream

                            if output:
                                print(f"{Fore.CYAN}ExeRunInfo{Fore.RESET} {Fore.BLUE}{exe_path}{Fore.RESET} 输出:\n{output}")
                                print()

    if exit_code_result_dict:
        for exit_code, exe_list in exit_code_result_dict.items():
            print(f"{Fore.CYAN}ExeRunInfo{Fore.RESET} 以下可执行文件以退出代码 {Fore.RED}{exit_code}{Fore.RESET} 退出:")
            count = len(exe_list)
            if detailed or count <= EXE_LIST_LIMIT:
                for exe in exe_list:
                    print(f" - {Fore.BLUE}{exe}{Fore.RESET}")
            else:
                for exe in exe_list[:EXE_LIST_LIMIT]:
                    print(f" - {Fore.BLUE}{exe}{Fore.RESET}")
                print(f"   ... 等总共 {count} 个")
            find_explanation_for_error_code(exit_code)
            print()

    return found


def analyze_installation_verification_logs(dir_path: Path, detailed: bool) -> bool:
    """
    在 InstallationVerificationLogs 中查找错误信息，并输出找到的信息。

    Args:
        dir_path: InstallationVerificationLogs 日志目录
        detailed: 是否启用详细输出

    Returns:
        bool: 是否找到可能的错误
    """

    if not dir_path.is_dir():
        return False

    found = False

    # 将日志文件夹下的 .txt 递归替换为 .log
    for txt_file in dir_path.rglob("*.txt"):
        log_file = txt_file.with_suffix(".log")
        txt_file.rename(log_file)

    for image_file in dir_path.rglob("*.png"):
        if "ErrorScreenshot" in image_file.name:
            found = True
            print(f"{Fore.CYAN}Screenshot{Fore.RESET} 日志目录下存在错误截图: {Fore.BLUE}{image_file}{Fore.RESET}\n")

    keyword_map = KEYWORD_MAP
    if detailed:
        keyword_map += DETAILED_KEYWORD_MAP

    for log_file in dir_path.rglob("*.log"):
        with open(log_file, encoding="utf-8", errors="ignore") as f:
            for line in f:
                for kw in keyword_map:
                    exclude_substrings = EXCLUDE_MAP.get(kw.keyword, [])
                    if (
                        kw.matched(line, log_file.name)
                        and (not any(exclude in line for exclude in exclude_substrings))
                    ):
                        found = True
                        highlighted_line = re.sub(
                            re.escape(kw.keyword),
                            lambda m: f"{Fore.RED}{m.group(0)}{Fore.RESET}",
                            line.strip(),
                            flags=re.IGNORECASE
                        )
                        print(f"{Fore.CYAN}Analysis{Fore.RESET} {kw.explanation.get_colored_message()}\n{highlighted_line} {Fore.BLUE}in{Fore.RESET} {log_file}")

                        # 扩展提示
                        match kw.keyword:
                            case "Installation failed with exit code":
                                # Installation failed with exit code 123
                                if matched := re.search(r"exit code (-?\d+)", line, re.IGNORECASE):
                                    find_explanation_for_error_code(matched.group(1))
                                    if matched.group(1) == "-2147467260":
                                        print(f"{消息头.提示} 这可能是{Fore.YELLOW}验证管道的一个已知问题{Fore.RESET}导致的: https://github.com/microsoft/winget-pkgs/issues/323120")
                            case "ShellExecute installer failed" | "MSIX installer failed":
                                if matched := re.search(f"{kw.keyword}:\\s*(-?\\d+)", line, re.IGNORECASE):
                                    find_explanation_for_error_code(matched.group(1))
                            case "Package failed updates, dependency or conflict validation.":
                                print(f"{消息头.提示} 这可能是因为你在清单中指定的包依赖在 winget 源中并不存在，请检查并提交依赖清单。")
                                find_explanation_for_error_code("80073CF3")
                            case _:
                                pass

                        if "0x" in line:
                            # FIXME 当前判断日志行中是否有 0x 的逻辑，是在先匹配到错误关键词的情况下才会触发，预期只要匹配到 0x 就会触发
                            # 0x00000000 (Hex, 0x + 8个字符)
                            # 不是每个错误代码都能找到解释的，没找到解释就没显示
                            matched = re.search(r"0x[0-9A-Fa-f]{8}", line)
                            if matched:
                                find_explanation_for_error_code(matched.group(0))

                        print()  # 换行

                        break  # 当前行已匹配到关键词，换下一行

    return found


def find_explanation_for_error_code(exit_code: str | int):
    """
    尝试从 ExitCodes.csv 中找退出代码的解释

    Args:
        exit_code: 退出代码
    """

    exit_code = str(exit_code)

    try:
        winget_pkgs_path = 读取配置("paths.winget-pkgs", 静默=True)
        if isinstance(winget_pkgs_path, str):
            exit_codes_csv_path = Path(winget_pkgs_path) / "Tools" / "ManualValidation" / "ExitCodes.csv"
            del winget_pkgs_path
            if exit_codes_csv_path.is_file():
                try:
                    with open(exit_codes_csv_path, encoding="utf-8") as csv_file:
                        exit_codes_io = io.StringIO(csv_file.read())
                except PermissionError as e:
                    raise TryOtherMethods from e
            else:
                raise TryOtherMethods
        else:
            raise TryOtherMethods
    except TryOtherMethods:
        # 既然用户本地无法读取这个文件，就从 GitHub 上获取
        # https://github.com/microsoft/winget-pkgs/blob/master/Tools/ManualValidation/ExitCodes.csv
        csvStr = 获取GitHub文件内容(
            "microsoft/winget-pkgs",
            "Tools/ManualValidation/ExitCodes.csv",
            read_token()
        )
        if csvStr:
            exit_codes_io = io.StringIO(csvStr)
        else:
            exit_codes_io = None

    if exit_codes_io:
        reader = csv.DictReader(exit_codes_io)
        for row in reader:
            if exit_code in [row["Hex"], row["Dec"], row["InvDec"], row["Symbol"]]:
                print(f"{消息头.提示} 此错误代码或许代表:")
                print(f"{消息头.提示} {" | ".join([f"Hex: {Fore.BLUE}{row['Hex']}{Fore.RESET}", f"Dec: {Fore.BLUE}{row['Dec']}{Fore.RESET}", f"InvDec: {Fore.BLUE}{row['InvDec']}{Fore.RESET}", f"Symbol: {Fore.BLUE}{row['Symbol']}{Fore.RESET}", f"Description: {Fore.BLUE}{row['Description']}{Fore.RESET}"]).replace(f"{Fore.BLUE}{exit_code}{Fore.RESET}", f"{Fore.MAGENTA}{exit_code}{Fore.RESET}")}")
