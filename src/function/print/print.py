from colorama import Fore
# 在各个工具中 init

class 消息头():
    信息 = f"{Fore.BLUE}INFO{Fore.RESET}"
    消息 = f"{Fore.BLUE}[!]{Fore.RESET}"
    问题 = f"{Fore.BLUE}?{Fore.RESET}"
    可选问题 = f"{Fore.BLUE}? (可选){Fore.RESET}"
    警告 = f"{Fore.YELLOW}WARN{Fore.RESET}"
    提示 = f"{Fore.YELLOW}Hint{Fore.RESET}"
    错误 = f"{Fore.RED}✕{Fore.RESET}"
    成功 = f"{Fore.GREEN}✓{Fore.RESET}"
    调试 = f"{Fore.CYAN}DEBUG{Fore.RESET}"
