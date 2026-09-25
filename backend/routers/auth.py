from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from exceptions import ErrorAutenticacion
from models import Usuario
from schemas.auth import LoginRequest, TokenResponse
from schemas.response import ApiResponse
from services.auth import crear_token_acceso, verificar_password

router = APIRouter(tags=["Autenticación"])


def _rechazar(mensaje: str):
    raise ErrorAutenticacion(mensaje)


@router.post("/login", response_model=ApiResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    if not usuario or not verificar_password(payload.password, usuario.password_hash):
        _rechazar("Credenciales incorrectas")
    if not usuario.activo:
        _rechazar("El usuario está inactivo")
    token = crear_token_acceso(usuario)
    return ApiResponse.ok(
        data=TokenResponse(access_token=token, token_type="bearer"),
        message="Inicio de sesión exitoso",
    )