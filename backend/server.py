from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

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
def get_item(item_abbreviation: str):
    return {"item_item_abbreviation": item_abbreviation, "message": f"Details for item {item_abbreviation}"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=5000, reload=True)