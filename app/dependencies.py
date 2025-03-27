from sqlmodel import Session

from app.db import engine


def get_session():
    """
    Dependency that provides a SQLModel session.

    This function creates a new SQLModel session using the provided engine and yields it.
    The session is automatically closed after the request is processed.

    To be used in function parameters like so:
    ```
    def endpoint(*, session: Session = Depends(get_session), ...)
    ```

    Yields:
        Session: A SQLModel session connected to the database.
    """
    with Session(engine) as session:
        yield session
