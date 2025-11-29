import keyring
from typing import cast, Any
from function.print.print import 消息头
from function.github.api import 请求GitHubAPI

def read_token(silent: bool = False):
    """尝试从钥匙环中读取 github-access-token.glm 密钥 (aka GitHub Token)"""

    try:
        token = keyring.get_password("github-access-token.glm", "github-access-token")
        if not token:
            if not silent:
                print("你可能还没设置glm的Token, 请尝试使用以下命令设置Token:\n    glm config --token <YOUR-TOKEN>\n")
            return 0
        return token
    except Exception as e:
        if not silent:
            print(f"{消息头.错误} 读取Token时出错:\n{e}")
        return 0

def 这是谁的Token(token: str | int | None) -> str | None:
    """
    通过 GitHub API 来确认这个 Token 是谁的，失败返回 None。
    """

    if not isinstance(token, str):
        return None
    响应 = 请求GitHubAPI("https://api.github.com/user", token)
    响应 = cast(dict[str, Any], 响应)
    谁的 = 响应.get("login", None)
    if isinstance(谁的, str):
        return 谁的
    else:
        return None
