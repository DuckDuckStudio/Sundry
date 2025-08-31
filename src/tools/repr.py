import os
from colorama import Fore, init
from function.print.print import 消息头

def main(args: list[str]):
    init(autoreset=True)

    if (len(args) == 1):
        if os.path.exists(args[0]):
            return repr_file(args[0])
        else:
            return repr_text(args[0])
    elif (len(args) == 2):
        if os.path.exists(args[0]):
            return repr_file(args[0], args[1])
        else:
            return repr_text(args[0], args[1])
    else:
        print(f"{消息头.错误}{Fore.RED}参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

def repr_file(path: str, encode: str="utf-8"):
    try:
        with open(os.path.normpath(path), "r", encoding=encode) as f:
            print(f"{Fore.CYAN}{repr(f.read())}")
        return 0
    except PermissionError:
        print(f"{消息头.错误}{Fore.RED}没有权限{Fore.RESET}")
        return 1
    except FileNotFoundError:
        print(f"{消息头.错误}{Fore.RED}文件不存在{Fore.RESET}")
        return 1
    except (LookupError, UnicodeDecodeError) as e:
        print(f"{消息头.错误}编码错误: {Fore.RED}{e}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{消息头.错误}未知错误: {Fore.RED}{e}{Fore.RESET}")
        return 1

def repr_text(text: str, encode: str="utf-8"):
    try:
        print(f"{Fore.CYAN}{repr(text.encode(encode))}")
        return 0
    except (LookupError, UnicodeDecodeError) as e:
        print(f"{消息头.错误}编码错误: {Fore.RED}{e}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{消息头.错误}未知错误: {Fore.RED}{e}{Fore.RESET}")
        return 1
