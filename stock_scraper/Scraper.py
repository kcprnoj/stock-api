from requests import get, post, Response
from abc import abstractmethod

from requests.api import head
from utils import get_random_agent

class Scraper:
    def __init__(self):
        self.indexes = list()
        self.companies = list()
        self.blacklist = list()
        self.main_url = ""

    def get_indexes(self) -> list:
        return self.indexes

    def get_companies(self) -> list:
        return self.companies

    def update_blacklist(self) -> None:
        headers = {'User-Agent': get_random_agent()}
        response = get(self.main_url + "/robots.txt", headers=headers)
        response = response.text.split('\n')
        self.blacklist = list()
        append = False
        for line in response:
            if line.find("User-agent: *") > -1:
                append = True
            elif line.find("User-agent: ") > -1:
                append = False
            elif append and line.find("Disallow: ") > -1:
                self.blacklist.append(line.replace("Disallow: ", self.main_url).split('?')[0])

    def get(self, url, headers = None) -> Response:
        if headers == None:
            headers = {'user-agent' : get_random_agent()}
        if url.split('?')[0] in self.blacklist:
            resp = Response()
            resp.status_code = 403
            return resp
        else:
            return get(url, headers=headers)

    def post(self, url: str, headers: dict = None, data: dict = None):
        if headers == None:
            headers = {'user-agent' : get_random_agent()}
        if url.split('?')[0] in self.blacklist:
            resp = Response()
            resp.status_code = 403
            return resp
        else:
            return post(url, data = data, headers = headers)

    @abstractmethod
    def update_companies(self, force: bool = False) -> None:
        pass

    @abstractmethod
    def update_indexes(self, force: bool = False) -> None:
        pass

    @abstractmethod
    def get_index(self, index: str) -> dict:
        pass

    @abstractmethod
    def get_index_companies(self, index: str, full: bool = False) -> list:
        pass

    @abstractmethod
    def get_company(self, name: str) -> dict:
        pass

    @abstractmethod
    def get_historical(self, name: str, start: str = None, end: str = None) -> list:
        pass