import pandas as pd
import pandas_ta as pdt
from .common import checkAdx , _filter , stopLossByAtr
def supertrend(df, indicator):
    length = _filter(indicator['strategy']["parameters"] , "name" , "length")[0]["value"]
    factor = float(_filter(indicator['strategy']["parameters"] , "name" , "factor")[0]["value"])
    if(len(df.index) > max([length , factor])):
        df.ta.supertrend(multiplier=factor,length=length,append=True)
        propsSupertrend = f'_{length}_{factor}'
        def longSignal(x):
            if x[f'SUPERTd{propsSupertrend}'] > 0 and df.iloc[x.name - 1][f'SUPERTd{propsSupertrend}'] < 0:
                return True
            return False
        def shortSignal(x):
            if x[f'SUPERTd{propsSupertrend}'] < 0 and df.iloc[x.name - 1][f'SUPERTd{propsSupertrend}'] > 0:
                return True
            return False
        def stopLossSupertrend(row):
            return 0.0
        df['long'] = df.apply(lambda x : longSignal(x) , axis=1)
        df['short'] = df.apply(lambda x : shortSignal(x) , axis=1)
        if(indicator['adxFilter']):
            df.ta.adx(append=True)
            df['short'] = df.apply(lambda x : checkAdx(x['ADX_14'] , x['short']) , axis=1)
            df['long'] = df.apply(lambda x : checkAdx(x['ADX_14'] , x['long']) , axis=1)
        if(_filter(indicator['stopOptions'], "isActive" , True)[0]["name"] == 'Atr'):
            df.ta.atr(append=True)
            df['stoploss'] = df.apply(lambda x : stopLossByAtr(x) , axis=1)
        if(_filter(indicator['stopOptions'], "isActive" , True)[0]["name"] == 'supertrend'):
            df['stoploss'] = df.apply(lambda x : stopLossSupertrend(x) , axis=1)

        return df

def threeSupertrend(df, indicator):
    df.ta.supertrend(multiplier=1,length=10,append=True)
    df.ta.supertrend(multiplier=2,length=11,append=True)
    df.ta.supertrend(multiplier=3,length=12,append=True)
    slowPropsSupertrend = '_10_1'
    midPropsSupertrend = '_11_2'
    longPropsSupertrend = '_12_3'
    def longSignal(x):
        if x[f'SUPERTd{longPropsSupertrend}'] > 0 and df.iloc[x.name - 1][f'SUPERTd{longPropsSupertrend}'] < 0:
            if(x[f'SUPERTd{slowPropsSupertrend}'] > 0 and x[f'SUPERTd{midPropsSupertrend}'] > 0):
                return True
        return False
    def shortSignal(x):
        if x[f'SUPERTd{longPropsSupertrend}'] < 0 and df.iloc[x.name - 1][f'SUPERTd{longPropsSupertrend}'] > 0:
            if(x[f'SUPERTd{slowPropsSupertrend}'] < 0 and x[f'SUPERTd{midPropsSupertrend}'] < 0):
                return True
        return False
    def stopLossSupertrend(row):
        return 0.0
    df['long'] = df.apply(lambda x : longSignal(x) , axis=1)
    df['short'] = df.apply(lambda x : shortSignal(x) , axis=1)
    # if(indicator['adxFilter']):
    #     df.ta.adx(append=True)
    #     df['short'] = df.apply(lambda x : checkAdx(x['ADX_14'] , x['short']) , axis=1)
    #     df['long'] = df.apply(lambda x : checkAdx(x['ADX_14'] , x['long']) , axis=1)
    if(_filter(indicator['stopOptions'], "isActive" , True)[0]["name"] == 'Atr'):
        df.ta.atr(append=True)
        df['stoploss'] = df.apply(lambda x : stopLossByAtr(x) , axis=1)
    if(_filter(indicator['stopOptions'], "isActive" , True)[0]["name"] == 'supertrend'):
        df['stoploss'] = df.apply(lambda x : stopLossSupertrend(x) , axis=1)
    return df
def DMI_OBV(df, indicator):
    if(len(df) > 150):
        df.ta.adx(length=14 , append = True)
        obv = df.ta.obv()
        obv = obv.to_frame()
        obv.rename(columns={"OBV" : "close"} , inplace=True)
        obv.ta.sma(length=100,append = True)
        deadCrossObv = obv['SMA_100'] > obv['close']
        goldrenCrossObv = obv['SMA_100'] < obv['close']
        df['goldrenCrossObv'] = pdt.tsignals(goldrenCrossObv ,  above=True, offset=0, asbool=True)['TS_Entries']
        df['deadCrossObv'] = pdt.tsignals(deadCrossObv ,  above=True, offset=0, asbool=True)['TS_Entries']
        goldrenCross = df['DMP_14'] > df['DMN_14']
        deadCross = df['DMP_14'] < df['DMN_14']
        df['goldrenCross'] = pdt.tsignals(goldrenCross ,  above=True, offset=0, asbool=True)['TS_Entries']
        df['deadCross'] = pdt.tsignals(deadCross ,  above=True, offset=0, asbool=True)['TS_Entries']
        def calculationLong(row):
            if(row['goldrenCrossObv'] and row['DMP_14'] > row['DMN_14']):
                return True
            if(row['goldrenCross'] and obv.iloc[row.name]['close'] > obv.iloc[row.name]['SMA_100']):
                return True
            return False
        def calculationShort(row):
            if(row['deadCrossObv'] and row['DMP_14'] < row['DMN_14']):
                return True
            if(row['deadCross'] and obv.iloc[row.name]['close'] < obv.iloc[row.name]['SMA_100']):
                return True
            return False
        df['long'] = df.apply(lambda x : calculationLong(x) , axis=1)
        df['short'] = df.apply(lambda x : calculationShort(x) , axis=1)
        return df.iloc[-2]
    return None


def ema(df, indicator):
    emaLength = _filter(indicator['strategy']["parameters"] , "name" , "length")[0]["value"]
    if(len(df.index) > emaLength):
        df.ta.ema(length=emaLength, append = True)
        deadCross = df[f"EMA_{emaLength}"] > df['close']
        goldrenCross = df[f"EMA_{emaLength}"] < df['close']
        df['short'] = pdt.tsignals(deadCross, above=True, offset=0, asbool=True)['TS_Entries']
        df['long'] = pdt.tsignals(goldrenCross, above=False, offset=0, asbool=True)['TS_Entries']
        return df.iloc[-2]
    return None
        