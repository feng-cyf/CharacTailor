from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


# 自定义异常类
class CustomException(Exception):
    def __init__(self, message: str, code: int = 400):
        self.message = message
        self.code = code


# 异常处理类
class ExceptionHandler:
    @staticmethod
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 500, "message": "服务器内部错误", "detail": str(exc)}
        )

    @staticmethod
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": 422, "message": "请求参数验证失败", "detail": exc.errors()}
        )

    @staticmethod
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"code": exc.code, "message": exc.message}
        )

    @classmethod
    def register(cls, app):
        # 注册全局异常处理器
        app.add_exception_handler(Exception, cls.global_exception_handler)
        # 注册请求验证异常处理器
        app.add_exception_handler(RequestValidationError, cls.validation_exception_handler)
        # 注册自定义异常处理器
        app.add_exception_handler(CustomException, cls.custom_exception_handler)