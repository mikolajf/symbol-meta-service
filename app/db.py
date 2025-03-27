from sqlalchemy import create_engine
from sqlmodel import SQLModel

# TODO <MFido> [26/03/2025] this should be "productionized" and moved to a more robust solution
# A SQLite database file named database.db is specified, and its URL is constructed. The connect_args dictionary is
# used to set the check_same_thread option to False, which allows the database to be accessed from multiple threads.
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """This function uses SQLModel's metadata.create_all method to create the database tables based on the models
    defined in the application."""
    SQLModel.metadata.create_all(engine)
