import ctypes
import json
import subprocess
from collections.abc import Callable
from pathlib import Path

from catfood.functions.print import MSHead
from colorama import Fore

from function.args import get_manifest_dir_from_args
from function.constant.registry import REGISTRY_ENTRY
from function.files.manifest import validate_manifest
from function.registry import read_installer_registry_entries


def main(args: list[str]) -> int:
    """
    `sundry verify` 命令的入口函数。

    Args:
        args:
            传入的参数列表
            - `sundry verify <清单文件夹路径>`
            - `sundry verify <GitHub PR 链接或编号>`
            - `sundry verify <包标识符> <包版本>`

    Returns:
        int: 退出代码。
    """

    manifest_dir: Path | None = get_manifest_dir_from_args(args)
    if not manifest_dir:
        return 1

    result = validate_manifest(manifest_dir)
    if result:
        return result
    del result

    old_registry_entries: list[REGISTRY_ENTRY] = read_installer_registry_entries()

    result = operate_local_manifest(manifest_dir, _test_install)
    if result:
        return result
    del result

    new_registry_entries: list[REGISTRY_ENTRY] = read_installer_registry_entries()

    registry_entries_diff: list[REGISTRY_ENTRY] = []
    for registry_entry in new_registry_entries:
        if registry_entry not in old_registry_entries:
            registry_entries_diff.append(registry_entry)

    if registry_entries_diff:
        for i, registry_entry in enumerate(registry_entries_diff):
            print(
                f"{f'({i+1}/{len(registry_entries_diff)})' if len(registry_entries_diff) > 1 else MSHead.Message} 注册表条目变更："
            )
            registry_entry.print_yaml()

    else:
        print(f"{MSHead.Warning} 没有找到注册表条目变更")

    try:
        input("按 ENTER 继续测试卸载，按 CTRL + C 结束...")
        result = operate_local_manifest(manifest_dir, _test_uninstall)
        if result:
            return result
        del result
    except KeyboardInterrupt:
        pass

    print(f"{MSHead.Success} 成功测试指定的清单")
    return 0


def _test_install(manifest_dir: Path) -> int:
    """
    尝试使用 `winget install --manifest` 命令安装清单。

    Args:
        manifest_dir: 清单文件目录所在位置路径。

    Returns:
        int: WinGet 退出代码
    """

    try:
        print(f"{MSHead.Information} 尝试安装 {manifest_dir} ...")
        subprocess.run(
            [
                "winget",
                "install",
                "--manifest",
                manifest_dir,
                "--accept-source-agreements",
                "--accept-package-agreements",
            ],
            check=True,
        )
        return 0
    except subprocess.CalledProcessError as e:
        print(
            f"{MSHead.Error} 尝试安装包失败，WinGet 返回非零退出代码 {Fore.RED}{e.returncode}{Fore.RESET}"
        )
        return e.returncode


def _test_uninstall(manifest_dir: Path) -> int:
    """
    尝试使用 `winget uninstall --manifest` 命令卸载清单。

    Args:
        manifest_dir: 清单文件目录所在位置路径。

    Returns:
        int: WinGet 退出代码。
    """

    try:
        print(f"{MSHead.Information} 尝试卸载 {manifest_dir} ...")
        subprocess.run(
            [
                "winget",
                "uninstall",
                "--manifest",
                manifest_dir,
                "--accept-source-agreements",
            ],
            check=True,
        )
        return 0
    except subprocess.CalledProcessError as e:
        print(
            f"{MSHead.Error} 尝试卸载包失败，WinGet 返回非零退出代码 {Fore.RED}{e.returncode}{Fore.RESET}"
        )
        return e.returncode


def operate_local_manifest(manifest_dir: Path, operation: Callable[[Path], int]) -> int:
    """
    （如果未启用）尝试临时启用 WinGet 本地清单操作，然后运行指定的操作函数。

    Args:
        manifest_dir:
            清单文件夹所在位置路径，将作为参数传递给 `operation` 指定的函数。
        operation:
            需要运行的操作函数。

    Returns:
        1: 处理 WinGet 本地清单设置时遇到错误。
        int: WinGet 退出代码。
    """

    try:
        winget_settings = json.loads(
            subprocess.check_output(
                ["winget", "settings", "export"], text=True, timeout=10
            )
        )

        if not isinstance(winget_settings, dict):
            raise TypeError(
                f"解析后的 WinGet 设置不是字典，而是 {type(winget_settings).__name__}"
            )
    except subprocess.CalledProcessError as e:
        print(
            f"{MSHead.Error} 获取 winget 设置失败: {Fore.BLUE}{' '.join(e.cmd)}{Fore.RESET} 命令返回非零退出代码 {Fore.RED}{e.returncode}{Fore.RESET}"
        )
        return e.returncode
    except json.JSONDecodeError as e:
        print(
            f"{MSHead.Error} 解析 winget 设置失败:\n{e.doc}\n{Fore.RED}{e.msg}{Fore.RESET}"
        )
        return 1
    except TypeError as e:
        print(f"{MSHead.Error} {e}")
        return 1

    temporarily_enabled = False
    # 如果没有启用本地清单
    if not winget_settings.get("adminSettings", {}).get("LocalManifestFiles", False):  # pyright: ignore[reportUnknownMemberType]
        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            # 启用本地清单操作需要管理员权限
            print(f"{MSHead.Error} 你没有启用本地清单操作，临时启用它需要管理员权限")
            print(
                f"{MSHead.Hint} 请在管理员权限的终端中运行: {Fore.BLUE}winget settings --enable LocalManifestFiles{Fore.RESET}"
            )
            return 1
        else:
            try:
                subprocess.run(
                    ["winget", "settings", "--enable", "LocalManifestFiles"], check=True
                )
                temporarily_enabled = True
                print(
                    f"{MSHead.Message} 临时启用 WinGet 本地清单操作 (LocalManifestFiles)"
                )
            except subprocess.CalledProcessError as e:
                print(
                    f"{MSHead.Error} 你没有启用本地清单操作，Sundry 尝试临时启用它但 WinGet 返回了非零退出代码 {Fore.RED}{e.returncode}{Fore.RESET}"
                )
                return e.returncode

    result: int = operation(manifest_dir)

    if temporarily_enabled:
        try:
            print(f"{MSHead.Message} 还原 LocalManifestFiles 设置")
            subprocess.run(
                ["winget", "settings", "--disable", "LocalManifestFiles"], check=True
            )
        except subprocess.CalledProcessError as e:
            print(
                f"{MSHead.Error} 还原 LocalManifestFiles 设置失败，WinGet 返回非零退出代码 {Fore.RED}{e.returncode}{Fore.RESET}"
            )
            print(
                f"{MSHead.Hint} 手动运行 {Fore.BLUE}{' '.join(e.cmd)}{Fore.RESET} 命令还原"
            )
            return e.returncode

    return result
