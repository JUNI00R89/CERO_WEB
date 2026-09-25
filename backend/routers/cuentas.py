from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import cuenta_controller
from database import get_db
from dependencies.auth import get_usuario_actual
from models import Usuario
from schemas.cuenta import CuentaCreate, CuentaOut, CuentaUpdate
from schemas.response import ApiResponse, Page

router = APIRouter(prefix="/cuentas", tags=["Cuentas"])


@router.get("", response_model=ApiResponse[Page[CuentaOut]])
def listar_cuentas(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    tipo: Literal["efectivo", "tarjeta", "ahorro", "inversion", "credito"] | None = Query(None),
    usuario_id: int | None = Query(None, ge=1),
    sort_by: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    resultado = cuenta_controller.listar_cuentas(
        db, page=page, limit=limit, tipo=tipo, usuario_id=usuario_id,
        sort_by=sort_by, order=order, usuario_actual=usuario_actual,
    )
    data = Page(
        items=[CuentaOut.model_validate(item) for item in resultado.items],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
    return ApiResponse.ok(data=data, message="Cuentas obtenidas correctamente")


@router.get("/{cuenta_id}", response_model=ApiResponse[CuentaOut])
def obtener_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    cuenta = cuenta_controller.obtener_cuenta(db, cuenta_id, usuario_actual)
    return ApiResponse.ok(
        data=CuentaOut.model_validate(cuenta), message="Cuenta obtenida correctamente"
    )


@router.post("", response_model=ApiResponse[CuentaOut], status_code=201)
def crear_cuenta(
    payload: CuentaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    cuenta = cuenta_controller.crear_cuenta(db, payload, usuario_actual)
    return ApiResponse.ok(
        data=CuentaOut.model_validate(cuenta), message="Cuenta creada correctamente"
    )


@router.put("/{cuenta_id}", response_model=ApiResponse[CuentaOut])
def actualizar_cuenta(
    cuenta_id: int,
    payload: CuentaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    cuenta = cuenta_controller.actualizar_cuenta(db, cuenta_id, payload, usuario_actual)
    return ApiResponse.ok(
        data=CuentaOut.model_validate(cuenta), message="Cuenta actualizada correctamente"
    )


@router.delete("/{cuenta_id}", response_model=ApiResponse)
def eliminar_cuenta(
    cuenta_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    cuenta_controller.eliminar_cuenta(db, cuenta_id, usuario_actual)
    return ApiResponse.ok(message="Cuenta eliminada correctamente")
