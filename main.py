import fastapi
from stock_scraper import Controller

app = fastapi.FastAPI()
controller = Controller()

@app.get("/indexes")
async def get_indexes():
    return controller.get_indexes()

@app.get("/companies")
async def get_companies():
    return controller.get_companies()

@app.get("/index")
async def get_index(name: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    return controller.get_index(name)

@app.get("/index_comapnies")
async def get_index(name: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    return controller.get_index_companies(name)

@app.get("/company")
async def get_company(name: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    return controller.get_company(name)

@app.get("/historical_data")
async def get_company(name: str = None, start: str = None, end: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    return controller.get_historical(name, start = start, end = end)