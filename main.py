import fastapi
from stock_scraper.InvestingScraper import InvestingScraper

app = fastapi.FastAPI()
scraper = InvestingScraper()

@app.get("/indexes")
async def get_indexes():
    return scraper.parse_indexes()

@app.get("/index")
async def get_index(indexName: str = None):
    return scraper.parse_index(indexName = indexName)

@app.get("/company")
async def get_company(companyName: str = None, companyIndex: str = None):
    if companyName == None:
        return fastapi.Response(status_code=404)
    return scraper.parse_company(companyName, companyIndex = companyIndex)

@app.get("/historical_data")
async def get_company(companyName: str = None, companyIndex: str = None, startDate: str = None, endDate: str = None):
    if companyName == None:
        return fastapi.Response(status_code=404)
    return scraper.parse_historial_data(companyName, companyIndex = companyIndex, startDate = startDate, endDate = endDate)