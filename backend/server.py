from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Item, TimeSeriesPoint
from seed import seed, wipe
from fastapi.middleware.gzip import GZipMiddleware

Base.metadata.create_all(bind=engine)

seed()

app = FastAPI()

app.add_middleware(GZipMiddleware, minimum_size=1000)

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

@app.get("/item/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item.id, Item.name).filter(Item.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    stmt = (
        db.query(
            TimeSeriesPoint.timestamp,
            (TimeSeriesPoint.best_price + 2**63).label("best_price"),
            TimeSeriesPoint.rap,
            TimeSeriesPoint.favorited
        )
        .filter(TimeSeriesPoint.item_id == item_id)
        .order_by(TimeSeriesPoint.timestamp)
    )

    rows = stmt.all()
    timestamps, best_prices, raps, favorited = zip(*rows) if rows else ([], [], [], [])

    return {
        "id": item.id,
        "name": item.name,
        "time_series": {
            "timestamp": list(map(int, timestamps)),
            "best_price": list(map(int, best_prices)),
            "rap": list(raps),
            "favorited": list(favorited)
        }
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, reload=True)
