from fastapi import FastAPI
from .routers import symbols

app = FastAPI()

# Include more routes here
app.include_router(symbols.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
