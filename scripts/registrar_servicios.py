import sys
import requests

GW, CONTRASENA = sys.argv[1], sys.argv[2]
SERVICIOS = ["gateway", "ventas", "ia", "imagenes"]
TIEMPO_ESPERA = 10
sesion = requests.Session()

token = sesion.post(
    f"{GW}/api/auth/login",
    timeout=TIEMPO_ESPERA,
    json={"usuario": "admin", "contrasena": CONTRASENA},
)
token.raise_for_status()

cab = {"Authorization": f"Bearer {token.json()['access_token']}"}
with open(".env.claves", "w") as f:
    for s in SERVICIOS:
        r = sesion.post(
            f"{GW}/api/auth/servicios",
            json={"servicio": s},
            headers=cab,
            timeout=TIEMPO_ESPERA,
        )
        r.raise_for_status()
        f.write(f"API_KEY_{s.upper()}={r.json()['api_key']}\n")
        print("registrado:", s)
print("Claves guardadas en .env.claves (agregue el archivo a .gitignore)")