from fastapi import FastAPI
from app.db.mongodb import db

app = FastAPI()

@app.get("/")
async def root():
    collections = await db.list_collection_names()
    return {"message": "Hello World", "collections": collections}

