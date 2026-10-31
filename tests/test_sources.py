from fastapi.testclient import TestClient
from app.models import Currency, Source
from sqlmodel import select

def test_create_source_with_only_name_returns_201_and_optionals_are_none(client: TestClient):
    response = client.post('/sources', json={'name': 'test1'})
    assert response.status_code == 201

    body = response.json()
    assert body['id'] is not None
    assert body['name'] == 'test1'
    assert body['website'] is None
    assert body['default_pay_cents'] is None
    assert body['default_currency'] is None

def test_source_with_all_fields_filled(client: TestClient):
    test_source = client.post('/sources', json={'name': 'test',
                                               'website': 'test.com',
                                               'default_pay_cents': 100,
                                               'default_currency': Currency.eur})

    assert test_source.status_code == 201
    body = test_source.json()
    assert body['name'] == 'test'
    assert body['website'] == 'test.com'
    assert body['default_pay_cents'] == 100
    assert body['default_currency'] == Currency.eur

def test_source_with_invalid_currency(client: TestClient):
    test_source1 = client.post('/sources', json={'name': 'test1','default_currency': 'gbp'})
    assert test_source1.status_code == 422

def test_duplicate_name_sources_first_return_201_second_409(client: TestClient):
    test_source1 = client.post('/sources', json={'name': 'test1'})
    assert test_source1.status_code == 201

    test_source2 = client.post('/sources', json={'name': 'test1'})
    assert test_source2.status_code == 409

def test_source_with_negative_pay(client: TestClient):
    test_source = client.post('/sources', json={'name': 'test', 'default_pay_cents': -1})
    assert test_source.status_code == 422

def test_source_with_free_pay(client: TestClient):
    test_source = client.post('/sources', json={'name': 'test', 'default_pay_cents': 0})
    assert test_source.status_code == 201

def test_source_with_empty_name(client: TestClient):
    test_source = client.post('/sources', json={'name': ''})
    assert test_source.status_code == 422

def test_source_with_name_only_being_whitespace(client: TestClient):
    test_source = client.post('/sources', json={'name': '  '})
    assert test_source.status_code == 422

def test_if_source_with_whitespace_before_and_after_is_stripped(client: TestClient):
    test_source = client.post('/sources', json={'name': '  test1   '})
    assert test_source.status_code == 201
    assert test_source.json()['name'] == 'test1'

def test_get_a_valid_source(client: TestClient):
    test_source = client.post('/sources', json={'name': 'test',
                                               'website': 'test.com',
                                               'default_pay_cents': 100,
                                               'default_currency': Currency.eur})

    source_return = client.get(f'/sources/{test_source.json()['id']}')

    assert source_return.status_code == 200
    body = source_return.json()
    assert body['name'] == 'test'
    assert body['website'] == 'test.com'
    assert body['default_pay_cents'] == 100
    assert body['default_currency'] == Currency.eur

def test_get_with_id_that_does_not_exist(client: TestClient):
    source_return = client.get('/sources/999')
    assert source_return.status_code == 404
    assert source_return.json()['detail'] == 'Source with that id does not exist.'


def test_get_empty_database_returns_200_and_empty_list(client: TestClient):
    response = client.get('/sources')

    assert response.status_code == 200
    assert response.json() == []

def test_create_two_sources_get_them_and_check_if_both_are_there(client: TestClient):
    test_source1 = client.post('/sources', json={'name': 'test1'})
    test_source2 = client.post('/sources', json={'name': 'test2'})

    assert test_source1.status_code == 201
    assert test_source2.status_code == 201
    response = client.get('/sources')

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[1]['name'] == 'test2'
    assert response.json()[0]['name'] == 'test1'
