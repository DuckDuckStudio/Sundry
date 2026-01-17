import os
import random
from colorama import Fore
from catfood.functions.print import 消息头
from catfood.functions.files import open_file
from function.constant.paths import FUN_TEXT_PATH
from catfood.exceptions.operation import OperationFailed

def main(args: list[str]) -> int:
    """
    sundry fun ...
    
    :param args: 参数
    :type args: list[str]
    :return: 退出代码
    :rtype: int
    """
    
    try:
        if (len(args) > 3):
            raise OperationFailed
        elif (not args) or (args[0] in ("随机", "random")):
            return 获取fun(随机=True)
        elif (len(args) == 1):
            match args[0]:
                case "get" | "list":
                    return 获取fun(随机=False)
                case "编辑" | "edit" | "打开" | "open":
                    return 编辑fun()
                case _:
                    raise OperationFailed
        elif (len(args) == 2):
            match args[0]:
                case "add" | "添加":
                    return 添加fun(args[1])
                case "remove" | "移除":
                    return 移除fun(args[1])
                case "import" | "导入":
                    return 导入fun(FUN_TEXT_PATH, os.path.normpath(os.path.abspath(args[1])))
                case _:
                    raise OperationFailed
        else:
            raise OperationFailed
    except OperationFailed:
        print(f"{消息头.错误} {Fore.RED}参数错误，使用 sundry help 来查看帮助{Fore.RESET}")
        return 1

def 编辑fun() -> int:
    print(f"{消息头.信息} fun.txt 位于 {FUN_TEXT_PATH}")
    print(f"{消息头.信息} 尝试打开 fun.txt ...")
    return open_file(FUN_TEXT_PATH)

def 导入fun(原fun文件: str, 导入fun文件: str) -> int:
    # 导入覆盖原
    try:
        if not os.path.exists(导入fun文件):
            raise FileNotFoundError()
        with open(导入fun文件, 'r', encoding="utf-8") as file:
            导入的fun: list[str] = file.readlines()
            if not 导入的fun:
                print(f"{消息头.警告} {Fore.BLUE}{导入fun文件}{Fore.RESET} (导入) {Fore.YELLOW}为空{Fore.RESET}")
                return 0
    except FileNotFoundError:
        print(f"{消息头.错误} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{导入fun文件}{Fore.RESET} (导入)")
        return 1
    except Exception as e:
        print(f"{消息头.错误} 读取 {Fore.BLUE}{导入fun文件}{Fore.RESET} (导入) 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 去重但保持原始顺序
    try:
        已有fun: set[str] = set()
        去重后的导入fun: list[str] = []
        for line in 导入的fun:
            if line not in 已有fun:
                已有fun.add(line)
                去重后的导入fun.append(line)
        导入的fun = 去重后的导入fun
    except Exception as e:
        print(f"{消息头.错误} 对 {Fore.BLUE}{导入的fun}{Fore.RESET} 去重时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 覆盖原fun文件
    try:
        if not os.path.exists(原fun文件):
            print(f"{消息头.错误} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{原fun文件}{Fore.RESET} (原始)")
            # 询问用户是否创建一个
            try:
                input(f"{消息头.问题} 创建个新的 fun.txt? [ENTER/CTRL+C]")
                with open(原fun文件, 'w', encoding="utf-8"):
                    pass
            except KeyboardInterrupt:
                print(f"\n{消息头.错误} 操作取消")
                return 1
        with open(原fun文件, 'w', encoding="utf-8") as file:
            file.writelines(导入的fun)
        print(f"{消息头.成功} 已将 {Fore.BLUE}{导入fun文件}{Fore.RESET} 导入到 {Fore.BLUE}{原fun文件}{Fore.RESET}")
        return 0
    except Exception as e:
        print(f"{消息头.错误} 导入 {Fore.BLUE}{导入fun文件}{Fore.RESET} 到 {Fore.BLUE}{原fun文件}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

def 移除fun(条目: str) -> int:
    try:
        条目 = 条目.replace("\n", "\\n")
        if not os.path.exists(FUN_TEXT_PATH):
            raise FileNotFoundError()
        with open(FUN_TEXT_PATH, 'r', encoding="utf-8") as file:
            lines = file.readlines()
        if not (f"{条目}\n" in lines):
            print(f"{消息头.警告} 在 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET} 中{Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{条目.replace("\\n", "\n")}{Fore.RESET}")
            return 0
        while f"{条目}\n" in lines:
            # 移除所有匹配的条目
            lines.remove(f"{条目}\n")
        with open(FUN_TEXT_PATH, 'w', encoding="utf-8") as file:
            file.writelines(lines)
        print(f"{消息头.成功} 已将 {Fore.BLUE}{条目.replace("\\n", "\n")}{Fore.RESET} 从 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET} 中移除")
        return 0
    except FileNotFoundError:
        print(f"{消息头.错误} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{消息头.错误} 移除 {Fore.BLUE}{条目.replace("\\n", "\n")}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

def 添加fun(新条目: str) -> int:
    # 查重
    try:
        新条目 = 新条目.replace("\n", "\\n")
        with open(FUN_TEXT_PATH, 'r', encoding="utf-8") as file:
            lines = file.readlines()
            if f"{新条目}\n" in lines:
                print(f"{消息头.警告} {Fore.BLUE}{新条目.replace("\\n", "\n")}{Fore.RESET} {Fore.YELLOW}已存在{Fore.RESET}于 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET}")
                return 0
    except FileNotFoundError:
        print(f"{消息头.错误} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET}")
        # 询问用户是否创建一个
        try:
            input(f"{消息头.问题} 创建个新的 fun.txt? [ENTER/CTRL+C]")
            with open(FUN_TEXT_PATH, 'w', encoding="utf-8"):
                pass
        except KeyboardInterrupt:
            print(f"\n{消息头.错误} 操作取消")
            return 1
    except Exception as e:
        print(f"{消息头.错误} 读取 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
    # 添加新条目
    try:
        with open(FUN_TEXT_PATH, 'a', encoding="utf-8") as file:
            file.write(f"{新条目}\n")
        print(f"{消息头.成功} 已将 {Fore.BLUE}{新条目.replace("\\n", "\n")}{Fore.RESET} 添加进 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET}")
        return 0
    except Exception as e:
        print(f"{消息头.错误} 添加 {Fore.BLUE}{新条目.replace("\\n", "\n")}{Fore.RESET} 到 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1

def 获取fun(随机: bool) -> int:
    try:
        if not os.path.exists(FUN_TEXT_PATH):
            raise FileNotFoundError()
        with open(FUN_TEXT_PATH, 'r', encoding="utf-8") as file:
            if content := file.read().strip():
                if 随机:
                    # 随机单个句子
                    lines: list[str] = []
                    for line in content.split("\n"):
                        if line.strip() and (not any(i in line for i in ("http://", "https://"))):
                            lines.append(line.strip().replace("\\n", "\n"))

                    if lines:
                        print(random.choice(lines))
                    else:
                        print(f"{消息头.错误} 没有合适的行以供随机")
                else:
                    # 整个文件，不处理 \n
                    print(content)
            else:
                print(f"{消息头.警告} {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET} {Fore.YELLOW}为空{Fore.RESET}")
        return 0
    except FileNotFoundError:
        print(f"{消息头.错误} {Fore.YELLOW}未找到{Fore.RESET} {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET}")
        return 1
    except Exception as e:
        print(f"{消息头.错误} 读取 {Fore.BLUE}{FUN_TEXT_PATH}{Fore.RESET} 时发生异常:\n{Fore.RED}{e}{Fore.RESET}")
        return 1
