from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_db_and_tables
from .routers import symbols, corp_actions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for the FastAPI application lifespan.

    This function is used to manage the lifespan of the FastAPI application.
    It creates the database and tables before the application starts and ensures
    that the resources are properly cleaned up after the application stops.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: This function yields control back to the FastAPI application.
    """

    # Create db and tables
    create_db_and_tables()

    # yield app
    yield


app = FastAPI(lifespan=lifespan)

# Include more routes here
app.include_router(symbols.router)
app.include_router(corp_actions.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
