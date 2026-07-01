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
