from pathlib import Path

from catfood.functions.format.github import IssueNumber
from catfood.functions.print import MSHead
from colorama import Fore

from function.constant.paths import VERIFY_TEMP_DIR
from function.files.manifest import 获取PR清单, 获取清单目录
from function.maintain.config import 读取配置
from tools.maintain.token import read_token


def get_manifest_dir_from_args(args: list[str]) -> None | Path:
    """
    从传入的参数中获取清单文件夹，返回清单文件夹的路径。

    如果获取失败则返回 None，并输出失败信息。

    Args:
        args:
            传入的参数列表
            - `... <清单文件夹路径>`
            - `... <GitHub PR 链接或编号>`
            - `... <包标识符> <包版本>`

    Returns:
        Path: 清单文件夹的路径，Path 形式。
        None: 获取失败。
    """

    if not args:
        print(f"{MSHead.Error} 请提供参数")
        return None
    elif len(args) == 1:
        # 路径优先
        manifest_dir: Path = Path(args[0]).resolve()

        if not manifest_dir.is_dir():
            if 读取配置("debug"):
                print(
                    f"{MSHead.Debug} 未找到目录 {Fore.BLUE}{manifest_dir}{Fore.RESET}，也许这是一个 GitHub PR 链接"
                )

            pr_number = IssueNumber(args[0])
            if not pr_number:
                print(
                    f"{MSHead.Error} 给定的参数既不是一个存在的文件夹路径，也不是一个 GitHub PR 链接或编号"
                )
                return None

            manifest_dir = Path(VERIFY_TEMP_DIR) / "PRManifest" / pr_number
            if 获取PR清单(pr_number, str(manifest_dir), read_token(silent=True)):
                return None  # 获取清单失败
    elif len(args) == 2:
        result = 获取清单目录(args[0], args[1])
        if not result:
            print(f"{MSHead.Error} 未能获取到仓库中的清单目录")
            return None

        manifest_dir = Path(result)
        del result
    else:
        print(f"{MSHead.Error} 参数太多")
        return None

    return manifest_dir
