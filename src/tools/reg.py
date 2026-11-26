"""
查找安装程序注册表条目。
"""

from typing import Literal

from catfood.functions.print import MSHead

from function.constant.registry import REGISTRY_ENTRY
from function.registry import read_installer_registry_entries


def main(args: list[str]) -> Literal[0, 1]:
    """
    `sundry reg <关键词>` 的入口函数。

    该命令用于查找匹配的安装程序注册表条目。

    不区分大小写。

    Args:
        args: 传入的参数列表，多个参数会合并为一个关键词。

    Returns:
        Literal[0, 1]: 退出代码。
    """

    keyword = " ".join(args).strip()
    if not keyword:
        print(f"{MSHead.Error} 请提供注册表条目搜索关键词")
        return 1

    matched_entries = find_installer_registry_entries(keyword)
    if not matched_entries:
        print(f"{MSHead.Information} 没有找到匹配的注册表条目")
        return 0

    prefix = "({index}/{total})" if len(matched_entries) > 1 else MSHead.Message
    for index, entry in enumerate(matched_entries, start=1):
        print(f"{prefix.format(index=index, total=len(matched_entries))} 注册表条目：")
        entry.print_yaml()

    return 0


def find_installer_registry_entries(keyword: str) -> list[REGISTRY_ENTRY]:
    """
    查找匹配的安装程序注册表条目。

    不区分大小写。

    Args:
        keyword: 查找关键词。

    Returns:
        list[REGISTRY_ENTRY]:
            匹配的注册表条目列表；
            没有匹配则为空列表。
    """

    return [
        entry
        for entry in read_installer_registry_entries()
        if _matches_registry_entry(entry, keyword)
    ]


def _matches_registry_entry(entry: REGISTRY_ENTRY, keyword: str) -> bool:
    """
    判断该注册表条目的 `AppsAndFeaturesEntries` 字段是否包含搜索关键词。

    不区分大小写。

    Args:
        entry: 指定的注册表条目。
        keyword: 搜索关键词。

    Returns:
        bool: 是否包含搜索关键词。
    """

    normalized_keyword: str = keyword.lower()
    return any(
        value is not None and normalized_keyword in value.lower()
        for value in (entry.ProductCode, entry.DisplayName, entry.DisplayVersion, entry.Publisher)
    )
