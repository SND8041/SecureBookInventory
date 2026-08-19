from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List

app = FastAPI()

# OAuth2 security setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Simple fake user database
users_db = {
    "admin": {
        "username": "admin",
        "password": "admin123"
    }
}


class Book(BaseModel):
    title: str
    author: str
    year: int
    language: str
    eng_translation: bool
    city: str
    country: str
    isbn: str


books_db: List[Book] = []

default_book = Book(
    title="The Da Vinci Code",
    author="Dan Brown",
    year=2003,
    language="English",
    eng_translation=True,
    city="New York",
    country="USA",
    isbn="978-0-7432-7356-5"
)

books_db.append(default_book)

default_book_2 = Book(
    title="The Niche of Lights (مشکات الأنوار)",
    author="Abu Hamid al-Ghazali",
    year=1095,
    language="Arabic",
    eng_translation=True,
    city="Cairo",
    country="Egypt",
    isbn="1409973840"
)

books_db.append(default_book_2)


# Login endpoint
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)

    if user is None:
        return {"error": "Invalid username"}

    if form_data.password != user["password"]:
        return {"error": "Invalid password"}

    return {
        "access_token": user["username"],
        "token_type": "bearer"
    }


# Simple function to check token
def check_login(token: str = Depends(oauth2_scheme)):
    if token in users_db:
        return token
    return {"error": "Unauthorized access"}


# Create or add a new book - protected
@app.post("/tool/", response_model=Book)
def create_book(book: Book, token: str = Depends(check_login)):
    books_db.append(book)
    return book


# Read all books - protected

@app.get("/readall/", response_model=List[Book])
def read_books(token: str = Depends(check_login)):
    return books_db

#protected endpoint
# Search endpoint should appear before /books/{isbn}
@app.get("/books/search/", response_model=Book)
def search_book(title: str, year: int, token: str = Depends(check_login)):
    for book in books_db:
        if book.title == title and book.year == year:
            return book
    return {"error": "Book not found"}


# Read one book - public
@app.get("/books/{isbn}", response_model=Book)
def read_book(isbn: str):
    for book in books_db:
        if book.isbn == isbn:
            return book
    return {"error": "Book not found"}


# Update an existing book - protected
@app.put("/books/{isbn}", response_model=Book)
def update_book(isbn: str, updated_book: Book, token: str = Depends(check_login)):
    for index, book in enumerate(books_db):
        if book.isbn == isbn:
            books_db[index] = updated_book
            return updated_book
    return {"error": "Book not found"}


# Delete a book - protected
@app.delete("/books/{isbn}", response_model=Book)
def delete_book(isbn: str, token: str = Depends(check_login)):
    for index, book in enumerate(books_db):
        if book.isbn == isbn:
            deleted_book = books_db.pop(index)
            return deleted_book
    return {"error": "Book not found"}