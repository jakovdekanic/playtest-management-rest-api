import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
# registers tables so create_all has something to create
from app.models import Source, Playtest
# registers the foreign key listener on the Engine class but
# imports only get session because of app.main import app
from app.database import get_session
from app.main import app
from fastapi.testclient import TestClient

@pytest.fixture(name="session")
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client(session: Session):
    def fake_session_get():
        return session
    
    client = TestClient(app)
    app.dependency_overrides[get_session] = fake_session_get
    yield client
    app.dependency_overrides.pop(get_session, None)
