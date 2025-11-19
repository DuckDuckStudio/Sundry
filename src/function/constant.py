class Response:
    # InstallerUrl 常见的意外响应类型
    unexpectedTypes: set[str] = {"xml", "json", "html"}
