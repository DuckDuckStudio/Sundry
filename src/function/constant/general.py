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

SUNDRY_VERSION: Final = "locale"
"""
Sundry 的版本
"""

PR_TOOL_NOTE: Final = f"### This PR is automatically created by [Sundry](https://github.com/DuckDuckStudio/Sundry/)🚀."
"""
拉取请求正文中的 Sundry 工具说明
"""

_config_value = 读取配置("git.retry_interval")
if not isinstance(_config_value, int):
    _config_value = 50

RETRY_INTERVAL: Final[int] = _config_value
"""
func/command/run 中的 runCommand 函数的重试间隔

默认为 50，单位为秒
"""
