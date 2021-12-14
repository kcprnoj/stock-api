from re import search
from urllib.parse import non_hierarchical

from requests.models import Response
from utils import get_random_agent
from os.path import exists, abspath
from os import getcwd, replace
from Scraper import Scraper
from lxml import html
from json import load, dump
from datetime import datetime
from pandas import to_datetime

class InvestingScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.indexes_id = dict()
        self.companies_id = dict()
        self.main_url = "https://www.investing.com"
        self.update_blacklist()
        self.update_indexes()
        self.update_companies()

    def update_companies(self, force: bool = False) -> None:
        path_file = abspath(getcwd()) + '/stock_scraper/data/investing_companies.json'
        if not force and exists(path_file):
            with open(path_file) as file:
                self.companies_id = load(file)
                self.companies = list(self.companies_id.keys())
                return

        for index in self.indexes:
            for company in self.get_index_companies(index, full = True):
                self.companies.append(company['Name'])
                self.companies_id[company['Name']] = {'ID' : company['ID'], 'index' : index, 'currency': self.indexes_id[index]['currency'], 'url': company['URL']}

        with open(path_file, "w") as f:
            dump(self.companies_id, f, indent = 6, ensure_ascii=False)

    def update_indexes(self, force: bool = False) -> None:
        path_file = abspath(getcwd()) + '/stock_scraper/data/investing_index.json'
        if not force and exists(path_file):
            with open(path_file) as file:
                self.indexes_id = load(file)
                self.indexes = list(self.indexes_id.keys())
                return

        response = self.get(self.main_url + "/equities/")
        response = html.fromstring(response.text)
        self.indexes = response.xpath('//select[@class="selectBox"]//option//text()')
        id = response.xpath('//select[@class="selectBox"]//option//@id')
        self.indexes_id = dict()
        for i in range(len(self.indexes)):
            self.indexes_id[self.indexes[i]] = {'ID': id[i]}
            urls = self.search(self.indexes[i])
            url = ''
            for u in urls:
                if 'indices' in u[0] and self.indexes[i] == u[1]:
                    url = u[0]
                    break

            if url == '':
                if self.get(self.main_url + '/indices/' + self.indexes[i].lower()).status_code == 200:
                    self.indexes_id[self.indexes[i]]['url'] = '/indices/' + self.indexes[i].lower()
                else:
                    self.indexes_id[self.indexes[i]]['url'] = ''
            else:
                self.indexes_id[self.indexes[i]]['url'] = url

            self.indexes_id[self.indexes[i]]['currency'] = self.get_index(self.indexes[i])['Currency']

        with open(path_file, 'w') as f:
            dump(self.indexes_id, f, indent = 6, ensure_ascii=False)

    def get_index(self, index: str) -> dict:
        return self.get_equity(self.main_url + self.indexes_id[index]['url'])

    def get_index_companies(self, index: str, full: bool = False) -> list:
        filter_url = self.main_url + '/equities/stocksFilter?noconstruct=1&smlID=0&sid=&tabletype=price&index_id='
        response = self.get(filter_url + self.indexes_id[index]['ID'])
        root = html.fromstring(response.text)
        result = []
        current_date = datetime.now()
        today = f"{current_date.day}-{current_date.month}-{current_date.year}"

        for row in root.xpath('//table//tbody//tr'):
            data = row.xpath('td//text()')
            if full:
                result.append({
                    'Name': data[1],
                    'Full Name': row.xpath('td//@title')[1],
                    'Last': float(data[2].replace(',', '')),
                    'High': float(data[3].replace(',', '')),
                    'Low': float(data[4].replace(',', '')),
                    'Change': float(data[5].replace(',', '').replace('+-', '+')),
                    'Change %': float(data[6].replace(',', '').replace('%', '').replace('+-', '+')),
                    'Volume': int(data[7].replace('.','').replace('K', '0').replace('M', '0000').replace('B','0000000')),
                    'Date': today + ' ' + data[8] if ':' in data[8] else str(to_datetime(data[8] + '/' + str(current_date.year))),
                    'URL': row.xpath('td//@href')[0],
                    'ID': str(row.xpath('td//@class')[4]).replace('pid-', '').replace('-last', '')
                })
            else:
                result.append({
                    'Name': data[1],
                    'Full Name': row.xpath('td//@title')[1],
                    'Last': float(data[2].replace(',', '')),
                    'High': float(data[3].replace(',', '')),
                    'Low': float(data[4].replace(',', '')),
                    'Change': float(data[5].replace(',', '').replace('+-', '+')),
                    'Change %': float(data[6].replace(',', '').replace('%', '').replace('+-', '+')),
                    'Volume': int(data[7].replace('.','').replace('K', '0').replace('M', '0000')),
                    'Date': today + ' ' + data[8] if ':' in data[8] else str(to_datetime(data[8] + '/' + str(current_date.year))),
                })
        return result

    def get_company(self, name: str) -> dict:
        return self.get_equity(self.main_url + self.companies_id[name]['url'])

    def get_equity(self, url: str) -> dict:
        response = self.get(url)
        if response.status_code != 200:
            return None

        root = html.fromstring(response.text)
        last_price = float(root.xpath('//span[@data-test="instrument-price-last"]')[0].text.replace(',',''))
        open_price = float(root.xpath('//dd[@data-test="open"]//text()')[0].replace(',',''))
        min_price = float(root.xpath('//dd[@data-test="dailyRange"]//text()')[0].replace(',',''))
        max_price = float(root.xpath('//dd[@data-test="dailyRange"]//text()')[2].replace(',',''))
        change_price = None
        try:
            change_pirce = float((root.xpath('//span[@data-test="instrument-price-change"]//text()')[0] +\
                                root.xpath('//span[@data-test="instrument-price-change"]//text()')[1]).replace(',',''))
        except:
            change_pirce = float((root.xpath('//span[@data-test="instrument-price-change"]//text()')[0]).replace(',',''))
        change_percent = float((root.xpath('//span[@data-test="instrument-price-change-percent"]//text()')[1] +\
                        root.xpath('//span[@data-test="instrument-price-change-percent"]//text()')[2]).replace(',','').replace(')', '').replace('%', ''))
        volume = None
        try:
            volume = int(root.xpath('//dd[@data-test="volume"]//text()')[0].replace(',',''))
        except:
            volume = 0
        currency = root.xpath('//span[@class="instrument-metadata_text__2iS5i font-bold"]//text()')[0]
        date = datetime.fromisoformat(root.xpath('//time//@datetime')[0].replace('Z', ''))

        return {
            'Last': last_price,
            'Open': open_price,
            'Low': min_price,
            'High': max_price,
            'Change': change_pirce,
            'Change %': change_percent,
            'Volume': volume,
            'Currency': currency,
            'Date': date.strftime("%m/%d/%Y %H:%M:%S")
        }

    def get_historical(self, name: str, start: str = None, end: str = None) -> list:
        equity = None
        if name in self.companies_id:
            equity = self.companies_id[name]
        elif name in self.indexes_id:
            equity = self.indexes_id[name]
        else:
            print("No equity like that")
            return None

        url = self.main_url + "/instruments/HistoricalDataAjax"
        headers = dict()
        headers["User-Agent"] = get_random_agent()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Accept-Encoding"] = "gzip, deflate"

        if start == None:
            startDate = "1/1/1970"
        if end == None:
            current_date = datetime.now()
            endDate = f"{current_date.day}/{current_date.month}/{current_date.year}"

        data = f"curr_id={equity['ID']}&st_date={startDate}&end_date={endDate}&sort_col=date&sort_ord=DESC&action=historical_data&header"
        response = self.post(url, headers=headers, data=data)

        if response.status_code != 200:
            return None

        root = html.fromstring(response.text)
        result = []
        for row in root.xpath('//table//tbody//tr'):
            data = row.xpath('td//text()')
            try:
                result.append({
                    'Date': str(to_datetime(data[0])),
                    'Close': float(data[1].replace(',', '')),
                    'Open': float(data[2].replace(',', '')),
                    'High': float(data[3].replace(',', '')),
                    'Low': float(data[4].replace(',', '')),
                    'Volume': int(data[5].replace('.','').replace('K', '0').replace('M', '0000').replace('-', '0')),
                })
            except:
                continue
        result.pop()
        return result

    def search(self, keyword: str) -> list:
        url = self.main_url + '/search/?q=' + keyword.replace('&', '%26')
        response = self.get(url)
        root = html.fromstring(response.text)
        results = root.xpath('//div[@class="js-inner-all-results-quotes-wrapper newResultsContainer quatesTable"]//a//@href')
        desc = root.xpath('//div[@class="js-inner-all-results-quotes-wrapper newResultsContainer quatesTable"]//a//span//text()')
        retval = list()
        for i in range(len(results)):
            retval.append([results[i], desc[i*3 + 1], desc[i*3 + 2]])
        return retval

scr = InvestingScraper()
print(scr.get_index_companies('MNSE 10'))