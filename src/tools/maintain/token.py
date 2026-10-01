"""
有关 GitHub Token 管理的函数。
"""

import os
from getpass import getpass
from typing import Literal

import keyring
import keyring.errors
from catfood.exceptions.operation import OperationFailed
from catfood.functions.print import MSHead
from colorama import Fore

from function.maintain.config import 读取配置


def main(operation: str) -> Literal[0, 1]:
    """
    ``sundry config token <set/remove>``

    此函数本质上就是一个中转站，如果你知道具体的操作，可以直接调用 ``set_token()`` 或 ``remove_token()``。

    :param operation: "set" 设置 Token，"remove" 移除设置的 Token。
    :type operation: str
    :return: 退出代码
    :rtype: Literal[0, 1]
    """

    match operation:
        case "set":
            return set_token()
        case "remove":
            return remove_token()
        case "":
            print(f"{MSHead.Error} 请告诉我你要做什么")
            return 1
        case _:
            print(f"{MSHead.Error} 未知的操作")
            return 1

def remove_token() -> Literal[0, 1]:
    """
    ``sundry config token remove`` 的实现。

    :return: 退出代码
    :rtype: Literal[0, 1]
    """

    try:
        keyring.delete_password(
            service_name="DuckStudio.Sundry-GitHubToken",
            username="GitHubToken"
        )
        print(f"{MSHead.Success} 成功移除设置的 Token")
        return 0
    except keyring.errors.PasswordDeleteError:
        print(f"{MSHead.Warning} 没有找到已设置的 Token")
        return 0
    except keyring.errors.KeyringError as e:
        print(f"{MSHead.Error} 移除 Token 时发生异常: ({type(e)}) {e}")
        return 1

def set_token() -> Literal[0, 1]:
    """
    ``sundry config token set`` 的实现。

    :return: 退出代码
    :rtype: Literal[0, 1]
    """

    token = getpass("请粘贴 Token: ")
    if not token.startswith(("ghp_", "github_pat_")):
        print(f"{MSHead.Error} Token 格式不正确，GitHub Token 应以 \"ghp_\" 或 \"github_pat_\" 开头。")
        return 1

    try:
        keyring.set_password(
            service_name="DuckStudio.Sundry-GitHubToken",
            username="GitHubToken",
            password=token
        )
        del token
        print(f"{MSHead.Success} 成功设置 Token")
        return 0
    except keyring.errors.KeyringError as e:
        print(f"{MSHead.Error} 设置 Token 时发生异常: ({type(e)}) {e}")
        return 1

def read_token(silent: bool = False) -> str | None:
    """
    尝试从配置文件中指定的源读取 GitHub Token，读取失败返回 ``None``。

    :pram silent: 是否在读取失败时保持沉默（不输出错误信息）
    :type silent: bool
    :return: 读取到的 Token，或 ``None``（如果读取失败）
    :rtype: str | None
    """

    try:
        source = 读取配置("github.token")
        if not isinstance(source, str):
            raise OperationFailed("未能从配置文件中获取 GitHub Token 读取源")

        if source == "env":
            if token := os.getenv("GITHUB_TOKEN"):
                return token
            else:
                raise OperationFailed("未能从环境变量 GITHUB_TOKEN 中读取 GitHub Token")
        else:
            token: str | None
            match source:
                case "keyring":
                    token = keyring.get_password(
                        "DuckStudio.Sundry-GitHubToken", "GitHubToken"
                    )
                case "komac":
                    token = keyring.get_password(
                        "github-access-token.komac", "github-access-token"
                    )
                case "glm":
                    token = keyring.get_password(
                        "github-access-token.glm", "github-access-token"
                    )
                case _:
                    raise OperationFailed(f"未知的 GitHub Token 读取源: {source}")

            if token:
                return token
            else:
                raise OperationFailed(f"未能从 {source} 源中读取 GitHub Token")
    except (OperationFailed, keyring.errors.KeyringError) as e:
        if not silent:
            print(f"{MSHead.Error} 读取 GitHub Token 失败: {Fore.RED}{e}{Fore.RESET}")
        return None
