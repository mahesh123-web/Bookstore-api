import pika
import json

def get_connection():
    credentials = pika.PlainCredentials("admin","admin")
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )

def publish_event(event_type: str, data: dict):
    connection = get_connection()
    channel = connection.channel()
    
    channel.exchange_declare(
        exchange="book_events",
        exchange_type="fanout"
    )
    
    event = {"event": event_type, "data": data}
    
    channel.basic_publish(
        exchange="book_events",
        routing_key="",
        body=json.dumps(event)
    )
    print(f"[→] Event published: {event_type} - {data ['title']}")
    connection.close()
    
if __name__ == "__main__":
    publish_event("book_created", {"id":10, "title":"New Book","price":29.99})
    publish_event("book_created", {"id":3, "title":"Old Book"})
    publish_event("book_created", {"id":5, "title":"Updated Book","price":14.99})
    