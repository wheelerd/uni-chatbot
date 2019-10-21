import urllib.request, json, alphavantage
import matplotlib.pyplot as plt

def get_stock_json(urlGiven):
    """Returns json data from api"""
    url = urlGiven
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        return data

def json_return_gainer():
    """Returns the data of the 10 most gainer companies daily"""
    url = "https://financialmodelingprep.com/api/v3/stock/gainers"
    data = get_stock_json(url)
    return data
    

def gainer_json_to_list():
    """Turns json into a list of dictionaries, each containing informatin about a stock"""
    data = json_return_gainer()
    stockList = data["mostGainerStock"]
    return stockList

def most_gainer_companies(dataRequired):
    """Returns specified data about the 10 gainer stocks"""
    stockList = gainer_json_to_list()
    dataRequired = dataRequired.split(' ')
    for i in range( len(stockList)):
        for x in range( len(dataRequired)):
            print(stockList[i][dataRequired[x]])

def stock_historical_price_data(company, days):
    """Shows a graph of a specific stocks closes for the specified number of days prior to the current date"""
    acronyms = alphavantage.jsonReturn(company)
    stock = acronyms[0]
    url = "https://financialmodelingprep.com/api/v3/historical-price-full/" + stock + "?serietype=line"
    data = get_stock_json(url)
    allDays = data["historical"]
    requestedDays = allDays[:days]
    closes = []
    dates = []
    for i in range( len(requestedDays)):
        closes.append(requestedDays[i]["close"])
        date = requestedDays[i]["date"]
        dates.append(date[5:])
    plt.plot(dates, closes)
    plt.show()
    
    
    

most_gainer_companies("companyName ticker changes price")

stock_historical_price_data("unilever", 14)