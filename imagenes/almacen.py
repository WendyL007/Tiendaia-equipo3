"""Adaptador de almacenamiento de objetos (API S3: SeaweedFS, Amazon S3, B2...).
Lo usa el microservicio Imágenes (Laboratorio 4) para hablar con SeaweedFS
mediante boto3, el SDK oficial de AWS para Python. Como casi todos los
proveedores imitan la API S3, cambiar de nube es cambiar variables de entorno.
Para usar otro proveedor (Google Drive, Dropbox, Azure Blob) basta con escribir
otra clase con los mismos tres métodos: subir, url y eliminar.
"""
import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

class AlmacenS3:
    """Envuelve un bucket S3 con tres operaciones: subir, url y eliminar."""
    
    def __init__(self):
        """Crea los clientes S3 a partir de variables de entorno y revisa el bucket."""
        cred = dict(
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION", "us-east-1"),
            config=Config(signature_version="s3v4")
        )

        self.bucket = os.environ["S3_BUCKET"]
        
        self.s3 = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT"), **cred)
        
        self.firmas = boto3.client(
            "s3", 
            endpoint_url=os.getenv("S3_PUBLIC_ENDPOINT", os.getenv("S3_ENDPOINT")), 
            **cred
        )
        
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.s3.create_bucket(Bucket=self.bucket)

    def subir(self, clave: str, datos: bytes, tipo: str, metadatos: dict) -> None:
        """Guarda los bytes como objeto 'clave'; ContentType se usa al descargar."""
        self.s3.put_object(
            Bucket=self.bucket, 
            Key=clave, 
            Body=datos,
            ContentType=tipo, 
            Metadata=metadatos
        )

    def url(self, clave: str, segundos: int = 3600) -> str:
        """URL prefirmada: acceso temporal sin hacer público el bucket.
        Se calcula localmente (no hay petición a S3): la URL lleva la firma y la
        expiración en sus parámetros; quien la tenga puede hacer GET hasta que
        venza. Devuelve la URL como texto.
        """
        return self.firmas.generate_presigned_url(
            "get_object", 
            Params={"Bucket": self.bucket, "Key": clave},
            ExpiresIn=segundos
        )

    def eliminar(self, clave: str) -> None:
        """Borra el objeto. S3 no marca error si la clave ya no existía."""
        self.s3.delete_object(Bucket=self.bucket, Key=clave)