import os
import random
from colorama import init, Fore
from function.files.open import open_file

def main(args: list[str]) -> int:
    init(autoreset=True)

    fun位置 = os.path.normpath(os.path.join(args[0], "fun.txt"))

    if (1 <= len(args) <= 2):
        if (len(args) == 1) or (args[1] in ["随机", "random"]):
            return 获取fun(fun位置, 随机=True)
        elif (len(args) == 2) and (args[1] in ["get", "list"]):
            return 获取fun(fun位置, 随机=False)
        elif (len(args) == 2) and (args[1] in ["编辑", "edit", "打开", "open"]):
            return 编辑fun(fun位置)
        else:
            print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
            return 1
    elif (len(args) == 3):
        if (args[1] in ["add", "添加"]):
            return 添加fun(fun位置, args[2])
        elif (args[1] in ["remove", "移除"]):
            return 移除fun(fun位置, args[2])
        elif (args[1] in ["import", "导入"]):
            return 导入fun(fun位置, os.path.normpath(os.path.abspath(args[2])))
        else:
            print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
            return 1
    else:
        print(f"{Fore.RED}✕ 参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

def 编辑fun(fun位置: str) -> int:
    print(f"{Fore.BLUE}INFO{Fore.RESET} fun.txt 位于 {fun位置}")
    print(f"{Fore.BLUE}INFO{Fore.RESET} 尝试打开 fun.txt ...")
    return open_file(fun位置)

def 导入fun(原fun文件: str, 导入fun文件: str) -> int:
    try:
        if not os.path.exists(导入fun文件):
            raise FileNotFoundError()
        with open(导入fun文件, 'r', encoding='utf-8') as file:
            导入fun: list[str] = file.readlines()
            if not 导入fun:
                print(f"{Fore.YELLOW}WARN{Fore.RESET} {Fore.BLUE}{导入fun文件}{Fore.RESET} (导入) {Fore.YELLOW}为空{Fore.RESET}")
                return 0
    except FileNotFoundError:
        print(f"{Fore.RED}✕{Fore.RESET} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{导入fun文件}{Fore.RESET} (导入)")
        return 1
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 读取 {Fore.BLUE}{导入fun文件}{Fore.RESET} (导入) 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 去重但保持原始顺序
    try:
        已有fun: set[str] = set()
        去重后的导入fun: list[str] = []
        for line in 导入fun:
            if line not in 已有fun:
                已有fun.add(line)
                去重后的导入fun.append(line)
        导入fun = 去重后的导入fun
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 对 {Fore.BLUE}{导入fun}{Fore.RESET} 去重时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 覆盖原fun文件
    try:
        if not os.path.exists(原fun文件):
            print(f"{Fore.RED}✕{Fore.RESET} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{原fun文件}{Fore.RESET} (原始)")
            # 询问用户是否创建一个
            try:
                input(f"{Fore.BLUE}?{Fore.RESET} 创建个新的 fun.txt? [ENTER/CTRL+C]")
                with open(原fun文件, 'w', encoding='utf-8') as file:
                    pass
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}✕{Fore.RESET} 操作取消")
                return 1
        with open(原fun文件, 'w', encoding='utf-8') as file:
            file.writelines(导入fun)
        print(f"{Fore.GREEN}✓{Fore.RESET} 已将 {Fore.BLUE}{导入fun文件}{Fore.RESET} 导入到 {Fore.BLUE}{原fun文件}{Fore.RESET}")
        return 0
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 导入 {Fore.BLUE}{导入fun文件}{Fore.RESET} 到 {Fore.BLUE}{原fun文件}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

def 移除fun(fun位置: str, 条目: str) -> int:
    try:
        if not os.path.exists(fun位置):
            raise FileNotFoundError()
        with open(fun位置, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if not (f"{条目}\n" in lines):
                print(f"{Fore.YELLOW}WARN{Fore.RESET} 在 {Fore.BLUE}{fun位置}{Fore.RESET} 中{Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{条目}{Fore.RESET}")
                return 0
            while f"{条目}\n" in lines:
                # 移除所有匹配的条目
                lines.remove(f"{条目}\n")
            with open(fun位置, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print(f"{Fore.GREEN}✓{Fore.RESET} 已将 {Fore.BLUE}{条目}{Fore.RESET} 从 {Fore.BLUE}{fun位置}{Fore.RESET} 中移除")
            return 0
    except FileNotFoundError:
        print(f"{Fore.RED}✕{Fore.RESET} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{fun位置}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 移除 {Fore.BLUE}{条目}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

def 添加fun(fun位置: str, 新条目: str) -> int:
    # 查重
    try:
        with open(fun位置, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if f"{新条目}\n" in lines:
                print(f"{Fore.YELLOW}WARN{Fore.RESET} {Fore.BLUE}{新条目}{Fore.RESET} {Fore.YELLOW}已存在{Fore.RESET}于 {Fore.BLUE}{fun位置}{Fore.RESET}")
                return 0
    except FileNotFoundError:
        print(f"{Fore.RED}✕{Fore.RESET} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{fun位置}{Fore.RESET}")
        # 询问用户是否创建一个
        try:
            input(f"{Fore.BLUE}?{Fore.RESET} 创建个新的 fun.txt? [ENTER/CTRL+C]")
            with open(fun位置, 'w', encoding='utf-8') as file:
                pass
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}✕{Fore.RESET} 操作取消")
            return 1
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 读取 {Fore.BLUE}{fun位置}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 添加新条目
    try:
        with open(fun位置, 'a', encoding='utf-8') as file:
            file.write(f"{新条目}\n")
        print(f"{Fore.GREEN}✓{Fore.RESET} 已将 {Fore.BLUE}{新条目}{Fore.RESET} 添加进 {Fore.BLUE}{fun位置}{Fore.RESET}")
        return 0
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 添加 {Fore.BLUE}{新条目}{Fore.RESET} 到 {Fore.BLUE}{fun位置}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

def 获取fun(fun位置: str, 随机: bool) -> int:
    try:
        if not os.path.exists(fun位置):
            raise FileNotFoundError()
        with open(fun位置, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:
                if 随机:
                    # 随机单个句子
                    随机句子 = None
                    while True: # 避免空行
                        随机句子 = random.choice(lines).strip().replace("\\n", "\n") # 多行好玩的
                        # 检查是否包含 http:// 或 https://
                        if 随机句子 and ("http://" not in 随机句子) and ("https://" not in 随机句子):
                            break
                    print(随机句子)
                else:
                    # 重置文件指针到文件开头
                    file.seek(0)
                    # 整个文件，不处理 \n
                    print(file.read())
            else:
                print(f"{Fore.YELLOW}⚠{Fore.RESET} {Fore.BLUE}{fun位置}{Fore.RESET} {Fore.YELLOW}为空{Fore.RESET}")
        return 0
    except FileNotFoundError:
        print(f"{Fore.RED}✕{Fore.RESET} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{fun位置}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}✕{Fore.RESET} 读取 {Fore.BLUE}{fun位置}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
