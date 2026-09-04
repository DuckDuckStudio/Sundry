import re

import pytest

from function.constant.regexes import LOGS_ZIP_DOWNLOAD_URL


@pytest.mark.parametrize(
    "content",
    (
        "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-425671-1-artifacts.zip",  # +, 1
        "https://cdn.winget.microsoft.com/artifacts/WinGetSvc-Validation-425671-10-artifacts.zip",  # +, +
    ),
)
def test_logs_zip_download_url(content: str):
    """
    测试日志下载链接匹配
    """

    result = re.findall(LOGS_ZIP_DOWNLOAD_URL, content)
    assert len(result) == 1, "应该有且仅匹配到 1 个日志下载链接"
