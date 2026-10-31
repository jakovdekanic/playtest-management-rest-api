from app.models import Source, Playtest, Currency, Status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError, NoSuchColumnError
from datetime import datetime,timezone
import pytest

def test_create_source(session: Session):

    wildduckdev = Source(name="WildDuckDev", website="https://wildduckdev.github.io", default_pay_cents=2000,default_currency=Currency.eur)
    session.add(wildduckdev)
    session.commit()
    playtest_test = Playtest(source_id=wildduckdev.id,
                             game_title="Game1",
                             genre="Genre1",
                             game_link="game.com",
                             pay_cents=2000,
                             currency=Currency.eur,
                             status=Status.not_started,
                             created_date=datetime.now(timezone.utc)
                             )
    session.add(playtest_test)
    session.commit()

    wildduckdev_return = session.get(Source, wildduckdev.id)
    playtest_return = session.get(Playtest, playtest_test.id)

    assert wildduckdev_return.name == 'WildDuckDev'
    assert wildduckdev_return.website == 'https://wildduckdev.github.io'
    assert wildduckdev_return.default_pay_cents == 2000
    assert wildduckdev_return.default_currency == Currency.eur

    assert playtest_return.source_id == wildduckdev.id
    assert playtest_return.game_title == "Game1"
    assert playtest_return.genre == "Genre1"
    assert playtest_return.game_link == "game.com"
    assert playtest_return.pay_cents == 2000
    assert playtest_return.currency == Currency.eur
    assert playtest_return.status == Status.not_started
    assert playtest_return.created_date != None
    print(playtest_return.created_date)


def test_playtest_created_date_defaults_to_now(session: Session):
    test_source = Source(name="Test")
    session.add(test_source)
    session.commit()
    test_playtest = Playtest(source_id=test_source.id,
                             game_title="Game2",
                             genre="Genre2",
                             game_link="game2.com",
                             pay_cents=500,
                             currency=Currency.usd,
                             status=Status.waiting_for_payment)
    session.add(test_playtest)
    session.commit()

    source_return = session.get(Source, test_source.id)
    playtest_return = session.get(Playtest, test_playtest.id)

    assert source_return.name == "Test"

    assert playtest_return.source_id == test_source.id
    assert playtest_return.game_title == 'Game2'
    assert playtest_return.genre == 'Genre2'
    assert playtest_return.game_link == 'game2.com'
    assert playtest_return.pay_cents == 500
    assert playtest_return.currency == Currency.usd
    assert playtest_return.status == Status.waiting_for_payment
    assert playtest_return.created_date != None

def test_playtest_requires_existing_source(session: Session):
    test_playtest = Playtest(source_id=999,
                             game_title="Game2",
                             genre="Genre2",
                             game_link="game2.com",
                             pay_cents=500,
                             currency=Currency.usd,
                             status=Status.waiting_for_payment)
    session.add(test_playtest)
    with pytest.raises(IntegrityError):
        session.commit()

def test_playtest_rejects_invalid_currency(session: Session):
    test_source = Source(name="test_source")
    session.add(test_source)
    session.commit()
    test_playtest = Playtest(source_id=test_source.id,
                             game_title="Game2",
                             genre="Genre2",
                             game_link="game2.com",
                             pay_cents=500,
                             currency='gbp',
                             status=Status.waiting_for_payment)
    session.add(test_playtest)
    session.commit()



