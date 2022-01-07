import fastapi
from stock_scraper import Adapter

app = fastapi.FastAPI(title = "StockAPI")
adapter = Adapter()

@app.get("/indexes")
async def get_indexes():
    return adapter.get_indexes()

@app.get("/companies")
async def get_companies():
    return adapter.get_companies()

@app.get("/index")
async def get_index(name: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    ret = adapter.get_index(name)
    if ret == None or ret == []:
        return fastapi.Response(status_code=404)
    else:
        return ret

@app.get("/index_comapnies")
async def get_index_companies(name: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    ret = adapter.get_index_companies(name)
    if ret == None or ret == []:
        return fastapi.Response(status_code=404)
    else:
        return ret

@app.get("/company")
async def get_company(name: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    ret = adapter.get_company(name)
    if ret == None or ret == []:
        return fastapi.Response(status_code=404)
    else:
        return ret

@app.get("/historical_data")
async def get_historical_data(name: str = None, start: str = None, end: str = None, interval: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    ret = adapter.get_historical(name, start = start, end = end, interval = interval)
    if ret == None or ret == []:
        return fastapi.Response(status_code=404)
    else:
        return ret

@app.get("/last_data")
async def get_last_data(name: str = None, type: str = None):
    if name == None:
        return fastapi.Response(status_code=404)
    ret = adapter.get_last(name, type = type)
    if ret == None or ret == []:
        return fastapi.Response(status_code=404)
    else:
        return ret