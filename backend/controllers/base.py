from exceptions import Conflicto, NoEncontrado, SinPermisos, SolicitudInvalida
from roles import ROL_ADMIN


def not_found(mensaje: str):
    raise NoEncontrado(mensaje)


def bad_request(mensaje: str):
    raise SolicitudInvalida(mensaje)


def conflict(mensaje: str):
    raise Conflicto(mensaje)


def forbidden(mensaje="No tienes permisos para realizar esta acción."):
    raise SinPermisos(mensaje)


def es_admin(usuario_actual) -> bool:
    return getattr(usuario_actual, "rol", None) == ROL_ADMIN


# Alias interno conservado por compatibilidad.
_es_admin = es_admin


def verificar_propietario(usuario_actual, recurso):
    """El recurso solo es accesible por su propietario (o por un admin)."""
    if not _es_admin(usuario_actual) and recurso.usuario_id != usuario_actual.id:
        forbidden()


def filtro_propiedad(usuario_actual, columna):
    if _es_admin(usuario_actual):
        return None
    return columna == usuario_actual.id


def asignar_propietario(usuario_actual, usuario_id_payload):
    if _es_admin(usuario_actual):
        return usuario_id_payload
    return usuario_actual.id


def build_order_by(model, sort_by: str, order: str):
    column = getattr(model, sort_by, None)
    if column is None:
        bad_request(f"Campo de ordenamiento inválido: {sort_by}")
    return column.asc() if order.lower() == "asc" else column.desc()


class ResultadoConsulta:
    def __init__(self, items, total, page, limit):
        self.items = items
        self.total = total
        self.page = page
        self.limit = limit

    def to_page(self):
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "limit": self.limit,
        }