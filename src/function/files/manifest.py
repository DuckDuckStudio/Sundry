import os
from function.maintain.config import 读取配置

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
