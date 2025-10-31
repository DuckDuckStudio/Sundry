import base64
import requests
from typing import Any
from exception.request import RequestException

def 获取GitHub文件内容(github_token: str | int | None, 仓库: str, 文件路径: str) -> str | None:
    """
    尝试通过 GitHub API 获取文件 base64，解码后返回。

    获取失败返回 `None`
    """

    try:
        # 由于政府政策，在中国大陆不允许使用 raw.githubusercontent.com
        # 127.0.0.1 欢迎你 XD
        # raw_url = f"https://raw.githubusercontent.com/{仓库}/refs/heads/{分支}/{文件路径}"

        api = f"https://api.github.com/repos/{仓库}/contents/{文件路径}"
        响应 = 请求GitHubAPI(api, github_token)
        if not 响应:
            raise RequestException(f"响应为空: {响应}")

        return base64.b64decode(响应["content"]).decode("utf-8")
    except Exception:
        return None
    
def 请求GitHubAPI(apiUrl: str, github_token: str | int | None = None) -> Any | None:
    """
    尝试向指定的 `apiUrl` 发送 `GET` 请求，返回 `响应.json()`

    遇到 `Exception` 返回 `None`
    """

    请求头: dict[str, str] = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    if not github_token:
        请求头.pop("Authorization", None)
    try:
        响应 = requests.get(apiUrl, headers=请求头)
        响应.raise_for_status()
        return 响应.json()
    except Exception:
        return None
