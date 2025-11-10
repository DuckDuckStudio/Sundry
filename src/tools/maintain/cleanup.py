import os
import shutil
import tempfile
from colorama import Fore, init
from function.print.print import 消息头
from function.maintain.config import 读取配置

def main(哪个工具: str) -> int:
    """
    清理指定工具运行产生的文件。  
    参数 1: 指定哪个工具
    """

    init(autoreset=True)

    if not 哪个工具:
        print(f"{消息头.警告} 未指定清理哪个工具产生的文件，默认清理所有 Sundry 产生的文件")
        哪个工具 = "aec"

    哪个工具 = 哪个工具.lower()

    工具别名 = {
        "logsAnalyse": ["日志分析", "logs-analyse", "log-analyse", "logs_analyse", "azure日志分析"],
        "remove": ["自动移除", "autoremove", "移除", "remove"],
        "verify": ["test", "验证", "测试"],
        "all": ["所有", "all"],
        "aec": ["除了缓存", "all-except-cache"]
    }
    for 工具名, 别名 in 工具别名.items():
        if (哪个工具 in 别名) or (哪个工具 == 工具名.lower()):
            哪个工具 = 工具名
            break
    # 如不是已知别名，原样传递

    临时目录 = os.path.join(tempfile.gettempdir(), "Sundry")
    待清理文件路径: list[str] = []

    if 哪个工具 in ["logsAnalyse", "all", "aec"]:
        待清理文件路径.append(os.path.join(临时目录, "AzurePiplines", "Logs"))
    if 哪个工具 in ["remove", "all", "aec"]:
        待清理文件路径.append(os.path.join(临时目录, "RemoveAndAutoRemove", "DownloadInstallers"))
    if 哪个工具 in ["verify", "all", "aec"]:
        待清理文件路径.append(os.path.join(临时目录, "Verify"))
    if 哪个工具 in ["cache", "all"]:
        待清理文件路径.append(os.path.join(临时目录, "Cache"))
    if not 待清理文件路径:
        print(f"{消息头.错误} 不知道该如何清理 {哪个工具} 产生的文件")
        return 1

    return 清理文件(待清理文件路径, 哪个工具)

def 清理文件(待清理文件路径: list[str], 哪个工具: str) -> int:
    """
    删除指定的文件夹并打印日志。  
    参数 1: 指定待清理文件夹的路径  
    参数 2: 指定日志输出中的工具名称
    """

    if 哪个工具 == "all":
        哪个工具 = "所有 Sundry"
    elif 哪个工具 == "aec": # aka "All Except Cache"
        哪个工具 = "除缓存外所有 Sundry"

    if 读取配置("debug"):
        print(f"{消息头.调试} [clean] 清理 {哪个工具} 产生的文件 | 路径列表: {", ".join(待清理文件路径)}")

    有清理 = False

    for 路径 in 待清理文件路径:
        try:
            shutil.rmtree(路径)
            有清理 = True
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"{消息头.错误} 清理 {哪个工具} 产生的文件时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
            return 1

    if 有清理:
        print(f"{消息头.成功} 成功清理 {哪个工具} 产生的文件")
    else:
        print(f"{消息头.消息} 没有需要清理的文件")
    return 0
