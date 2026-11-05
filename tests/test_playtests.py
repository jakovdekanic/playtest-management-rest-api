from fastapi.testclient import TestClient
from app.models import Currency, Status
from datetime import datetime, timezone

# helper source

def helper_source_empty(client: TestClient):
    helper_source = client.post('/sources', json={'name': 'source'})

    assert helper_source.status_code == 201
    return helper_source.json()

def helper_source_filled(client: TestClient):
    helper_source = client.post('/sources', json={'name': 'source',
                                          'website': 'source.com',
                                          'default_pay_cents': 1,
                                          'default_currency': Currency.eur})

    assert helper_source.status_code == 201
    return helper_source.json()

# tests

def test_playtest_with_all_fields_filled(client: TestClient):
    test_source = helper_source_empty(client)
    
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 5,
               'currency': Currency.eur,
               'status': Status.not_started, 
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)

    assert test_playtest.status_code == 201

    new_playtest = client.get(f'/playtests/{test_playtest.json()['id']}')
    assert new_playtest.status_code == 200
    new_body = new_playtest.json()

    assert new_body['id'] is not None
    assert new_body['game_title'] == payload['game_title']
    assert new_body['genre'] == payload['genre']
    assert new_body['game_link'] == payload['game_link']
    assert new_body['pay_cents'] == payload['pay_cents']
    assert new_body['currency'] == payload['currency']
    assert new_body['status'] == payload['status']
    assert new_body['created_date'] is not None
    assert new_body['source_id'] == payload['source_id']
