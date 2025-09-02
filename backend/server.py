from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Item
from seed import wipe_and_seed

Base.metadata.create_all(bind=engine)

wipe_and_seed()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI!"}

@app.post("/api/echo")
def echo(data: dict):
    return {"you_sent": data}

@app.get("/item/{item_abbreviation}")
def get_item(item_abbreviation: str, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.abbreviation == item_abbreviation).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {
        "abbreviation": item.abbreviation,
        "name": item.name,
        "value": item.value
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5001, reload=True)
