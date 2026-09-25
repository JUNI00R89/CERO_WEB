from fastapi import Depends

from dependencies.auth import get_usuario_actual
from exceptions import SinPermisos
from models import Usuario
from roles import ROL_ADMIN, ROL_USUARIO

MENSAJE_SIN_PERMISOS = "No tienes permisos para realizar esta acción."


def _rechazar(mensaje: str = MENSAJE_SIN_PERMISOS):
    raise SinPermisos(mensaje)


def es_admin(usuario) -> bool:
    return getattr(usuario, "rol", None) == ROL_ADMIN


def require_roles(*roles_permitidos: str):
    """Construye una dependencia que exige uno de los roles indicados.

    Reutiliza get_usuario_actual (Parte 6); no vuelve a validar el JWT.
    """

    def dependencia(usuario_actual: Usuario = Depends(get_usuario_actual)) -> Usuario:
        if usuario_actual.rol not in roles_permitidos:
            _rechazar()
        return usuario_actual

    return dependencia


def require_admin(usuario_actual: Usuario = Depends(get_usuario_actual)) -> Usuario:
    if usuario_actual.rol != ROL_ADMIN:
        _rechazar()
    return usuario_actual


def require_user(usuario_actual: Usuario = Depends(get_usuario_actual)) -> Usuario:
    if usuario_actual.rol != ROL_USUARIO:
        _rechazar()
    return usuario_actual
