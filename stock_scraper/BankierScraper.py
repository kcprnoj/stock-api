from .Scraper import Scraper
from lxml import html
from datetime import datetime, timedelta
from json import loads

class BankierScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.main_url = 'https://www.bankier.pl'
        self.companies_url = list()
        self.update_blacklist()
        self.update_indexes()
        self.update_companies()

    def update_companies(self, force: bool = False) -> None:
        for company in self.get_index_companies(''):
            self.companies.append(company['Name'])

    def update_indexes(self) -> None:
        response = self.get(self.main_url + '/gielda/notowania/akcje')
        if response.status_code != 200:
            return None
        response = html.fromstring(response.text)
        self.indexes = response.xpath('//select[@name="index"]//option//text()')[1:]

    def get_index(self, index: str) -> dict:
        return self.get_equity(index)

    def get_index_companies(self, index: str) -> list:
        response = self.get(self.main_url + '/gielda/notowania/akcje?index=' + index)
        if response.status_code != 200:
            return None

        response = html.fromstring(response.text)
        result = list()
        for row in response.xpath('//table//tbody//tr'):
            try:
                strdate = row[9].xpath('@data-sort-value')[0]
            except:
                continue
            date = datetime.strptime(strdate, "%Y-%m-%d %H:%M") - timedelta(hours=1)
            result.append({
                'Name': row[0][0].text,
                'Full Name': row[0][0].xpath('@title')[0],
                'Last': float(row[1].text.replace(',','.').replace(u'\xa0', u'')),
                'High': float(row[7].text.replace(',','.').replace(u'\xa0', u'')),
                'Low': float(row[8].text.replace(',','.').replace(u'\xa0', u'')),
                'Change.': round(float(row[2].text.replace(',', '.'))),
                'Change %': round(float(row[3].text.replace(',', '.').replace('%', ''))),
                'Volume': int(float(row[5].text.replace(',','.').replace(u'\xa0', u''))/float(row[1].text.replace(',','.').replace(u'\xa0', u''))),
                'Date': date.strftime("%d/%m/%Y %H:%M:%S")
            })
        return result

    def get_company(self, name: str) -> dict:
        return self.get_equity(name)

    def get_equity(self, name: str) -> dict:
        url = self.main_url + '/inwestowanie/profile/quote.html?symbol=' + name
        response = self.get(url)
        if response.status_code != 200:
            return
        root = html.fromstring(response.text)
        print(url)
        reference = float(root.xpath('//*[@id="referencePrice"]//@data-value')[0])
        date = datetime.fromtimestamp(int(root.xpath('//div[contains(@id,"last-trade")]//@data-last-epoch')[0])/1000)
        date -=  timedelta(hours=1)

        result = dict()
        result['Last'] = float(root.xpath('//div[contains(@id,"last-trade")]//@data-last')[0])
        result['Open'] = float(root.xpath('//div[contains(@id,"last-trade")]//@data-open')[0])
        result['Low'] = float(root.xpath('//div[contains(@id,"last-trade")]//@data-low')[0])
        result['High'] = float(root.xpath('//div[contains(@id,"last-trade")]//@data-high')[0])
        result['Volume'] = float(root.xpath('//div[contains(@id,"last-trade")]//@data-volume')[0])
        result['Change'] = round(result['Last'] - result['Open'], 2)
        result['Change %'] = round((result['Last'] - reference)/reference * 100, 2)
        result['Currency'] = 'PLN'
        result['Date'] = date.strftime("%d/%m/%Y %H:%M:%S")
        return result


    def get_historical(self, name: str, start: str = None, end: str = None) -> list:
        url = self.main_url + f'/new-charts/get-data?&symbol={name}&intraday=false&type=candlestick'

        date_to = 0
        date_from = 0

        if start == None and end == None:
            url += '&max_period=true'

        if start != None:
            date_from = int(datetime.strptime(start, '%d/%m/%Y').timestamp()*1000)

        if end != None:
            date_to = int(datetime.strptime(end, '%d/%m/%Y').timestamp()*1000)
        else:
            current_date = datetime.now()
            current_date = f"{current_date.day}/{current_date.month}/{current_date.year}"
            date_to = int(datetime.strptime(current_date, '%d/%m/%Y').timestamp()*1000)
        
        url += f'&date_from={date_from}&date_to={date_to}'
        return self.get_data(url)

    def get_last(self, name: str, type: str = None) -> list:
        if type == None:
            type = 'ohlc'
        url = self.main_url + f'/new-charts/get-data?symbol={name}&intraday=true&type={type}'
        return self.get_data(url, type = type)

    def get_data(self, url: str, type: str = None) -> list:
        response = self.get(url)
        if response.status_code != 200:
            return None
        data = loads(response.text)

        result = []
        for i in range(len(data['main'])):
            date = datetime.fromtimestamp(data['main'][i][0]/1000)
            date -=  timedelta(hours=1)
            volume = 0
            try:
                volume = data['volume'][i][1]
            except:
                pass
            if type == None or type == 'ohlc':
                result.append({
                    'Date' : date.strftime("%d/%m/%Y %H:%M:%S"),
                    'Close' : data['main'][i][4],
                    'Open' : data['main'][i][1],
                    'High' : data['main'][i][2],
                    'Low' : data['main'][i][3],
                    'Volume' : volume
                })
            elif type == 'area':
                result.append({
                    'Date' : date.strftime("%d/%m/%Y %H:%M:%S"),
                    'Last' : data['main'][i][1],
                    'Volume' : volume
                })
        return result