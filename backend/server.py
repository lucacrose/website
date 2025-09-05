from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import func
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

INTERVALS_LENGTHS = {
    "8h": 8,
    "1d": 8 * 3,
    "3d": 8 * 3 * 3,
    "7d": 8 * 3 * 7,
}

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
    interval: Literal["8h", "1d", "3d", "7d"] = Query(
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

    bucket_size = INTERVALS_LENGTHS.get(interval, 3)

    bucket_expr = (TimeSeriesPoint.timestamp // bucket_size) * bucket_size
    
    if chart_type == "line":
        fields = [bucket_expr.label("bucket")]
        if "best_price" in variables:
            fields.append(func.avg(TimeSeriesPoint.best_price).label("best_price"))
        if "rap" in variables:
            fields.append(func.avg(TimeSeriesPoint.rap).label("rap"))
        if "favorited" in variables:
            fields.append(func.avg(TimeSeriesPoint.favorited).label("favorited"))
        if "num_sellers" in variables:
            fields.append(func.avg(TimeSeriesPoint.favorited).label("num_sellers"))

        query = db.query(*fields).filter(TimeSeriesPoint.item_id == item_id)

        if start_ts:
            query = query.filter(TimeSeriesPoint.timestamp >= start_ts)
        if end_ts:
            query = query.filter(TimeSeriesPoint.timestamp <= end_ts)

        query = query.group_by("bucket").order_by("bucket")
        rows = query.all()

        data = {"timestamp": [r[0] for r in rows]}
        for i, var in enumerate(variables, start=1):
            if var in ["best_price", "rap", "favorited", "num_sellers"]:
                data[var] = [r[i] for r in rows]

    elif chart_type == "candle":
        if "best_price" not in variables:
            raise HTTPException(status_code=400, detail="Candles require best_price variable")

        subquery = (
            db.query(
                bucket_expr.label("bucket"),
                TimeSeriesPoint.timestamp,
                TimeSeriesPoint.best_price
            )
            .filter(TimeSeriesPoint.item_id == item_id)
        )

        if start_ts:
            subquery = subquery.filter(TimeSeriesPoint.timestamp >= start_ts)
        if end_ts:
            subquery = subquery.filter(TimeSeriesPoint.timestamp <= end_ts)

        subquery = subquery.subquery()

        query = db.query(
            subquery.c.bucket,
            func.min(subquery.c.best_price).label("low"),
            func.max(subquery.c.best_price).label("high"),
            func.first_value(subquery.c.best_price).over(
                partition_by=subquery.c.bucket, order_by=subquery.c.timestamp
            ).label("open"),
            func.last_value(subquery.c.best_price).over(
                partition_by=subquery.c.bucket, order_by=subquery.c.timestamp
            ).label("close")
        ).group_by(subquery.c.bucket).order_by(subquery.c.bucket)

        rows = query.all()

        data = {
            "timestamp": [r.bucket for r in rows],
            "open": [r.open for r in rows],
            "high": [r.high for r in rows],
            "low": [r.low for r in rows],
            "close": [r.close for r in rows]
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid chart_type")

    return data

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, reload=True)
