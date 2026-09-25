from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TIPOS_CUENTA = {"efectivo", "tarjeta", "ahorro", "inversion", "credito"}


class CuentaBase(BaseModel):
    nombre: str
    tipo: str
    saldo: Decimal = Field(default=Decimal("0"), ge=0)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        texto = value.strip()
        if len(texto) < 2 or len(texto) > 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return texto

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: str) -> str:
        if value not in TIPOS_CUENTA:
            raise ValueError(
                f"Tipo inválido: debe ser uno de {', '.join(sorted(TIPOS_CUENTA))}"
            )
        return value


class CuentaCreate(CuentaBase):
    usuario_id: int = Field(gt=0)


class CuentaUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
    saldo: Decimal | None = Field(default=None, ge=0)
    usuario_id: int | None = Field(default=None, gt=0)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return None
        texto = value.strip()
        if len(texto) < 2 or len(texto) > 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return texto

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: str | None) -> str | None:
        if value is not None and value not in TIPOS_CUENTA:
            raise ValueError(
                f"Tipo inválido: debe ser uno de {', '.join(sorted(TIPOS_CUENTA))}"
            )
        return value


class CuentaOut(CuentaBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)