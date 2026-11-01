from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from app.database import create_database, get_session
from sqlmodel import Session,select
from app.models import SourceRead, SourceCreate, Source, SourceUpdate
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

@app.get('/sources/{source_id}', status_code=200, response_model=SourceRead)
def get_source(source_id : int, session: Session = Depends(get_session)):
    received_source = session.get(Source, source_id)
    if received_source is None: 
        raise HTTPException(status_code=404, detail='Source with that id does not exist.')

    return received_source

@app.get('/sources', status_code=200, response_model=list[SourceRead])
def list_sources(session: Session = Depends(get_session)):
    return session.exec(select(Source).order_by(Source.id)).all()

@app.patch('/sources/{source_id}', status_code=200, response_model=SourceRead)
def update_source(source_id: int, body: SourceUpdate, session: Session = Depends(get_session)):
    old_source = session.get(Source, source_id)
    if old_source is None:
        raise HTTPException(status_code=404, detail='Source with that id does not exist.')


    source_data = body.model_dump(exclude_unset=True)
    old_source.sqlmodel_update(source_data)
    session.add(old_source)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail='A source with that name already exists.')
    session.refresh(old_source)
    return old_source
