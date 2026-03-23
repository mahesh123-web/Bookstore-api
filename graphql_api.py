import strawberry
from strawberry.fastapi import GraphQLRouter
from typing import Optional

@strawberry.type
class Author:
    id : int
    name : str
    country : str
    
@strawberry.type
class Book: 
    id : int
    title : str
    price : float
    genre : Optional[str]
    author_id : int
    
authors_data = {
    1: {"id":1, "name":"Mahesh","country":"India"},
    2: {"id":2, "name": "Ram","country":"India"},
} 

books_data = {
    1 : {"id":1, "title":"Harry Potter", "price":25.13, "genre":"Fantasy", "author_id":1},
    2 : {"id":2, "title": "Clean Code","price":85.34, "genre":"Technnology", "author_id":2},
    3 : {"id":3, "title": "Harry Potter 2", "price":42.35, "genre":"Fantasy","author_id":1}
}

@strawberry.type
class Query:
    @strawberry.field
    def books(self)->list[Book]:
        return[Book(**b) for b in books_data.values()]
    
    @strawberry.field
    def book(self, book_id:int)-> Optional[Book]:
        b = books_data.get(book_id)
        return Book(**b) if b else None
    
    @strawberry.field
    def authors(self)->list[Author]:
        return[Author(**a) for a in authors_data.values()]
    
    @strawberry.field
    def books_by_genre(self,genre:str)-> list[Book]:
        return[
            Book(**b) for b in books_data.values()
            if b["genre"].lower() == genre.lower()
        ]
        
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(
        self,
        title : str,
        price: float,
        author_id : int,
        genre : Optional[str] = None
    )->Book:
        new_id = max(books_data.keys()) + 1
        new_book = {
            "id" : new_id,
            "title" : title,
            "price" : price,
            "genre" : genre,
            "author_id" : author_id
        }
        books_data[new_id] = new_book
        return Book(**new_book)
    
    @strawberry.mutation
    def delete_book(self, book_id: int)->bool:
        if book_id in books_data:
            del books_data[book_id]
            return True
        return False
    
    
schema = GraphQLRouter(strawberry.Schema(query = Query, mutation = Mutation))
        