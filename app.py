from fastapi import FastAPI, HTTPException, Query, Body, Depends
from pydantic import BaseModel
from database.database import Database
from models.models import Note, UserSchema, UserLoginSchema
from authentication.auth_handler import AuthHandler
from authentication.auth_bearer import JWTBearer

from dotenv import load_dotenv
from logger import get_logger
import os 

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
TABLE_NAME = os.getenv("TABLE_NAME")

app = FastAPI()
logger = get_logger(__name__)


database = Database(DATABASE_URL)
database.connect()

users = []

def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

## User registraction 
@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user)
    return AuthHandler.signJWT(user.email)

## User login
@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return AuthHandler.signJWT(user.email)
    return {
        "error": "User doesn't exist!"
    }

# check if user exists
def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False


# create note
@app.post("/api/notes/", dependencies=[Depends(JWTBearer())], tags=['notes'])
def create_note(note: Note):
    # Insert new note into the database
    database.insert_data(TABLE_NAME, {"title": note.title, "body": note.body})
    return {"message": "note created successfully"}

# fetch notes
@app.get("/api/notes/")
def read_notes():
    # Fetch notes from the database with pagination
    notes = database.fetch_all(TABLE_NAME)
    return notes

# read a note
@app.get("/api/notes/{note_id}")
def read_note(note_id: int):
    # Fetch note by ID from the database
    note = database.fetch_by_id(TABLE_NAME, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="note not found")
    return note

# update a note
@app.put("/api/notes/{note_id}", dependencies=[Depends(JWTBearer())])
def update_note(note_id: int, note: Note):
    try:
        data = {"title": note.title, "body": note.body}
        # Check if the item exists
        note = database.fetch_by_id(TABLE_NAME, note_id)
        if not note:
            return {"message": "Not not found"}

        # Update the item
        database.update_data(TABLE_NAME, note_id, data)
        return {"message": "Item updated successfully"}
    except Exception as e:
        logger.error(f"Failed to update note | {e}")

# delete a note
@app.delete("/api/notes/{note_id}", dependencies=[Depends(JWTBearer())])
def delete_note(note_id: int):
    try:
        note = database.fetch_by_id(TABLE_NAME, note_id)
        if not note:
            return {"message": "Note not found"}
        # Delete note from the database
        database.delete_data(TABLE_NAME, note_id)
        return {"message: Failed to delete note"}
    except Exception as e:
        logger.error(f"Failed to delete note | {e}")

# search note based on keyword
@app.get("/api/search/", dependencies=[Depends(JWTBearer())])
def keyword_search(query: str):
    result = database.search_by_keywords(TABLE_NAME, query)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
