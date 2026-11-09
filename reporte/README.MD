## Reporte del laboratorio

## Parte F: almacenamiento en la nube y adaptador Azure

### Comparación de rendimiento

Los valores se generan desde `resultados_almacenamiento.csv`. Para regenerar la
tabla y las gráficas después de agregar mediciones:

```bash
python scripts/generar_reporte_almacenamiento.py
```

La tabla de comparación es [tabla_comparativa.csv](../tabla_comparativa.csv).
Las gráficas usan medias y desviaciones estándar de cada prueba:

- [Velocidad de subida](./grafica_subida.svg)
- [Velocidad de descarga](./grafica_bajada.svg)
- [Latencia de archivos pequeños](./grafica_latencia_pequenos.svg)
- [Rendimiento de archivos pequeños](./grafica_rendimiento_pequenos.svg)

El CSV incluye `seaweedfs-laptop`, `supabase-codespace` y `b2-codespace`,
con cero errores en las filas actuales. Para completar la comparación entre
laptop y Codespace faltan las ejecuciones locales de Supabase y B2; no se
atribuyen a la laptop mediciones hechas desde el Codespace.

En cada equipo, ejecutar una vez por proveedor usando los archivos de entorno
correspondientes:

```bash
set -a
source bench-supabase.env
set +a
DESTINO=supabase-codespace python scripts/bench_almacenamiento.py

set -a
source bench-b2.env
set +a
DESTINO=b2-codespace python scripts/bench_almacenamiento.py
```

En la laptop, repetir usando `DESTINO=supabase-laptop` y `DESTINO=b2-laptop`.
Así se mantiene un archivo de credenciales por proveedor, pero cada ejecución
queda etiquetada según dónde se midió. Los archivos `bench-*.env` están
excluidos por `.gitignore`; no incluir credenciales en el reporte.

### Adaptador Azure Blob Storage

`imagenes/almacen_azure.py` implementa la misma interfaz `subir`, `url` y
`eliminar` que `imagenes/almacen.py`. El servicio usa el SDK
`azure-storage-blob`; Azurite emula Blob Storage localmente. La conexión
interna del contenedor usa `http://azurite:10000/devstoreaccount1`, mientras
que el navegador recibe URL SAS firmada con lectura y vencimiento de una hora,
dirigida a `http://localhost:10000/devstoreaccount1`. `ALMACEN` selecciona
`s3` (predeterminado) o `azure`; cualquier otro valor impide el arranque con un
mensaje explícito.

| Aspecto | S3 / SeaweedFS | Azure Blob / Azurite |
|---|---|---|
| Adaptador | `imagenes/almacen.py`, API S3 con boto3 | `imagenes/almacen_azure.py`, Blob Storage SDK |
| Dependencia | `boto3` | `azure-storage-blob` |
| Configuración local | Servicio SeaweedFS y credenciales S3 del `.env` | Servicio Azurite y cadena de conexión de desarrollo |
| Acceso temporal | URL prefirmada `get_object` | SAS con permiso de lectura y expiración |
| Producción | Cambiar endpoint, bucket y credenciales por los del proveedor S3 | Cambiar cadena de conexión y endpoint público por los de una cuenta Azure |
| Cambios en el servicio de imágenes | Ninguno: conserva la interfaz del adaptador | Ninguno en los endpoints: conserva la interfaz del adaptador |

### Pruebas para capturas

Seleccionar y reconstruir Azure:

```bash
ALMACEN=azure docker compose up -d --build azurite imagenes gateway
```

Subir, consultar la URL y borrar una imagen:

```bash
curl -i -X POST http://localhost:8080/api/imagenes \
  -F producto_id=2 -F "archivo=@cafe.jpg;type=image/jpeg"
curl -s http://localhost:8080/api/imagenes/2 | python -m json.tool
curl -i -X DELETE http://localhost:8080/api/imagenes/2
```

La URL devuelta debe abrirse desde el navegador y contener `?` seguido de una
SAS. Para volver a S3:

```bash
ALMACEN=s3 docker compose up -d --build imagenes gateway
```

Las pruebas negativas de tipo no admitido (415) y archivo mayor de 5 MB (413)
se ejecutan contra el mismo endpoint POST. El producto usado para las pruebas
debe existir en el servicio Productos.