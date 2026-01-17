"""
Sundry 所需的一些路径的常量。
"""

import sys
import os.path
import tempfile
from typing import Final

SUNDRY_LOCATION: Final[str] = os.path.normpath(os.path.dirname(os.path.abspath(sys.argv[0])))
"""
Sundry 自身的安装位置。
"""

SUNDRY_TEMP_DIR: Final[str] = os.path.join(tempfile.gettempdir(), "Sundry")
"""
Sundry 存放临时文件的位置。

%TEMP%/Sundry/**
"""

CACHE_DIR: Final[str] = os.path.join(SUNDRY_TEMP_DIR, "Cache")
"""
Sundry 存放缓存的位置。

%TEMP%/Sundry/Cache/**
"""

CONFIG_FILE_PATH: Final[str] = os.path.join(os.path.expanduser("~"), ".config", "DuckStudio", "Sundry", "config.json")
"""
Sundry 的配置文件所在位置。

~/.config/DuckStudio/Sundry/config.json
"""

FUN_TEXT_PATH: Final[str] = os.path.join(SUNDRY_LOCATION, "fun.txt")
"""
Sundry 的 fun.txt 所在位置。

%SUNDRY_LOCATION%/fun.txt
"""

# ===============================================================================

AZP_LOGS_DIR: Final[str] = os.path.join(SUNDRY_TEMP_DIR, "AzurePipelines")
"""
logs-analyse 命令存放从 Azure Pipline 上下载的日志的位置。

%TEMP%/Sundry/AzurePipelines/**
"""

# ===============================================================================

INSTELLER_DOWNLOAD_DIR: Final[str] = os.path.join(SUNDRY_TEMP_DIR, "RemoveAndAutoRemove", "DownloadInstallers")
"""
remove 和 autoremove 命令在验证包版本可用性时，存放通过 `winget download -d ...` 下载的安装程序的位置。

%TEMP%/Sundry/RemoveAndAutoRemove/DownloadInstallers/**
"""

# ===============================================================================

VERIFY_TEMP_DIR: Final[str] = os.path.join(SUNDRY_TEMP_DIR, "Verify")
"""
verify 命令存放临时文件的位置。

%TEMP%/Sundry/Verify/**
"""

# ===============================================================================

MANIFESTS_DIR: Final[str] = os.path.join(SUNDRY_TEMP_DIR, "VerifyAndValidate", "Manifests")
"""
verify 和 validate 命令存放从 PR 获取到的清单文件的位置。

%TEMP%/Sundry/VerifyAndValidate/Manifests/**
"""
