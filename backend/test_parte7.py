import os, sys
os.environ["DATABASE_URL"] = "sqlite:///./test_p7.db"
os.environ["SECRET_KEY"] = "clave-de-prueba-larga-1234567890"
sys.path.insert(0, ".")
for f in ("test_p7.db",):
    if os.path.exists(f): os.remove(f)

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, Base, engine
import models
from services.auth import hash_password, decodificar_token

Base.metadata.create_all(bind=engine)
db = SessionLocal()
db.add(models.Usuario(nombre="Ada", apellido="Admin", correo="admin@cero.com",
                      password_hash=hash_password("admin12345"), rol="admin", activo=True))
db.commit(); db.close()

c = TestClient(app)
ok = lambda cond, msg: print(("PASS  " if cond else "FALLA ") + msg) or (None if cond else fails.append(msg))
fails = []

def login(correo, pw):
    r = c.post("/login", json={"correo": correo, "password": pw})
    return r.json()["data"]["access_token"]

def H(t): return {"Authorization": f"Bearer {t}"}

# registro público de dos usuarios, intentando escalar privilegios
r = c.post("/usuarios", json={"nombre":"Ana","apellido":"Uno","correo":"a@cero.com","password":"pass12345","rol":"admin"})
ok(r.status_code==201 and r.json()["data"]["rol"]=="usuario", "Registro publico no permite auto-asignarse rol admin")
uid_a = r.json()["data"]["id"]
r = c.post("/usuarios", json={"nombre":"Beto","apellido":"Dos","correo":"b@cero.com","password":"pass12345"})
uid_b = r.json()["data"]["id"]

ta, tb = login("a@cero.com","pass12345"), login("b@cero.com","pass12345")
tadm = login("admin@cero.com","admin12345")

ok(decodificar_token(ta)["rol"]=="usuario" and decodificar_token(tadm)["rol"]=="admin", "El JWT contiene el rol")
ok(c.get("/usuarios/me", headers=H(ta)).json()["data"]["rol"]=="usuario", "El usuario autenticado obtiene su rol (/usuarios/me)")
ok("password_hash" not in c.get("/usuarios/me", headers=H(ta)).json()["data"], "La sesion no expone password_hash")

# rutas administrativas
ok(c.get("/usuarios", headers=H(ta)).status_code==403, "Usuario estandar: 403 al listar usuarios")
ok(c.get("/usuarios", headers=H(tadm)).status_code==200, "Admin: puede listar usuarios")
r = c.delete(f"/usuarios/{uid_b}", headers=H(ta))
ok(r.status_code==403 and "permisos" in r.json()["detail"]["message"], "Usuario estandar: 403 en DELETE /usuarios/{id} con mensaje claro")
ok(c.get("/usuarios", headers=H(ta)).status_code==403 and c.get("/usuarios").status_code==401, "Sin token = 401, con token sin permisos = 403")

# propiedad de datos: cuentas y categorias
r = c.post("/cuentas", headers=H(ta), json={"nombre":"Caja A","tipo":"efectivo","saldo":100,"usuario_id":uid_b})
ok(r.status_code==201 and r.json()["data"]["usuario_id"]==uid_a, "usuario_id del cliente se ignora: la cuenta queda en el propietario real")
cuenta_a = r.json()["data"]["id"]
cat_a = c.post("/categorias", headers=H(ta), json={"nombre":"Sueldo","tipo":"ingreso","usuario_id":uid_a}).json()["data"]["id"]
cuenta_b = c.post("/cuentas", headers=H(tb), json={"nombre":"Caja B","tipo":"efectivo","usuario_id":uid_b}).json()["data"]["id"]
cat_b = c.post("/categorias", headers=H(tb), json={"nombre":"Bono","tipo":"ingreso","usuario_id":uid_b}).json()["data"]["id"]

ok(c.get(f"/cuentas/{cuenta_a}", headers=H(tb)).status_code==403, "Usuario B: 403 al leer la cuenta de A")
ok(c.put(f"/cuentas/{cuenta_a}", headers=H(tb), json={"nombre":"Hackeada"}).status_code==403, "Usuario B: 403 al modificar la cuenta de A")
ok(c.delete(f"/cuentas/{cuenta_a}", headers=H(tb)).status_code==403, "Usuario B: 403 al eliminar la cuenta de A")
ok(c.get(f"/categorias/{cat_a}", headers=H(tb)).status_code==403, "Usuario B: 403 al leer la categoria de A")
lst = c.get("/cuentas", headers=H(ta)).json()["data"]
ok(lst["total"]==1 and lst["items"][0]["id"]==cuenta_a, "El listado solo devuelve las cuentas propias")
_f = c.get(f"/cuentas?usuario_id={uid_b}", headers=H(ta)).json()["data"]
ok(all(i["usuario_id"]==uid_a for i in _f["items"]), "Manipular ?usuario_id no expone datos de otro usuario")
ok(c.get("/cuentas", headers=H(tadm)).json()["data"]["total"]==2, "Admin ve todas las cuentas")

# movimientos y presupuestos
mov = c.post("/movimientos", headers=H(ta), json={"tipo":"ingreso","monto":50,"fecha":"2026-01-01T00:00:00","usuario_id":uid_a,"cuenta_id":cuenta_a,"categoria_id":cat_a})
ok(mov.status_code==201, "Usuario A crea su movimiento")
mov_a = mov.json()["data"]["id"]
r = c.post("/movimientos", headers=H(ta), json={"tipo":"ingreso","monto":50,"fecha":"2026-01-01T00:00:00","usuario_id":uid_a,"cuenta_id":cuenta_b,"categoria_id":cat_a})
ok(r.status_code==403, "403 al crear movimiento sobre una cuenta ajena")
ok(c.get(f"/movimientos/{mov_a}", headers=H(tb)).status_code==403, "Usuario B: 403 al leer el movimiento de A")
ok(c.get("/movimientos", headers=H(tb)).json()["data"]["total"]==0, "El listado de movimientos solo muestra los propios")

pre = c.post("/presupuestos", headers=H(ta), json={"monto_limite":500,"fecha_inicio":"2026-01-01","fecha_fin":"2026-01-31","usuario_id":uid_a,"categoria_id":cat_a})
ok(pre.status_code==201, "Usuario A crea su presupuesto")
pre_a = pre.json()["data"]["id"]
ok(c.post("/presupuestos", headers=H(ta), json={"monto_limite":500,"fecha_inicio":"2026-01-01","fecha_fin":"2026-01-31","usuario_id":uid_a,"categoria_id":cat_b}).status_code==403, "403 al crear presupuesto con categoria ajena")
ok(c.put(f"/presupuestos/{pre_a}", headers=H(tb), json={"monto_limite":1}).status_code==403, "Usuario B: 403 al modificar el presupuesto de A")

meta = c.post("/metas-ahorro", headers=H(ta), json={"nombre":"Viaje","monto_objetivo":1000,"fecha_objetivo":"2026-12-01","usuario_id":uid_b})
ok(meta.status_code==201 and meta.json()["data"]["usuario_id"]==uid_a, "La meta de ahorro se asigna al propietario autenticado")
meta_a = meta.json()["data"]["id"]
ok(c.delete(f"/metas-ahorro/{meta_a}", headers=H(tb)).status_code==403, "Usuario B: 403 al eliminar la meta de A")
ok(c.get(f"/metas-ahorro/{meta_a}", headers=H(tadm)).status_code==200, "Admin puede consultar la meta de A")

# usuarios: self vs otros
ok(c.get(f"/usuarios/{uid_b}", headers=H(ta)).status_code==403, "Usuario A: 403 al consultar el perfil de B")
ok(c.get(f"/usuarios/{uid_a}", headers=H(ta)).status_code==200, "Usuario A puede consultar su propio perfil")
ok(c.put(f"/usuarios/{uid_a}", headers=H(ta), json={"rol":"admin"}).status_code==403, "403 al intentar auto-promoverse a admin")
ok(c.put(f"/usuarios/{uid_a}", headers=H(ta), json={"nombre":"Anita"}).status_code==200, "Usuario A puede editar sus propios datos")
ok(c.put(f"/usuarios/{uid_b}", headers=H(tadm), json={"rol":"admin"}).status_code==200, "Admin puede cambiar el rol de un usuario")
uid_c = c.post("/usuarios", json={"nombre":"Caro","apellido":"Tres","correo":"c@cero.com","password":"pass12345"}).json()["data"]["id"]
ok(c.delete(f"/usuarios/{uid_c}", headers=H(ta)).status_code==403, "Usuario estandar no puede eliminar a otro usuario")
ok(c.delete(f"/usuarios/{uid_c}", headers=H(tadm)).status_code==200, "Admin puede eliminar un usuario")

# partes 1-6 siguen vivas
ok(c.get("/").status_code==200 and c.post("/login", json={"correo":"a@cero.com","password":"mala"}).status_code==401, "Partes 1-6: raiz y login siguen funcionando")

print()
print(f"{'TODO OK' if not fails else 'FALLOS: ' + str(fails)}")
