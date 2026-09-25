from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), index=True, nullable=False
    )
    cuenta_id: Mapped[int] = mapped_column(
        ForeignKey("cuentas.id"), index=True, nullable=False
    )
    categoria_id: Mapped[int] = mapped_column(
        ForeignKey("categorias.id"), index=True, nullable=False
    )

    usuario = relationship("Usuario", back_populates="movimientos")
    cuenta = relationship("Cuenta", back_populates="movimientos")
    categoria = relationship("Categoria", back_populates="movimientos")