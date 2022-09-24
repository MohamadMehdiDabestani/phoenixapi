from . import bot_indicator as ind


def callFuncs(coin , indicator):
    MAP_FUNC = {
        "supertrend" : ind.supertrend,
        "DMI_OBV" : ind.DMI_OBV,
        "EMA" : ind.ema,

    }
    return MAP_FUNC[indicator['strategy']['name']](coin , indicator)
