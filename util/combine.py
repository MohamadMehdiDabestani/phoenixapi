from ta.volume import VolumeWeightedAveragePrice
def ema(coin , length):
    return coin.ta.ema(length=length)

def sma(coin , length):
    return coin.ta.sma(length=length)
def vwap(coin , length):
    return VolumeWeightedAveragePrice(high=coin['high'], low=coin['low'], close=coin["close"], volume=coin['volume'], window=length, fillna=True).volume_weighted_average_price()
mapper = {"EMA":ema,"sma":sma , 'vwap' : vwap}
def get(ind , coin , length):
    return mapper[ind](coin , length)