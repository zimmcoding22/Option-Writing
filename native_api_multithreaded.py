from ibapi import wrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper #just for decorator
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import * 
from time import sleep
import time
import pandas as pd
import threading
import math


class TestApp(wrapper.EWrapper, EClient):
    def __init__(self):
        wrapper.EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.reqIsFinished = True
        self.started = False
        self.nextValidOrderId = 0

    @iswrapper
    def nextValidId(self, orderId:int):
        print("setting nextValidOrderId: %d", orderId)
        # we can start now

    @iswrapper
    def error(self, reqId:TickerId, errorCode:int, errorString:str):
        pass
        print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " ,     errorString)

    @iswrapper
    # ! [contractdetails]
    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        super().contractDetails(reqId, contractDetails)
##        print("ContractDetails. ReqId:", reqId, contractDetails.summary.symbol,
##              contractDetails.summary.secType, "ConId:", contractDetails.summary.conId,
##          "@", contractDetails.summary.exchange)
        # ! [contractdetails]

    @iswrapper
    # ! [contractdetailsend]
    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)
        print("ContractDetailsEnd. ", reqId, "\n")
        self.done = True  # This ends the messages loop
        # ! [contractdetailsend]

    @iswrapper
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        #super().tickPrice(reqId, tickType, price, attrib)
        #print("callback")
        for i in range(len(contracts)):
            fields = [[TickTypeEnum.LAST, "last"], [TickTypeEnum.BID, "bid"], [TickTypeEnum.ASK, "ask"], [TickTypeEnum.HIGH, "high"], [TickTypeEnum.LOW, "low"]]
            for field in fields:
                store_data(field, i, contracts, tickType, reqId, price)


def store_data(field, idx, df, ticker_type, req_id, price):
    tt, col = 0, 1
    if (ticker_type == field[tt]):
        if (req_id == idx):
            if (isinstance(df, pd.DataFrame)):
                lock.acquire()
                df.loc[idx, [field[col]]] = price
                lock.release()
            else:
                print("this isn't a dataframe")    

def function(ticker, app, id_):
    global num_requests
    for i in range(1):
        contract = Contract()
        contract.symbol = ticker
        contract.secType = "STK"
        contract.currency = "USD"
        contract.exchange = "SMART"
        lock.acquire()
        num_requests+=1
        lock.release()
        app.reqMarketDataType(market_data_type)
        #print("ticker id: ", id_)
        #print(contract)
        app.reqMktData(id_, contract, "", False, False, [])
        app.run()
        app.done = True
    
socket_port = 4000
ticker_id = 0
contracts = pd.DataFrame([["AAPL", None, None, None, None, None], ["FB", None, None, None, None, None], ["CMG", None, None, None, None, None], ["GOOG", None, None, None, None, None], ["BMY", None, None, None, None, None],
                          ["F", None, None, None, None, None], ["W", None, None, None, None, None], ["ETSY", None, None, None, None, None], ["LMT", None, None, None, None, None], ["DAL", None, None, None, None, None],
                          ["LUV", None, None, None, None, None], ["RTN", None, None, None, None, None], ["AMZN", None, None, None, None, None], ["NKE", None, None, None, None, None], ["BBY", None, None, None, None, None],
                          ["BBBY", None, None, None, None, None], ["CRON", None, None, None, None, None], ["CRM", None, None, None, None, None], ["BABA", None, None, None, None, None], ["MU", None, None, None, None, None]])
contracts.columns = ["ticker", "bid", "ask", "last", "high", "low"]
start_time = time.time()
market_data_type = 2
num_requests = 0

app = TestApp()
app.connect("127.0.0.1", socket_port, clientId=123)
#app.disconnect()
print(app.isConnected())
lock = threading.Lock()
jobs = []

for index, row in contracts.iterrows():
    thread = threading.Thread(target=function, args=(row["ticker"], app, index))
    thread.start()
    jobs.append(thread)


print(jobs)


for j in jobs:
    j.join()

print("total num requests: ", num_requests)
##thread_one = threading.Thread(target=function, args=(contracts.loc[0, ["ticker"]].values[0], app, 0))
##thread_two = threading.Thread(target=function, args=(contracts.loc[2, ["ticker"]].values[0], app, 2))
##thread_one.start()
##thread_two.start()
###app.done = True
##thread_one.join()
##thread_two.join()

    
##    function(row["ticker"], app, index)
##    app.run()
    #app.done = True
    #app = TestApp()
    #app.connect("127.0.0.1", socket_port, clientId=123)
    
end_time = time.time()
final = end_time - start_time
print("total time elapsed: %.2f" % (final))
print(contracts)


