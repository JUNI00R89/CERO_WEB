import os

from dotenv import load_dotenv

load_dotenv()

ALGORITMO_JWT = "HS256"
ACCESS_TOKEN_EXPIRE_DEFAULT_MINUTOS = 30

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL no está configurado en el archivo .env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está configurado en el archivo .env")


def get_access_token_expire_minutes() -> int:
    try:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(ACCESS_TOKEN_EXPIRE_DEFAULT_MINUTOS)))
    except ValueError:
        return ACCESS_TOKEN_EXPIRE_DEFAULT_MINUTOS