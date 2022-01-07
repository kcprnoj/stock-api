import pytest
from requests import get
import time

@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(2)

@pytest.mark.repeat(50)
def test_server_get_historical_1():
    response = get('http://127.0.0.1:8000/historical_data?name=Allegro')
    assert response.status_code == 200

@pytest.mark.repeat(50)
def test_server_get_historical_2():
    response = get('http://127.0.0.1:8000/historical_data?name=ALLEGRO')
    assert response.status_code == 200