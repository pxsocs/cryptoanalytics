import requests
import json
from datetime import date, datetime, timedelta
from pathlib import Path
import pandas as pd
from flask import Flask, render_template, url_for, request
import logging

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

    # File is outdated or DNE, let's grab new data
    print(f"Downloading history for {ticker} on {fx} terms")
    print("Please wait - this can take a few minutes...")

    # See https://min-api.cryptocompare.com/documentation for API details
    baseURL = "https://min-api.cryptocompare.com/data/histoday?fsym="+ticker +\
        "&tsym="+fx+"&allData=true"
    print(f" URL = {baseURL}")

    time_frame = 0
    #  For some reason, the CryptoCompare API retuns only 30 days of data
    #  from time to time. Not sure why. This forces the download until done.

    while time_frame < 3000000:
        request = requests.get(baseURL)
        data = request.json()
        time_frame = data['TimeFrom'] - data['TimeTo']

    if (data['Response'] == "Error"):
        print("Error Downloading Data - something went wrong")
        return("error")

    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
    print(f"Done with {filename}")

    print("Success. Downloaded historical prices. Data saved locally")
    return (data)


def p2f(x):
    # Convert a percentage string into float
    return float(x.strip('%'))/100


def create_stats(ticker, fx, force, frequency,
                 period_exclude, start_date, end_date):
    # Store the data in a dictionary for later use in html
    stats = {}

    # Download the prices
    price_data = pricegrabber(ticker, fx, force)

    if price_data == "error":
        stats['status'] = "error"
        stats = json.dumps(stats)

        return (stats)

    stats['ticker'] = ticker
    stats['fx'] = fx
    stats['frequency'] = frequency
    stats['period_exclude'] = period_exclude
    stats['start_date'] = start_date
    stats['end_date'] = end_date

    # Convert data to Panda's Dataframe, include relevant columns,
    # retrieve data
    df = pd.DataFrame.from_dict(price_data["Data"])
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    df['grouped_pct'] = df['close'].pct_change(frequency)
    df['return_day_pct'] = df['close'].pct_change(1)
    df['End Date'] = df.index
    df['Start Date'] = df.index.shift(frequency*(-1), freq="1D")
    df['Start Price'] = df['close'].shift(frequency, freq="1D")

    # Save the initial and end date of available data downloaded
    stats['set_final_time'] = df.index.max()
    stats['set_initial_time'] = df.index.min()

    # Filter the dataframe to only include selected dates
    df = df[(df.index >= start_date) & (df.index <= end_date)]

    df_nlargest_tmp = df.nlargest(period_exclude, 'grouped_pct')

    # When setting the nlargest, we need to remove the sets that have
    # overlapping days and only keep the largest one.
    # For that we can iterate until the nlargest have the right number
    # of period_exclude but with no overlapping dates.
    # stats['nlargest'] = df.nlargest(period_exclude, 'grouped_pct')

    non_duplicate_count = 0
    include_non_dup = 1

    while non_duplicate_count != period_exclude:
        # First check if any of the dates overlap and store on duplicate column
        counter = 0
        df_nlargest_tmp['duplicate'] = False
        for index, row in df_nlargest_tmp.iterrows():
            if counter == 0:  # skip the first row
                counter += 1
                continue

            for check in range(0, counter):
                lower_bound = df_nlargest_tmp.index[check] - timedelta(
                    days=frequency)
                upper_bound = df_nlargest_tmp.index[check] + timedelta(
                    days=frequency)
                if index > lower_bound and index < upper_bound:
                    df_nlargest_tmp.set_value(index, 'duplicate', True)
            counter += 1

        non_duplicate_count = (df_nlargest_tmp[df_nlargest_tmp[
            "duplicate"] == False].count()[0])

        # Set a limit on number of tries - then exit
        max_tries = 100
        if (include_non_dup >= max_tries):
            print("Error: Could not achieve the requested number of blocks")
            # print(df_nlargest_tmp)
            break

        if non_duplicate_count != period_exclude:
            df_nlargest_tmp = df.nlargest(
                period_exclude + include_non_dup, 'grouped_pct')
            include_non_dup += 1

    # Only keep the unique periods

    df_nlargest_tmp = df_nlargest_tmp[df_nlargest_tmp.duplicate == False]

    stats['nlargest'] = df_nlargest_tmp

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
    stats['exclude_nlargest_tr'] = ((1 + stats['period_tr']) / (
        1 + stats['nlargest_tr'])) - 1

    stats['exclude_nsmallest_tr'] = (1 + stats['period_tr']) / (
        1 + stats['nsmallest_tr']) - 1

    stats['mean_daily_return_period'] = df['return_day_pct'].mean()
    stats['mean_nperiod_return'] = df['grouped_pct'].mean()

    # Formatting the results to return a JSON & HTML Table
    stats['start_date'] = stats['start_date'].strftime('%m/%d/%Y')
    stats['end_date'] = stats['end_date'].strftime('%m/%d/%Y')
    stats['set_initial_time'] = stats['set_initial_time'].strftime('%m/%d/%Y')
    stats['set_final_time'] = stats['set_final_time'].strftime('%m/%d/%Y')

    nlargest_df = df_nlargest_tmp

    nlargest_df['grouped_pct'] = nlargest_df['grouped_pct'] * 100
    nlargest_df['grouped_pct'] = nlargest_df['grouped_pct'].apply(
        "{:,.2f}%".format)
    nlargest_df['close'] = nlargest_df['close'].apply("{:,.4f}".format)

    nlargest_df['Start Price'] = nlargest_df[
        'Start Price'].apply("{:,.4f}".format)

    nlargest_df = nlargest_df.drop(
        columns=['low', 'open', 'high', 'volumeto', 'volumefrom',
                 'return_day_pct'])

    nlargest_df.rename(columns={'close': 'Final Price'}, inplace=True)
    nlargest_df.rename(columns={'grouped_pct': 'Return on period'},
                       inplace=True)

    nlargest_df = nlargest_df[['Start Date', 'End Date',
                               'Start Price', 'Final Price',
                               'Return on period']]

    stats['nlargest'] = nlargest_df.to_html(
        classes=["text-right small table table-striped"], border=0,
        index=False)
    # stats['nlargest'] = stats['nlargest'].to_json()
    stats['nsmallest'] = stats['nsmallest'].to_json()

    # Include Histogram Data in JSON
    df['return_day_pct'] = df['return_day_pct'] * 100
    stats['histogram'] = df['return_day_pct'].values.tolist()
    stats['histogram_dates'] = df.index.values.tolist()

    stats['bar_chart_returns'] = {}
    stats['bar_chart_returns']['categories'] = list(range(1, period_exclude+1))
    df_nlargest_tmp['grouped_pct'] = df_nlargest_tmp['grouped_pct'].str.rstrip(
        '%').astype('float')
    stats['bar_chart_returns']['data'] = df_nlargest_tmp[
        'grouped_pct'].values.tolist()

    stats['status'] = "success"
    stats = json.dumps(stats)

    return (stats)


# Start main route at /
# ---------------------
@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')


@app.route("/stats_json", methods=['GET'])
def stats_json():

    # Read inputs
    force = request.args.get('force')
    ticker = request.args.get('ticker')
    fx = request.args.get('fx')
    frequency = int(request.args.get('frequency'))
    period_exclude = int(request.args.get('period_exclude'))
    start_date = request.args.get('start_date')
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = request.args.get('end_date')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    stats = create_stats(
        ticker, fx, force, frequency, period_exclude, start_date, end_date)

    return(stats)


# Init Log File
logging.basicConfig(filename='debug_hodl.log', level=logging.INFO)
logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# Start Flask Server
if __name__ == '__main__':
    app.run(debug=True)
