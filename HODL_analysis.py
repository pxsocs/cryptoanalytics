import requests
import json


def pricegrabber(ticker, fx):
    # Downloads historical prices from cryptocompare and stores locally
    # Example pricegrabber("BTC", "USD")
    print(f"Downloading history for {ticker} on {fx} terms")
    print("Please wait - this can take a few minutes...")
    baseURL = "https://min-api.cryptocompare.com/data/histoday?fsym="+ticker +\
        "&tsym="+fx
    print(f" URL = {baseURL}")

    request = requests.get(baseURL, timeout=2)
    data = request.json()

    filename = 'historical_prices/'+ticker+'.json'

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

    print(f"Done with {filename}")

    return (data)


test = pricegrabber("BTC", "USD")
print(test)
