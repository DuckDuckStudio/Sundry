class Response:
    # InstallerUrl 常见的意外响应类型
    unexpectedTypes: set[str] = {"xml", "json", "html"}

# logsAnalyse.py
EXE_LIST_LIMIT = 3 # ExeRunInfo 输出的 exe 文件个数限制，超过限制的信息会被裁断。仅在非详细模式下使用。
