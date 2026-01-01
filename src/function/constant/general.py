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
