from .BankierScraper import BankierScraper
from .InvestingScraper import InvestingScraper
from .Scraper import Scraper

class Controller:

    def __init__(self) -> None:
        self.scrapers = [BankierScraper(), InvestingScraper()]

    def get_index(self, index: str) -> dict:
        scraper = self.get_scraper_by_index(index)
        if scraper != None:
            return scraper.get_index(index)
        else:
            return None

    def get_index_companies(self, index: str) -> list:
        scraper = self.get_scraper_by_index(index)
        if scraper != None:
            return scraper.get_index_companies(index)
        else:
            return None

    def get_company(self, name: str) -> dict:
        scraper = self.get_scraper_by_company(name)
        print (scraper)
        if scraper != None:
            return scraper.get_company(name)
        else:
            return None

    def get_historical(self, name: str, start: str = None, end: str = None) -> list:
        scraper = self.get_scraper_by_company(name)
        if scraper != None:
            return scraper.get_historical(name, start = start, end = end)
        else:
            return None

    def get_indexes(self) -> list:
        retval = []
        for scraper in self.scrapers:
            retval += scraper.get_indexes()
        return retval

    def get_companies(self) -> list:
        retval = []
        for scraper in self.scrapers:
            retval += scraper.get_companies()
        return retval

    def get_scraper_by_index(self, index: str) -> Scraper:
        for scraper in self.scrapers:
            if index in scraper.get_indexes():
                return scraper
        return None

    def get_scraper_by_company(self, company: str) -> Scraper:
        for scraper in self.scrapers:
            if company in scraper.get_companies():
                return scraper
        return None