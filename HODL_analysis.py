import requests
import json
from datetime import date
from pathlib import Path
import pandas as pd


def pricegrabber(ticker, fx, force):
    # Downloads historical prices from cryptocompare and stores locally
    # Example pricegrabber("BTC", "USD")

    # Check first is there is a local file that was updated today
    filename = 'historical_prices/'+ticker+'.json'
    path = Path(filename)

    if force:
        print("Forced updated, not checking local file - downloading")

    if not force:
        timestamp = date.fromtimestamp(path.stat().st_mtime)
        if date.today() == timestamp:
            print("Local file was updated today. No need to download.")
            with open(filename, 'r') as fh:
                data = json.loads(fh.read())
            return (data)

    # File is outdated or dne, let's grab new data
    print(f"Downloading history for {ticker} on {fx} terms")
    print("Please wait - this can take a few minutes...")

    # See https://min-api.cryptocompare.com/documentation for API details
    baseURL = "https://min-api.cryptocompare.com/data/histoday?fsym="+ticker +\
        "&tsym="+fx+"&allData=true"
    print(f" URL = {baseURL}")

    request = requests.get(baseURL, timeout=2)
    data = request.json()

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    print(f"Done with {filename}")

    print("Success on downloading historical prices. Data saved locally")
    return (data)


price_data = pricegrabber("BTC", "USD", False)
df = pd.DataFrame.from_dict(price_data["Data"])
df['time'] = pd.to_datetime(df['time'], unit='s')
print(df)

initial_time = min(df['time'])
final_time = df['time'].max()
