from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy import event
from sqlalchemy.engine import Engine
# Registers tables before the create_all runs
from app.models import Source, Playtest
import pathlib

sqlite_file_name = "app.db"
sqlite_url = f"sqlite:///{pathlib.Path(__file__).parent.resolve() / sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, connect_args=connect_args)

@event.listens_for(Engine, "connect")
def set_pragma(dbapi_connection, connection_record):
    #ac = dbapi_connection.autocommit
    #dbapi_connection.autocommit = True

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

    #dbapi_connection.autocommit = ac

def get_session():
    with Session(engine) as session:
        yield session

def create_database():
    SQLModel.metadata.create_all(engine)
