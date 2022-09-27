# import requests
from cmath import log
import json
from fastapi import FastAPI
from util import bot
from util import strategy
from util import common
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost",
    "https://phoenixcrypto.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def test():
    return {"Hello" : "Wrold"}
class AnalysisItem(BaseModel):
    exchange: str
    strategy: dict
    coin : str
def analysisFunc(coin , item):
    print("coin" , coin)
    df = common.get_asset(item.exchange , 1 , coin , item.strategy['timeFrame'])

    if(item.strategy['chartType'] == "Heikin Ashi"):
        df.ta.ha(append=True)
        df.drop(['open','low','close', 'high'], axis=1, inplace=True)
        df.rename(columns={'HA_open' : "open" , 'HA_close' : "close" , 'HA_high' : 'high' , 'HA_low' : "low"} ,  inplace=True)
    analys = strategy.analysis(df , item.strategy["indicators"] ,item.strategy["combine"],coin , item.strategy['timeFrame']  , 
    item.exchange)
    return json.dumps(analys, indent=4, sort_keys=True, default=str)

@app.post("/analzer")
async def analysis(item : AnalysisItem):
    retry = 0
    try:
        analys = analysisFunc(item.coin , item)
        return {"success" : True , "data":analys}
    except TypeError as err:
        print(err)
        if(retry == 0):
            try:
                analys = analysisFunc(f"{item.coin}:USDT" , item)
                retry = 1
                return {"success" : True , "data":analys}
            except err:
                print(err)
                return {"success" : True , "data":json.dumps({
                        "coinName" : item.coin,
                        "time": {}
                    }, indent=4, sort_keys=True, default=str)}
    except BaseException as err:
        print(err);
        return {"success" : True , "data":json.dumps({
            "coinName" : item.coin,
            "time": {}
        }, indent=4, sort_keys=True, default=str)}


class CoinItem(BaseModel):
    exchange: str
    coin : str
    timeFrame : str
@app.post("/coin")
async def coin(item : CoinItem):
    retry = 0
    try:
        coin = common.getJsonCoin(item.exchange , 1 , item.coin , item.timeFrame)
        return {"success" : True , "data":coin}
    except TypeError as err:
        if(retry == 0):
            try:
                analys = analysisFunc(f"{item.coin}:USDT" , item)
                retry = 1
                return {"success" : True , "data":analys}
            except err:
                print(err)
                return {"success" : True , "data":json.dumps({
                        "coinName" : item.coin,
                        "time": {}
                    }, indent=4, sort_keys=True, default=str)}
    except BaseException as err:
        print(err);
        return {"success" : True , "data":json.dumps({
            "coinName" : item.coin,
            "time": {}
        }, indent=4, sort_keys=True, default=str)}

# getJsonCoin
# def handleOpenTrade(coins , strategy):
#     # _finally = [{'long' : True , 'time':"2020/05/12T12:30:30" ,'coin': "ADA/USDT" , 'entry':0.9}]
#     _finally = []
#     time = ''
#     for coin in coins:
#         print(coin)
#         df = common.get_asset("bybit" , 1 , coin , strategy['timeFrame'])
#         if(strategy['chartType'] == "Heikin Ashi"):
#             df.ta.ha(append=True)
#             df.drop(['open','low','close', 'high'], axis=1, inplace=True)
#             df.rename(columns={'HA_open' : "open" , 'HA_close' : "close" , 'HA_high' : 'high' , 'HA_low' : "low"} ,  inplace=True)
#         analys = bot.callFuncs(df ,strategy)
#         if(analys is not None):
#             if(analys['long']):
#                 _finally.append({'long' : True , 'time':analys['time'] ,'coin': coin , 'entry':df.iloc[-1]['close']})
#             if(analys['short']):
#                 _finally.append({'short' : True , 'time':analys['time'] ,'coin': coin , 'entry':df.iloc[-1]['close']})
#             time = df.iloc[-1]['time']
#     _json = json.dumps({"signals" : _finally , 'time' : time}, indent=4, sort_keys=True, default=str)
#     requests.post("https://phoenixcrypto.vercel.app/api/tel/send" , data=_json)
#     print('sent' , _finally)
# "BTC/USDT:USDT,ADA/USDT,SOL/USDT,ETH/USDT,LUNA/USDT,MATIC/USDT,1INCH/USDT,AAVE/USDT,ALGO/USDT,ANKR/USDT,APE/USDT,AR/USDT,ATOM/USDT,AUDIO/USDT,AVAX/USDT,AXS/USDT,BAT/USDT,BCH/USDT,BNB/USDT,BTC/USDT,BTT/USDT,CAKE/USDT,CELO/USDT,CHZ/USDT,COMP/USDT,CRO/USDT,DASH/USDT,DGB/USDT,EGLD/USDT,ENJ/USDT,ENS/USDT,EOS/USDT,ETC/USDT,ETH/USDT,FIL/USDT,FLOW/USDT,FTM/USDT,FTT/USDT,GALA/USDT,GMT/USDT,GRT/USDT,HBAR/USDT,HNT/USDT,HOT/USDT,ICP/USDT,ICX/USDT,IMX/USDT,IOST/USDT,IOTA/USDT,IOTX/USDT,KAVA/USDT,KDA/USDT,KLAY/USDT,KSM/USDT,LINK/USDT,LPT/USDT,LRC/USDT,LTC/USDT,LUNA/USDT,LUNA/USDT,MANA/USDT,MATIC/USDT,MINA/USDT,MKR/USDT,NEAR/USDT,NEO/USDT,NFT/USDT,OCEAN/USDT,OMG/USDT,ONE/USDT,ONT/USDT,QNT/USDT,QTUM/USDT,REN/USDT,RNDR/USDT,ROSE/USDT,RSR/USDT,RUNE/USDT,SAND/USDT,SCRT/USDT,SC/USDT,SHIBA/USDT,SKL/USDT,SNX/USDT,SOL/USDT,SRM/USDT,STORJ/USDT,STX/USDT,SUSHI/USDT,SXP/USDT,THETA/USDT,UNI/USDT,WAVES/USDT,WAXP/USDT,WOO/USDT,XEC/USDT,XEM/USDT,XLM/USDT,XMR/USDT,XRP/USDT,XTZ/USDT,YFI/USDT,YGG/USDT,ZEC/USDT,ZEN/USDT,ZIL/USDT,ZRX/USDT"

# timeFrames = {'1d' : 24 * 60 * 60 , '2d' : 48 * 60 * 60  , '3d' : 72 * 60 * 60 , '1h': 60 * 60 , '2h' : 120 * 60 , '3h': 180 * 60  , '4h': 240 * 60  , '5h': 300 * 60  , '6h': 360 * 60  , '7h': 420 * 60  , '8h': 480 * 60 , '9h':540*60 , '10h':600*60,'11h':660*60,'12h': 720*60,'30m' : 30 , '15m' : 15 , '1m' : 1 , '5m' : 5}
# api key : PKQ4ZQ0H9JO6OUX8P2G5
# secret : i3C5GFFqGbWDMbbOLtvOrCwOUDOtadwIc58w67ye