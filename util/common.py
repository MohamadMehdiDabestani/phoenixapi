import pytz
import re
from datetime import datetime
import pandas as pd
import pandas_ta as pdt
import ccxt
result = {}
limit = {}

def _filter(data , prop , val):
    return list(filter(lambda d: d[prop] == val, data))


def updateResult(propName , value):
    global result
    result[propName] = {}
    result[propName] = value

def getCross(obj , name):
    return obj["cross"][name]

def precentageDifferent(price , source):
    arr = [price , source]
    return (((max(arr)-min(arr))/max(arr)) * 100)

def getBreak(obj , name):
    return obj["breake"][name]

def calculateLimit(df):
    global limit
    delta = pd.Timedelta(f"{limit['day']}days {limit['hours']}hours {limit['minutes']}min")
    if str(delta) == "0 days 00:00:00" or limit["type"] == "default":
        result = df.to_dict(orient='records')
        return result[-1]["time"] if len(result) > 0 else {}
    filteringDelta =  df[df['time'] >= pd.Timestamp.today() - delta]
    filteringDelta = filteringDelta.to_dict(orient='records')
    return filteringDelta[-1]["time"] if len(filteringDelta) > 0 else {}
    
def cross(dates ,data , _above , offset=0):
    crosses = pdt.tsignals(data, above=_above, offset=offset, asbool=True)
    crosses = crosses.loc[crosses['TS_Entries'] == True]
    if(len(crosses.index) == 0):
        return {}
    crosses['time'] = dates
    crosses.set_index('time',append = True)
    dicts = crosses.to_dict(orient='records')
    return dicts[-1]["time"] if len(dicts) > 0 else {}

def _break(dates ,value, state ,_above,offset=0):
    breaking = pdt.xsignals(value , state[0],state[1], offset=offset,above=_above , long=False, asbool=True)
    breaking = breaking.loc[breaking['TS_Entries'] == True]
    if(len(breaking.index) == 0):
        return {}
    breaking['time'] = dates
    breaking.set_index('time',append = True)
    return calculateLimit(breaking)

def initialize(coinName , timeFrame , _limit , _exchange):
    global result
    global limit
    result.clear()
    result["coinName"] = coinName
    result["timeFrame"] = timeFrame
    result["exchange"] = _exchange
    limit = _limit

def checkAdx(adxValue , signal):
    return adxValue > 25 & signal

def stopLossByAtr(row):
    return row['open'] + row["ATRr_14"]  if row['short'] == True else row['open'] - row["ATRr_14"]

def retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
    num_retries = 0
    try:
        num_retries += 1
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
        return ohlcv
    except Exception:
        if num_retries > max_retries:
            # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')
            raise


def scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit):
    timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
    timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
    timedelta = limit * timeframe_duration_in_ms
    now = exchange.milliseconds()
    all_ohlcv = []
    fetch_since = since
    while fetch_since < now:
        ohlcv = retry_fetch_ohlcv(
            exchange, max_retries, symbol, timeframe, fetch_since, limit)
        fetch_since = (
            ohlcv[-1][0] + 1) if len(ohlcv) else (fetch_since + timedelta)
        all_ohlcv = all_ohlcv + ohlcv
    return exchange.filter_by_since_limit(all_ohlcv, since, None, key=0)


def get_asset(exchange_id, max_retries, symbol, timeframe , congfigExchange = {'enableRateLimit': True}):
    
    startDateTZ = datetime.now(tz=pytz.timezone(
        "Atlantic/Reykjavik"))
    chartTimeframe = timeframe
    startDate = startDateTZ.strftime("%Y-%m-%d %H:%M:%S")
    regex = re.compile("^(?P<numbers>\d*)(?P<letters>\w*)$")
    def splitingNumbersAndLetter(entry):
        (numbers, letters) = regex.search(entry).groups()
        return (numbers or None, letters or None)
    t = splitingNumbersAndLetter(chartTimeframe)
    print(list(t))
    if(list(t)[1].lower() == 'm'):
        chartTimeframe = f"{list(t)[0]}t"
    dates = pd.date_range(end=startDate, periods=550, freq=chartTimeframe.upper()).to_frame(name='time')
    

    dates = dates.loc[dates['time'] < startDate]
    date = dates.to_dict(orient='records')
    date = date[0]
    # instantiate the exchange by id
    exchange = getattr(ccxt, exchange_id)(congfigExchange)

    # convert since from string to milliseconds integer if needed
    since = exchange.parse8601(date['time'].strftime('%Y-%m-%d %X'))

    ohlcv = scrape_ohlcv(exchange, max_retries, symbol,
                         timeframe, since, 550)

    df = pd.DataFrame(
        ohlcv, columns=["time", "open", "high", "low", "close", "volume"])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

def getJsonCoin(exchange_id, max_retries, symbol, timeframe , congfigExchange = {'enableRateLimit': True}):
    startDateTZ = datetime.now(tz=pytz.timezone(
        "Atlantic/Reykjavik"))
    chartTimeframe = timeframe
    startDate = startDateTZ.strftime("%Y-%m-%d %H:%M:%S")
    regex = re.compile("^(?P<numbers>\d*)(?P<letters>\w*)$")
    def splitingNumbersAndLetter(entry):
        (numbers, letters) = regex.search(entry).groups()
        return (numbers or None, letters or None)
    t = splitingNumbersAndLetter(chartTimeframe)
    print(list(t))
    if(list(t)[1].lower() == 'm'):
        chartTimeframe = f"{list(t)[0]}t"
    dates = pd.date_range(end=startDate, periods=550, freq=chartTimeframe.upper()).to_frame(name='time')
    

    dates = dates.loc[dates['time'] < startDate]
    date = dates.to_dict(orient='records')
    date = date[0]
    # instantiate the exchange by id
    exchange = getattr(ccxt, exchange_id)(congfigExchange)

    # convert since from string to milliseconds integer if needed
    since = exchange.parse8601(date['time'].strftime('%Y-%m-%d %X'))

    ohlcv = scrape_ohlcv(exchange, max_retries, symbol,
                         timeframe, since, 550)
    return ohlcv