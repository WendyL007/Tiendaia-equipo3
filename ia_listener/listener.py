import os
import time
import pika
import redis
import requests

# ConfiguraciÃ³n desde variables de entorno
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
PARAMS = (pika.URLParameters(RABBITMQ_HOST) if "://" in RABBITMQ_HOST else pika.ConnectionParameters(RABBITMQ_HOST))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
IA_URL = os.getenv("IA_URL", "http://ia:8000")

# Cliente de Redis
r = redis.Redis(host=REDIS_HOST, decode_responses=True)

def callback(ch, method, properties, body):
    try:
        # Requisito 2: Incrementa en Redis y evalÃºa mÃºltiplo de 50
        n = r.incr("ia_listener:ventas")
        if n % 50 == 0:
            res = requests.post(f"{IA_URL}/ia/train", timeout=120)
            print(f"[IA-Listener] Reentrenamiento disparado (venta #{n}). CÃ³digo HTTP: {res.status_code}", flush=True)
        
        # Requisito 3: ConfirmaciÃ³n exitosa al final
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[IA-Listener] Error procesando evento: {e}", flush=True)
        # Requisito 3: Descarte de mensaje venenoso con nack (sin reencolar)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def consumir():
    # Requisito 4: Ciclo de reconexiÃ³n continua
    while True:
        try:
            connection = pika.BlockingConnection(PARAMS)
            channel = connection.channel()

            # Requisito 1: DeclaraciÃ³n de exchange, cola propia y binding
            channel.exchange_declare(exchange='tienda.eventos', exchange_type='topic', durable=True)
            channel.queue_declare(queue='ia_listener', durable=True)
            channel.queue_bind(exchange='tienda.eventos', queue='ia_listener', routing_key='venta.*')

            channel.basic_consume(queue='ia_listener', on_message_callback=callback)
            print("[IA-Listener] Escuchando eventos...", flush=True)
            channel.start_consuming()
        except Exception as e:
            print(f"[IA-Listener] Error de conexiÃ³n, reintentando en 3s... ({e})", flush=True)
            time.sleep(3)

if __name__ == "__main__":
    consumir()
