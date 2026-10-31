from fastapi.testclient import TestClient
from app.models import Currency, Source

# POST /sources - tests

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

# GET /sources/{id} tests

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

# GET /sources - tests

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

# PATCH /sources/{id} - tests

def helper_create_dummy_source(client: TestClient):
    test_source = client.post('/sources', json={'name': 'test',
                                                'website': 'test.com',
                                                'default_pay_cents': 100,
                                                'default_currency': 'eur'})
    assert test_source.status_code == 201
    return test_source
 

def test_patch_name_only_changes_name_and_keeps_other_fields(client: TestClient):
    test_source = helper_create_dummy_source(client)
    created = test_source.json()
    source_id = created['id']

    test_patch = client.patch(f'/sources/{source_id}', json={'name': 'update_name'})

    body = test_patch.json()
    assert test_patch.status_code == 200
    assert body['name'] == 'update_name'
    assert body['website'] == created['website']
    assert body['default_pay_cents'] == created['default_pay_cents']
    assert body['default_currency'] == created['default_currency']

def test_patch_pay_only_changes_pay_and_keeps_name(client: TestClient):
    test_source = helper_create_dummy_source(client)
    created = test_source.json()
    source_id = created['id']

    test_patch = client.patch(f'/sources/{source_id}', json={'default_pay_cents': 150})

    body = test_patch.json()
    assert test_patch.status_code == 200
    assert body['name'] == created['name']
    assert body['website'] == created['website']
    assert body['default_pay_cents'] == 150
    assert body['default_currency'] == created['default_currency']

def test_patch_website_and_currency_together(client: TestClient):
    test_source = helper_create_dummy_source(client)
    created = test_source.json()
    source_id = created['id']

    test_patch = client.patch(f'/sources/{source_id}', json={'default_currency': 'eur', 'website': 'test2.com'})

    body = test_patch.json()
    assert test_patch.status_code == 200
    assert body['name'] == created['name']
    assert body['website'] == 'test2.com'
    assert body['default_pay_cents'] == created['default_pay_cents']
    assert body['default_currency'] == 'eur'

def test_patch_pay_to_zero_is_allowed(client: TestClient):
    test_source = helper_create_dummy_source(client)
    created = test_source.json()
    source_id = created['id']

    test_patch = client.patch(f'/sources/{source_id}', json={'default_pay_cents': 0})

    body = test_patch.json()
    assert test_patch.status_code == 200
    assert body['name'] == created['name']
    assert body['website'] == created['website']
    assert body['default_pay_cents'] == 0
    assert body['default_currency'] == created['default_currency']

def test_patch_empty_body_returns_200_and_changes_nothing(client: TestClient):
    test_source = helper_create_dummy_source(client)
    created = test_source.json()
    source_id = created['id']

    test_patch = client.patch(f'/sources/{source_id}', json={})

    body = test_patch.json()
    assert test_patch.status_code == 200
    assert body['name'] == created['name']
    assert body['website'] == created['website']
    assert body['default_pay_cents'] == created['default_pay_cents']
    assert body['default_currency'] == created['default_currency']



