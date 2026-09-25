from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import meta_ahorro_controller
from database import get_db
from dependencies.auth import get_usuario_actual
from models import Usuario
from schemas.meta_ahorro import MetaAhorroCreate, MetaAhorroOut, MetaAhorroUpdate
from schemas.response import ApiResponse, Page

router = APIRouter(prefix="/metas-ahorro", tags=["Metas de Ahorro"])


@router.get("", response_model=ApiResponse[Page[MetaAhorroOut]])
def listar_metas_ahorro(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    usuario_id: int | None = Query(None, ge=1),
    sort_by: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    resultado = meta_ahorro_controller.listar_metas_ahorro(
        db, page=page, limit=limit, usuario_id=usuario_id, sort_by=sort_by,
        order=order, usuario_actual=usuario_actual,
    )
    data = Page(
        items=[MetaAhorroOut.model_validate(item) for item in resultado.items],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
    return ApiResponse.ok(data=data, message="Metas de ahorro obtenidas correctamente")


@router.get("/{meta_id}", response_model=ApiResponse[MetaAhorroOut])
def obtener_meta_ahorro(
    meta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    meta = meta_ahorro_controller.obtener_meta_ahorro(db, meta_id, usuario_actual)
    return ApiResponse.ok(
        data=MetaAhorroOut.model_validate(meta), message="Meta de ahorro obtenida correctamente"
    )


@router.post("", response_model=ApiResponse[MetaAhorroOut], status_code=201)
def crear_meta_ahorro(
    payload: MetaAhorroCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    meta = meta_ahorro_controller.crear_meta_ahorro(db, payload, usuario_actual)
    return ApiResponse.ok(
        data=MetaAhorroOut.model_validate(meta), message="Meta de ahorro creada correctamente"
    )


@router.put("/{meta_id}", response_model=ApiResponse[MetaAhorroOut])
def actualizar_meta_ahorro(
    meta_id: int,
    payload: MetaAhorroUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    meta = meta_ahorro_controller.actualizar_meta_ahorro(db, meta_id, payload, usuario_actual)
    return ApiResponse.ok(
        data=MetaAhorroOut.model_validate(meta), message="Meta de ahorro actualizada correctamente"
    )


@router.delete("/{meta_id}", response_model=ApiResponse)
def eliminar_meta_ahorro(
    meta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    meta_ahorro_controller.eliminar_meta_ahorro(db, meta_id, usuario_actual)
    return ApiResponse.ok(message="Meta de ahorro eliminada correctamente")
