from routers.auth import router as auth_router
from routers.categorias import router as categorias_router
from routers.cuentas import router as cuentas_router
from routers.metas_ahorro import router as metas_ahorro_router
from routers.movimientos import router as movimientos_router
from routers.presupuestos import router as presupuestos_router
from routers.usuarios import router as usuarios_router

all_routers = [
    auth_router,
    usuarios_router,
    cuentas_router,
    categorias_router,
    movimientos_router,
    presupuestos_router,
    metas_ahorro_router,
]