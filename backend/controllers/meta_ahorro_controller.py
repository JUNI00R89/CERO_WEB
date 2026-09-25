from sqlalchemy.orm import Session

from controllers.base import (
    ResultadoConsulta,
    asignar_propietario,
    build_order_by,
    filtro_propiedad,
    not_found,
    verificar_propietario,
)
from models import MetaAhorro, Usuario
from schemas.meta_ahorro import MetaAhorroCreate, MetaAhorroUpdate


def _validar_usuario(db: Session, usuario_id: int):
    if not db.query(Usuario).filter(Usuario.id == usuario_id).first():
        not_found(f"Usuario {usuario_id} no existe")


def crear_meta_ahorro(db: Session, payload: MetaAhorroCreate, usuario_actual) -> MetaAhorro:
    usuario_id = asignar_propietario(usuario_actual, payload.usuario_id)
    _validar_usuario(db, usuario_id)
    meta = MetaAhorro(
        nombre=payload.nombre,
        monto_objetivo=payload.monto_objetivo,
        monto_actual=payload.monto_actual,
        fecha_objetivo=payload.fecha_objetivo,
        usuario_id=usuario_id,
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta


def listar_metas_ahorro(
    db: Session,
    page: int,
    limit: int,
    usuario_id: int | None,
    sort_by: str,
    order: str,
    usuario_actual,
) -> ResultadoConsulta:
    query = db.query(MetaAhorro)
    filtro = filtro_propiedad(usuario_actual, MetaAhorro.usuario_id)
    if filtro is not None:
        query = query.filter(filtro)
    elif usuario_id is not None:
        query = query.filter(MetaAhorro.usuario_id == usuario_id)
    query = query.order_by(build_order_by(MetaAhorro, sort_by, order))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return ResultadoConsulta(items, total, page, limit)


def obtener_meta_ahorro(db: Session, meta_id: int, usuario_actual) -> MetaAhorro:
    meta = db.query(MetaAhorro).filter(MetaAhorro.id == meta_id).first()
    if not meta:
        not_found(f"Meta de ahorro {meta_id} no existe")
    verificar_propietario(usuario_actual, meta)
    return meta


def actualizar_meta_ahorro(
    db: Session, meta_id: int, payload: MetaAhorroUpdate, usuario_actual
) -> MetaAhorro:
    meta = obtener_meta_ahorro(db, meta_id, usuario_actual)
    datos = payload.model_dump(exclude_unset=True)
    if "usuario_id" in datos:
        datos["usuario_id"] = asignar_propietario(usuario_actual, datos["usuario_id"])
        _validar_usuario(db, datos["usuario_id"])
    for campo, valor in datos.items():
        setattr(meta, campo, valor)
    db.commit()
    db.refresh(meta)
    return meta


def eliminar_meta_ahorro(db: Session, meta_id: int, usuario_actual) -> MetaAhorro:
    meta = obtener_meta_ahorro(db, meta_id, usuario_actual)
    db.delete(meta)
    db.commit()
    return meta
