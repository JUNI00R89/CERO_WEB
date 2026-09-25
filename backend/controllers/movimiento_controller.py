from sqlalchemy.orm import Session

from controllers.base import (
    ResultadoConsulta,
    asignar_propietario,
    build_order_by,
    filtro_propiedad,
    forbidden,
    not_found,
    verificar_propietario,
)
from models import Categoria, Cuenta, Movimiento, Usuario
from schemas.movimiento import MovimientoCreate, MovimientoUpdate


def _validar_relaciones(
    db: Session, usuario_id: int, cuenta_id: int, categoria_id: int, usuario_actual
):
    if not db.query(Usuario).filter(Usuario.id == usuario_id).first():
        not_found(f"Usuario {usuario_id} no existe")

    cuenta = db.query(Cuenta).filter(Cuenta.id == cuenta_id).first()
    if not cuenta:
        not_found(f"Cuenta {cuenta_id} no existe")
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        not_found(f"Categoria {categoria_id} no existe")

    # La cuenta y la categoría deben pertenecer al propietario del movimiento.
    verificar_propietario(usuario_actual, cuenta)
    verificar_propietario(usuario_actual, categoria)
    if cuenta.usuario_id != usuario_id or categoria.usuario_id != usuario_id:
        forbidden()


def crear_movimiento(db: Session, payload: MovimientoCreate, usuario_actual) -> Movimiento:
    usuario_id = asignar_propietario(usuario_actual, payload.usuario_id)
    _validar_relaciones(db, usuario_id, payload.cuenta_id, payload.categoria_id, usuario_actual)
    movimiento = Movimiento(
        tipo=payload.tipo,
        monto=payload.monto,
        descripcion=payload.descripcion,
        fecha=payload.fecha,
        usuario_id=usuario_id,
        cuenta_id=payload.cuenta_id,
        categoria_id=payload.categoria_id,
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def listar_movimientos(
    db: Session,
    page: int,
    limit: int,
    tipo: str | None,
    usuario_id: int | None,
    cuenta_id: int | None,
    categoria_id: int | None,
    sort_by: str,
    order: str,
    usuario_actual,
) -> ResultadoConsulta:
    query = db.query(Movimiento)
    if tipo is not None:
        query = query.filter(Movimiento.tipo == tipo)
    if cuenta_id is not None:
        query = query.filter(Movimiento.cuenta_id == cuenta_id)
    if categoria_id is not None:
        query = query.filter(Movimiento.categoria_id == categoria_id)
    filtro = filtro_propiedad(usuario_actual, Movimiento.usuario_id)
    if filtro is not None:
        query = query.filter(filtro)
    elif usuario_id is not None:
        query = query.filter(Movimiento.usuario_id == usuario_id)
    query = query.order_by(build_order_by(Movimiento, sort_by, order))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return ResultadoConsulta(items, total, page, limit)


def obtener_movimiento(db: Session, movimiento_id: int, usuario_actual) -> Movimiento:
    movimiento = db.query(Movimiento).filter(Movimiento.id == movimiento_id).first()
    if not movimiento:
        not_found(f"Movimiento {movimiento_id} no existe")
    verificar_propietario(usuario_actual, movimiento)
    return movimiento


def actualizar_movimiento(
    db: Session, movimiento_id: int, payload: MovimientoUpdate, usuario_actual
) -> Movimiento:
    movimiento = obtener_movimiento(db, movimiento_id, usuario_actual)
    datos = payload.model_dump(exclude_unset=True)
    if "usuario_id" in datos:
        datos["usuario_id"] = asignar_propietario(usuario_actual, datos["usuario_id"])
    usuario_id = datos.get("usuario_id", movimiento.usuario_id)
    cuenta_id = datos.get("cuenta_id", movimiento.cuenta_id)
    categoria_id = datos.get("categoria_id", movimiento.categoria_id)
    _validar_relaciones(db, usuario_id, cuenta_id, categoria_id, usuario_actual)
    for campo, valor in datos.items():
        setattr(movimiento, campo, valor)
    db.commit()
    db.refresh(movimiento)
    return movimiento


def eliminar_movimiento(db: Session, movimiento_id: int, usuario_actual) -> Movimiento:
    movimiento = obtener_movimiento(db, movimiento_id, usuario_actual)
    db.delete(movimiento)
    db.commit()
    return movimiento
