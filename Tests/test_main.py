import sys
sys.path.insert(0, '../App/')
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_main():
# Send a GET request to the root "/"
    response = client.get('/')
    #Assert that the HTTP status code is 200 (OK)
    print("health", response.status_code)

test_read_main()
