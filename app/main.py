from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles validation errors for incoming requests.

    This function is an exception handler for `RequestValidationError` exceptions
    raised during the validation of incoming requests. It returns a JSON response
    with a status code of 422 (Unprocessable Entity) and includes details about
    the validation errors.

    Args:
        request (Request): The incoming request that caused the validation error.
        exc (RequestValidationError): The exception instance containing details about the validation error.

    Returns:
        JSONResponse: A JSON response containing the error message, details of the validation errors,
            and original request body.
    """
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "error": "Request could not be processed due to error in data, see details section.",
                "detail": exc.errors(),
                "body": exc.body,
            }
        ),
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}
