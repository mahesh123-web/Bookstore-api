import pika
import json
import time

def get_connection():
    credentials = pika.PlainCredentials("admin","admin")
    return pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", credentials=credentials)
    )
    
def publish_book_job(book_data: dict):
    connection = get_connection()
    channel = connection.channel()
    
    channel.queue_declare(queue="book_processing", durable=True)
    
    channel.basic_publish(
        exchange="",
        routing_key="book_processing",
        body=json.dumps(book_data),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    
    print(f"[->]Published Job: {book_data['title']}")
    connection.close()
    
if __name__ =="__main__":
    
    books = [
        {"id":1, "title":"Clean Code", "action": "generate_summary"},
        {"id":2, "title": "Harry Potter", "action": "generate_summary"},
        {"id":3, "title": "The Pragmatic Prog", "action": "extract_keywords"},
        {"id":4, "title": "Design Patterns", "action": "generate_summary"},
        {"id":5, "title": "Refactoring", "action": "extract_keywords"} 
    ]
    
    for book in books:
        publish_book_job(book)
        time.sleep(0.5)
    print("[✓]All jobs published") 