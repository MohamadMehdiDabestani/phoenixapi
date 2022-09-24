import numpy as np
import pandas as pd
from .common import updateResult , result , precentageDifferent
from scipy.stats import linregress
def detectionBaseCandle(row):
    realbody = abs(row.open - row.close)
    candle_range = row.high - row.low
    if(realbody >= 0.27 * candle_range):
        return False
    # if(row.close > row.open):
    return True if candle_range > realbody else False
def detectionBaseArea(row , df):
    if(len(df) <= row.name + 5):
        return pd.Series([False, False])
    x_l = np.array(np.linspace(
        df.iloc[row.name:row.name + 4]['close'].min(), df.iloc[row.name:row.name + 4]['close'].max(), 5))
    y_l = np.array(df.iloc[row.name:row.name + 5]['close'])
    if(len(x_l) % 5 != 0 or len(y_l) % 5 != 0):
        return pd.Series([False, False])
    reg_l = linregress(x_l, y_l)
    if reg_l.slope < -0.9 and df.iloc[row.name + 1].close < df.iloc[row.name + 1].open:
        return pd.Series([True, "sup"])
    elif reg_l.slope > 0.9 and df.iloc[row.name + 1].close > df.iloc[row.name + 1].open:
        return pd.Series([True, "res"])
    return pd.Series([False, False])

def detectionEnableBase(row , df):
    if(len(df) <= row.name + 5):
        return False
    if(row.baseAreaType == 'sup'):
        sup_range = df.iloc[row.name + 5:][(df['low'] > row.low) | (df['close'] > row.low)] # fix the bug
        if(sup_range.empty):
            return True
    elif(row.baseAreaType == 'res'):
        res_range = df.iloc[row.name + 5:][(df['high'] < row.low) | (df['close'] < row.low)] # fix the bug
        if(res_range.empty):
            return True
    return False

def base(coin , indicator , combine):
    print("==== base called")

    coin['baseCandle'] = coin.apply(lambda row: detectionBaseCandle(row), axis=1)
    coin['baseArea'] = False
    coin['baseAreaType'] = False
    coin['baseAreaEnable'] = False
    coin[['baseArea' , 'baseAreaType']] = coin.loc[coin['baseCandle'] == True].apply(lambda row: detectionBaseArea(row , coin), axis=1)
    coin['baseAreaEnable'] = coin.loc[coin['baseArea'] == True].apply(lambda row: detectionEnableBase(row , coin), axis=1)
    if(coin.loc[coin['baseAreaEnable'] == True].empty):
        updateResult("base" , False)
    else:
        coin['diff'] = coin.loc[coin['baseAreaEnable'] == True].apply(lambda row:  precentageDifferent(coin.iloc[-1].close,row.low), axis=1)
        res_min = coin[(coin['baseAreaType'] == "sup") & (coin['diff'] == coin[coin['baseAreaType'] == "sup"]['diff'].min())]
        sup_min = coin[(coin['baseAreaType'] == "res") & (coin['diff'] == coin[coin['baseAreaType'] == "res"]['diff'].min())]
        bases = {}
        if(not sup_min.empty):
            bases["base_sup_precent"] = sup_min.iloc[0]['diff']
            bases["base_sup_range"] = [sup_min.iloc[0]['low'] , sup_min.iloc[0]['high']]
        else:
            bases["base_sup_precent"] = False
            bases["base_sup_range"] = False
        if(not res_min.empty):
            bases["base_res_precent"] = res_min.iloc[0]['diff']
            bases["base_res_range"] = [res_min.iloc[0]['low'] , res_min.iloc[0]['high']]
        else:
            bases["base_res_precent"] = False
            bases["base_res_range"] = False
        updateResult("base" , bases)