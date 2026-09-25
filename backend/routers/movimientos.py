from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import movimiento_controller
from database import get_db
from dependencies.auth import get_usuario_actual
from models import Usuario
from schemas.movimiento import MovimientoCreate, MovimientoOut, MovimientoUpdate
from schemas.response import ApiResponse, Page

router = APIRouter(prefix="/movimientos", tags=["Movimientos"])


@router.get("", response_model=ApiResponse[Page[MovimientoOut]])
def listar_movimientos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    tipo: Literal["ingreso", "gasto"] | None = Query(None),
    usuario_id: int | None = Query(None, ge=1),
    cuenta_id: int | None = Query(None, ge=1),
    categoria_id: int | None = Query(None, ge=1),
    sort_by: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    resultado = movimiento_controller.listar_movimientos(
        db,
        page=page,
        limit=limit,
        tipo=tipo,
        usuario_id=usuario_id,
        cuenta_id=cuenta_id,
        categoria_id=categoria_id,
        sort_by=sort_by,
        order=order,
        usuario_actual=usuario_actual,
    )
    data = Page(
        items=[MovimientoOut.model_validate(item) for item in resultado.items],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
    return ApiResponse.ok(data=data, message="Movimientos obtenidos correctamente")


@router.get("/{movimiento_id}", response_model=ApiResponse[MovimientoOut])
def obtener_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    movimiento = movimiento_controller.obtener_movimiento(db, movimiento_id, usuario_actual)
    return ApiResponse.ok(
        data=MovimientoOut.model_validate(movimiento), message="Movimiento obtenido correctamente"
    )


@router.post("", response_model=ApiResponse[MovimientoOut], status_code=201)
def crear_movimiento(
    payload: MovimientoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    movimiento = movimiento_controller.crear_movimiento(db, payload, usuario_actual)
    return ApiResponse.ok(
        data=MovimientoOut.model_validate(movimiento), message="Movimiento creado correctamente"
    )


@router.put("/{movimiento_id}", response_model=ApiResponse[MovimientoOut])
def actualizar_movimiento(
    movimiento_id: int,
    payload: MovimientoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    movimiento = movimiento_controller.actualizar_movimiento(
        db, movimiento_id, payload, usuario_actual
    )
    return ApiResponse.ok(
        data=MovimientoOut.model_validate(movimiento),
        message="Movimiento actualizado correctamente",
    )


@router.delete("/{movimiento_id}", response_model=ApiResponse)
def eliminar_movimiento(
    movimiento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    movimiento_controller.eliminar_movimiento(db, movimiento_id, usuario_actual)
    return ApiResponse.ok(message="Movimiento eliminado correctamente")
