from . import indicator as ind
from . import RTM
from .common import result , initialize
def callFuncs(name , coin , indicator , combineIndicator):
    MAP_FUNC = {
        'volume' : ind.volume,
        'macd': ind.macd,
        'EMA': ind.ema,
        'bbands': ind.bb,
        'rsi': ind.rsi,
        "ichimoku" : ind.ichimoku,
        "tsi" : ind.tsi,
        "S&R" : ind.SandR,
        "cti" : ind.cti,
        "cci" : ind.cci,
        "ssf" : ind.ssf,
        "base" : RTM.base,
        "supertrend" : ind.supertrend,
        "trendline" : ind.trendline,
        "bband_tsi" : ind.bband_tsi,
        "threeSupertrend" : ind.threeSupertrend,
        'threeEma' : ind.threeEma,
        'DMI_OBV' : ind.DMI_OBV,
        'DMI' : ind.DMI,
        'vwap' : ind.vwap,
        'VWAP_DMI' : ind.VWAP_DMI,

    }
    MAP_FUNC[name](coin, indicator , combineIndicator )


def analysis(df , strategy ,combineIndicator, coinName , timeFrame , exchange):
    initialize(coinName , timeFrame , exchange)
    for ind in strategy:
        callFuncs(ind["name"], df , ind,combineIndicator )
    return result
