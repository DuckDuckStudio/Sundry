import os
import subprocess
from colorama import Fore
from function.maintain.config import 读取配置
from catfood.exceptions.operation import TryOtherMethods

class 清单信息:
    版本列表= ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0", "1.6.0", "1.7.0", "1.9.0", "1.10.0", "1.12.0"]
    旧版本列表 = 版本列表[:-1]
    最新版本 = 版本列表[-1]
    类型列表 = [
        "installer", # 安装程序清单
        "defaultLocale", # 默认本地化清单
        "locale", # 本地化清单
        "version", # 版本清单
        "singleton", # 单例清单，已弃用
        "merged" # 合并后的清单，常见于验证管道
    ]

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
                    if os.path.isdir(os.path.join(清单目录, 文件夹, 文件)):
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

def FormatManifest(Manifest: str, Comment: str = "# Created with Sundry-Locale") -> str:
    """格式化清单内容"""

    # 修改 ManifestVersion 和版本号
    for OldManifestVersion in 清单信息.旧版本列表:
        # 修改 ManifestVersion
        if f"ManifestVersion: {OldManifestVersion}" in Manifest:
            print(f"更新 ManifestVersion: {Fore.RED}{OldManifestVersion}{Fore.RESET} -> {Fore.GREEN}{清单信息.最新版本}{Fore.RESET}")
            Manifest = Manifest.replace(f"ManifestVersion: {OldManifestVersion}", f"ManifestVersion: {清单信息.最新版本}")

        # 修改 schema 引用，只替换版本号部分
        if f"{OldManifestVersion}.schema.json" in Manifest:
            print(f"更新 schema 引用: {Fore.RED}{OldManifestVersion}{Fore.RESET}.schema.json -> {Fore.GREEN}{清单信息.最新版本}{Fore.RESET}.schema.json")
            Manifest = Manifest.replace(f"{OldManifestVersion}.schema.json", f"{清单信息.最新版本}.schema.json")

    # 替换工具注释
    '''
    判断是否 `清单文件内容`为空 或 第一行以`#`开头
        如果是，在`清单文件内容`第一行前面追加三行工具注释与`# yaml-language-server: $schema=...`与一个空行。
    否则，`清单文件内容`有内容且第一行以`#`开头
        再判断`清单文件内容`第一行是否以`# yaml-language-server`开头
            如果是，在`清单文件内容`第一行前面追加一行工具注释
            如果不是，将`清单文件内容`第一行替换为工具注释
    '''

    # 按行分割文件内容
    lines: list[str] = Manifest.splitlines()

    if (not lines) or (not lines[0].startswith("#")): # https://github.com/DuckDuckStudio/Sundry/issues/28
        # 如果清单文件内容为空或第一行不是以#开头
        # 第一行前面追加三行
        lines.insert(0, "")
        if "\nManifestType: installer" in Manifest: # 安装程序清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.{清单信息.最新版本}.schema.json")
        elif "\nManifestType: defaultLocale" in Manifest: # 默认区域清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.defaultLocale.{清单信息.最新版本}.schema.json")
        elif "\nManifestType: locale" in Manifest: # 一般区域清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.locale.{清单信息.最新版本}.schema.json")
        else: # 版本清单
            lines.insert(0, f"# yaml-language-server: $schema=https://aka.ms/winget-manifest.version.{清单信息.最新版本}.schema.json")
        lines.insert(0, Comment)
    # 否则第一行是#开头
    else:
        # 判断第一行是否以# yaml-language-server开头
        if lines[0].startswith("# yaml-language-server"):
            # 如果是，追加一行
            lines.insert(0, Comment)
        else:
            # 否则，替换第一行
            lines[0] = Comment

    # 将修改后的内容重新合并为一个字符串并赋值回清单文件内容
    Manifest = "\n".join(lines)

    # 确保最后有且只有一行空行
    if not Manifest.endswith('\n'): # 如果最后没有换行符
        Manifest += '\n' # 添加一个换行符
    else: # 如果有了
        Manifest = Manifest.rstrip('\n') + '\n'
        # 管他几个先全移除 -> 添加一个换行符
        # .rstrip() 去除文本末尾的指定字符

    return Manifest
