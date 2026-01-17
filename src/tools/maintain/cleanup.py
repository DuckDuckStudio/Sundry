import os
import shutil
from colorama import Fore
from catfood.functions.print import 消息头
from function.constant.paths import SUNDRY_TEMP_DIR

def main(哪个工具: str) -> int:
    """
    清理指定工具运行产生的文件。
    """

    if not 哪个工具:
        print(f"{消息头.警告} 未指定清理哪个工具产生的文件，默认清理除缓存外所有 Sundry 产生的文件 (aec)")
        哪个工具 = "aec"

    哪个工具 = 哪个工具.lower()

    工具别名 = {
        "logsAnalyse": ["日志分析", "logs-analyse", "log-analyse", "logs_analyse", "azure日志分析"],
        "remove": ["自动移除", "autoremove", "移除"],
        "verify": ["验证"],
        "all": ["所有"],
        "aec": ["除了缓存", "all-except-cache"]
    }
    for 工具名, 别名 in 工具别名.items():
        if (哪个工具 in 别名) or (哪个工具 == 工具名.lower()):
            哪个工具 = 工具名
            break
    # 如不是已知别名，原样传递

    if 哪个工具 == "logsAnalyse":
        from function.constant.paths import AZP_LOGS_DIR
        待清理文件路径 = AZP_LOGS_DIR
    elif 哪个工具 == "remove":
        from function.constant.paths import INSTELLER_DOWNLOAD_DIR
        待清理文件路径 = INSTELLER_DOWNLOAD_DIR
    elif 哪个工具 == "verify":
        from function.constant.paths import VERIFY_TEMP_DIR
        待清理文件路径 = VERIFY_TEMP_DIR
    elif 哪个工具 == "cache":
        from function.constant.paths import CACHE_DIR
        待清理文件路径 = CACHE_DIR
    elif 哪个工具 == "all":
        哪个工具 = "所有 Sundry"
        待清理文件路径 = SUNDRY_TEMP_DIR
    elif 哪个工具 == "aec":
        待清理文件路径 = SUNDRY_TEMP_DIR
    else:
        print(f"{消息头.错误} 不知道该如何清理 {哪个工具} 产生的文件")
        return 1

    return 清理文件(待清理文件路径, 哪个工具)

def 清理文件(待清理文件路径: str, 哪个工具: str) -> int:
    """
    删除指定的文件夹并打印日志。
    
    :param 待清理文件路径: 指定待清理文件夹的路径
    :type 待清理文件路径: str
    :param 哪个工具: 指定日志输出中的工具名称
    :type 哪个工具: str
    :return: 退出代码
    :rtype: int
    """

    try:
        if 哪个工具 == "aec": # aka "All Except Cache"
            哪个工具 = "除缓存外所有 Sundry"

            有清理 = False

            for i in os.listdir(待清理文件路径):
                if i != "Cache":
                    当前路径 = os.path.join(待清理文件路径, i)
                    有清理 = True
                    if os.path.isfile(当前路径):
                        os.remove(当前路径)
                    elif os.path.isdir(当前路径):
                        shutil.rmtree(当前路径)

            if 有清理:
                print(f"{消息头.成功} 成功清理 {哪个工具} 产生的文件")
            else:
                print(f"{消息头.消息} 没有需要清理的文件")

            return 0
        else:
            try:
                shutil.rmtree(待清理文件路径)
                print(f"{消息头.成功} 成功清理 {哪个工具} 产生的文件")
            except FileNotFoundError:
                print(f"{消息头.消息} 没有需要清理的文件")

            return 0
    except Exception as e:
        print(f"{消息头.错误} 清理 {哪个工具} 产生的文件时出现异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
