import os
import jwt
import requests
from fastapi import FastAPI, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

RUTAS = {
    "clientes": os.getenv("CLIENTES_URL", "http://clientes:8000"),
    "productos": os.getenv("PRODUCTOS_URL", "http://productos:8000"),
    "ventas": os.getenv("VENTAS_URL", "http://ventas:8000"),
    "ia": os.getenv("IA_URL", "http://ia:8000"),
    "notificaciones": os.getenv("NOTIF_URL", "http://notificaciones:8000"),
    "imagenes": os.getenv("IMAGENES_URL", "http://imagenes:8000"),
    "auth": os.getenv("AUTH_URL", "http://auth:8000"),
}

JWT_SECRET = os.getenv("JWT_SECRET", "")
API_KEY = os.getenv("API_KEY", "")

PUBLICO = {("GET", "productos"), ("GET", "imagenes"), ("POST", "auth")}

PERMISOS = {
    ("GET", "clientes"): {"vendedor", "analista"},
    ("POST", "clientes"): {"vendedor"},
    ("PUT", "clientes"): {"vendedor"},
    ("GET", "ventas"): {"vendedor", "analista"},
    ("POST", "ventas"): {"vendedor"},
    ("GET", "ia"): {"analista"},
    ("POST", "ia"): {"analista"},
    ("GET", "notificaciones"): {"vendedor"},
}

app = FastAPI(title="TiendaIA - API Gateway")

ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_methods=["*"],
    allow_headers=["*"],
)

sesion = requests.Session()
TIEMPO_ESPERA = 60
TIEMPO_SALUD = 3


def autorizar(metodo: str, svc: str, ruta: str, auth: str | None):
    if (metodo, svc) in PUBLICO:
        return "anonimo", None
    if not JWT_SECRET:
        return "anonimo", None
    if not auth or not auth.lower().startswith("bearer "):
        return None, JSONResponse({"detail": "Token requerido"}, 401)
    try:
        datos = jwt.decode(auth[7:], JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None, JSONResponse({"detail": "Token inválido o expirado"}, 401)
    roles = set(datos.get("roles", []))
    permitidos = PERMISOS.get((metodo, svc), set())
    if svc == "ia" and ruta.startswith("train"):
        permitidos = set()
    if "admin" in roles or roles & permitidos:
        return datos["sub"], None
    return None, JSONResponse({"detail": "Permiso insuficiente"}, 403)


@app.get("/health")
async def salud():
    estado = {}
    for nombre, url in RUTAS.items():
        try:
            r = await run_in_threadpool(
                sesion.get, f"{url}/health", timeout=TIEMPO_SALUD
            )
            estado[nombre] = r.status_code == 200
        except requests.RequestException:
            estado[nombre] = False
    return {"gateway": "ok", "servicios": estado}


@app.api_route("/api/{svc}", methods=["GET", "POST"])
@app.api_route(
    "/api/{svc}/{ruta:path}", methods=["GET", "POST", "PUT", "DELETE"]
)
async def proxy(svc: str, req: Request, ruta: str = ""):
    if svc not in RUTAS:
        return Response(status_code=404)
    usuario, error = autorizar(
        req.method, svc, ruta, req.headers.get("authorization")
    )
    if error:
        return error
    cabeceras = {
        "content-type": req.headers.get("content-type", "application/json"),
        "x-api-key": API_KEY,
        "x-usuario": usuario,
    }
    if svc == "auth" and req.headers.get("authorization"):
        cabeceras["authorization"] = req.headers["authorization"]
    destino = f"{RUTAS[svc]}/{svc}" + (f"/{ruta}" if ruta else "")
    cuerpo = await req.body()
    r = await run_in_threadpool(
        sesion.request,
        req.method,
        destino,
        params=list(req.query_params.multi_items()),
        data=cuerpo,
        headers=cabeceras,
        timeout=TIEMPO_ESPERA,
        allow_redirects=False,
    )
    return Response(
        r.content, r.status_code, media_type=r.headers.get("content-type")
    )
#parte B:Reemplazar el código del gateway echa 