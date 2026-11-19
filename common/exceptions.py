"""零 Qt 异常层。

所有业务异常从此派生，保持 ui 层与业务层的解耦。
"""


class AppError(Exception):
    """应用基础异常。"""


class ConfigError(AppError):
    """配置相关错误。"""


class PromptError(AppError):
    """提示词加载/解析相关错误。"""


class ServiceError(AppError):
    """服务层错误。"""
