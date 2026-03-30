import pika
import json
import time
import sys

def get_connection():
    credentials = pika.PlainCredentials("admin","admin")
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )
    
def process_book(book_data : dict) -> str:
    action = book_data.get("action")
    title = book_data.get("title")
    
    if action == "generate_summary":
        time.sleep(2)
        return f"Summary generated for{title}"
    elif action == "extract_keywords":
        time.sleep(1)
        return f"keywords generated for {title}"
    else:
        raise ValueError(f"Unknown action: {action}")
    
def on_message(channel, method, properties,body):
    book_data = json.loads(body)
    worker_id = sys.argv[1] if len(sys.argv)> 1 else "1"
    print(f"[Worker {worker_id}] Recieved: {book_data['title']}")
    
    try:
        result = process_book(book_data)
        print(f"[Worker {worker_id}] Done : {result}")
        
        channel.basic_ack(delivery_tag = method.delivery_tag)
        
    except Exception as e:
        print(f"[Worker {worker_id}] Failed {e}")
        
        channel.basic_nack(
            delivery_tag = method.delivery_tag,
            requeue = False
        )
def start_worker():
    connection = get_connection()
    channel = connection.channel()
    
    channel.queue_declare(queue="book_processing", durable=True)
    
    channel.basic_qos(prefetch_count=1)
    
    channel.basic_consume(
        queue="book_processing",
        on_message_callback=on_message
    )
    
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "1"
    print(f"[Worker {worker_id}]  Waiting for jobs....")
    channel.start_consuming()
    
if __name__=="__main__":
    start_worker()