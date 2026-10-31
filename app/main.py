from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from app.database import create_database, get_session
from sqlmodel import Session
from app.models import SourceRead, SourceCreate, Source
from sqlalchemy.exc import IntegrityError


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield 

app = FastAPI(lifespan=lifespan)

@app.get('/health')
def get_health():
    return {'status': 'ok'}

@app.post('/sources', status_code=201, response_model=SourceRead)
def create_source(body: SourceCreate, session: Session = Depends(get_session)):
    source = Source.model_validate(body)
    session.add(source)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='A source with that name already exists.')
    session.refresh(source)
    return source
