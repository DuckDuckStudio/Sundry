import os
import subprocess
from function.maintain.config import 读取配置
from exception.operation import TryOtherMethods

class 清单信息:
    版本列表= ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0", "1.9.0", "1.10.0"]
    旧版本列表 = ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0", "1.9.0"]
    最新版本 = "1.10.0"
    类型列表 = ["installer", "defaultLocale", "locale", "version", "singleton"]

def 获取清单目录(包标识符: str, 包版本: str | None = None, winget_pkgs目录: str | None = None) -> str | None:
    """
    传入字体或软件包标识符、winget_pkgs目录（不传则自动从配置文件中获取），获取该包的清单目录。

    获取失败返回 None。

    此函数没有输出。
    """

    if not winget_pkgs目录:
        配置值 = 读取配置("paths.winget-pkgs")
        if isinstance(配置值, str):
            winget_pkgs目录 = 配置值
        else:
            return None

    可能的包类型 = ["manifests", "fonts"]

    for 包类型 in 可能的包类型:
        清单目录 = os.path.join(winget_pkgs目录, 包类型, 包标识符[0].lower(), *包标识符.split('.'))
        if 包版本:
            清单目录 = os.path.join(清单目录, 包版本)
        if os.path.exists(清单目录):
            return 清单目录

    return None
        
def 获取现有包版本(包标识符: str, winget_pkgs仓库: str | None = None) -> list[str] | None:
    """
    尝试获取指定的包的现有版本，并返回版本列表: list[str]

    没获取到则返回 None
    """

    版本列表: list[str] = []

    try:
        # 从本地仓库获取版本号
        清单目录 = 获取清单目录(包标识符, winget_pkgs目录=winget_pkgs仓库)
        if not 清单目录:
            raise TryOtherMethods
        
        for 文件夹 in os.listdir(清单目录):
            if os.path.isdir(os.path.join(清单目录, 文件夹)):
                for 文件 in os.listdir(os.path.join(清单目录, 文件夹)):
                    if os.path.isdir(文件):
                        # 如果这个版本文件夹下面还有目录，则代表这可能是类似 Nightly 版本的软件包的标识符的一部分
                        break
                else:
                    # 如果前面的 for 没有 break，则执行
                    版本列表.append(文件夹)
    except TryOtherMethods:
        # 从 WinGet 输出获取版本号
        结果 = subprocess.run(
            ["winget", "show", "--id", 包标识符, "-s", "winget", "-e", "--versions"],
            capture_output=True, text=True, check=True
        )

        离开始还有几行 = 3
        for 行 in [line for line in 结果.stdout.splitlines() if line.strip()]:
            if (离开始还有几行 < 1):
                版本列表.append(行)
            if (包标识符 in 行) or (离开始还有几行 < 3):
                离开始还有几行 -= 1

    if 版本列表:
        return 版本列表
    else:
        return None
