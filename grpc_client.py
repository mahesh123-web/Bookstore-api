from generated import bookstore_pb2
from generated import bookstore_pb2_grpc

import grpc
# import bookstore_pb2
# import bookstore_pb2_grpc

def run():
    with grpc.insecure_channel("localhost: 500051") as channel:
        stub = bookstore_pb2_grpc.BookstoreServiceStub(channel)
        
        
        print("==== Get Book 1 ======")
        response = stub.GetBook(bookstore_pb2.BookRequest(book_id = 1))
        print(f"Title: {response.title}, Price: ${response.price}")
        
        
        print("\n=== List All Books ===")
        book_list = stub.ListBooks(bookstore_pb2.Empty())
        for book in book_list.books:
            print(f" [{book.id}] {book.title} - ${book.price}")
            
            
        print("\n=== Search Books ===")
        response = stub.SearchBooks(
            bookstore_pb2.SearchRequest(genre = "Technology", max_price = 90.00)
        )
        for book in response.books:
            print(f"[{book.id}] {book.title} - ${book.price:.2f}")
            
            
        print("\n === Get Book 999 (not found) ===")
        try:
            response = stub.GetBook(bookstore_pb2.BookRequest(book_id=999))
        except grpc.RpcError as e:
            print(f"Error : {e.code()} - {e.details()}")
            
if __name__ == "__main__":
    run()