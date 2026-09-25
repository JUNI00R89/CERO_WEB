from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from controllers import categoria_controller
from database import get_db
from dependencies.auth import get_usuario_actual
from models import Usuario
from schemas.categoria import CategoriaCreate, CategoriaOut, CategoriaUpdate
from schemas.response import ApiResponse, Page

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("", response_model=ApiResponse[Page[CategoriaOut]])
def listar_categorias(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    tipo: Literal["ingreso", "gasto"] | None = Query(None),
    usuario_id: int | None = Query(None, ge=1),
    sort_by: str = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    resultado = categoria_controller.listar_categorias(
        db, page=page, limit=limit, tipo=tipo, usuario_id=usuario_id,
        sort_by=sort_by, order=order, usuario_actual=usuario_actual,
    )
    data = Page(
        items=[CategoriaOut.model_validate(item) for item in resultado.items],
        total=resultado.total,
        page=resultado.page,
        limit=resultado.limit,
    )
    return ApiResponse.ok(data=data, message="Categorías obtenidas correctamente")


@router.get("/{categoria_id}", response_model=ApiResponse[CategoriaOut])
def obtener_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    categoria = categoria_controller.obtener_categoria(db, categoria_id, usuario_actual)
    return ApiResponse.ok(
        data=CategoriaOut.model_validate(categoria), message="Categoría obtenida correctamente"
    )


@router.post("", response_model=ApiResponse[CategoriaOut], status_code=201)
def crear_categoria(
    payload: CategoriaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    categoria = categoria_controller.crear_categoria(db, payload, usuario_actual)
    return ApiResponse.ok(
        data=CategoriaOut.model_validate(categoria), message="Categoría creada correctamente"
    )


@router.put("/{categoria_id}", response_model=ApiResponse[CategoriaOut])
def actualizar_categoria(
    categoria_id: int,
    payload: CategoriaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    categoria = categoria_controller.actualizar_categoria(
        db, categoria_id, payload, usuario_actual
    )
    return ApiResponse.ok(
        data=CategoriaOut.model_validate(categoria), message="Categoría actualizada correctamente"
    )


@router.delete("/{categoria_id}", response_model=ApiResponse)
def eliminar_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual),
):
    categoria_controller.eliminar_categoria(db, categoria_id, usuario_actual)
    return ApiResponse.ok(message="Categoría eliminada correctamente")
