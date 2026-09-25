from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T | None = None

    @classmethod
    def ok(cls, data=None, message="Operación exitosa"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message, data=None):
        return cls(success=False, message=message, data=data)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int