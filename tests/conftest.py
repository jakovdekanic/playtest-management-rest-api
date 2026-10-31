import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
# registers tables so create_all has something to create
from app.models import Source, Playtest
# registers the foreign key listener on the Engine class 
import app.database

@pytest.fixture(name="session")
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
