from colorama import Fore
# 在各个工具中 init

# WARNING
# 整个项目有大量 (400+) 日志输出，如果统一修改用这个函数需要大量工作。
# 一些新的工具可能会使用这个函数。

def PrintLogs(消息: str, 等级: str = "INFO") -> None:
    '''
    依据日志等级打印带有等级和对应颜色标头的日志消息。  
    例如 "SUCCESS" -> f"{Fore.GREEN}✓{Fore.RESET} {消息}"  
    等级有 [INFO, NOTICE, WARN, HINT, ERROR, SUCCESS]
    '''

    等级 = 等级.upper()

    颜色 = {
        "INFO": Fore.BLUE,
        "NOTICE": Fore.BLUE,
        "WARN": Fore.YELLOW,
        "HINT": Fore.YELLOW,
        "ERROR": Fore.RED,
        "SUCCESS": Fore.GREEN
    }.get(等级, "")

    # 转换等级标头
    等级 = {
        "NOTICE": "[!]",
        # "WARN": "⚠",
        "ERROR": "✕",
        "SUCCESS": "✓",
    }.get(等级, 等级)

    print(f"{颜色}{等级}{Fore.RESET} {消息}")
