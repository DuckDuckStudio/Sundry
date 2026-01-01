"""tools/logsAnalyse.py 的常量"""

from typing import Final

EXE_LIST_LIMIT: Final[int] = 3
"""
ExeRunInfo 输出的 exe 文件个数限制 (3个)，超过限制的信息会被裁断。

仅在非详细模式下使用。
"""
