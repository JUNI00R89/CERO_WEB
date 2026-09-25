from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

TIPOS_MOVIMIENTO = {"ingreso", "gasto"}


class MovimientoBase(BaseModel):
    tipo: str
    monto: Decimal = Field(gt=0)
    descripcion: str | None = Field(default=None, max_length=500)

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: str) -> str:
        if value not in TIPOS_MOVIMIENTO:
            raise ValueError("Tipo inválido: debe ser 'ingreso' o 'gasto'")
        return value

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, value: str | None) -> str | None:
        if value is None:
            return None
        texto = value.strip()
        if not texto:
            return None
        if len(texto) > 500:
            raise ValueError("La descripción no puede superar los 500 caracteres")
        return texto


class MovimientoCreate(MovimientoBase):
    fecha: datetime | None = None
    usuario_id: int = Field(gt=0)
    cuenta_id: int = Field(gt=0)
    categoria_id: int = Field(gt=0)


class MovimientoUpdate(BaseModel):
    tipo: str | None = None
    monto: Decimal | None = Field(default=None, gt=0)
    descripcion: str | None = Field(default=None, max_length=500)
    fecha: datetime | None = None
    usuario_id: int | None = Field(default=None, gt=0)
    cuenta_id: int | None = Field(default=None, gt=0)
    categoria_id: int | None = Field(default=None, gt=0)

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, value: str | None) -> str | None:
        if value is not None and value not in TIPOS_MOVIMIENTO:
            raise ValueError("Tipo inválido: debe ser 'ingreso' o 'gasto'")
        return value

    @field_validator("descripcion")
    @classmethod
    def validar_descripcion(cls, value: str | None) -> str | None:
        if value is None:
            return None
        texto = value.strip()
        if not texto:
            return None
        if len(texto) > 500:
            raise ValueError("La descripción no puede superar los 500 caracteres")
        return texto


class MovimientoOut(MovimientoBase):
    id: int
    fecha: datetime
    usuario_id: int
    cuenta_id: int
    categoria_id: int

    model_config = ConfigDict(from_attributes=True)