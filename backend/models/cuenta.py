from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Cuenta(Base):
    __tablename__ = "cuentas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), index=True, nullable=False
    )

    usuario = relationship("Usuario", back_populates="cuentas")
    movimientos = relationship("Movimiento", back_populates="cuenta")