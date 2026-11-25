"""
有关注册表的函数
"""

import os.path
import winreg

from function.constant.registry import REGISTRY_ENTRY, REGISTRY_FIELDS


def read_installer_registry_entries() -> list[REGISTRY_ENTRY]:
    """
    从注册表中读取安装程序相关条目。

    Returns:
        读取到的注册表条目实例列表。
    """

    registry_entries: list[REGISTRY_ENTRY] = []

    # 读取机器范围 (64位和32位)
    registry_entries.extend(
        _read_registry_entries(
            winreg.HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
            winreg.KEY_WOW64_64KEY,
        )
    )

    registry_entries.extend(
        _read_registry_entries(
            winreg.HKEY_LOCAL_MACHINE,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
            winreg.KEY_WOW64_32KEY,
        )
    )

    # 读取用户范围
    registry_entries.extend(
        _read_registry_entries(
            winreg.HKEY_CURRENT_USER,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
        )
    )

    return registry_entries


def _read_registry_entries(
    hive: int, subkey: str, access: int = 0
) -> list[REGISTRY_ENTRY]:
    """
    从注册表中读取指定项的条目。

    Args:
        hive:
            注册表根键。
        subkey:
            注册表子项路径。
        access:
            访问权限标志，默认为 0（不指定）。

    Returns:
        读取到的注册表条目实例列表。
    """

    entries: list[REGISTRY_ENTRY] = []
    try:
        with winreg.ConnectRegistry(None, hive) as reg:
            with winreg.OpenKey(reg, subkey, 0, winreg.KEY_READ | access) as key:
                index = 0
                while True:
                    try:
                        subkey_name: str = winreg.EnumKey(key, index)
                        index += 1
                        with winreg.OpenKey(key, subkey_name) as subkey_handle:
                            entries.append(
                                _read_registry_entry(
                                    hive, subkey, subkey_name, subkey_handle, access
                                )
                            )
                    except PermissionError:
                        continue
                    except OSError as e:
                        if e.winerror == 259:  # 没有更多项目
                            break
    except FileNotFoundError:
        pass
    return entries


def _read_registry_entry(
    hive: int,
    parent_subkey: str,
    subkey_name: str,
    subkey_handle: winreg.HKEYType,
    access: int = 0,
) -> REGISTRY_ENTRY:
    """
    从注册表项句柄读取单个条目。

    Args:
        hive:
            注册表根键。
        parent_subkey:
            父注册表项路径。
        subkey_name:
            当前子项名称。
        subkey_handle:
            当前子项句柄。
        access:
            注册表访问视图标志。

    Returns:
        读取到的注册表条目实例。
    """

    entry: dict[str, str | None] = {
        "RegistryPath": _get_registry_path(hive, parent_subkey, subkey_name, access),
        "Scope": ("machine" if hive == winreg.HKEY_LOCAL_MACHINE else "user"),
        "ProductCode": subkey_name,
    }
    for field in REGISTRY_FIELDS:
        entry[field] = _read_registry_value(subkey_handle, field)
    return REGISTRY_ENTRY.from_dict(entry)


def _get_registry_path(
    hive: int, parent_subkey: str, subkey_name: str, access: int = 0
) -> str:
    """
    生成当前注册表项的完整路径字符串。

    Args:
        hive:
            注册表根键。
        parent_subkey:
            父注册表项路径。
        subkey_name:
            当前子项名称。
        access:
            注册表访问视图标志。

    Returns:
        当前注册表项的完整路径字符串。
    """

    hive_name = (
        "HKEY_LOCAL_MACHINE"
        if hive == winreg.HKEY_LOCAL_MACHINE
        else "HKEY_CURRENT_USER"
    )
    subkey_path = parent_subkey
    if (access == winreg.KEY_WOW64_32KEY) and parent_subkey.upper().startswith(
        "SOFTWARE\\"
    ):
        subkey_path = parent_subkey.replace("SOFTWARE\\", "SOFTWARE\\WOW6432Node\\", 1)

    return f"{hive_name}\\{subkey_path}\\{subkey_name}"


def _read_registry_value(key: winreg.HKEYType, name: str) -> str | None:
    """
    从注册表项中读取指定名称的键的字符串值。

    Args:
        key:
            注册表项句柄。
        name:
            要读取的值的名称。

    Returns:
        str: 读取到的值的字符串。
        None: 未找到该键。
    """

    try:
        value, value_type = winreg.QueryValueEx(key, name)

        # 有关值的类型，请参阅
        # https://learn.microsoft.com/zh-cn/windows/win32/shell/hkey-type
        if value_type == winreg.REG_EXPAND_SZ:
            # 展开环境变量
            return os.path.expandvars(value)
        else:
            # 其他类型转换为字符串
            return str(value)
    except FileNotFoundError:
        return None
