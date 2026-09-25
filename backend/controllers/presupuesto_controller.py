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
from models import Categoria, Presupuesto, Usuario
from schemas.presupuesto import PresupuestoCreate, PresupuestoUpdate


def _validar_relaciones(db: Session, usuario_id: int, categoria_id: int, usuario_actual):
    if not db.query(Usuario).filter(Usuario.id == usuario_id).first():
        not_found(f"Usuario {usuario_id} no existe")
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        not_found(f"Categoria {categoria_id} no existe")
    # La categoría referenciada debe pertenecer al propietario del presupuesto.
    verificar_propietario(usuario_actual, categoria)
    if categoria.usuario_id != usuario_id:
        forbidden()


def crear_presupuesto(db: Session, payload: PresupuestoCreate, usuario_actual) -> Presupuesto:
    usuario_id = asignar_propietario(usuario_actual, payload.usuario_id)
    _validar_relaciones(db, usuario_id, payload.categoria_id, usuario_actual)
    presupuesto = Presupuesto(
        monto_limite=payload.monto_limite,
        fecha_inicio=payload.fecha_inicio,
        fecha_fin=payload.fecha_fin,
        usuario_id=usuario_id,
        categoria_id=payload.categoria_id,
    )
    db.add(presupuesto)
    db.commit()
    db.refresh(presupuesto)
    return presupuesto


def listar_presupuestos(
    db: Session,
    page: int,
    limit: int,
    usuario_id: int | None,
    categoria_id: int | None,
    sort_by: str,
    order: str,
    usuario_actual,
) -> ResultadoConsulta:
    query = db.query(Presupuesto)
    if categoria_id is not None:
        query = query.filter(Presupuesto.categoria_id == categoria_id)
    filtro = filtro_propiedad(usuario_actual, Presupuesto.usuario_id)
    if filtro is not None:
        query = query.filter(filtro)
    elif usuario_id is not None:
        query = query.filter(Presupuesto.usuario_id == usuario_id)
    query = query.order_by(build_order_by(Presupuesto, sort_by, order))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return ResultadoConsulta(items, total, page, limit)


def obtener_presupuesto(db: Session, presupuesto_id: int, usuario_actual) -> Presupuesto:
    presupuesto = db.query(Presupuesto).filter(Presupuesto.id == presupuesto_id).first()
    if not presupuesto:
        not_found(f"Presupuesto {presupuesto_id} no existe")
    verificar_propietario(usuario_actual, presupuesto)
    return presupuesto


def actualizar_presupuesto(
    db: Session, presupuesto_id: int, payload: PresupuestoUpdate, usuario_actual
) -> Presupuesto:
    presupuesto = obtener_presupuesto(db, presupuesto_id, usuario_actual)
    datos = payload.model_dump(exclude_unset=True)
    if "usuario_id" in datos:
        datos["usuario_id"] = asignar_propietario(usuario_actual, datos["usuario_id"])
    usuario_id = datos.get("usuario_id", presupuesto.usuario_id)
    categoria_id = datos.get("categoria_id", presupuesto.categoria_id)
    _validar_relaciones(db, usuario_id, categoria_id, usuario_actual)
    for campo, valor in datos.items():
        setattr(presupuesto, campo, valor)
    db.commit()
    db.refresh(presupuesto)
    return presupuesto


def eliminar_presupuesto(db: Session, presupuesto_id: int, usuario_actual) -> Presupuesto:
    presupuesto = obtener_presupuesto(db, presupuesto_id, usuario_actual)
    db.delete(presupuesto)
    db.commit()
    return presupuesto
