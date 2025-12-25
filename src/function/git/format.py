def branchName(name: str) -> str:
    """
    格式化分支名

    如 `9 9 6` -> `9_9_6`

    :param name: 需要格式化的分支名
    :type name: str
    :return: 格式化后的分支名
    :rtype: str
    """

    # 单独写这个 func 是怕万一以后又有什么新的需要处理
    # 如果多的话可以开个 dict，然后 for

    return name.replace(" ", "_")
