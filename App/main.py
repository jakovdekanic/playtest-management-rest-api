from fastapi import FastAPI
import sqlmodel
import pytest


app = FastAPI()

@app.get('/')
async def read_root():
    return {'message': 'Hello World!'}
