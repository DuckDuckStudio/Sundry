from colorama import Fore
# 在各个工具中 init

class 消息头():
    # 特殊
    消息 = f"{Fore.BLUE}[!]{Fore.RESET}"
    问题 = f"{Fore.BLUE}?{Fore.RESET}"
    可选问题 = f"{Fore.BLUE}? (可选){Fore.RESET}"
    # 日志输出
    信息 = f"{Fore.BLUE}INFO{Fore.RESET}"
    成功 = f"{Fore.GREEN}✓{Fore.RESET}"
    错误 = f"{Fore.RED}✕{Fore.RESET}"
    警告 = f"{Fore.YELLOW}WARN{Fore.RESET}"
    调试 = f"{Fore.CYAN}DEBUG{Fore.RESET}"
    提示 = f"{Fore.YELLOW}Hint{Fore.RESET}"
    # 内部
    内部警告 = f"{Fore.YELLOW}WARN (内部){Fore.RESET}"
    内部错误 = f"{Fore.RED}✕ (内部){Fore.RESET}"

def 多行带头输出(内容: str, 头: str) -> None:
    """
    输出多行带消息头的内容。
    """

    for 行 in 内容:
        print(f"{头} {行}")
