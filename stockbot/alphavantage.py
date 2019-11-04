import urllib.request, json

#Makes use of the alphavantage api to return data about a specific stock

def jsonReturn(keyword):
    keyword = spaceCheck(keyword)
    url = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=" + keyword + "&apikey=VUUG2MG0ELJZOOGF"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        results = data["bestMatches"]
        return jsonStrip(results)

def jsonStrip(results):
    acronyms = []
    for i in range (len(results)):
        acronyms.append(results[i]["1. symbol"])
    return acronyms

def spaceCheck(keyword):
    if (' ' in keyword):
        keyword = keyword.replace(' ','+')
    return keyword

def time_series_weekly(stock):
    """Returns weekly time series for a stock"""
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=" + stock + "&apikey=VUUG2MG0ELJZOOGF"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        results = data["Weekly Time Series"]
        return results

print(time_series_weekly("MSFT"))
        
    

#financialmodellingprep has an api that does something similar but just returns a long list so would take ages

#print(jsonReturn("apple"))
