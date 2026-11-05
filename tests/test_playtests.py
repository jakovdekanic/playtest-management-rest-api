from fastapi.testclient import TestClient
from app.models import Currency, Status
from datetime import datetime, timezone, timedelta

# helper source

def helper_source_empty(client: TestClient):
    helper_source = client.post('/sources', json={'name': 'source'})

    assert helper_source.status_code == 201
    return helper_source.json()

def helper_source_filled(client: TestClient):
    helper_source = client.post('/sources', json={'name': 'source',
                                          'website': 'source.com',
                                          'default_pay_cents': 1,
                                          'default_currency': Currency.usd})

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
    
    test_body = test_playtest.json()
    assert test_body['id'] is not None
    assert test_body['game_title'] == payload['game_title']
    assert test_body['genre'] == payload['genre']
    assert test_body['game_link'] == payload['game_link']
    assert test_body['pay_cents'] == payload['pay_cents']
    assert test_body['currency'] == payload['currency']
    assert test_body['status'] == payload['status']
    assert test_body['created_date'] is not None
    assert test_body['source_id'] == payload['source_id']


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

def test_nonexistent_source_id_returns_422(client: TestClient):
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 5,
               'currency': Currency.eur,
               'status': Status.not_started, 
               'source_id': 999}

    test_playtest = client.post('/playtests', json=payload)

    assert test_playtest.status_code == 422
    assert test_playtest.json()['detail'] == f"A source with id:{payload['source_id']} does not exist."

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_default_pay_cents_and_currency_when_the_playtest_does_not_have_them(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)

    assert test_playtest.status_code == 201

    get_playtest = client.get(f'/playtests/{test_playtest.json()['id']}')
    assert get_playtest.status_code == 200
    
    assert get_playtest.json()['currency'] == test_source['default_currency']
    assert get_playtest.json()['pay_cents'] == test_source['default_pay_cents']

def test_default_values_for_currency_and_pay_cents_set_to_zero_and_eur_if_none_are_passed(client: TestClient):
    test_source = helper_source_empty(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201

    get_playtest = client.get(f'/playtests/{test_playtest.json()['id']}')
    assert get_playtest.status_code == 200
    assert get_playtest.json()['currency'] == 'eur'
    assert get_playtest.json()['pay_cents'] == 0

def test_playtest_pay_cents_zero_but_source_has_a_default_higher_result_should_be_zero(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201

    get_playtest = client.get(f'/playtests/{test_playtest.json()['id']}')
    assert get_playtest.status_code == 200
    assert get_playtest.json()['pay_cents'] == 0

# GET '/playtests' tests

def test_empty_database_returns_empty_list_and_200(client: TestClient):
    get_playtests = client.get('/playtests')

    assert get_playtests.status_code == 200
    assert get_playtests.json() == []

def test_create_two_playtests_get_them_and_check_if_both_are_there(client: TestClient):
    test_source = helper_source_empty(client)
    test_playtest = client.post('/playtests', json={'game_title': 'game1',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'status': Status.not_started,
               'source_id': test_source['id']})

    test_playtest2 = client.post('/playtests', json={'game_title': 'game2',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'status': Status.not_started,
               'source_id': test_source['id']})

    assert test_playtest.status_code == 201
    assert test_playtest2.status_code == 201

    response = client.get('/playtests')
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[1]['game_title'] == 'game2'
    assert response.json()[0]['game_title'] == 'game1'

# GET playtests/id tests

def test_invalid_currency_returns_422(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': 'gbp',
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_invalid_status_returns_422(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': 'invalid_status',
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_negative_pay_returns_422(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': -1,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_empty_game_title(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': '',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_whitespace_only_game_title(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': '  ',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_empty_genre(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': '',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_whitespace_only_genre(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': '  ',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_empty_game_link(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': '',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_whitespace_only_game_link(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': '  ',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_missing_source_id_returns_422(client: TestClient):
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_null_source_id_returns_422(client: TestClient):
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': None}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_source_id_returns_422(client: TestClient):
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': 'abc'}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422

    response = client.get('/playtests')
    assert response.status_code == 200
    assert response.json() == []

def test_strings_are_stripped(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': '  game  ',
               'genre': '  genre  ',
               'game_link': '  game.com  ',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201

    response = client.get(f'/playtests/{test_playtest.json()['id']}')
    response_body = response.json()
    assert response.status_code == 200
    assert response_body['game_title'] == 'game'
    assert response_body['genre'] == 'genre'
    assert response_body['game_link'] == 'game.com'

def test_client_passed_id_and_datetime_are_ignored(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id'],
               'id': 12,
               'created_date': datetime.strptime("2000-12-02",'%Y-%m-%d').isoformat()}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201

    response = client.get(f'/playtests/{test_playtest.json()['id']}')
    response_body = response.json()
    assert response.status_code == 200
    assert response_body['id'] != 12
    assert datetime.fromisoformat(response_body['created_date']).year != 2000

def test_datetime_returns_with_a_utc_offset(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201

    response = client.get(f'/playtests/{test_playtest.json()['id']}')
    response_body = response.json()
    assert response.status_code == 200
    assert datetime.fromisoformat(response_body['created_date']).utcoffset() == timedelta(0)

def test_get_playtest_by_id_with_a_nonexistent_id_returns_404_with_detail(client: TestClient):
    test_response = client.get('/playtests/999')
    assert test_response.status_code == 404
    assert test_response.json()['detail'] == 'Playtest with that id does not exist.'

def test_client_currency_over_source_default(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201
    
    response = client.get(f"/playtests/{test_playtest.json()['id']}")
    assert response.status_code == 200
    assert response.json()['currency'] == Currency.eur

def test_status_not_given_returns_not_started(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 0,
               'currency': Currency.eur,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 201
    
    response = client.get(f"/playtests/{test_playtest.json()['id']}")
    assert response.status_code == 200
    assert response.json()['status'] == Status.not_started

def test_non_integer_pay_returns_422(client: TestClient):
    test_source = helper_source_filled(client)
    payload = {'game_title': 'game',
               'genre': 'genre',
               'game_link': 'game.com',
               'pay_cents': 5.5,
               'currency': Currency.eur,
               'status': Status.not_started,
               'source_id': test_source['id']}

    test_playtest = client.post('/playtests', json=payload)
    assert test_playtest.status_code == 422
    response = client.get('/playtests')
    assert response.status_code == 200
    assert len(response.json()) == 0
