"""
通用常量
"""

from typing import Final

from function.maintain.config import 读取配置

UNEXPECTED_TYPES: Final[set[str]] = {"xml", "json", "html"}
"""
InstallerUrl 常见的意外响应类型。
- xml
- json
- html
"""

SUNDRY_VERSION: Final = "develop"
"""
Sundry 的版本
"""

# pylint: disable=line-too-long
PR_TOOL_NOTE: Final = f"> This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/) {f'{SUNDRY_VERSION} version' if SUNDRY_VERSION in ('develop', 'locale') else f'version {SUNDRY_VERSION}'} 🚀."
"""
拉取请求正文中的 Sundry 工具说明。

- 特殊版本
> This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/) locale/develop version 🚀.

- 一般版本
> This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/) version x.x.x 🚀.
"""

def _get_retry_interval() -> int:
    """
    尝试从 git.retry_interval 配置获取 Git 操作重试间隔秒数，
    如果没能获取到返回默认值 50 秒。

    Returns:
        int: Git 操作重试间隔秒数，默认为 50 秒。
    """

    _config_value = 读取配置("git.retry_interval")
    if not isinstance(_config_value, int):
        _config_value = 50

    return _config_value

RETRY_INTERVAL: int
"""
Git 操作重试间隔秒数

默认为 50 秒
"""

# TODO 通过配置文件设置请求超时时间
REQUEST_TIMEOUT: Final = 30
"""
请求超时时间（秒）
"""

def __getattr__(name: str) -> int:
    """
    初始化需要读取配置的常量

    - RETRY_INTERVAL

    Args:
        name: 读取的属性的名称

    Returns:
        int: 初始化后的值

    Raises:
        AttributeError: 意外的名称
    """

    if name == "RETRY_INTERVAL":
        _retry_interval = _get_retry_interval()
        globals()["RETRY_INTERVAL"] = _retry_interval
        return _retry_interval
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
