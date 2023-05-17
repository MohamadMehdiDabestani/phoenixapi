from ta.volume import VolumeWeightedAveragePrice
import math
import numpy as np
import ccxt
import pandas as pd
import pandas_ta as pdt
from .common import getBreak , updateResult , _filter , getCross , result,cross,_break , precentageDifferent 
from .combine import get as getCombine
from scipy.stats import linregress
def rsi(coin , indicator , combine):
    rsiLength = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    _propsRsi = f"_{rsiLength}"
    if(len(coin.index) > rsiLength):
        coin.ta.rsi(length = rsiLength , append = True)
        rsiLine = coin[f"RSI{_propsRsi}"]
        if indicator["isEnableBreake"]:
            offset = getBreak(indicator,'offset')
            if(getBreak(indicator,'side') == 'both'):
                if getBreak(indicator,'type') == "line":
                    updateResult("rsi_break_line_downwards", _break(coin['time'] , rsiLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],True, offset))
                    updateResult("rsi_break_line_upwards", _break(coin['time'] , rsiLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],False, offset))
                if getBreak(indicator,'type') == "area":
                    updateResult("rsi_break_area_downwards", _break(coin['time'] , rsiLine ,getBreak(indicator,'area'),True , offset))
                    updateResult("rsi_break_area_upwards", _break(coin['time'] , rsiLine ,getBreak(indicator,'area'),False , offset))
            else:
                _side = getBreak(indicator,'side') == "downwards"
                if getBreak(indicator,'type') == "line":
                    updateResult(f"rsi_break_line_{getBreak(indicator,'side')}", _break(coin['time'] , rsiLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],_side, offset))
                if getBreak(indicator,'type') == "area":
                    updateResult(f"rsi_break_area_{getBreak(indicator,'side')}", _break(coin['time'] , rsiLine ,getBreak(indicator,'area'),_side , offset))
        if indicator["isBinding"]:
            if(combine[0]['id'] > 0):
                combineRsi = _filter(combine , "combinedIndicatorId" , indicator["id"])
                for combine in combineRsi:
                    combineParameter = _filter(combine["parametersCombine"] , "name" , "length")[0]['value']
                    updateResult(f"rsi_{rsiLength}_{combine['name']}_{combineParameter}_cross_downwards" , {})
                    updateResult(f"rsi_{rsiLength}_{combine['name']}_{combineParameter}_cross_upwards" , {})
                    source = rsiLine.to_frame()
                    source.rename(columns={f"RSI{_propsRsi}" : "close"} , inplace=True)
                    ind = getCombine(combine["name"] , source, combineParameter)
                    offset = combine["offset"]
                    dedCross = ind > rsiLine
                    goldrenCross = ind < rsiLine
                    if combine['side'] == "upwards":
                                updateResult(f"rsi_{rsiLength}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,offset))
                    if combine['side'] == "downwards":
                                updateResult(f"rsi_{rsiLength}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,offset))
                    if combine['side'] == "both":
                                updateResult(f"rsi_{rsiLength}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,offset))
                                updateResult(f"rsi_{rsiLength}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,offset))

def ema(coin, indicator , combine):
    emaLength = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    if(len(coin.index) > emaLength):
        coin.ta.ema(length=emaLength, append = True)
        emaLine = coin[f"EMA_{emaLength}"]
        precentageDiff = float(_filter(indicator['settings'] , 'name' , 'precentageDifferent')[0]['value'])
        if precentageDiff > 0:
            def calculationDiff(row):
                return precentageDifferent(row[f"EMA_{emaLength}"] ,row['close']) <= precentageDiff
            coin['diffCalculation'] = coin.apply(lambda x : calculationDiff(x) , axis=1)
            if len(coin.loc[coin['diffCalculation'] == True]) > 0:
                updateResult("EMA_precentage" , coin.loc[coin['diffCalculation'] == True].iloc[-1]['time'])
            else:
                updateResult("EMA_precentage" , {})
        if indicator["isEnableBreake"]:
            _side = getBreak(indicator,'side')
            _type = getBreak(indicator,'type')
            break_offset = getBreak(indicator,'offset')
            if(_side == "both"):
                updateResult(f"EMA_break_{_type}_upwards",_break(coin['time'] , emaLine ,[coin['close'] , coin['close']],True , break_offset))
                updateResult(f"EMA_break_{_type}_downwards",_break(coin['time'] , emaLine ,[coin['close'] , coin['close']],False , break_offset))
            else:
                _sideCheck = _side == "upwards"
                updateResult(f"EMA_break_{_type}_{_side}",_break(coin['time'] , emaLine ,[coin['close'] , coin['close']],_sideCheck , break_offset))
        if indicator["isBinding"]:
                if(combine[0]['id'] > 0):
                    combineEma = _filter(combine , "combinedIndicatorId" , indicator["id"])
                    for combine in combineEma:
                        combineParameter = _filter(combine["parametersCombine"] , "name" , "length")[0]['value']
                        print("combineParameter" ,combineParameter)
                        if(len(coin.index) > combineParameter):
                            ind = getCombine(combine["name"] , coin.filter(['close']), combineParameter)
                            offset = combine["offset"]
                            dedCross = ind < emaLine
                            goldrenCross = ind > emaLine
                            if combine['side'] == "upwards":
                                        updateResult(f"EMA_{emaLength}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,False,offset))
                            if combine['side'] == "downwards":
                                        updateResult(f"EMA_{emaLength}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,True,offset))
                            if combine['side'] == "both":
                                        updateResult(f"EMA_{emaLength}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,False,offset))
                                        updateResult(f"EMA_{emaLength}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,True,offset))

def bb(coin, indicator , combine):
    bbLength = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    coin.ta.bbands(length=bbLength , append = True)
    if(len(coin.index) > bbLength):
        coin[f"BBP_{bbLength}_2.0"] = coin[f"BBP_{bbLength}_2.0"].astype('float64')
        sensitivity = float(_filter(indicator["settings"] , "name" , "sensitivity")[0]["value"])
        bbandSensitivity_plus = calculateLimit(coin[coin[f"BBP_{bbLength}_2.0"] >= sensitivity])
        updateResult("sensitivity_plus" ,bbandSensitivity_plus)
        bbandSensitivity_minus = calculateLimit(coin[coin[f"BBP_{bbLength}_2.0"] <= 1 - sensitivity])
        updateResult("sensitivity_minus" ,bbandSensitivity_minus)

def macd(coin, indicator , combine):
    MACDs = _filter(indicator["parameters"] , "name" , "MACDs")[0]["value"]
    signal = _filter(indicator["parameters"] , "name" , "signal")[0]["value"]
    MACD = _filter(indicator["parameters"] , "name" , "MACD")[0]["value"]
    if(len(coin.index) > max([MACDs , MACD , signal])):
        coin.ta.macd(fast=MACD,slow=MACDs,signal=signal,append=True)
        _propsMacd = f"_{MACD}_{MACDs}_{signal}"
        if indicator["isEnableCross"]:
            signalLineCalculated = coin[f"MACDs{_propsMacd}"]
            macdLineCalculated = coin[f"MACD{_propsMacd}"]
            cross_offset = getCross(indicator , "offset")
            goldrenCross = macdLineCalculated > signalLineCalculated
            dedCross = macdLineCalculated < signalLineCalculated
            getData = {"downwards" : dedCross , "upwards" : goldrenCross}
            _side = getBreak(indicator,'side') == "downwards"
            if getCross(indicator,'side') == "both":
                updateResult("macd_cross_upwards" ,cross(coin['time'],goldrenCross,False,cross_offset))
                updateResult("macd_cross_downwards" ,cross(coin['time'] ,dedCross ,True,cross_offset))
            else:
                updateResult(f"macd_cross_{getCross(indicator,'side')}" ,cross(coin['time'],getData[getCross(indicator,'side')] , _side,cross_offset))

        if indicator["isEnableBreake"]:
            _side = getBreak(indicator,'side')
            macdBreakLine = coin[_filter(indicator['parameters'] , "defaultBreaking" , True)[0]["name"] + _propsMacd]
            break_offset = getBreak(indicator,'offset')
            if(_side == "both"):
                if getBreak(indicator,'type') == "line":
                    updateResult("macd_break_line_upwards",_break(coin['time'] , macdBreakLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],False, break_offset))
                    updateResult("macd_break_line_downwards",_break(coin['time'] , macdBreakLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],True, break_offset))
                if getBreak(indicator,'type') == "area":
                   updateResult("macd_break_area_downwards",_break(coin['time'] , macdBreakLine ,getBreak(indicator,'area'),True , break_offset))
                   updateResult("macd_break_area_upwards",_break(coin['time'] , macdBreakLine ,getBreak(indicator,'area'),False , break_offset))
            else:
                _sideCheck = _side == "downwards"
                if getBreak(indicator,'type') == "line":
                        updateResult(f"macd_break_line_{_side}",_break(coin['time'] , macdBreakLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],_sideCheck, break_offset))
                if getBreak(indicator,'type') == "area":
                       updateResult(f"break_macd_area_{_side}",_break(coin['time'] , macdBreakLine ,getBreak(indicator,'area'),_sideCheck , break_offset))

def ichimoku(coin, indicator , combine):
    senku = _filter(indicator["parameters"] , "name" , "senku")[0]["value"]
    tenkan = _filter(indicator["parameters"] , "name" , "ITS")[0]["value"]
    kijun = _filter(indicator["parameters"] , "name" , "IKS")[0]["value"]
    coin.ta.ichimoku(kijun=kijun,tenkan=tenkan ,senku=senku, append = True)
    if indicator["isEnableCross"]:
        cross_offset = getCross(indicator , 'offset')
        first_line = _filter(indicator["parameters"] , "defaultCrossing" ,True)[0]
        second_line = _filter(indicator["parameters"] , "defaultCrossed" ,True)[0]
        second_line = coin.filter(regex=second_line["name"] +".").squeeze()
        first_line = coin.filter(regex=first_line["name"] +".").squeeze()
        if not second_line.empty or not first_line.empty:
            dedCross =  second_line > first_line
            goldrenCross =  second_line < first_line
            getData = {"downwards" : dedCross , "upwards" : goldrenCross}
            if getCross(indicator,'side') == "both":
                updateResult("ichimoku_cross_downwards" ,cross(coin['time'] ,dedCross ,cross_offset))
                updateResult("ichimoku_cross_upwards" ,cross(coin['time'],goldrenCross,cross_offset))
            else:
                updateResult(f"ichimoku_cross_{getCross(indicator , 'side')}" ,cross(coin['time'],getData[getCross(indicator,'side')],cross_offset))

def SandR(coin, indicator , combine):
    global result
    global exchange
    updateResult("S&R" , {})
    precentage = int(_filter(indicator["settings"] , "name" , "precentage")[0]["value"])
    timeFrames = _filter(indicator["settings"] , "name" , "timeFrames")[0]["value"]
    difficulty = _filter(indicator["parameters"] , "name" , "difficult")[0]["value"]
    _exchange = getattr(ccxt, result['exchange'])
    currentCoinName = result["coinName"]
    for t in timeFrames:
        bars = _exchange().fetch_ohlcv(currentCoinName,  timeframe=t, limit=300)
        df = pd.DataFrame(bars, columns=["time", "open", "high", "low", "close", "volume"])
        ichi = df.ta.ichimoku(append = False)[0]
        objs = result["S&R"]
        objs[t] = []
        if(ichi is not None):
            def getSupport(maxDiff, diff, tenkan_sen, kijun_sen, tenkan_sen_second, kijun_sen_second):
                if(tenkan_sen == tenkan_sen_second and kijun_sen == kijun_sen_second):
                    if(diff == maxDiff):
                        line = ichi["ITS_9"][i]
                        objs[t].append(line)
                        #  remove dublicate
                        objs[t] = list(set(objs[t]))
                        #  remove dublicate
                            
            for i, row in ichi.iterrows():
                for diff in range(1, difficulty + 1):
                    if(len(ichi.index) <= i + diff):
                        if(len(objs[t]) > 0):
                            _type = _filter(indicator["settings"] , "name" , "type")[0]["value"]
                            if(_type == "default"):
                                high = list(filter(lambda x : x > df.iloc[-1]['close'] , objs[t]))
                                low = list(filter(lambda x : x < df.iloc[-1]['close'] , objs[t]))
                                high.sort()
                                low.sort()
                                objs[t] = [high[0] if len(high) > 0 else 0, low[-1] if len(low) > 0 else 0]
                            else:
                                objs[t] = []
                                highLvels = list(filter(lambda x : precentageDifferent(df.iloc[-1]["close"] , x) <= precentage , high))
                                lowLvels = list(filter(lambda x : precentageDifferent(df.iloc[-1]["close"] , x) <= precentage , low))
                                objs[t] = lowLvels + highLvels
                        break
                    getSupport(difficulty, diff, ichi["ITS_9"][i], ichi["IKS_26"][i],
                            ichi["ITS_9"][i + diff], ichi["IKS_26"][i + diff])

def trendline(coin, indicator , combine):
    df = coin.iloc[-120:]
    # df = coin.copy()
    df['Number'] = np.arange(len(df))+1
    df_high = df.copy()
    df_low = df.copy()
    high_limit = 0
    low_limit = 0
    while len(df_high)>2:
        high_limit += 1
        if(high_limit == 10):
            break
        slope, intercept, r_value, p_value, std_err = linregress(x=df_high['Number'], y=df_high['high'])
        df_high = df_high.loc[df_high['high'] > slope * df_high['Number'] + intercept]
    while len(df_low)>2:
        low_limit += 1
        if(low_limit == 10):
            break
        slope, intercept, r_value, p_value, std_err = linregress(x=df_low['Number'], y=df_low['low'])
        df_low = df_low.loc[df_low['low'] < slope * df_low['Number'] + intercept]
    slope, intercept, r_value, p_value, std_err = linregress(x=df_high['Number'], y=df_high['close'])
    df['Uptrend'] = slope * df['Number'] + intercept
    slope, intercept, r_value, p_value, std_err = linregress(x=df_low['Number'], y=df_low['close'])
    df['Downtrend'] = slope * df['Number'] + intercept
    Uptrend = df.filter(['time' , "Uptrend"]).rename(columns={'time' : "x" , "Uptrend" : 'y'}).to_dict(orient='records')
    Downtrend = df.filter(['time' , "Downtrend"]).rename(columns={'time' : "x" , "Downtrend" : 'y'}).to_dict(orient='records')
    obj = {}
    if(not math.isnan(Downtrend[0]['y'])):
        touchd = df.loc[df['low'] <= df["Downtrend"]].loc[df['close'] >= df['Downtrend']]
        touchd['time'] = pd.to_datetime(touchd['time'] , unit='ms')
        touchd = touchd.to_dict(orient='records')
        touchd = touchd[-1]['time'] if len(touchd) > 0 else {}
        updateResult("downtrend_last_touch" , touchd)
        obj["downtrend"] = Downtrend
    if(not math.isnan(Uptrend[0]['y'])):
        touchu = df.loc[df['high'] >= df["Uptrend"]].loc[df['close'] <= df['Uptrend']]
        touchu['time'] = pd.to_datetime(touchu['time'] , unit='ms')
        touchu = touchu.to_dict(orient='records')
        touchu = touchu[-1]['time'] if len(touchu) > 0 else {}
        updateResult("uptrend_last_touch" , touchu)
        obj["uptrend"] = Uptrend
    updateResult("trendline" , obj)

def tsi(coin, indicator ,combine):
    slow = _filter(indicator["parameters"] , "name" , "TSI")[0]["value"]
    signal = _filter(indicator["parameters"] , "name" , "signal")[0]["value"]
    fast = _filter(indicator["parameters"] , "name" , "TSIs")[0]["value"]
    if(len(coin.index) > max([slow , fast , signal])):
        coin.ta.tsi(slow=slow,fast=fast,signal=signal,append=True)
        _propsTsi = f"_{fast}_{slow}_{signal}"
        if indicator["isEnableCross"]:
            shortLine = coin[f"TSIs{_propsTsi}"]
            tsiLineCalculated = coin[f"TSI{_propsTsi}"]
            cross_offset = getCross(indicator , "offset")
            goldrenCross = tsiLineCalculated > shortLine
            dedCross = tsiLineCalculated < shortLine
            getData = {"downwards" : dedCross , "upwards" : goldrenCross}
            _side = getBreak(indicator,'side') == "downwards"
            if getCross(indicator,'side') == "both":
                updateResult("tsi_cross_upwards" ,cross(coin['time'],goldrenCross,False,cross_offset))
                updateResult("tsi_cross_downwards" ,cross(coin['time'] ,dedCross ,True,cross_offset))
            else:
                updateResult(f"tsi_cross_{getCross(indicator,'side')}" ,cross(coin['time'],getData[getCross(indicator,'side')] , _side,cross_offset))

        if indicator["isEnableBreake"]:
            _side = getBreak(indicator,'side')
            tsiBreakLine = coin[_filter(indicator['parameters'] , "defaultBreaking" , True)[0]["name"] + _propsTsi]
            break_offset = getBreak(indicator,'offset')
            if(_side == "both"):
                if getBreak(indicator,'type') == "line":
                    updateResult("tsi_break_line_upwards",_break(coin['time'] , tsiBreakLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],False, break_offset))
                    updateResult("tsi_break_line_downwards",_break(coin['time'] , tsiBreakLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],True, break_offset))
                if getBreak(indicator,'type') == "area":
                   updateResult("tsi_break_area_downwards",_break(coin['time'] , tsiBreakLine ,getBreak(indicator,'area'),True , break_offset))
                   updateResult("tsi_break_area_upwards",_break(coin['time'] , tsiBreakLine ,getBreak(indicator,'area'),False , break_offset))
            else:
                _sideCheck = _side == "downwards"
                if getBreak(indicator,'type') == "line":
                        updateResult(f"tsi_break_line_{_side}",_break(coin['time'] , tsiBreakLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],_sideCheck, break_offset))
                if getBreak(indicator,'type') == "area":
                       updateResult(f"tsi_break_area_{_side}",_break(coin['time'] , tsiBreakLine ,getBreak(indicator,'area'),_sideCheck , break_offset))

def supertrend(coin, indicator , combine):
    length = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    factor = float(_filter(indicator["parameters"] , "name" , "factor")[0]["value"])
    if(len(coin.index) > max([length , factor])):
        coin.ta.supertrend(multiplier=factor,length=length,append=True)
        propsSupertrend = f'_{length}_{factor}'
        obj = {"long" : {} , "short":{}}
        def calculateSignal(x):
            if x[f'SUPERTd{propsSupertrend}'] > 0 and coin.iloc[x.name - 1][f'SUPERTd{propsSupertrend}'] < 0:
                obj['long'] = x['time']
            if x[f'SUPERTd{propsSupertrend}'] < 0 and coin.iloc[x.name - 1][f'SUPERTd{propsSupertrend}'] > 0:
                obj['short'] = x['time']
        coin.apply(lambda x : calculateSignal(x) , axis=1)
        updateResult("supertrend_long" , obj['long'])
        updateResult("supertrend_short" , obj['short'])

def cti(coin, indicator , combine):
    length = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    if(len(coin.index) > length):
        coin.ta.cti(length = length , append = True)
        ctiLine = coin[f"CTI_{length}"]
        if indicator["isEnableBreake"]:
            offset = getBreak(indicator,'offset')
            if(getBreak(indicator,'side') == 'both'):
                if getBreak(indicator,'type') == "line":
                    updateResult("cti_break_line_downwards", _break(coin['time'] , ctiLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],True, offset))
                    updateResult("cti_break_line_upwards", _break(coin['time'] , ctiLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],False, offset))
                if getBreak(indicator,'type') == "area":
                    updateResult("cti_break_area_downwards", _break(coin['time'] , ctiLine ,getBreak(indicator,'area'),True , offset))
                    updateResult("cti_break_area_upwards", _break(coin['time'] , ctiLine ,getBreak(indicator,'area'),False , offset))
            else:
                _side = getBreak(indicator,'side') == "downwards"
                if getBreak(indicator,'type') == "line":
                    updateResult(f"cti_break_line_{getBreak(indicator,'side')}", _break(coin['time'] , ctiLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],_side, offset))
                if getBreak(indicator,'type') == "area":
                    updateResult(f"cti_break_area_{getBreak(indicator,'side')}", _break(coin['time'] , ctiLine ,getBreak(indicator,'area'),_side , offset))

def cci(coin, indicator , combine):
    length = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    if(len(coin.index) > length):
        coin.ta.cci(length = length , append = True)
        cciLine = coin[f"CCI_{length}_0.015"]
        if indicator["isEnableBreake"]:
            offset = getBreak(indicator,'offset')
            if(getBreak(indicator,'side') == 'both'):
                if getBreak(indicator,'type') == "line":
                    updateResult("cci_break_line_downwards", _break(coin['time'] , cciLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],True, offset))
                    updateResult("cci_break_line_upwards", _break(coin['time'] , cciLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],False, offset))
                if getBreak(indicator,'type') == "area":
                    updateResult("cci_break_area_downwards", _break(coin['time'] , cciLine ,getBreak(indicator,'area'),True , offset))
                    updateResult("cci_break_area_upwards", _break(coin['time'] , cciLine ,getBreak(indicator,'area'),False , offset))
            else:
                _side = getBreak(indicator,'side') == "downwards"
                if getBreak(indicator,'type') == "line":
                    updateResult(f"cci_break_line_{getBreak(indicator,'side')}", _break(coin['time'] , cciLine ,[getBreak(indicator,'line'),getBreak(indicator,'line')],_side, offset))
                if getBreak(indicator,'type') == "area":
                    updateResult(f"cci_break_area_{getBreak(indicator,'side')}", _break(coin['time'] , cciLine ,getBreak(indicator,'area'),_side , offset))

def ssf(coin, indicator , combine):
    ssfLength = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    poles = _filter(indicator["parameters"] , "name" , "poles")[0]["value"]
    if(poles <= 3):
        if(len(coin.index) > ssfLength):
            coin.ta.ssf(length=ssfLength,poles=poles, append = True)
            _ssfProps = f'_{ssfLength}_{poles}'
            ssfLine = coin[f"SSF{_ssfProps}"]
            precentageDiff = float(_filter(indicator['settings'] , 'name' , 'precentageDifferent')[0]['value'])
            if precentageDiff > 0:
                def calculationDiff(row):
                    return precentageDifferent(row[f"SSF{_ssfProps}"] ,row['close']) <= precentageDiff
                coin['diffCalculation'] = coin.apply(lambda x : calculationDiff(x) , axis=1)
                if len(coin.loc[coin['diffCalculation'] == True]) > 0:
                    updateResult("ssf_precentage" , coin.loc[coin['diffCalculation'] == True].iloc[-1]['time'])
                else:
                    updateResult("ssf_precentage" , {})
            if indicator["isEnableBreake"]:
                _side = getBreak(indicator,'side')
                _type = getBreak(indicator,'type')
                break_offset = getBreak(indicator,'offset')
                if(_side == "both"):
                    updateResult(f"ssf_break_{_type}_upwards",_break(coin['time'] , ssfLine ,[coin['close'] , coin['close']],True , break_offset))
                    updateResult(f"ssf_break_{_type}_downwards",_break(coin['time'] , ssfLine ,[coin['close'] , coin['close']],False , break_offset))
                else:
                    _sideCheck = _side == "upwards"
                    updateResult(f"ssf_break_{_type}_{_side}",_break(coin['time'] , ssfLine ,[coin['close'] , coin['close']],_sideCheck , break_offset))
            if indicator["isBinding"]:
                    if(combine[0]['id'] > 0):
                        combineSsf = _filter(combine , "combinedIndicatorId" , indicator["id"])
                        for combine in combineSsf:
                            combineParameter = _filter(combine["parametersCombine"] , "name" , "length")[0]['value']
                            print("combineParameter" ,combineParameter)
                            if(len(coin.index) > combineParameter):
                                ind = getCombine(combine["name"] , coin.filter(['close']), combineParameter)
                                offset = combine["offset"]
                                dedCross = ind < ssfLine
                                goldrenCross = ind > ssfLine
                                if combine['side'] == "upwards":
                                            updateResult(f"ssf_{ssfLength}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,False,offset))
                                if combine['side'] == "downwards":
                                            updateResult(f"ssf_{ssfLength}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,True,offset))
                                if combine['side'] == "both":
                                            updateResult(f"ssf_{ssfLength}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,False,offset))
                                            updateResult(f"ssf_{ssfLength}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,True,offset))

def bband_tsi(coin, indicator , combine):
    df = coin.copy()
    df.ta.ha(append=True)
    df.drop(['open','low','close', 'high'], axis=1, inplace=True)
    df.rename(columns={'HA_open' : "open" , 'HA_close' : "close" , 'HA_high' : 'high' , 'HA_low' : "low"} ,  inplace=True)
    df.ta.adx(append=True)
    df.ta.bbands(length=20, append=True)
    df.ta.tsi(slow=14, fast=3, signal=3, append=True)
    shortLine = df["TSIs_3_14_3"]
    tsiLineCalculated = df["TSI_3_14_3"]
    goldrenCross = tsiLineCalculated > shortLine
    deadCross = tsiLineCalculated < shortLine
    def calculationHighBB(row):
        if (precentageDifferent(row['BBU_20_2.0'], row['BBL_20_2.0']) < 3.5) or row['low'] >= row["BBM_20_2.0"]:
            return False
        if(row['close'] >= row["BBU_20_2.0"] or row['high'] >= row['BBU_20_2.0']):
            return True
        if(row['high'] <= row['BBU_20_2.0']):
            if(precentageDifferent(row['high'], row['BBU_20_2.0']) < 1.3):
                return True
        return False


    def calculationLowBB(row):
        if(precentageDifferent(row['BBU_20_2.0'], row['BBL_20_2.0']) < 3.5 or row['high'] >= row["BBM_20_2.0"]):
            return False
        if(row['close'] <= row["BBL_20_2.0"] or row['low'] <= row['BBL_20_2.0']):
            return True
        if(row['low'] >= row['BBL_20_2.0']):
            if(precentageDifferent(row['low'], row['BBL_20_2.0']) < 1.3):
                return True
        return False

    df['low_bb'] = df.apply(lambda x: calculationLowBB(x), axis=1)
    df['high_bb'] = df.apply(lambda x: calculationHighBB(x), axis=1)
    df["goldrenCross"] = pdt.tsignals(
        goldrenCross, above=False, asbool=True)['TS_Entries']
    df["deadCross"] = pdt.tsignals(deadCross, above=True, asbool=True)['TS_Entries']


    def detectionShortSignal(x):
        if(x["ADX_14"] < 25):
            return False
        if (x['high_bb'] and x['deadCross']):
            return True
        if(len(df.index) > x.name+1):
            if (x['high_bb'] and df.iloc[x.name+1]['deadCross']):
                return True
        return False


    def detectionLongSignal(x):
        if(x["ADX_14"] < 25):
            return False
        if (x['low_bb'] and x['goldrenCross']):
            return True
        return False

    # def calculationStopLoss(row):
    #     if(row['short'] == True):
    #         return row['open'] + row["ATRr_14"]
    #     if(row['long'] == True):
    #         return row['open'] - row["ATRr_14"]
    #     return 0.0
    df['short'] = df.apply(lambda x: detectionShortSignal(x), axis=1)
    df['long'] = df.apply(lambda x: detectionLongSignal(x), axis=1)
    # df['stoploss'] = df.apply(lambda x: calculationStopLoss(x), axis=1)

    if(len(df.loc[df['long'] == True]) > 0):
        updateResult("bband_tsi_long",df.loc[df['long'] == True].iloc[-1]['time'])
    else:
        updateResult("bband_tsi_long",{})
    if(len(df.loc[df['short'] == True]) > 0):
        updateResult("bband_tsi_short",df.loc[df['short'] == True].iloc[-1]['time'])
    else:
        updateResult("bband_tsi_short",{})

def threeSupertrend(coin, indicator , combine):

    print("threeSupertrend")
    coin.ta.supertrend(multiplier=1,length=10,append=True)
    coin.ta.supertrend(multiplier=2,length=11,append=True)
    coin.ta.supertrend(multiplier=3,length=12,append=True)
    slowPropsSupertrend = '_10_1.0'
    midPropsSupertrend = '_11_2.0'
    longPropsSupertrend = '_12_3.0'
    def longSignal(x):
        if x[f'SUPERTd{longPropsSupertrend}'] > 0 and coin.iloc[x.name - 1][f'SUPERTd{longPropsSupertrend}'] < 0:
            if(x[f'SUPERTd{slowPropsSupertrend}'] > 0 and x[f'SUPERTd{midPropsSupertrend}'] > 0):
                return True
        return False
    def shortSignal(x):
        if x[f'SUPERTd{longPropsSupertrend}'] < 0 and coin.iloc[x.name - 1][f'SUPERTd{longPropsSupertrend}'] > 0:
            if(x[f'SUPERTd{slowPropsSupertrend}'] < 0 and x[f'SUPERTd{midPropsSupertrend}'] < 0):
                return True
        return False
    coin['long'] = coin.apply(lambda x : longSignal(x) , axis=1)
    print(coin)
    coin['short'] = coin.apply(lambda x : shortSignal(x) , axis=1)
    
    updateResult("threesupertrend_long" , coin.loc[coin['long'] == True].iloc[-1]['time'])
    updateResult("threesupertrend_short" , coin.loc[coin['short'] == True].iloc[-1]['time'])

def threeEma(coin, indicator , combine):
    coin.ta.ema(length=9, append = True)
    coin.ta.ema(length=25, append = True)
    coin.ta.ema(length=200, append = True)
    def calculationLong(row):
        if(row['goldrenCross'] and row['close'] > row['EMA_200']):
            return True
        if(row['close'] > row['EMA_200'] and coin.iloc[row.name - 1]['EMA_200'] > coin.iloc[row.name - 1]['open'] and row['EMA_9'] > row['EMA_25']):
            return True
        return False
    def calculationShort(row):
        if(row['deadCross'] and row['close'] < row['EMA_200']):
            return True
        if(row['close'] < row['EMA_200'] and coin.iloc[row.name - 1]['EMA_200'] < coin.iloc[row.name - 1]['close'] and row['EMA_9'] < row['EMA_25']):
            return True
        return False
    deadCross = coin['EMA_9'] < coin['EMA_25']
    goldrenCross = coin['EMA_9'] > coin['EMA_25']
    coin['deadCross'] = pdt.tsignals(deadCross, above=True, offset=0, asbool=True)['TS_Entries']
    coin['goldrenCross'] = pdt.tsignals(goldrenCross, above=True, offset=0, asbool=True)['TS_Entries']
    coin['short'] = coin.apply(lambda x : calculationShort(x) , axis=1)
    coin['long'] = coin.apply(lambda x : calculationLong(x) , axis=1)
    if(len(coin.loc[coin['long'] == True]) > 0):
        updateResult("threeEma_long",coin.loc[coin['long'] == True].iloc[-1]['time'])
    else:
        updateResult("threeEma_long",{})
    if(len(coin.loc[coin['short'] == True]) > 0):
        updateResult("threeEma_short",coin.loc[coin['short'] == True].iloc[-1]['time'])
    else:
        updateResult("threeEma_short",{})

def DMI_OBV(coin, indicator , combine):
    coin.ta.adx(length=14 , append = True)
    obv = coin.ta.obv()
    obv = obv.to_frame()
    obv.rename(columns={"OBV" : "close"} , inplace=True)
    obv.ta.sma(length=100,append = True)
    deadCrossObv = obv['SMA_100'] > obv['close']
    goldrenCrossObv = obv['SMA_100'] < obv['close']
    coin['goldrenCrossObv'] = pdt.tsignals(goldrenCrossObv ,  above=True, offset=0, asbool=True)['TS_Entries']
    coin['deadCrossObv'] = pdt.tsignals(deadCrossObv ,  above=True, offset=0, asbool=True)['TS_Entries']
    goldrenCross = coin['DMP_14'] > coin['DMN_14']
    deadCross = coin['DMP_14'] < coin['DMN_14']
    coin['goldrenCross'] = pdt.tsignals(goldrenCross ,  above=True, offset=0, asbool=True)['TS_Entries']
    coin['deadCross'] = pdt.tsignals(deadCross ,  above=True, offset=0, asbool=True)['TS_Entries']
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
    coin['long'] = coin.apply(lambda x : calculationLong(x) , axis=1)
    coin['short'] = coin.apply(lambda x : calculationShort(x) , axis=1)
    
    if(len(coin.loc[coin['long'] == True]) > 0):
        updateResult("DMI_OBV_long",coin.loc[coin['long'] == True].iloc[-1]['time'])
    else:
        updateResult("DMI_OBV_long",{})
    if(len(coin.loc[coin['short'] == True]) > 0):
        updateResult("DMI_OBV_short",coin.loc[coin['short'] == True].iloc[-1]['time'])
    else:
        updateResult("DMI_OBV_short",{})

def DMI(coin, indicator , combine):
    length = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    if(len(coin) > length):
        coin.ta.adx(length=length, append = True)
        if indicator["isEnableCross"]:
            goldrenCross = coin['DMP_14'] > coin['DMN_14']
            deadCross = coin['DMP_14'] < coin['DMN_14']
            updateResult("DMI_cross_upwards" ,cross(coin['time'],goldrenCross,False,0))
            updateResult("DMI_cross_downwards" ,cross(coin['time'] ,deadCross ,True,0))
        x = np.array(np.linspace(coin.iloc[-11:]['ADX_14'].min(), coin.iloc[-11:]['ADX_14'].max() , 11))
        y = np.array(coin.iloc[-11:]['ADX_14'])
        reg = linregress(x,y)
        if reg.slope < -0.5:
            updateResult("ADX_way" ,"downside")
        elif reg.slope > 0.5:
            updateResult("ADX_way" ,"upside")
        else:
            updateResult("ADX_way" ,"sideway")

def vwap(coin, indicator , combine):
    period = _filter(indicator["parameters"] , "name" , "length")[0]["value"]
    if(len(coin.index) > period):
        coin[f'vwap_{period}'] = VolumeWeightedAveragePrice(high=coin['high'], low=coin['low'], close=coin["close"], volume=coin['volume'], window=period, fillna=True).volume_weighted_average_price()
        vwapLine = coin[f"vwap_{period}"]
        x = np.array(np.linspace(coin.iloc[-10:][f"vwap_{period}"].min(), coin.iloc[-10:][f"vwap_{period}"].max() , 10))
        y = np.array(coin.iloc[-10:][f"vwap_{period}"])
        reg = linregress(x,y)
        if reg.slope < -0.5:
            updateResult("vwap_way" ,"downside")
        elif reg.slope > 0.5:
            updateResult("vwap_way" ,"upside")
        else:
            updateResult("vwap_way" ,"sideway")
        precentageDiff = float(_filter(indicator['settings'] , 'name' , 'precentageDifferent')[0]['value'])
        if precentageDiff > 0:
            def calculationDiff(row):
                return precentageDifferent(row[f"vwap_{period}"] ,row['close']) <= precentageDiff
            coin['diffCalculation'] = coin.apply(lambda x : calculationDiff(x) , axis=1)
            if len(coin.loc[coin['diffCalculation'] == True]) > 0:
                updateResult("vwap_precentage" , coin.loc[coin['diffCalculation'] == True].iloc[-1]['time'])
            else:
                updateResult("vwap_precentage" , {})
        
        if indicator["isEnableBreake"]:
            _side = getBreak(indicator,'side')
            _type = getBreak(indicator,'type')
            break_offset = getBreak(indicator,'offset')
            if(_side == "both"):
                updateResult(f"vwap_break_{_type}_upwards",_break(coin['time'] , vwapLine ,[coin['close'] , coin['close']],True , break_offset))
                updateResult(f"vwap_break_{_type}_downwards",_break(coin['time'] , vwapLine ,[coin['close'] , coin['close']],False , break_offset))
            else:
                _sideCheck = _side == "upwards"
                updateResult(f"vwap_break_{_type}_{_side}",_break(coin['time'] , vwapLine ,[coin['close'] , coin['close']],_sideCheck , break_offset))
        if indicator["isBinding"]:
                if(combine[0]['id'] > 0):
                    combineVwap = _filter(combine , "combinedIndicatorId" , indicator["id"])
                    for combine in combineVwap:
                        combineParameter = _filter(combine["parametersCombine"] , "name" , "length")[0]['value']
                        print("combineParameter" ,combineParameter)
                        if(len(coin.index) > combineParameter):
                            ind = getCombine(combine["name"] , coin, combineParameter)
                            offset = combine["offset"]
                            dedCross = ind < vwapLine
                            goldrenCross = ind > vwapLine
                            if combine['side'] == "upwards":
                                        updateResult(f"vwap_{period}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,False,offset))
                            if combine['side'] == "downwards":
                                        updateResult(f"vwap_{period}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,True,offset))
                            if combine['side'] == "both":
                                        updateResult(f"vwap_{period}_{combine['name']}_{combineParameter}_cross_upwards" ,cross(coin['time'],goldrenCross,False,offset))
                                        updateResult(f"vwap_{period}_{combine['name']}_{combineParameter}_cross_downwards" ,cross(coin['time'],dedCross,True,offset))

def VWAP_DMI(coin, indicator , combine) :
    coin.ta.adx(length=14 , append = True)
    period = 25
    coin[f'vwap_25'] = VolumeWeightedAveragePrice(high=coin['high'], low=coin['low'], close=coin["close"], volume=coin['volume'], window=period, fillna=True).volume_weighted_average_price()
    goldrenCross = coin['DMP_14'] > coin['DMN_14']
    deadCross = coin['DMN_14'] > coin['DMP_14']
    goldrenCross_vwap = coin[f"vwap_{period}"] < coin["close"]
    deadCross_vwap = coin[f"vwap_{period}"] > coin["close"]
    coin["deadCross"] = pdt.tsignals(deadCross, above=True, asbool=True)["TS_Entries"]
    coin["goldrenCross"] = pdt.tsignals(goldrenCross, above=True, asbool=True)["TS_Entries"]
    coin["deadCross_vwap"] = pdt.tsignals(deadCross_vwap, above=True, asbool=True)["TS_Entries"]
    coin["goldrenCross_vwap"] = pdt.tsignals(goldrenCross_vwap, above=True, asbool=True)["TS_Entries"]
    
    def calculationShortSignal(row):
        if row["deadCross"] == True and row[f"vwap_{period}"] > row["close"]:
            return True
        if row["deadCross_vwap"] == True and row["DMP_14"] < row["DMN_14"]:
            return True
        return False

    def calculationLongSignal(row):
        if row["goldrenCross"] == True and row[f"vwap_{period}"] < row["close"]:
            return True
        if row["goldrenCross_vwap"] == True and row["DMP_14"] > row["DMN_14"]:
            return True
        return False
    coin['VWAP_DMI_short'] = coin.apply(lambda row : calculationShortSignal(row) , axis=1)
    coin['VWAP_DMI_long'] = coin.apply(lambda row : calculationLongSignal(row) , axis=1)
    
    if(len(coin.loc[coin['VWAP_DMI_long'] == True]) > 0):
        updateResult("VWAP_DMI_long",coin.loc[coin['VWAP_DMI_long'] == True].iloc[-1]['time'])
    else:
        updateResult("VWAP_DMI_long",{})
    if(len(coin.loc[coin['VWAP_DMI_short'] == True]) > 0):
        updateResult("VWAP_DMI_short",coin.loc[coin['VWAP_DMI_short'] == True].iloc[-1]['time'])
    else:
        updateResult("VWAP_DMI_short",{})

def volume(coin, indicator , combine):
    x = np.array(np.linspace(
    coin.iloc[-3:]['volume'].min(), coin.iloc[-3:]['volume'].max(), 3))
    y = np.array(coin.iloc[-3:]['volume'])
    reg = linregress(x, y)
    if reg.slope < -0.5:
        updateResult("volume_way" ,"downside")
    elif reg.slope > 0.5:
        updateResult("volume_way" ,"upside")
    else:
        updateResult("volume_way" ,"sideway")

