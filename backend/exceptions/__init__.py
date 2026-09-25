class ErrorDominio(Exception):
    """Error base del dominio de Cero.

    Todos los errores propios del negocio heredan de esta clase.
    El handler registrado en handlers/ convierte su status_code
    y mensaje en la respuesta ApiResponse correspondiente.
    """

    status_code = 400

    def __init__(self, mensaje: str, headers: dict | None = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.headers = headers


class SolicitudInvalida(ErrorDominio):
    status_code = 400


class ErrorAutenticacion(ErrorDominio):
    status_code = 401


class SinPermisos(ErrorDominio):
    status_code = 403


class NoEncontrado(ErrorDominio):
    status_code = 404


class Conflicto(ErrorDominio):
    status_code = 409