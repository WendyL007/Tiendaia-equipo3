TiendaIA - EQUIPO 3 
## Despliegue en Render (Lab 5, Parte B)
- Cliente web (Static Site): https://tiendaia-equipo3.onrender.com
- IA-Service (Web Service): https://tiendaia-equipo3-1mc7.onrender.com

Configuración escrita a mano (se reemplaza por render.yaml en la Parte C):
- Static Site: Branch main, Root Directory frontend, Build Command vacío, Publish Directory .
- IA-Service: Python 3, Branch main, Root Directory ia_service, Build `pip install -r requirements.txt`, Start `uvicorn app:app --host 0.0.0.0 --port $PORT`, plan Free
- Variables: VENTAS_URL (URL pública del gateway + /api), MODELO_PATH=/tmp/modelo.joblib, PYTHON_VERSION=3.12.7
