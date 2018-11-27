import requests
import json
from datetime import date, datetime
from pathlib import Path
import pandas as pd
from flask import Flask

app = Flask(__name__)


def pricegrabber(ticker, fx, force):
    # Downloads historical prices from cryptocompare and stores locally
    # Example pricegrabber("BTC", "USD")

    # Check first is there is a local file that was updated today
    filename = 'historical_prices/'+ticker+'.json'
    path = Path(filename)

    if force:
        print("Forced updated, not checking local file - downloading")

    if not force:
        try:
            timestamp = date.fromtimestamp(path.stat().st_mtime)
        except FileNotFoundError:
            timestamp = 0

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

    print("Success. Downloaded historical prices. Data saved locally")
    return (data)


def create_stats(ticker, fx, force, frequency,
                 period_exclude, start_date, end_date):
    # Store the data in a dictionary for later use in html
    stats = {}
    stats['ticker'] = ticker
    stats['fx'] = fx
    stats['frequency'] = frequency
    stats['period_exclude'] = period_exclude
    stats['start_date'] = start_date
    stats['end_date'] = end_date

    # Download the prices
    price_data = pricegrabber(ticker, fx, force)

    # Convert data to Panda's Dataframe, include relevant columns,
    # retrieve data
    df = pd.DataFrame.from_dict(price_data["Data"])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df['grouped_pct'] = df['close'].pct_change(frequency)
    df['return_day_pct'] = df['close'].pct_change(1)

    # Save the initial and end date of available data downloaded
    stats['set_final_time'] = df.index.max()
    stats['set_initial_time'] = min(df.index)

    # Filter the dataframe to only include selected dates
    df = df[(df.index >= start_date) & (df.index <= end_date)]

    stats['nlargest'] = df.nlargest(period_exclude, 'grouped_pct')
    stats['nsmallest'] = df.nsmallest(period_exclude, 'grouped_pct')

    # TR for the period
    stats['ticker_start_value'] = df.iloc[0]['close']
    stats['ticker_end_value'] = df.iloc[-1]['close']
    stats['period_tr'] = (stats['ticker_end_value'
                                ] / stats['ticker_start_value']) - 1

    # Calculate the compounded TR of nlargest
    # moves & then do the same for smallest
    nlargest_tr = 1
    for element in stats['nlargest']['grouped_pct']:
        nlargest_tr = nlargest_tr * (1+element)
    nlargest_tr = nlargest_tr - 1
    stats['nlargest_tr'] = nlargest_tr
    stats['nlargest_mean'] = stats['nlargest']['grouped_pct'].mean()

    nsmallest_tr = 1
    for element in stats['nsmallest']['grouped_pct']:
        nsmallest_tr = nsmallest_tr * (1+element)
    nsmallest_tr = nsmallest_tr-1
    stats['nsmallest_tr'] = nsmallest_tr
    stats['nsmallest_mean'] = stats['nsmallest']['grouped_pct'].mean()

    stats['nboth_tr'] = ((1+nlargest_tr)*(1+nsmallest_tr))-1
    stats['exclude_nlargest_tr'] = (1 + stats['period_tr']) * (
        1 - stats['nlargest_tr']) - 1
    stats['exclude_nsmallest_tr'] = (1 + stats['period_tr']) * (
        1 - stats['nsmallest_tr']) - 1

    stats['mean_daily_return_period'] = df['return_day_pct'].mean()
    stats['mean_nperiod_return'] = df['grouped_pct'].mean()

    return (stats)


# Start main route at /
# ---------------------
@app.route("/")
@app.route("/home")
def home():
    # Inputs
    ticker = "BTC"
    fx = "USD"
    force = False
    frequency = 3
    period_exclude = 15
    start_date = datetime(2016, 1, 1)
    end_date = datetime.today()

    stats = create_stats(
        ticker, fx, force, frequency, period_exclude, start_date, end_date)

    # Formatting the results
    stats['start_date'] = stats['start_date'].strftime('%m/%d/%Y')
    stats['end_date'] = stats['end_date'].strftime('%m/%d/%Y')
    stats['set_initial_time'] = stats['set_initial_time'].strftime('%m/%d/%Y')
    stats['set_final_time'] = stats['set_final_time'].strftime('%m/%d/%Y')

    # data['portfolio_value'] = data['portfolio_value'].apply("$ {:,.2f}".format)
    # data['NAV'] = data['NAV'].apply("{:,.2f}".format)
    # data['pchange'] = data['pchange'].apply("$ {:,.2f}".format)
    # data['navpchange'] = data['navpchange']*100
    # data['navpchange'] = data['navpchange'].apply("{:,.2f}%".format)
    #
    # data2 = data.rename(columns={
    #     'date': 'Date', 'portfolio_value': 'Portfolio Value ($)',
    #     'pchange': 'Portfolio Change ($)', 'NAV': 'NAV',
    #     'navpchange': 'NAV Change (%)'})
    #
    stats['nlargest'] = stats['nlargest'].to_json()
    stats['nsmallest'] = stats['nsmallest'].to_json()

    print(stats)

    stats_json = json.dumps(stats)
    print(stats_json)
    return(stats_json)


# Start Flask Server
if __name__ == '__main__':
    app.run(debug=True)
