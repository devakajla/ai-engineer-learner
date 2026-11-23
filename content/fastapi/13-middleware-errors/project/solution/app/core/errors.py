"""Domain errors. They describe WHAT went wrong, never HOW it maps to HTTP."""


class AppError(Exception):
    code = "app_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    code = "not_found"


class ConflictError(AppError):
    code = "conflict"
