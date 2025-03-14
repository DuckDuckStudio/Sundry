import os
import sys
from colorama import Fore, init

def main():
    init(autoreset=True)

    if (len(sys.argv) == 2):
        if os.path.exists(sys.argv[1]):
            return repr_file(sys.argv[1])
        else:
            return repr_text(sys.argv[1])
    elif (len(sys.argv) == 3):
        if os.path.exists(sys.argv[1]):
            return repr_file(sys.argv[1], sys.argv[2])
        else:
            return repr_text(sys.argv[1], sys.argv[2])
    else:
        print(f"{Fore.RED}✕ 请按照以下格式传入参数:")
        print(f"{Fore.BLUE}sundry repr <文件路径/文本内容> [编码(默认 UTF-8)]{Fore.RESET}")
        return 1

def repr_file(path, encode="utf-8"):
    try:
        with open(path, "r", encoding=encode) as f:
            print(f"{Fore.CYAN}{repr(f.read())}")
        return 0
    except PermissionError:
        print(f"{Fore.RED}✕ 没有权限")
        return 1
    except FileNotFoundError:
        print(f"{Fore.RED}✕ 文件不存在")
        return 1
    except (LookupError, UnicodeDecodeError) as e:
        print(f"{Fore.RED}✕{Fore.RESET} 编码错误: {Fore.RED}{e}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 未知错误: {Fore.RED}{e}{Fore.RESET}")
        return 1

def repr_text(text, encode="utf-8"):
    try:
        print(f"{Fore.CYAN}{repr(text.encode(encode))}")
        return 0
    except (LookupError, UnicodeDecodeError) as e:
        print(f"{Fore.RED}✕{Fore.RESET} 编码错误: {Fore.RED}{e}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 未知错误: {Fore.RED}{e}{Fore.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
