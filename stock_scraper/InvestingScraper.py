import requests_html
from requests.structures import CaseInsensitiveDict
import requests
from lxml import html
from utils import get_random_agent
import datetime 

class InvestingScraper:
    def __init__(self):
        self.equities_url = 'https://investing.com/equities/'
        self.filter_url = 'https://investing.com/equities/stocksFilter?noconstruct=1&smlID=0&sid=&tabletype=price&index_id='
        self.headers = {
            'User-Agent': get_random_agent()
        }

    def parse_indexes(self):
        session = requests_html.HTMLSession()
        response = session.get(self.equities_url, headers = self.headers)
        names = response.html.xpath('//select[@class="selectBox"]//option//text()')
        IDs = response.html.xpath('//select[@class="selectBox"]//option//@id')
        return dict(zip(names, IDs))

    def parse_index(self, indexName = None, indexID = None):
        if indexName == None and indexID == None:
            return None
        elif indexID == None:
            indexID = self.parse_indexes()[indexName]

        session = requests_html.HTMLSession()
        response = session.get(self.filter_url + indexID, headers = self.headers)
        root = html.fromstring(response.content)
        result = []

        for row in root.xpath('//table//tbody//tr'):
            data = row.xpath('td//text()')
            result.append({
                'Name': data[1],
                'Full Name': row.xpath('td//@title')[1],
                'URL': row.xpath('td//@href')[0],
                'Last': data[2],
                'High': data[3],
                'Low': data[4],
                'Change': data[5],
                'Change%': data[6],
                'Vol.': data[7],
                'Date': data[8],
                'pageID': str(row.xpath('td//@class')[4]).replace('pid-', '').replace('-last', '')
            })
        return result

    def parse_company(self, companyName, companyURL = None, companyIndex = None):
        if companyName != None and companyURL == None and companyIndex == None:
            for indexName, indexID in self.parse_indexes().items():
                companies = self.parse_index(indexID = indexID)
                for company in companies:
                    if company['Name'] == companyName:
                        return company
        if companyName != None and companyURL == None and companyIndex != None:
            companies = self.parse_index(indexName = companyIndex)
            for company in companies:
                if company['Name'] == companyName:
                    return company

    def parse_historial_data(self, companyName, companyIndex = None, startDate = None, endDate = None):

        company = self.parse_company(companyName, companyIndex = companyIndex)

        url = "https://www.investing.com/instruments/HistoricalDataAjax"
        headers = CaseInsensitiveDict()
        headers["User-Agent"] = get_random_agent()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["Accept-Encoding"] = "gzip, deflate"

        if startDate == None:
            startDate = "1/1/1970"
        if endDate == None:
            current_date = datetime.datetime.now()
            endDate = f"{current_date.day}/{current_date.month}/{current_date.year}"

        data = f"curr_id={company['pageID']}&st_date={startDate}&end_date={endDate}&sort_col=date&sort_ord=DESC&action=historical_data&header"
        response = requests.post(url, headers=headers, data=data)
        print(data)
        if response.status_code != 200:
            return 404
        root = html.fromstring(response.text)

        result = []
        try:
            for row in root.xpath('//table//tbody//tr'):
                data = row.xpath('td//text()')
                result.append({
                    'Date': data[0],
                    'Close': data[1],
                    'Open': data[2],
                    'High': data[3],
                    'Low': data[4],
                    'Vol': data[5],
                    'Change': data[6]
                })
            result.pop()
        except:
            print("An error wihle parsing occured")
            return 500
        return result

scr = InvestingScraper()
scr.parse_historial_data("Allegro", companyIndex="WIG30")