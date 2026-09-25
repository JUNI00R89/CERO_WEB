from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from config import ALGORITMO_JWT, SECRET_KEY, get_access_token_expire_minutes


def _claves_jwt():
    return SECRET_KEY, get_access_token_expire_minutes()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_password(password: str, hash_almacenado: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_almacenado.encode("utf-8"))
    except ValueError:
        return False


def crear_token_acceso(usuario) -> str:
    secret, expiracion_minutos = _claves_jwt()
    exp = datetime.now(timezone.utc) + timedelta(minutes=expiracion_minutos)
    payload = {
        "sub": str(usuario.id),
        "correo": usuario.correo,
        "rol": usuario.rol,
        "exp": exp,
    }
    return jwt.encode(payload, secret, algorithm=ALGORITMO_JWT)


def decodificar_token(token: str) -> dict:
    secret, _ = _claves_jwt()
    return jwt.decode(token, secret, algorithms=[ALGORITMO_JWT])