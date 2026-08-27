import re
from typing import Final

# logsAnalyse.py
LOGS_ZIP_DOWNLOAD_URL: Final[re.Pattern[str]] = re.compile(r"https://cdn\.winget\.microsoft\.com/artifacts/WinGetSvc-Validation-\d+-\d-artifacts\.zip")
