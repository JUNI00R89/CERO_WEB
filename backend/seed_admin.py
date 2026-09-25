"""
Script para crear un usuario administrador inicial.

Uso:
    cd backend
    python seed_admin.py

Requiere que las dependencias del backend ya estén instaladas
(pip install -r requirements.txt) y el archivo .env configurado.
"""

from database import Base, SessionLocal, engine
from models import Usuario
from services.auth import hash_password

CORREO = "admin@cero.com"
PASSWORD = "Admin1234"
NOMBRE = "Admin"
APELLIDO = "Cero"
ROL = "admin"


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existente = db.query(Usuario).filter(Usuario.correo == CORREO).first()
        if existente:
            print(f"Ya existe un usuario con el correo {CORREO}. No se creó ninguno nuevo.")
            return

        usuario = Usuario(
            nombre=NOMBRE,
            apellido=APELLIDO,
            correo=CORREO,
            password_hash=hash_password(PASSWORD),
            rol=ROL,
            activo=True,
        )
        db.add(usuario)
        db.commit()
        print("Usuario creado correctamente:")
        print(f"  Correo:     {CORREO}")
        print(f"  Contraseña: {PASSWORD}")
        print(f"  Rol:        {ROL}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
