from colorama import Fore
from typing import cast, Any
from catfood.functions.print import 消息头
from function.maintain.config import 读取配置
from catfood.functions.github.api import 请求GitHubAPI
from catfood.exceptions.operation import OperationFailed

def read_token(silent: bool = False) -> str | None:
    """尝试从配置文件中指定的源读取 Token，读取失败返回 None"""

    try:
        source: None | str | tuple[str, str] | bool = 读取配置("github.token")
        if not isinstance(source, str):
            raise OperationFailed("未能从配置文件中获取读取源")

        if source == "env":
            import os
            if token := os.getenv("GITHUB_TOKEN"):
                return token
            else:
                raise OperationFailed("没有读取到 Token，请确保您设置了 GITHUB_TOKEN 环境变量")
        else:
            import keyring
            if source == "glm":
                service_name, username = ("github-access-token.glm", "github-access-token")
            elif source == "komac":
                service_name, username = ("github-access-token.komac", "github-access-token")
            else:
                raise OperationFailed(f"未知的读取源 {source}")
         
            if token := keyring.get_password(service_name, username):
                return token
            else:
                raise OperationFailed(f"没有读取到 Token，请确保您设置了 {source} 的 Token ({service_name}, {username})")
    except OperationFailed as e:
        if not silent:
            print(f"{消息头.错误} 读取 Token 失败: {Fore.RED}{e}{Fore.RESET}")
        return None

def 这是谁的Token(token: str | int | None) -> str | None:
    """
    通过 GitHub API 来确认这个 Token 是谁的，失败返回 None。
    """

    if not isinstance(token, str):
        return None
    响应 = 请求GitHubAPI("https://api.github.com/user", token=token)
    响应 = cast(dict[str, Any], 响应)
    谁的 = 响应.get("login", None)
    if isinstance(谁的, str):
        return 谁的
    else:
        return None
