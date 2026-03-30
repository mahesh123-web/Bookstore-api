import pika, json

def get_connection():
    credentials = pika.PlainCredentials("admin","admin")
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )
    
def handle_event(channel, method, properties, body):
    event = json.loads(body)
    etype = event["event"]
    data = event["data"]
    
    
    if etype == "book.created":
        print(f"[AI Pipeline] Generating embedings for: '{data['title']}'")
        print(f"[AI Pipeline] Adding to vector databsse...")
    elif etype == "book.updated":
        print(f"[AI Pipeline] Re-indexing updated book: '{data['title']}'")
    elif etype == "book.deleted":
        print(f"[AI Pipeline] Removing from vector database: '{data['title']}'")
        
    channel.basic_ack(delivery_tag = method.delivery_tag)
    
def start():
    connection = get_connection()
    channel = connection.channel()
    
    channel.exchange_declare(exchange="book_events", exchange_type="fanout")
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="book_events", queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=handle_event)
    
    
    print(f"[AI Pipeline] Listening for book events...")
    channel.start_consuming()
    
if __name__ == "__main__":
    start()