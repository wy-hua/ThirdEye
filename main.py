
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()


@app.get("/")
async def root():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"message": f"Hello World! Current time is: {current_time}"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# Add this class to define the request body structure
class QueryRequest(BaseModel):
    query: str

@app.post("/album_query")
async def album_query(request: QueryRequest):
    return {"message": f"Hello {request.query}"}
