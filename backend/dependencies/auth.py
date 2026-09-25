import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from exceptions import ErrorAutenticacion
from models import Usuario
from services.auth import decodificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
oauth2_scheme_opcional = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def _error_autenticacion(mensaje: str):
    raise ErrorAutenticacion(mensaje, headers={"WWW-Authenticate": "Bearer"})


def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = decodificar_token(token)
    except jwt.ExpiredSignatureError:
        _error_autenticacion("Token expirado")
    except jwt.PyJWTError:
        _error_autenticacion("Token inválido")

    usuario_id = payload.get("sub")
    if not usuario_id or not usuario_id.isdigit():
        _error_autenticacion("Token inválido")

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if not usuario:
        _error_autenticacion("Token inválido")
    return usuario


def get_usuario_actual_opcional(
    token: str | None = Depends(oauth2_scheme_opcional),
    db: Session = Depends(get_db),
) -> Usuario | None:
    """Devuelve el usuario autenticado si hay token válido, o None si no lo hay.

    Se usa en rutas públicas que cambian de comportamiento cuando quien llama
    es un administrador (por ejemplo, el registro de usuarios).
    """
    if not token:
        return None
    return get_usuario_actual(token=token, db=db)
