from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import usuario_controller
from database import get_db
from dependencies.auth import get_usuario_actual, get_usuario_actual_opcional
from dependencies.permissions import require_admin
from models import Usuario
from schemas.response import ApiResponse, Page
from schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/me", response_model=ApiResponse[UsuarioOut])
def obtener_usuario_actual(usuario: Usuario = Depends(get_usuario_actual)):
    return ApiResponse.ok(
        data=UsuarioOut.model_validate(usuario), message="Usuario autenticado obtenido correctamente"
    )


@router.get("", response_model=ApiResponse[Page[UsuarioOut]])
def listar_usuarios(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    rol: Literal["usuario", "admin"] | None = Query(None),
    activo: bool | None = Query(None),
    sort_by: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin),
):
    """Listado completo de usuarios: solo administradores."""
    resultado = usuario_controller.listar_usuarios(
        db, page=page, limit=limit, rol=rol, activo=activo, sort_by=sort_by, order=order
    )
    data = Page(
        items=[UsuarioOut.model_validate(item) for item in resultado.items],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
    return ApiResponse.ok(data=data, message="Usuarios obtenidos correctamente")


@router.get("/{usuario_id}", response_model=ApiResponse[UsuarioOut])
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    usuario = usuario_controller.obtener_usuario(db, usuario_id, usuario_actual)
    return ApiResponse.ok(
        data=UsuarioOut.model_validate(usuario), message="Usuario obtenido correctamente"
    )


@router.post("", response_model=ApiResponse[UsuarioOut], status_code=201)
def crear_usuario(
    payload: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario | None = Depends(get_usuario_actual_opcional),
):
    """Registro público. Solo un admin autenticado puede asignar rol o estado."""
    usuario = usuario_controller.crear_usuario(db, payload, usuario_actual)
    return ApiResponse.ok(
        data=UsuarioOut.model_validate(usuario), message="Usuario creado correctamente"
    )


@router.put("/{usuario_id}", response_model=ApiResponse[UsuarioOut])
def actualizar_usuario(
    usuario_id: int,
    payload: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    usuario = usuario_controller.actualizar_usuario(db, usuario_id, payload, usuario_actual)
    return ApiResponse.ok(
        data=UsuarioOut.model_validate(usuario), message="Usuario actualizado correctamente"
    )


@router.delete("/{usuario_id}", response_model=ApiResponse)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin),
):
    """Acción administrativa: solo administradores."""
    usuario_controller.eliminar_usuario(db, usuario_id, admin)
    return ApiResponse.ok(message="Usuario eliminado correctamente")
