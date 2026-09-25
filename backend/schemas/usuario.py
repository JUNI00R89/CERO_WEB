from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from roles import ROL_POR_DEFECTO, ROLES_VALIDOS


def _validar_texto_corto(value: str, etiqueta: str) -> str:
    texto = value.strip()
    if len(texto) < 2 or len(texto) > 100:
        raise ValueError(f"{etiqueta} debe tener entre 2 y 100 caracteres")
    return texto


def _validar_password(value: str | None) -> str | None:
    if value is None:
        return None
    if len(value) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
    return value


class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    correo: EmailStr
    rol: str = Field(default=ROL_POR_DEFECTO, max_length=20)
    activo: bool = True

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        return _validar_texto_corto(value, "El nombre")

    @field_validator("apellido")
    @classmethod
    def validar_apellido(cls, value: str) -> str:
        return _validar_texto_corto(value, "El apellido")

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, value: str) -> str:
        if value not in ROLES_VALIDOS:
            raise ValueError("Rol inválido: debe ser 'usuario' o 'admin'")
        return value


class UsuarioCreate(UsuarioBase):
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        return _validar_password(value)


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    correo: EmailStr | None = None
    password: str | None = None
    rol: str | None = Field(default=None, max_length=20)
    activo: bool | None = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str | None) -> str | None:
        return _validar_texto_corto(value, "El nombre") if value is not None else None

    @field_validator("apellido")
    @classmethod
    def validar_apellido(cls, value: str | None) -> str | None:
        return _validar_texto_corto(value, "El apellido") if value is not None else None

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str | None) -> str | None:
        return _validar_password(value)

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, value: str | None) -> str | None:
        if value is not None and value not in ROLES_VALIDOS:
            raise ValueError("Rol inválido: debe ser 'usuario' o 'admin'")
        return value


class UsuarioOut(UsuarioBase):
    id: int
    fecha_creacion: datetime

    model_config = ConfigDict(from_attributes=True)