import urllib.request, json

def convert(currency1,currency2):
    url = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=" + currency1 + "&to_currency=" + currency2 + "&apikey=VUUG2MG0ELJZOOGF"
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
        results = data["Realtime Currency Exchange Rate"]
    return results

def getCurrencyData(results, key):
    for k in results:
        if k[0] == str(key):
            return results[k]
