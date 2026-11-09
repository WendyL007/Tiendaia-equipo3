import os
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.core.exceptions import ResourceNotFoundError

class AlmacenAzure:
    def __init__(self):
        self.contenedor = "tiendaia-imagenes" # En Azure los buckets se llaman containers
        connection_string = os.environ["AZURE_CONNECTION_STRING"]
        configuracion = dict(
            parte.split("=", 1)
            for parte in connection_string.split(";")
            if "=" in parte
        )
        self.account_name = configuracion.get("AccountName")
        self.account_key = configuracion.get("AccountKey")
        if not self.account_name or not self.account_key:
            raise ValueError(
                "AZURE_CONNECTION_STRING debe incluir AccountName y AccountKey "
                "para generar URLs SAS."
            )
        self.endpoint_publico = os.getenv(
            "AZURE_PUBLIC_ENDPOINT", "http://localhost:10000/devstoreaccount1"
        ).rstrip("/")
        self.cliente = BlobServiceClient.from_connection_string(connection_string)
        
        # Crear contenedor si no existe
        try:
            self.cliente.get_container_client(self.contenedor).get_container_properties()
        except ResourceNotFoundError:
            self.cliente.create_container(self.contenedor)

    def subir(self, clave: str, datos: bytes, tipo: str, metadatos: dict) -> None:
        blob_client = self.cliente.get_blob_client(container=self.contenedor, blob=clave)
        blob_client.upload_blob(
            datos, 
            overwrite=True, 
            content_settings=ContentSettings(content_type=tipo),
            metadata=metadatos
        )

    def url(self, clave: str, segundos: int = 3600) -> str:
        sas_token = generate_blob_sas(
            account_name=self.account_name,
            account_key=self.account_key,
            container_name=self.contenedor,
            blob_name=clave,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=segundos)
        )
        return f"{self.endpoint_publico}/{self.contenedor}/{clave}?{sas_token}"

    def eliminar(self, clave: str) -> None:
        blob_client = self.cliente.get_blob_client(container=self.contenedor, blob=clave)
        try:
            blob_client.delete_blob()
        except ResourceNotFoundError:
            pass # S3 no marca error si no existe, Azure sí, por eso lo ignoramos