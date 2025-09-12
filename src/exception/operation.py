# 操作异常

class TryOtherMethods(Exception):
    """尝试当前方法失败，请尝试其他方法。"""

class OperationFailed(Exception):
    """当前操作失败"""
