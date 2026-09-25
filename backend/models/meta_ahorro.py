from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class MetaAhorro(Base):
    __tablename__ = "metas_ahorro"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    monto_objetivo: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    monto_actual: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=0)
    fecha_objetivo: Mapped[date] = mapped_column(Date, nullable=False)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id"), index=True, nullable=False
    )

    usuario = relationship("Usuario", back_populates="metas_ahorro")