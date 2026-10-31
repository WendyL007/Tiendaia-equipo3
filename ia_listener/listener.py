import os
import time
import pika
import redis
import requests

# Configuración desde variables de entorno
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
IA_URL = os.getenv("IA_URL", "http://ia:8000")

# Cliente de Redis
r = redis.Redis(host=REDIS_HOST, decode_responses=True)

def callback(ch, method, properties, body):
    try:
        # Requisito 2: Incrementa en Redis y evalúa múltiplo de 50
        n = r.incr("ia_listener:ventas")
        if n % 50 == 0:
            res = requests.post(f"{IA_URL}/ia/train", timeout=120)
            print(f"[IA-Listener] Reentrenamiento disparado (venta #{n}). Código HTTP: {res.status_code}", flush=True)
        
        # Requisito 3: Confirmación exitosa al final
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[IA-Listener] Error procesando evento: {e}", flush=True)
        # Requisito 3: Descarte de mensaje venenoso con nack (sin reencolar)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def consumir():
    # Requisito 4: Ciclo de reconexión continua
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()

            # Requisito 1: Declaración de exchange, cola propia y binding
            channel.exchange_declare(exchange='tienda.eventos', exchange_type='topic', durable=True)
            channel.queue_declare(queue='ia_listener', durable=True)
            channel.queue_bind(exchange='tienda.eventos', queue='ia_listener', routing_key='venta.*')

            channel.basic_consume(queue='ia_listener', on_message_callback=callback)
            print("[IA-Listener] Escuchando eventos...", flush=True)
            channel.start_consuming()
        except Exception as e:
            print(f"[IA-Listener] Error de conexión, reintentando en 3s... ({e})", flush=True)
            time.sleep(3)

if __name__ == "__main__":
    consumir()