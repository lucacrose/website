from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Item, TimeSeriesPoint
from seed import seed, wipe
from fastapi.middleware.gzip import GZipMiddleware
from typing import Literal, List

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
    item = db.get(Item, item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return {
        "id": item.id,
        "name": item.name
    }

@app.get("/item/{item_id}/graph")
def get_graph(
    item_id: int,
    interval: Literal["8h", "1d", "3d", "1w"] = Query(
        "1d", description="Aggregation interval"
    ),
    chart_type: Literal["line", "candle"] = Query(
        "line", description="Chart type"
    ),
    start_ts: int | None = None,
    end_ts: int | None = None,
    variables: List[str] = Query(["rap"], description="Included variables"),
    db: Session = Depends(get_db)
):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    fields = [TimeSeriesPoint.timestamp]
    allowed_vars = {"best_price", "rap", "favorited", "num_sellers"}
    selected_vars = [v for v in variables if v in allowed_vars]

    for v in selected_vars:
        fields.append(getattr(TimeSeriesPoint, v))

    query = select(*fields).where(TimeSeriesPoint.item_id == item_id)

    if start_ts:
        query = query.where(TimeSeriesPoint.timestamp >= start_ts)
    
    if end_ts:
        query = query.where(TimeSeriesPoint.timestamp <= end_ts)

    query = query.order_by(TimeSeriesPoint.timestamp)

    rows = db.execute(query).all()

    if rows:
        unpacked = list(zip(*rows))
        data = {"timestamp": list(unpacked[0])}
        for i, var in enumerate(selected_vars, start=1):
            data[var] = list(unpacked[i])
    else:
        data = {"timestamp": []}
        for var in selected_vars:
            data[var] = []

    rows = db.execute(query).all()

    return data

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, reload=True)
