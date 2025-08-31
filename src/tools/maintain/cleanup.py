import os
import shutil
import tempfile
from colorama import Fore, init
from function.print.print import 消息头

def main(哪个工具: str) -> int:
    '''
    清理指定工具运行产生的文件。  
    参数 1: 指定哪个工具
    '''

    init(autoreset=True)

    if not 哪个工具:
        print(f"{消息头.警告}未指定清理哪个工具产生的文件，默认清理所有 Sundry 产生的文件")
        哪个工具 = "all"

    哪个工具 = 哪个工具.lower()
    
    工具别名 = {
        "logsAnalyse": ["日志分析", "logs-analyse", "log-analyse", "logs_analyse", "azure日志分析"],
        "remove": ["自动移除", "autoremove", "移除", "remove"],
        "verify": ["test", "验证", "测试"],
        "all": ["所有", "all"]
    }
    for 工具名, 别名 in 工具别名.items():
        if (哪个工具 in 别名) or (哪个工具 == 工具名.lower()):
            哪个工具 = 工具名
            break
    # 如不是已知别名，原样传递
    
    if 哪个工具 == "logsAnalyse":
        待清理文件路径 = os.path.join(tempfile.gettempdir(), "Sundry", "AzurePiplines", "Logs")
    elif 哪个工具 == "remove":
        待清理文件路径 = os.path.join(tempfile.gettempdir(), "Sundry", "RemoveAndAutoRemove", "DownloadInstallers")
    elif 哪个工具 == "verify":
        待清理文件路径 = os.path.join(tempfile.gettempdir(), "Sundry", "Verify")
    elif 哪个工具 == "all":
        待清理文件路径 = os.path.join(tempfile.gettempdir(), "Sundry")
    else:
        print(f"{消息头.错误}不知道该如何清理 {哪个工具} 产生的文件")
        return 1
    
    return 清理文件(待清理文件路径, 哪个工具)
    
def 清理文件(待清理文件路径: str, 哪个工具: str) -> int:
    '''
    删除指定的文件夹并打印日志。  
    参数 1: 指定待清理文件夹的路径  
    参数 2: 指定日志输出中的工具名称
    '''

    if 哪个工具 == "all":
        哪个工具 = "所有 Sundry 产生的文件"

    try:
        shutil.rmtree(待清理文件路径)
        print(f"{消息头.成功}成功清理 {哪个工具}")
        return 0
    except FileNotFoundError:
        print(f"{消息头.消息}没有需要清理的文件")
        return 0
    except Exception as e:
        print(f"{消息头.错误}清理 {哪个工具} 时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
