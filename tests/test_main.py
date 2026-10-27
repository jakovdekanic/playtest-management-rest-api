from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
# Send a GET request to "/health"
    response = client.get('/health')
    #Assert that the HTTP status code is 200 (OK)
    assert response.status_code == 200

    assert response.json() == {'status': 'ok'}

