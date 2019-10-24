import urllib.request, json, alphavantage
import matplotlib.pyplot as plt

def get_stock_json(urlGiven):
    """Returns json data from api"""
    url = urlGiven
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        return data

def market_open_check():
    """Checks if the stock markets are currently open"""
    url = "https://financialmodelingprep.com/api/v3/is-the-market-open"
    data = get_stock_json(url)
    marketState = data["isTheStockMarketOpen"]
    if marketState:
        print("The market is open")
    else:
        print("The market is closed")

def market_holidays():
    """Shows the market holidays of the previous, current and next year"""
    url = "https://financialmodelingprep.com/api/v3/is-the-market-open"
    data = get_stock_json(url)
    allYearData = data["stockMarketHolidays"]
    for i in range( len(allYearData)):
        keys = list((allYearData[i]).keys())
        for x in range( len(keys)):
            print (keys[x] + " : " + str(allYearData[i][keys[x]]))
    

def most_gainer_companies(dataRequired):
    """Returns specified data about the 10 most gainer stocks"""
    url = "https://financialmodelingprep.com/api/v3/stock/gainers"
    data = get_stock_json(url)
    stockList = data["mostGainerStock"]
    dataRequired = dataRequired.split(' ')
    for i in range( len(stockList)):
        for x in range( len(dataRequired)):
            print(stockList[i][dataRequired[x]])

def most_active_companies(dataRequired):
    """Returns specified data about the 10 most active stocks"""
    url = "https://financialmodelingprep.com/api/v3/stock/actives"
    data = get_stock_json(url)
    stockList = data["mostActiveStock"]
    dataRequired = dataRequired.split(' ')
    for i in range( len(stockList)):
        for x in range( len(dataRequired)):
            print(stockList[i][dataRequired[x]])

def most_loser_companies(dataRequired):
    """Returns specified data about the 10 most loser stocks"""
    url = "https://financialmodelingprep.com/api/v3/stock/losers"
    data = get_stock_json(url)
    stockList = data["mostLoserStock"]
    dataRequired = dataRequired.split(' ')
    for i in range( len(stockList)):
        for x in range( len(dataRequired)):
            print(stockList[i][dataRequired[x]])

def major_indexes(dataRequired):
    """Returns specified data about the major indexes"""
    url = "https://financialmodelingprep.com/api/v3/majors-indexes"
    data = get_stock_json(url)
    stockList = data["majorIndexesList"]
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

def stock_sectors():
    """Shows the change in percentage of the 11 stock market sectors"""
    url = "https://financialmodelingprep.com/api/v3/stock/sectors-performance"
    data = get_stock_json(url)
    sectorInfo = data["sectorPerformance"]
    for i in range( len(sectorInfo)):
        print(sectorInfo[i]["sector"])
        print(sectorInfo[i]["changesPercentage"])

def stock_profile(stock):
    """Returns the profile of a stock"""
    url = "https://financialmodelingprep.com/api/v3/company/profile/" + stock
    data = get_stock_json(url)
    profile = data["profile"]
    profileTypes = ["price", "beta", "volAvg", "mktCap", "lastDiv", "range", "changes", "changesPercentage", "companyName", "exchange", "industry", "website", "description", "ceo", "sector"]
    for i in range( len(profileTypes)):
        print(profileTypes[i] + " : " + str(profile[profileTypes[i]]))

def stock_price(stock):
    """Returns the price of a stock in realtime"""
    url = "https://financialmodelingprep.com/api/v3/stock/real-time-price/" + stock
    data = get_stock_json(url)
    price = data["price"]
    print(price)

def annual_income_statements(stock, year):
    """Returns annual income statements of a stock for a specified year"""
    url = "https://financialmodelingprep.com/api/v3/financials/income-statement/" + stock
    data = get_stock_json(url)
    incomeSheets = data["financials"]
    for i in range( len(incomeSheets)):
        date = incomeSheets[i]["date"]
        dateYear = date[:4]
        if (int(dateYear) == year):
            keys = list((incomeSheets[i]).keys())
            for x in range( len(keys)):
                print (keys[x] + " : " + str(incomeSheets[i][keys[x]]))

    

#stock_price("MSFT")
    
#stock_profile("AAPL")

#most_gainer_companies("companyName ticker changes price")

#most_active_companies("companyName ticker changes price")

#most_loser_companies("companyName ticker changes price")

#major_indexes("indexName ticker changes price")

#stock_historical_price_data("unilever", 14)

#stock_sectors()

#market_open_check()

#market_holidays()

#annual_income_statements("AAPL", 2016)
