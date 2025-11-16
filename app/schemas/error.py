from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """
    Ошибка
    """

    status: str = "error"
    message: str