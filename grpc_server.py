from generated import bookstore_pb2
from generated import bookstore_pb2_grpc
import grpc
from concurrent import futures
# import bookstore_pb2
# import bookstore_pb2_grpc

books_data = {
    1 : {"id": 1, "title": "Harry Potter", "price":51.25, "genre":"Fantasy"},
    2 : {"id": 2, "title": "Clean Code", "price":85.18, "genre": "Technology"},
}


class BookstoreServicer(bookstore_pb2_grpc.BookstoreServiceServicer):
    def GetBook(self, reequest, context):
        book = books_data.get(reequest.book_id)
        if not book:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Book Not found")
            return bookstore_pb2.BookResponse()
        return bookstore_pb2.BookResponse(**book)
    
    def ListBooks(self,request, context):
        books = [bookstore_pb2.BookResponse(**b) for b in books_data.values()]
        return bookstore_pb2.BookListResponse(books=books)
    
    def SearchBooks(self, request, coontext):
        genre = request.genre.lower()
        max_price = request.max_price
        
        filtered_books = []
        
        for book in books_data.values():
            if genre and book["genre"].lower() != genre:
                continue
            if max_price and book["price"] > max_price:
                continue
            filtered_books.append(bookstore_pb2.BookResponse(**book))
        return bookstore_pb2.BookListResponse(books = filtered_books)
    
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bookstore_pb2_grpc.add_BookstoreServiceServicer_to_server(
        BookstoreServicer(), server
    )
    server.add_insecure_port("[::]:500051")
    print("gRPC server running on port 50051")
    server.start()
    server.wait_for_termination()
        
if __name__ == "__main__":
    serve()
        
        