from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from exceptions import ErrorDominio
from schemas.response import ApiResponse


def _cuerpo_error(mensaje: str):
    """Formato de error consistente con el resto de la API."""
    return {"detail": ApiResponse.error(message=mensaje, data=None).model_dump()}


def registrar_handlers(app: FastAPI) -> None:
    @app.exception_handler(ErrorDominio)
    async def _error_dominio_handler(request: Request, exc: ErrorDominio):
        return JSONResponse(
            status_code=exc.status_code,
            content=_cuerpo_error(exc.mensaje),
            headers=exc.headers,
        )

    @app.exception_handler(HTTPException)
    async def _http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict):
            content = exc.detail
        else:
            content = _cuerpo_error(str(exc.detail))
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=_cuerpo_error("Datos de entrada inválidos. Revisa los campos enviados."),
        )

    @app.exception_handler(Exception)
    async def _catch_all_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=_cuerpo_error("Error interno del servidor"),
        )