import os
import time
import requests
from fastapi import Header, HTTPException, Request

AUTH_URL = os.getenv("AUTH_URL", "http://auth:8000")
TIEMPO_ESPERA = 3
_cache: dict[str, tuple[str, float]] = {}
TTL = 60
sesion = requests.Session()


def requiere_servicio(request: Request, x_api_key: str | None = Header(default=None)):
    if request.url.path == "/health":
        return None
    if not x_api_key:
        raise HTTPException(401, "API Key requerida")
    servicio, expira = _cache.get(x_api_key, (None, 0))
    if time.time() > expira:
        r = sesion.get(f"{AUTH_URL}/auth/validar-clave",
            headers={"x-api-key": x_api_key}, timeout=TIEMPO_ESPERA)
        if r.status_code != 200:
            raise HTTPException(403, "API Key inválida")
        servicio = r.json()["servicio"]
        _cache[x_api_key] = (servicio, time.time() + TTL)
    return servicio