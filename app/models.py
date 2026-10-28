from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from enum import StrEnum
from datetime import datetime

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

