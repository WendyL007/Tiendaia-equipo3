import os
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from azure.core.exceptions import ResourceNotFoundError

class AlmacenAzure:
    def __init__(self):
        self.contenedor = "tiendaia-imagenes" # En Azure los buckets se llaman containers
        self.cliente = BlobServiceClient.from_connection_string(os.environ["AZURE_CONNECTION_STRING"])
        
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
            account_name="devstoreaccount1",
            account_key="Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==",
            container_name=self.contenedor,
            blob_name=clave,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(seconds=segundos)
        )
        endpoint_publico = os.getenv("AZURE_PUBLIC_ENDPOINT")
        return f"{endpoint_publico}/{self.contenedor}/{clave}?{sas_token}"

    def eliminar(self, clave: str) -> None:
        blob_client = self.cliente.get_blob_client(container=self.contenedor, blob=clave)
        try:
            blob_client.delete_blob()
        except ResourceNotFoundError:
            pass # S3 no marca error si no existe, Azure sí, por eso lo ignoramos