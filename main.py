from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from typing import Optional

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from auth import(
    Token, create_access_token, verify_password,fake_user_db,get_current_user,require_admin
)
 

app = FastAPI(title="BookStore API",version="1.0")

# --------DATA Models--------------------------

class Book(BaseModel):
    title:str
    author_id:int
    price:float
    genre:Optional[str] = None
    
class Author(BaseModel):
    name:str
    country:str
    
class Review(BaseModel):
    reviewer: str
    rating: int
    comment: str

# --------IN - MEMORY Data store-----------------------------

authors_db = {}
books_db = {}
reviews_db = {}

author_counter = 1
book_counter = 1
review_counter = 1 


#-------------------Login endpoints-----------------------

@app.post("/auth/login", response_model = Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_user_db.get(form_data.username)
    
    #verifying the user exists And password matches the hash
    
    if not user or not verify_password(form_data.password,user["hashed_password"]):
        raise HTTPException(
            status_code = 401,
            detail = "Incorrect username or password"
        )
    # create and return the JWT token
    token = create_access_token(data = {"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

#-------Aauthor Endpoints--------------------------------------

@app.get("/authors")
def list_authors():
    return list(authors_db.values())
@app.post("/authors", status_code = 201)
def create_author(author:Author, current_user: dict = Depends(get_current_user)):
    global author_counter
    new_author = {"id":author_counter, **author.dict()}
    authors_db[author_counter] = new_author
    author_counter+=1
    return new_author

@app.get("/authors/{author_id}")
def get_author(author_id:int):
    if author_id not in authors_db:
        raise HTTPException(status_code=404,detail="Author Not Found")
    return authors_db[author_id]

@app.put("/authors/{author_id}")
def update_author(author_id: int , author:Author, current_user: dict = Depends(get_current_user)):
    if author_id not in authors_db:
        raise HTTPException(status_code = 404, detail="Author not found")
    authors_db[author_id] = {"id":author_id, **author.dict()}
    return authors_db[author_id]

@app.delete("/authors/{author_id}" ,status_code=204)
def delete_author(author_id:int, current_user: dict = Depends(require_admin)):
    if author_id not in authors_db:
        raise HTTPException(status_code = 404, detail="Author Not Found")
    del authors_db[author_id]
    

#---------Book Endpoints--------------------

@app.get("/books")
def list_books():
    return list(books_db.values())

@app.post("/books",status_code=201)
def create_book(book:Book, current_user: dict = Depends(get_current_user)):
    global book_counter
    if  book.author_id not in authors_db:
        raise HTTPException(status_code = 400, detail="Author does not exist")
    new_book = {"id":book_counter,**book.dict()}
    books_db[book_counter] = new_book
    book_counter+=1
    return new_book

@app.get("/books/{book_id}")
def get_book(book_id:int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return books_db[book_id]


@app.put("/books/{book_id}")
def update_book(book_id:int, book:Book, current_user: dict = Depends(get_current_user)):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    books_db[book_id] = {"id":book_id, **book.dict()}
    return books_db[book_id]

@app.delete("/books/{book_id}",status_code=204)
def delete_book(book_id:int , current_user: dict = Depends(require_admin)):
    if book_id not in books_db:
        raise HTTPException(status_code=404,detail="Book not found")
    del books_db[book_id]
    
#----Review Endpoints------------------------

@app.get("/books/{book_id}/reviews")
def list_reviews(book_id:int):
    if book_id not in books_db:
        raise HTTPException(status_code=404,detail="Book not found")
    return [v for (bid,_),v in reviews_db.items() if bid == book_id]

@app.post("/books/{book_id}/reviews",status_code=201)
def create_review(book_id:int, review:Review , current_user: dict = Depends(get_current_user)):
    global review_counter
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    if not 1<=review.rating<=5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    new_review = {"id":review_counter, "book_id":book_id, **review.dict()}
    reviews_db[(book_id,review_counter)] = new_review
    review_counter+=1
    return new_review

@app.get("/books/{book_id}/reviews/{review_id}")
def get_review(book_id:int, review_id: int):
    review = reviews_db.get((book_id,review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@app.delete("/books/{book_id}/reviews/{review_id}" ,status_code=204)
def delete_review(book_id:int, review_id:int, current_user: dict = Depends(require_admin)):
    if(book_id,review_id) not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    del reviews_db[(book_id,review_id)]
    
    
#--------Books By Author------------------------

def books_by_author(author_id:int):
    if author_id not in authors_db:
        raise HTTPException(status_code=404, detail="Author not found")
    return [b for b in books_db.values() if b["author_id"]==author_id]

#---------------Search point-----------------------

@app.get("/books/search")
def search_books(title:Optional[str]=None, max_price: Optional[float]=None):
    results=[]
    
    for book in books_db.values():
        if title and title.lower() not in book["title"].lower():
            continue
        if max_price is not None and book["price"]> max_price:
            continue
        
        results.append(book)
        
    return results
    
    
