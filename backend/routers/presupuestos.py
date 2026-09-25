from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import presupuesto_controller
from database import get_db
from dependencies.auth import get_usuario_actual
from models import Usuario
from schemas.presupuesto import PresupuestoCreate, PresupuestoOut, PresupuestoUpdate
from schemas.response import ApiResponse, Page

router = APIRouter(prefix="/presupuestos", tags=["Presupuestos"])


@router.get("", response_model=ApiResponse[Page[PresupuestoOut]])
def listar_presupuestos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    usuario_id: int | None = Query(None, ge=1),
    categoria_id: int | None = Query(None, ge=1),
    sort_by: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    resultado = presupuesto_controller.listar_presupuestos(
        db, page=page, limit=limit, usuario_id=usuario_id, categoria_id=categoria_id,
        sort_by=sort_by, order=order, usuario_actual=usuario_actual,
    )
    data = Page(
        items=[PresupuestoOut.model_validate(item) for item in resultado.items],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
    return ApiResponse.ok(data=data, message="Presupuestos obtenidos correctamente")


@router.get("/{presupuesto_id}", response_model=ApiResponse[PresupuestoOut])
def obtener_presupuesto(
    presupuesto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    presupuesto = presupuesto_controller.obtener_presupuesto(db, presupuesto_id, usuario_actual)
    return ApiResponse.ok(
        data=PresupuestoOut.model_validate(presupuesto),
        message="Presupuesto obtenido correctamente",
    )


@router.post("", response_model=ApiResponse[PresupuestoOut], status_code=201)
def crear_presupuesto(
    payload: PresupuestoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    presupuesto = presupuesto_controller.crear_presupuesto(db, payload, usuario_actual)
    return ApiResponse.ok(
        data=PresupuestoOut.model_validate(presupuesto),
        message="Presupuesto creado correctamente",
    )


@router.put("/{presupuesto_id}", response_model=ApiResponse[PresupuestoOut])
def actualizar_presupuesto(
    presupuesto_id: int,
    payload: PresupuestoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    presupuesto = presupuesto_controller.actualizar_presupuesto(
        db, presupuesto_id, payload, usuario_actual
    )
    return ApiResponse.ok(
        data=PresupuestoOut.model_validate(presupuesto),
        message="Presupuesto actualizado correctamente",
    )


@router.delete("/{presupuesto_id}", response_model=ApiResponse)
def eliminar_presupuesto(
    presupuesto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    presupuesto_controller.eliminar_presupuesto(db, presupuesto_id, usuario_actual)
    return ApiResponse.ok(message="Presupuesto eliminado correctamente")
