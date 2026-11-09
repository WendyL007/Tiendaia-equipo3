"""Microservicio Imágenes de TiendaIA (Laboratorio 4).
Guarda las fotos de los productos en un almacenamiento de objetos con API S3
(SeaweedFS en el laboratorio) y entrega URL prefirmadas para descargarlas.
Consulta y actualiza al microservicio Productos por HTTP con requests; la
lógica de S3 vive en almacen.py.
"""
import hashlib # huella SHA-256 para verificar la integridad del archivo
import os
import uuid # nombres únicos: dos fotos nunca se sobrescriben entre sí
import requests # cliente HTTP para llamar al microservicio Productos
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from almacen import AlmacenS3 # adaptador S3 (subir, url, eliminar)

# ---------------------------------------------------------------- Configuración
PRODUCTOS_URL = os.getenv("PRODUCTOS_URL", "http://productos:8000")
# Tipos MIME aceptados -> extensión del archivo que se guarda en el bucket
TIPOS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
MAX_BYTES = 5 * 1024 * 1024 # 5 MB: límite para no llenar el almacenamiento

# Selector de adaptador de almacenamiento
if os.getenv("ALMACEN", "s3") == "azure":
    from almacen_azure import AlmacenAzure
    almacen = AlmacenAzure()
else:
    almacen = AlmacenS3()

TIEMPO_ESPERA = 5 # segundos máximos de espera a Productos
sesion = requests.Session() # reutiliza conexiones TCP con Productos
app = FastAPI(title="TiendaIA - Imágenes")

# ---------------------------------------------------------------- Subir imagen
@app.post("/imagenes", status_code=201)
async def subir(producto_id: int = Form(gt=0), archivo: UploadFile = File(...)):
    """Recibe una imagen, la almacena en S3 o Azure y la asocia al producto."""

    # 1. Validar el tipo de archivo.
    if archivo.content_type not in TIPOS:
        raise HTTPException(415, "Solo se aceptan JPEG, PNG o WebP")

    # 2. Consultar el producto. Si no existe, responder 404.
    p = producto(producto_id)

    # 3. Leer los bytes del archivo.
    datos = await archivo.read()

    # 4. Validar el tamaño máximo permitido.
    if len(datos) > MAX_BYTES:
        raise HTTPException(413, "La imagen excede 5 MB")

    # 5. Generar una clave única para almacenar la imagen.
    clave = f"productos/{producto_id}/{uuid.uuid4().hex}.{TIPOS[archivo.content_type]}"

    # 6. Calcular la huella SHA-256.
    sha = hashlib.sha256(datos).hexdigest()

    # 7. Subir la imagen al almacenamiento.
    almacen.subir(
        clave,
        datos,
        archivo.content_type,
        {"sha256": sha}
    )

    # 8. Si existe una imagen anterior, eliminarla.
    if p.get("imagen_key"):
        almacen.eliminar(p["imagen_key"])

    # 9. Asociar la nueva imagen al producto.
    asociar(producto_id, clave)

    return {
        "producto_id": producto_id,
        "clave": clave,
        "bytes": len(datos),
        "sha256": sha
    }
    
# ---------------------------------------------------------------- Obtener imagen
@app.get("/imagenes/{producto_id}")
def obtener(producto_id: int):
    """Devuelve una URL prefirmada para descargar la imagen."""

    # 1. Consultar el producto.
    p = producto(producto_id)

    # 2. Obtener la clave de la imagen.
    clave = p.get("imagen_key")

    # 3. Verificar que el producto tenga una imagen.
    if not clave:
        raise HTTPException(404, "El producto no tiene imagen")

    # 4. Generar una URL prefirmada válida durante una hora.
    url = almacen.url(clave)

    return {
        "producto_id": producto_id,
        "url": url,
        "expira_en_s": 3600
    }
    
# ---------------------------------------------------------------- Eliminar imagen
@app.delete("/imagenes/{producto_id}", status_code=204)
def eliminar(producto_id: int):
    """Elimina la imagen del almacenamiento y su asociación."""

    # 1. Consultar el producto.
    p = producto(producto_id)

    # 2. Obtener la clave de la imagen.
    clave = p.get("imagen_key")

    # 3. Verificar que tenga una imagen asociada.
    if not clave:
        raise HTTPException(404, "El producto no tiene imagen")

    # 4. Eliminar el objeto del almacenamiento.
    almacen.eliminar(clave)

    # 5. Quitar la asociación de la imagen en Productos.
    asociar(producto_id, None)
    
# ---------------------------------------------------------------- Funciones auxiliares

def producto(pid: int) -> dict:
    """Consulta un producto mediante el microservicio Productos."""
    r = sesion.get(f"{PRODUCTOS_URL}/productos/{pid}", timeout=TIEMPO_ESPERA)
    if r.status_code == 404:
        raise HTTPException(404, "Producto no encontrado")
    r.raise_for_status()
    return r.json()

def asociar(pid: int, clave: str | None):
    """Actualiza la clave de imagen asociada a un producto."""
    r = sesion.put(
        f"{PRODUCTOS_URL}/productos/{pid}/imagen",
        json={"imagen_key": clave},
        timeout=TIEMPO_ESPERA
    )
    if r.status_code == 404:
        raise HTTPException(404, "Producto no encontrado")
    r.raise_for_status()
    return r.json()

# ---------------------------------------------------------------- Health Check

@app.get("/health")
def health():
    """Comprueba que Imagen-Service esté disponible."""
    # S3 usa 'bucket', Azure usa 'contenedor'
    nombre_almacen = getattr(almacen, "bucket", getattr(almacen, "contenedor", "desconocido"))
    return {
        "servicio": "imagenes",
        "status": "ok",
        "bucket": nombre_almacen
    }
