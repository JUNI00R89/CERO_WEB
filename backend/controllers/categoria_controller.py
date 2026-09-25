from sqlalchemy.orm import Session

from controllers.base import (
    ResultadoConsulta,
    asignar_propietario,
    build_order_by,
    filtro_propiedad,
    not_found,
    verificar_propietario,
)
from models import Categoria, Usuario
from schemas.categoria import CategoriaCreate, CategoriaUpdate


def _validar_usuario(db: Session, usuario_id: int):
    if not db.query(Usuario).filter(Usuario.id == usuario_id).first():
        not_found(f"Usuario {usuario_id} no existe")


def crear_categoria(db: Session, payload: CategoriaCreate, usuario_actual) -> Categoria:
    usuario_id = asignar_propietario(usuario_actual, payload.usuario_id)
    _validar_usuario(db, usuario_id)
    categoria = Categoria(
        nombre=payload.nombre,
        tipo=payload.tipo,
        usuario_id=usuario_id,
    )
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def listar_categorias(
    db: Session,
    page: int,
    limit: int,
    tipo: str | None,
    usuario_id: int | None,
    sort_by: str,
    order: str,
    usuario_actual,
) -> ResultadoConsulta:
    query = db.query(Categoria)
    if tipo is not None:
        query = query.filter(Categoria.tipo == tipo)
    filtro = filtro_propiedad(usuario_actual, Categoria.usuario_id)
    if filtro is not None:
        query = query.filter(filtro)
    elif usuario_id is not None:
        query = query.filter(Categoria.usuario_id == usuario_id)
    query = query.order_by(build_order_by(Categoria, sort_by, order))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return ResultadoConsulta(items, total, page, limit)


def obtener_categoria(db: Session, categoria_id: int, usuario_actual) -> Categoria:
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        not_found(f"Categoria {categoria_id} no existe")
    verificar_propietario(usuario_actual, categoria)
    return categoria


def actualizar_categoria(
    db: Session, categoria_id: int, payload: CategoriaUpdate, usuario_actual
) -> Categoria:
    categoria = obtener_categoria(db, categoria_id, usuario_actual)
    datos = payload.model_dump(exclude_unset=True)
    if "usuario_id" in datos:
        datos["usuario_id"] = asignar_propietario(usuario_actual, datos["usuario_id"])
        _validar_usuario(db, datos["usuario_id"])
    for campo, valor in datos.items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


def eliminar_categoria(db: Session, categoria_id: int, usuario_actual) -> Categoria:
    categoria = obtener_categoria(db, categoria_id, usuario_actual)
    db.delete(categoria)
    db.commit()
    return categoria