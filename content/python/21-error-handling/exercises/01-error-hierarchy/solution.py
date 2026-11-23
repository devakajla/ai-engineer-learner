class AppError(Exception):
    status_code = 500

    def to_dict(self) -> dict:
        return {"error": type(self).__name__, "message": str(self)}


class NotFoundError(AppError):
    status_code = 404

    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(f"{resource} {resource_id} not found")
        self.resource = resource
        self.resource_id = resource_id


class ConflictError(AppError):
    status_code = 409


class ValidationError(AppError):
    status_code = 422

    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"{field}: {message}")
        self.field = field

    def to_dict(self) -> dict:
        return {**super().to_dict(), "field": self.field}
