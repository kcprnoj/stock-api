import pytest
from requests import get
from stock_scraper.BankierScraper import BankierScraper
from stock_scraper.InvestingScraper import InvestingScraper
import time

@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(2)

def test_server_get_historical_1():
    response = get('http://127.0.0.1:8000/historical_data?name=Allegro')
    assert response.status_code == 200

def test_server_get_historical_2():
    response = get('http://127.0.0.1:8000/historical_data?name=ALLEGRO')
    assert response.status_code == 200

def test_server_get_historical_interval_1():
    response = get('http://127.0.0.1:8000/historical_data?name=ALLEGRO&interval=7D')
    assert response.status_code == 200

def test_server_get_historical_interval_2():
    response = get('http://127.0.0.1:8000/historical_data?name=Allegro&interval=7D')
    assert response.status_code == 200

def test_server_get_historical_date_1():
    response = get('http://127.0.0.1:8000/historical_data?name=ALLEGRO&start=14%2F10%2F2020&end=05%2F01%2F2022')
    assert response.status_code == 200

def test_server_get_historical_date_2():
    response = get('http://127.0.0.1:8000/historical_data?name=Allegro&start=14%2F10%2F2020&end=05%2F01%2F2022')
    assert response.status_code == 200

def test_server_get_historical_wrong_name():
    response = get('http://127.0.0.1:8000/historical_data?name=A')
    assert response.status_code == 404

def test_server_indexes():
    response = get('http://127.0.0.1:8000/indexes')
    assert response.status_code == 200

def test_server_index_WIG30():
    response = get('http://127.0.0.1:8000/index?name=WIG30')
    assert response.status_code == 200

def test_server_index_companies_WIG30():
    response = get('http://127.0.0.1:8000/index_comapnies?name=WIG30')
    assert response.status_code == 200

def test_server_index_SP500():
    response = get('http://127.0.0.1:8000/index?name=S%26P%20500')
    assert response.status_code == 200

def test_server_index_companies_SP500():
    response = get('http://127.0.0.1:8000/index_comapnies?name=S%26P%20500')
    assert response.status_code == 200

def test_server_companies():
    response = get('http://127.0.0.1:8000/indexes')
    assert response.status_code == 200

@pytest.mark.timeout(300)
def test_server_companies_wig30():
    WIG30 = ['ALIOR','ALLEGRO','AMREST','ASSECOPOL','CCC','CDPROJEKT','CYFRPLSAT','DINOPL','ENEA','EUROCASH','GRUPAAZOTY','JSW','KGHM','LOTOS','LPP',
            'MBANK','MERCATOR','MILLENNIUM','ORANGEPL','PEKAO','PEPCO','PGE','PGNIG','PKNORLEN','PKOBP','PZU','SANPL','TAURONPE','TSGAMES', 'XTB']
    for company in WIG30:
        response = get(f'http://127.0.0.1:8000/company?name={company}')
        assert response.status_code == 200

def test_robots_bankier():
    bankier = BankierScraper()
    response = bankier.get('https://www.bankier.pl/forum/wyslij-znajomemu')
    assert response.status_code == 403

def test_robots_investing():
    bankier = InvestingScraper()
    response = bankier.get('https://www.investing.com/admin')
    assert response.status_code == 403

@pytest.mark.timeout(200)
def test_server_timetest():
    companies = [
        "ALLEGRO", "ALIOR", "AMREST", "ASSECOPOL", "CCC", "CDPROJEKT", "CYFRPLSAT", "DINOPL", "ENEA", "EUROCASH",
        "Boeing", "General Motors", "Chevron", "Citigroup", "Bank of America", "Caterpillar", "Intel", "Microsoft", "Ford Motor", "eBay"
    ]
    for company in companies:
        response = get(f'http://127.0.0.1:8000/historical_data?name={company}')
        assert response.status_code == 200
