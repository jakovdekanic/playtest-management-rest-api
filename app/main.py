from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_database, engine
from sqlmodel import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    yield 

app = FastAPI(lifespan=lifespan)

@app.get('/health')
def get_health():
    return {'status': 'ok'}
