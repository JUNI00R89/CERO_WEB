from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MetaAhorroBase(BaseModel):
    nombre: str
    monto_objetivo: Decimal = Field(gt=0)
    monto_actual: Decimal = Field(default=Decimal("0"), ge=0)
    fecha_objetivo: date

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        texto = value.strip()
        if len(texto) < 2 or len(texto) > 100:
            raise ValueError("El nombre debe tener entre 2 y 100 caracteres")
        return texto


class MetaAhorroCreate(MetaAhorroBase):
    usuario_id: int = Field(gt=0)


class MetaAhorroUpdate(BaseModel):
    nombre: str | None = None
    monto_objetivo: Decimal | None = Field(default=None, gt=0)
    monto_actual: Decimal | None = Field(default=None, ge=0)
    fecha_objetivo: date | None = None
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


class MetaAhorroOut(MetaAhorroBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)