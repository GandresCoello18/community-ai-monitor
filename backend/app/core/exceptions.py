class AppException(Exception):
    """Base application exception with HTTP mapping."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=404)


class ValidationError(AppException):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code=code, message=message, status_code=400)
