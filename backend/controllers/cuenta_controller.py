from sqlalchemy.orm import Session

from controllers.base import (
    ResultadoConsulta,
    asignar_propietario,
    build_order_by,
    filtro_propiedad,
    not_found,
    verificar_propietario,
)
from models import Cuenta, Usuario
from schemas.cuenta import CuentaCreate, CuentaUpdate


def _validar_usuario(db: Session, usuario_id: int):
    if not db.query(Usuario).filter(Usuario.id == usuario_id).first():
        not_found(f"Usuario {usuario_id} no existe")


def crear_cuenta(db: Session, payload: CuentaCreate, usuario_actual) -> Cuenta:
    usuario_id = asignar_propietario(usuario_actual, payload.usuario_id)
    _validar_usuario(db, usuario_id)
    cuenta = Cuenta(
        nombre=payload.nombre,
        tipo=payload.tipo,
        saldo=payload.saldo,
        usuario_id=usuario_id,
    )
    db.add(cuenta)
    db.commit()
    db.refresh(cuenta)
    return cuenta


def listar_cuentas(
    db: Session,
    page: int,
    limit: int,
    tipo: str | None,
    usuario_id: int | None,
    sort_by: str,
    order: str,
    usuario_actual,
) -> ResultadoConsulta:
    query = db.query(Cuenta)
    if tipo is not None:
        query = query.filter(Cuenta.tipo == tipo)
    filtro = filtro_propiedad(usuario_actual, Cuenta.usuario_id)
    if filtro is not None:
        query = query.filter(filtro)
    elif usuario_id is not None:
        query = query.filter(Cuenta.usuario_id == usuario_id)
    query = query.order_by(build_order_by(Cuenta, sort_by, order))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return ResultadoConsulta(items, total, page, limit)


def obtener_cuenta(db: Session, cuenta_id: int, usuario_actual) -> Cuenta:
    cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if not cuenta:
        not_found(f"Cuenta {cuenta_id} no existe")
    verificar_propietario(usuario_actual, cuenta)
    return cuenta


def actualizar_cuenta(
    db: Session, cuenta_id: int, payload: CuentaUpdate, usuario_actual
) -> Cuenta:
    cuenta = obtener_cuenta(db, cuenta_id, usuario_actual)
    datos = payload.model_dump(exclude_unset=True)
    if "usuario_id" in datos:
        datos["usuario_id"] = asignar_propietario(usuario_actual, datos["usuario_id"])
        _validar_usuario(db, datos["usuario_id"])
    for campo, valor in datos.items():
        setattr(cuenta, campo, valor)
    db.commit()
    db.refresh(cuenta)
    return cuenta


def eliminar_cuenta(db: Session, cuenta_id: int, usuario_actual) -> Cuenta:
    cuenta = obtener_cuenta(db, cuenta_id, usuario_actual)
    db.delete(cuenta)
    db.commit()
    return cuenta