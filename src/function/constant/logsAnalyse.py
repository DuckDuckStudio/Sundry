"""tools/logsAnalyse.py 的常量"""

from dataclasses import dataclass
from typing import Final

from colorama import Fore

EXE_LIST_LIMIT: Final[int] = 3
"""
ExeRunInfo 输出的 exe 文件个数限制 (3个)，超过限制的信息会被裁断。

仅在非详细模式下使用。
"""


@dataclass
class Explanation:
    """
    日志中的关键词对应的解释

    Attributes:
        message: 关键词对应的解释
        color: 解释文本的颜色
    """

    message: str
    color: str | None = None

    def get_colored_message(self) -> str:
        """
        获取带颜色的解释内容。

        Returns:
            str:
                带颜色的解释内容；
                如果该解释没有指定颜色，则原样返回解释内容。
        """

        if self.color is None:
            return self.message

        return f"{self.color}{self.message}{Fore.RESET}"


@dataclass
class LogKeyWord:
    """
    日志中的关键词

    Attributes:
        keyword: 关键词文本
        explanation: 对应的解释
        file: 限定文件名
    """

    keyword: str
    explanation: Explanation
    file: str | None = None

    def matched(self, content: str, file_name: str | None = None) -> bool:
        """
        判断内容是否匹配关键词，不区分大小写。

        Args:
            content: 指定的内容

        Returns:
            bool: 是否匹配
        """

        if self.keyword.lower() in content.lower():
            if self.file is None:
                return True
            elif file_name is not None:
                return self.file.lower() in file_name.lower()

        return False


KEYWORD_MAP: Final[tuple[LogKeyWord, ...]] = (
    LogKeyWord("[FAIL] Installer failed security check", Explanation("安装程序未通过安全检查", Fore.YELLOW)),
    LogKeyWord("ShellExecute installer failed", Explanation("Shell 执行安装程序失败", Fore.YELLOW)),
    LogKeyWord("Installation failed with exit code", Explanation("以非正常退出代码退出", Fore.RED)),
    LogKeyWord("Package failed updates, dependency or conflict validation.", Explanation("安装依赖错误", Fore.YELLOW)),
    LogKeyWord(
        "CmdTool: Failed with hr = 0x8050111c. Check C:\\Users\\VALIDA~1\\AppData\\Local\\Temp\\MpCmdRun.log for more information",
        Explanation("Defender 扫描失败，这不是误报，这可能和 https://github.com/microsoft/winget-pkgs/issues/399077 有关", Fore.YELLOW),
        "Log_InstallationClient",
    ),
)
"""
InstallationVerificationLogs 中匹配的关键词。

不包括详细模式添加的关键词。
"""

DETAILED_KEYWORD_MAP: Final[tuple[LogKeyWord, ...]] = (
    LogKeyWord("InternetOpenUrl() failed.", Explanation("遇到了网络错误", Fore.RED)),
    LogKeyWord("MSIX installer failed", Explanation("MSIX 安装程序失败", Fore.RED)),
    LogKeyWord("fail", Explanation("一般错误")),
    LogKeyWord("error", Explanation("一般错误")),
    LogKeyWord("Exception", Explanation("异常")),
)
"""
InstallationVerificationLogs 在详细模式中额外匹配的关键词。
"""

EXCLUDE_MAP = {
    "error": [
        # 无关错误
        "Standard error:",
        "The FileSystemWatcher has detected an error",
        "error.exe",  # 不是错误，只是名字带 error 的可执行文件。例如 Git.Git 的 C:\Program Files\Git\usr\bin\gpg-error.exe
    ],
    "fail": [
        "Failed to open available source: msstore",  # msstore 的问题
    ],
}
"""
InstallationVerificationLogs 中匹配的关键词的排除字符串。
"""
