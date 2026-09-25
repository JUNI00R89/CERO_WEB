from pydantic import BaseModel, ConfigDict, Field, field_validator

TIPOS_CATEGORIA = {"ingreso", "gasto"}


class CategoriaBase(BaseModel):
    nombre: str
    tipo: str

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
        if value not in TIPOS_CATEGORIA:
            raise ValueError("Tipo inválido: debe ser 'ingreso' o 'gasto'")
        return value


class CategoriaCreate(CategoriaBase):
    usuario_id: int = Field(gt=0)


class CategoriaUpdate(BaseModel):
    nombre: str | None = None
    tipo: str | None = None
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
        if value is not None and value not in TIPOS_CATEGORIA:
            raise ValueError("Tipo inválido: debe ser 'ingreso' o 'gasto'")
        return value


class CategoriaOut(CategoriaBase):
    id: int
    usuario_id: int

    model_config = ConfigDict(from_attributes=True)