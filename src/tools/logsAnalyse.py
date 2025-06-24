import os
import re
import shutil
import zipfile
import requests
from colorama import Fore, init

def main(args: list[str]) -> int:
    # sundry logs-analyse <Azure Pipline Url> [是否保留日志文件] [是否显示一般错误/异常]

    init(autoreset=True)

    # 获取 Azure Pipline 运行链接
    if len(args) < 1:
        print(f"{Fore.RED}✕{Fore.RESET} 请提供 Azure Pipline Url")
        return 1
    
    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在验证提供的 Azure Pipline Url...")

    azure_url = args[0]
    if azure_url.startswith("https://github.com/"):
        # 无效和 return 在下面的 if
        print(f"{Fore.YELLOW}Hint{Fore.RESET} 请提供 Validation Pipeline Run 的 URL 而不是 GitHub 的 URL")
    
    if not azure_url.startswith("https://dev.azure.com/"):
        print(f"{Fore.RED}✕{Fore.RESET} 无效的 Azure Pipline Url")
        return 1
    
    # 从 URL 中提取 buildId
    build_id = azure_url.split("buildId=")[-1].replace("&view=results", "")
    
    # 获取该运行的信息（权限公开）
    api_url = f"https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_apis/build/builds/{build_id}?api-version=7.1"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"{Fore.RED}✕{Fore.RESET} 无法获取构建信息: {api_url} 响应 {Fore.RED}{response.status_code}{Fore.RESET}")
        return 1
    
    build_info = response.json()
    # 获取管道名称
    pipeline_name = build_info.get("definition", {}).get("name")

    if not pipeline_name:
        print(f"{Fore.RED}✕{Fore.RESET} 无法确定这是不是验证管道运行")
        return 1
    elif pipeline_name != "WinGetSvc-Validation":
        print(f"{Fore.RED}✕{Fore.RESET} 这似乎不是验证管道的运行: {pipeline_name}")
        return 1
    
    print(f"{Fore.GREEN}✓{Fore.RESET} 成功验证提供的 Azure Pipline Url。")

    # ===========================================================================================

    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在获取管道运行 ({build_id}) 的日志...")

    # 获取日志下载链接，并将其下载到 %Temp%/Sundry/AzurePiplines/Logs/{build_id}/ 下，没有则创建文件夹
    logs_url = f"https://dev.azure.com/shine-oss/8b78618a-7973-49d8-9174-4360829d979b/_apis/build/builds/{build_id}/artifacts?artifactName=InstallationVerificationLogs&api-version=7.1&%24format=zip"
    logs_dir = os.path.join(os.environ["TEMP"], "Sundry", "AzurePiplines", "Logs", build_id)
    logs_zip_path = os.path.join(logs_dir, "logs.zip")

    # 如果原先存在同名zip文件
    if os.path.exists(logs_zip_path):
        if input(f"{Fore.BLUE}?{Fore.RESET} 下载位置下{Fore.YELLOW}已存在同名日志文件{Fore.RESET} {Fore.BLUE}{logs_zip_path}{Fore.RESET}，我应该移除它吗? [Y/n]: ").lower() not in ["y", "yes", "是", ""]:
            print(f"{Fore.RED}✕{Fore.RESET} 下载位置下存在同名文件")
            return 1
        else:
            # 移除它
            os.remove(logs_zip_path)
        
    # 如果解压后的位置存在同名目录
    if os.path.exists(logs_dir):
        if input(f"{Fore.BLUE}?{Fore.RESET} 解压位置下{Fore.YELLOW}已存在同名日志目录{Fore.RESET} {Fore.BLUE}{logs_dir}{Fore.RESET}，我应该移除它吗? [Y/n]: ").lower() not in ["y", "yes", "是", ""]:
            print(f"{Fore.RED}✕{Fore.RESET} 解压位置下存在同名目录")
            return 1
        else:
            # 移除它
            shutil.rmtree(logs_dir)
            # 再建个空的
            os.makedirs(logs_dir, exist_ok=True)
    else:
        os.makedirs(logs_dir, exist_ok=True)
        
    # 下载日志文件
    print(f"{Fore.BLUE}INFO{Fore.RESET} 正在下载日志文件到 {logs_zip_path}...")
    response = requests.get(logs_url)
    if response.status_code != 200:
        print(f"{Fore.RED}✕{Fore.RESET} 无法下载日志文件: {logs_url} 响应 {Fore.RED}{response.status_code}{Fore.RESET}")
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

    # =============================================

    # 看看解压后的日志文件夹中有没有 .png 文件，有则输出位置
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

    # 查看日志中是否有带有以下关键词的行
    keyword_map = {
        "Installation failed with exit code": ("以非正常退出代码退出", Fore.RED),
        "[FAIL] Installer failed security check": ("安装程序未通过安全检查", Fore.YELLOW),
        "No suitable installer found": ("未找到合适的安装程序", Fore.YELLOW),
    }

    if (len(args) == 3) and (args[2].lower() in ["true", "yes", "y", "是"]):
        # 追加这些关键词
        keyword_map.update({
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
                                print(f"{Fore.CYAN}Analyse{Fore.RESET} {result_str}\n{highlighted_line} {Fore.BLUE}in{Fore.RESET} {file}")
                                if keyword == "Installation failed with exit code":
                                    print(f"{Fore.YELLOW}Hint{Fore.RESET} 您可以在 https://github.com/microsoft/winget-cli/blob/master/doc/windows/package-manager/winget/returnCodes.md 上查找对应退出代码的解释。")
                                elif keyword == "No suitable installer found":
                                    print(f"{Fore.YELLOW}Hint{Fore.RESET} 这可能是因为您提交的软件包的安装程序定义和依赖中的安装程序定义不匹配。")
                                    print(f"{Fore.YELLOW}Hint{Fore.RESET} 举个例子，当上游依赖只支持 x64 架构，而您提交的清单中的安装程序还支持 x86 架构时，WinGet 会因为找不到 x86 的依赖安装程序而失败。")
                                    print(f"{Fore.YELLOW}Hint{Fore.RESET} 具体需要如何处理此错误尚不确定: https://github.com/microsoft/winget-pkgs/issues/152555")
                                break

    if not 找到可能的问题了吗:
        print(f"{Fore.YELLOW}WARN{Fore.RESET} 未找到可能的问题")
        if not ((len(args) == 3) and (args[2].lower() in ["true", "yes", "y", "是"])):
            if (len(args) == 2):
                print(f"{Fore.YELLOW}Hint{Fore.RESET} 请尝试使用 {Fore.BLUE}sundry logs-analyse \"{azure_url}\" \"{args[1]}\" y{Fore.RESET} 来查看一般错误/异常")
            else:
                print(f"{Fore.YELLOW}Hint{Fore.RESET} 请尝试使用 {Fore.BLUE}sundry logs-analyse \"{azure_url}\" \"[是否保留日志文件]\" y{Fore.RESET} 来查看一般错误/异常")

    if (len(args) >= 2):
        if (args[1].lower() in ["true", "yes", "y", "是"]):
            # 打开日志文件
            os.startfile(logs_dir)
        elif (args[1].lower() in ["false", "no", "n", "否"]):
            # 移除它
            shutil.rmtree(logs_dir)
            print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件目录。")
        else:
            print(f"{Fore.YELLOW}WARN{Fore.RESET} 指定的参数 1 无效，{Fore.BLUE}{args[1]}{Fore.RESET} 不能表达是否要保留日志文件")
            if (input(f"{Fore.BLUE}?{Fore.RESET} 你想要保留日志文件吗? [Y/n]: ").lower() in ["y", "yes", "是", ""]):
                # 打开日志文件
                os.startfile(logs_dir)
            else:
                # 移除它
                shutil.rmtree(logs_dir)
                print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件目录。")
    else:
        if (input(f"{Fore.BLUE}?{Fore.RESET} 你想要保留日志文件吗? [Y/n]: ").lower() in ["y", "yes", "是", ""]):
            # 打开日志文件
            os.startfile(logs_dir)
        else:
            # 移除它
            shutil.rmtree(logs_dir)
            print(f"{Fore.GREEN}✓{Fore.RESET} 已删除日志文件目录。")

    return 0
