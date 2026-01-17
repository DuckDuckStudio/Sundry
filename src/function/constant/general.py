"""
通用常量
"""

from typing import Final

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
