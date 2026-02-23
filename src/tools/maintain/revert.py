import os
import subprocess
from colorama import Fore
from catfood.constant import YES, NO
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置

def main(args: list[str]) -> int:
    # 格式化输入
    if (len(args) < 3):
        print(f"{消息头.错误} 参数不够")
        print(f"{消息头.提示} 运行 sundry help 查看帮助")
        return 1

    # 第 1 个参数 - 需要还原的仓库
    if args[0].lower() in ["both", "all", "双仓库", "所有"]:
        需要还原的仓库 = ("pkgs", "tools")
    elif args[0].lower() in ["pkgs", "winget-pkgs", "清单仓库", "包仓库"]:
        需要还原的仓库 = ["pkgs"]
    elif args[0].lower() in ["tools", "winget-tools", "工具仓库", "日志仓库"]:
        需要还原的仓库 = ["tools"]
    else:
        print(f"{消息头.错误} 需要还原的仓库 (参数1) 不是有效值。")
        return 1

    # 第 2 个参数 - 是否已提交
    if args[1].lower() in (*YES, "已提交"):
        是否已提交 = True
    elif args[1].lower() in (*NO, "未提交"):
        是否已提交 = False
    else:
        print(f"{消息头.错误} 是否已提交 (参数2) 不是有效值。")
        return 1

    # 第 3 个参数 - 是否丢弃
    if args[2].lower() in (*YES, "丢弃"):
        是否丢弃 = True
    elif args[2].lower() in (*NO, "不丢弃"):
        是否丢弃 = False
    else:
        print(f"{消息头.错误} 是否丢弃 (参数3) 不是有效值。")
        return 1

    for repo in 需要还原的仓库:
        仓库路径 = 读取配置(f"paths.winget-{repo}")
        if isinstance(仓库路径, str) and 仓库路径:
            if not 还原(
                repo,
                仓库路径,
                是否已提交,
                是否丢弃
            ):
                # 还原过程中发生错误，中止
                return 1
        else:
            print(f"{消息头.错误} 未能读到 {repo} 仓库的路径")
            return 1
    else:
        return 0

def 还原(哪个仓库: str, 仓库路径: str, 是否已提交: bool, 是否丢弃: bool) -> bool:
    """
    尝试还原指定的仓库
    
    :param 哪个仓库: pkgs 或 tools
    :type 哪个仓库: str
    :param 仓库路径: 指定仓库文件夹的所在位置
    :type 仓库路径: str
    :param 是否已提交: 仓库中的修改是否已经提交？
    :type 是否已提交: bool
    :param 是否丢弃: 是否需要丢弃仓库中的修改
    :type 是否丢弃: bool
    :return: 是否成功还原
    :rtype: bool
    """

    try:
        os.chdir(仓库路径)
        # 获取当前所在分支
        当前分支 = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
        if ((当前分支 == "master") and (哪个仓库 == "pkgs")) or ((当前分支 == "main") and (哪个仓库 == "tools")):
            print(f"{消息头.错误} [{哪个仓库}仓库] 你不能丢弃主分支")
            return False
        
        if ((not 是否已提交) and 是否丢弃):
            # 提交丢弃内容
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "--no-gpg-sign", "-m", "丢弃"], check=True)

        # 签回主分支
        主分支 = "master" if 哪个仓库 == "pkgs" else "main"
        subprocess.run(["git", "checkout", 主分支], check=True)

        if 当前分支:
            # 丢弃分支
            subprocess.run(["git", "branch", "-D", 当前分支], check=True)
        else:
            print(f"{消息头.警告} [{哪个仓库}仓库] 未获取到需要丢弃的分支名称")
    except Exception as e:
        print(f"{消息头.错误} 尝试还原 {哪个仓库} 仓库时出现异常: {Fore.RED}{e}{Fore.RESET}")
        return False
    print(f"{消息头.成功} 已还原 {哪个仓库} 仓库")
    return True
