from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La contraseña no puede estar vacía")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"