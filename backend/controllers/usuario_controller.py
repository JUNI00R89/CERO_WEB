from sqlalchemy.orm import Session

from controllers.base import (
    ResultadoConsulta,
    es_admin,
    build_order_by,
    conflict,
    forbidden,
    not_found,
)
from models import Usuario
from roles import ROL_POR_DEFECTO
from schemas.usuario import UsuarioCreate, UsuarioUpdate
from services.auth import hash_password

CAMPOS_SOLO_ADMIN = {"rol", "activo"}


def _verificar_acceso_a_usuario(usuario_actual, usuario_id: int):
    """Un usuario estándar solo puede operar sobre su propia cuenta."""
    if not es_admin(usuario_actual) and usuario_actual.id != usuario_id:
        forbidden()


def crear_usuario(db: Session, payload: UsuarioCreate, usuario_actual=None) -> Usuario:
    if db.query(Usuario).filter(Usuario.correo == payload.correo).first():
        conflict(f"El correo {payload.correo} ya está registrado")
    # Solo un administrador puede asignar rol o estado al crear un usuario.
    if es_admin(usuario_actual):
        rol = payload.rol
        activo = payload.activo
    else:
        rol = ROL_POR_DEFECTO
        activo = True
    usuario = Usuario(
        nombre=payload.nombre,
        apellido=payload.apellido,
        correo=payload.correo,
        password_hash=hash_password(payload.password),
        rol=rol,
        activo=activo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def listar_usuarios(
    db: Session,
    page: int,
    limit: int,
    rol: str | None,
    activo: bool | None,
    sort_by: str,
    order: str,
) -> ResultadoConsulta:
    query = db.query(Usuario)
    if rol is not None:
        query = query.filter(Usuario.rol == rol)
    if activo is not None:
        query = query.filter(Usuario.activo == activo)
    query = query.order_by(build_order_by(Usuario, sort_by, order))
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return ResultadoConsulta(items, total, page, limit)


def obtener_usuario(db: Session, usuario_id: int, usuario_actual=None) -> Usuario:
    if usuario_actual is not None:
        _verificar_acceso_a_usuario(usuario_actual, usuario_id)
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        not_found(f"Usuario {usuario_id} no existe")
    return usuario


def actualizar_usuario(
    db: Session, usuario_id: int, payload: UsuarioUpdate, usuario_actual=None
) -> Usuario:
    usuario = obtener_usuario(db, usuario_id, usuario_actual)
    datos = payload.model_dump(exclude_unset=True)
    if not es_admin(usuario_actual) and CAMPOS_SOLO_ADMIN & datos.keys():
        forbidden()
    if "correo" in datos and datos["correo"] != usuario.correo:
        existe = (
            db.query(Usuario)
            .filter(Usuario.correo == datos["correo"], Usuario.id != usuario_id)
            .first()
        )
        if existe:
            conflict(f"El correo {datos['correo']} ya está registrado")
    if "password" in datos:
        datos["password_hash"] = hash_password(datos.pop("password"))
    for campo, valor in datos.items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar_usuario(db: Session, usuario_id: int, usuario_actual=None) -> Usuario:
    usuario = obtener_usuario(db, usuario_id, usuario_actual)
    if usuario_actual is not None and usuario_actual.id == usuario_id:
        forbidden("Un administrador no puede eliminar su propia cuenta.")
    db.delete(usuario)
    db.commit()
    return usuario
