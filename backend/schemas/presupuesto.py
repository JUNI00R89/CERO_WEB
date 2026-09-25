from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PresupuestoBase(BaseModel):
    monto_limite: Decimal = Field(gt=0)
    fecha_inicio: date
    fecha_fin: date

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")
        return self


class PresupuestoCreate(PresupuestoBase):
    usuario_id: int = Field(gt=0)
    categoria_id: int = Field(gt=0)


class PresupuestoUpdate(BaseModel):
    monto_limite: Decimal | None = Field(default=None, gt=0)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    usuario_id: int | None = Field(default=None, gt=0)
    categoria_id: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_inicio is not None
            and self.fecha_fin is not None
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")
        return self


class PresupuestoOut(PresupuestoBase):
    id: int
    usuario_id: int
    categoria_id: int

    model_config = ConfigDict(from_attributes=True)