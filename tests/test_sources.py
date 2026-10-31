from fastapi.testclient import TestClient

def test_create_source_with_only_name_returns_201_and_optionals_are_none(client: TestClient):
    response = client.post('/sources', json={'name': 'test1'})
    assert response.status_code == 201

    body = response.json()
    assert body['id'] is not None
    assert body['name'] == 'test1'
    assert body['website'] is None
    assert body['default_pay_cents'] is None
    assert body['default_currency'] is None

