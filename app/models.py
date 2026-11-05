from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from enum import StrEnum
from datetime import datetime,timezone
from pydantic import StringConstraints
from typing import Annotated

class Currency(StrEnum):
    eur = 'eur'
    usd = 'usd'

class Status(StrEnum):
    not_started = 'not_started'
    waiting_for_game = 'waiting_for_game'
    completed = 'completed'
    waiting_for_payment = 'waiting_for_payment'

class Source(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name"),)
    id: int | None = Field(default=None, primary_key=True)
    name: str
    website: str | None = None
    default_pay_cents: int | None = None
    default_currency: Currency | None = None

class Playtest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="source.id")
    game_title: str
    genre: str
    game_link: str
    pay_cents: int
    currency: Currency
    status: Status
    created_date: datetime = Field(default_factory=lambda : datetime.now(timezone.utc))



class SourceCreate(SQLModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    website: str | None = None
    default_pay_cents: int | None = Field(default=None, ge=0)
    default_currency: Currency | None = None

class SourceRead(SQLModel):
    id: int
    name: str
    website: str | None = None
    default_pay_cents: int | None = None
    default_currency: Currency | None = None

class SourceUpdate(SQLModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] = None
    website: str | None = None
    default_pay_cents: int | None = Field(default=None, ge=0)
    default_currency: Currency | None = None

class PlaytestCreate(SQLModel):
    source_id: int
    game_title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    genre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    game_link: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    pay_cents: int | None = Field(default=None, ge=0)
    currency: Currency | None = None
    status: Status = Status.not_started

class PlaytestRead(SQLModel):
    id: int
    source_id: int
    game_title: str
    genre: str
    game_link: str
    pay_cents: int
    currency: Currency
    status: Status
    created_date: datetime


