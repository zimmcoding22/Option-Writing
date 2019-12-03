from ibapi import wrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper #just for decorator
from ibapi.common import *
from ibapi.contract import *
from ibapi.ticktype import *
from ibapi.order_state import OrderState
from ibapi.order import (OrderComboLeg, Order)
from time import sleep
import time
import sys
import pandas as pd
from functools import reduce
from datetime import datetime
from tools import Tools
from operations import Operations

class TestApp(wrapper.EWrapper, EClient):
    
    def __init__(self):
        wrapper.EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.reqIsFinished = True
        self.started = False
        #self.nextValidOrderId = 0
        #self.nextValidId()

    @iswrapper
    def nextValidId(self, orderId:int):
        global order_id
        print("setting nextValidOrderId: %d", orderId)
        order_id = orderId
        # we can start now

    @iswrapper
    def error(self, reqId:TickerId, errorCode:int, errorString:str):
        print("Error. Id: " , reqId, " Code: " , errorCode , " Msg: " , errorString)
        if (errorString == "No security definition has been found for the request"):
            error_list.append(reqId)

    @iswrapper
    def contractDetails(self, reqId, contractDetails):
        global leg__
        leg = leg__
        if (reqId == request_id):
            print(reqId, contractDetails.contract.conId)
            legs[leg] = contractDetails.contract.conId

    @iswrapper
    def contractDetailsEnd(self, reqId: int):
        print("contract details id end")
        contract_details.append(reqId)
        self.done = True

    @iswrapper
    def securityDefinitionOptionParameter(self, reqId: int, exchange: str, underlyingConId: int, tradingClass: str, multiplier: str, expirations: SetOfString, strikes: SetOfFloat):
        #super().securityDefinitionOptionParameter(reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes)
        if (reqId == index):
            contracts.loc[reqId, ["strikes"]] = str(sorted(strikes))
            contracts.loc[reqId, ["expirations"]] = str(sorted(expirations))
            #self.done = True
            
    @iswrapper
    def symbolSamples(self, reqId: int, contractDescriptions: ListOfContractDescription):
        #super().symbolSamples(reqId, contractDescriptions)
        #if (reqId == index):
        for contractDescription in contractDescriptions:
            derivSecTypes = ""
            for derivSecType in contractDescription.derivativeSecTypes:
                derivSecTypes += derivSecType
                derivSecTypes += " "
                if (contractDescription.contract.symbol == row["ticker"]):
                    contracts.loc[reqId, ["con_id"]] = int(contractDescription.contract.conId)
        #if (row["con_id"] is not None):
            #self.done = True

    @iswrapper
    def tickOptionComputation(self, reqId: TickerId, tickType: TickType, impliedVol: float, delta: float, optPrice: float, pvDividend: float, gamma: float, vega: float, theta: float, undPrice: float):
        #super().tickOptionComputation(reqId, tickType, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice)
        global current_delta
        if (opt_data):
            if (reqId == strike_index):
                received_list.append(reqId)
                if (tickType == TickTypeEnum.MODEL_OPTION):
                    print("delta: ", delta)
                    temp_df.loc[reqId, ["delta"]] = round(delta, 10)
                    current_delta = abs(delta)
                    temp_df.loc[reqId, ["gamma"]] = round(gamma, 10)
                    temp_df.loc[reqId, ["theta"]] = round(theta, 10)
                    temp_df.loc[reqId, ["vega"]] = round(vega, 10)
                    temp_df.loc[reqId, ["implied_volatility"]] = round(impliedVol, 10)
                    #self.done = True
                
    @iswrapper
    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        #super().tickPrice(reqId, tickType, price, attrib)
        if (not opt_data):
            if (reqId == index):
                if (tickType == TickTypeEnum.LAST):
                    contracts.loc[reqId, ["stock_last"]] = price   
        else:
            if (not spreads):
                if (reqId == strike_index):
                    if (tickType == TickTypeEnum.BID):
                        print("bid: ", price)
                        temp_df.loc[reqId, ["bid"]] = price 
                    if (tickType == TickTypeEnum.ASK):
                        print("ask: ", price)
                        temp_df.loc[reqId, ["ask"]] = price
            else:
                if (monitoring):
                    if (reqId == index):
                        if (right == 'C'):
                            if (tickType == TickTypeEnum.ASK):
                                contracts.loc[reqId, ["call_ask"]] = price
                            if (tickType == TickTypeEnum.ASK):
                                contracts.loc[reqId, ["call_bid"]] = price
                        else:
                            if (tickType == TickTypeEnum.ASK):
                                contracts.loc[reqId, ["put_ask"]] = price
                            if (tickType == TickTypeEnum.BID):
                                contracts.loc[reqId, ["put_bid"]] = price                                            
                else:
                    if (reqId == request_id):
                        print("spreads callback")
                        if (tickType == TickTypeEnum.BID):
                            print("bid: ", price)
                            spreads_dict[spread][bid_] = price
                        if (tickType == TickTypeEnum.ASK):
                            print("ask: ", price)
                            spreads_dict[spread][ask_] = price
                            
                            
    @iswrapper
    def tickSize(self, reqId: TickerId, tickType: TickType, size: float):
        if (opt_data):
            if (reqId == strike_index):
                if (tickType == TickTypeEnum.VOLUME):
                    temp_df.loc[reqId, ["volume"]] = size
                if (tickType == TickTypeEnum.OPTION_CALL_OPEN_INTEREST):
                    temp_df.loc[reqId, ["open_interest"]] = size
                if (tickType == TickTypeEnum.BID_SIZE):
                    temp_df.loc[reqId, ["bid_size"]] = size
                if (tickType == TickTypeEnum.ASK_SIZE):
                    temp_df.loc[reqId, ["ask_size"]] = size
                    
    @iswrapper
    def openOrder(self, orderId:OrderId, contract:Contract, order:Order, orderState:OrderState):
        global margin_impact
        margin_impact = float(orderState.initMarginChange)


def restart():
    global app
    app.done = True
    app = TestApp()
    app.connect("127.0.0.1", socket_port, clientId=123)

request_id = 1
order_id = 0
ticker = "GS"
side = "put"
client_id = 101
account_size = 100000
socket_port = 7497
market_data_type = 1
max_margin = 50000
error_list, received_list, contract_details = [], [], []
sell_leg_target, buy_leg_target = .2, .01
app = TestApp()
tools = Tools()
app.connect("127.0.0.1", socket_port, clientId=client_id)
print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                        app.twsConnectionTime()))
contracts = pd.DataFrame([[ticker, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, side]])
contracts.columns = ["ticker", "con_id", "stock_last", "put_bid", "put_ask", "put_contract","call_bid", "call_ask", "call_contract" , "strikes", "expirations", "delta", "gamma", "theta", "vega", "volume", "open_interest", "implied_volatility", "num_contracts", "direction"]
start = time.time()

app.reqIds(1)
app.run()
print("next order id: " , order_id)

#get con ids/expirations
finished = False
print("requesting con ids")
while (not finished):
    print(contracts)
    finished = True
    for index, row in contracts.iterrows():
        print(row["ticker"])
        if (row["con_id"] is None):
            finished = False
            app.reqMatchingSymbols(index, row["ticker"])
            app.run()
            restart()
print("requesting strikes and expirations")
finished  = False
while (not finished):
    finished = True
    for index, row in contracts.iterrows():
        if (row["strikes"] is None):
            finished = False
            app.reqSecDefOptParams(index, row["ticker"] ,"", "STK", row["con_id"])
            app.run()
            restart()
print("requesting stock last")
finished, opt_data = False, False
exchange = "SMART"
while (not finished):
    finished = True
    for index, row in contracts.iterrows():
        if (row["stock_last"] is None):
            finished = False
            contract = tools.createContract(row["ticker"], "STK", '', '', '')
            app.reqMarketDataType(market_data_type)
            app.reqMktData(index, contract, '', False, False, [])
            app.run()
            restart()
            
#determine correct expirations and replace list of expirations with chosen expiration
min_days_till_expiration, max_days_till_expiration = 3, 9
if (ticker == "AMZN"):
    min_buy_wing_delta = .002
else:
    min_buy_wing_delta = .001
replacements = ('\'', ''), ('{', ''), ('}', ''), (' ', ''), ('[', ''), (']', '')
format_ = "%Y%m%d"
date = str(datetime.now())[:10].replace('-', '')
chosen_expiration = ""
for index, row in contracts.iterrows():
    expirations_list = reduce(lambda key, replacement: key.replace(*replacement), replacements, row["expirations"]).split(',')
    row["expirations"] = []
    print(row["expirations"])
    for exp in expirations_list:
        days_till_expiration = tools.findNumberOfDays(date, exp)
        if (days_till_expiration >= min_days_till_expiration and days_till_expiration <= max_days_till_expiration):
            row["expirations"].append(exp)

for index, row in contracts.iterrows():
    print(index, row) 

outer_start = time.time()
#for each underlying, for each expiration, load in full options chain until appropriate combo is found
monitoring = False
opt_data = True
for index, row in contracts.iterrows():
    inner_start = time.time()
    for exp in row["expirations"]:
        right = ''
        #calls on first iteration, puts on second. "both" feature is depricated, but I've left this code block here in case it makes sense to reimplement
        for i in range(2):
            if (i == 0 and (row["direction"] == "both" or row["direction"] == "call")):
                print("checking call side")
                right = 'C'
            elif (i == 0 and row["direction"] == "put"):
                continue
            elif (i == 1 and (row["direction"] == "both" or row["direction"] == "put")):
                print("checking put side")
                right = 'P'
            elif (i == 1 and row["direction"] == "call"):
                continue
            else:
                print("error")
                pass
            spreads = False
            strikes = [float(strike) for strike in row["strikes"].replace('[', '').replace(']', '').split(',')]
            starting_index = 0
            if (right == 'C'):
                for strike in strikes:
                    if (strike < row["stock_last"]):
                        starting_index+=1
                    else:
                        break
            else:
                strikes = strikes[::-1]
                for strike in strikes:
                    if (strike > row["stock_last"]):
                        starting_index+=1
                    else:
                        break
            temp_df  = pd.DataFrame([[]])
            current_delta = None
            for strike_index, strike in enumerate(strikes[starting_index:]):
                print("current delta: ", current_delta)
                if (current_delta is not None and current_delta <= min_buy_wing_delta):
                    print("last delta")
                    break
                if (temp_df.empty):
                    temp_df = pd.DataFrame([[strike, None, None, None, None, None, None, None, None, None, None, None]], columns = ["strike", "volume", "open_interest", "implied_volatility", "delta", "gamma", "theta", "vega", "bid", "bid_size", "ask", "ask_size"])
                else:
                    new_row = pd.DataFrame([[strike, None, None, None, None, None, None, None, None, None, None, None]], columns = ["strike", "volume", "open_interest", "implied_volatility", "delta", "gamma", "theta", "vega", "bid", "bid_size", "ask", "ask_size"])
                    temp_df = temp_df.append(new_row, ignore_index=True)
                finished = False
                while (not finished):
                    print("requesting data for %s at %.2f for index: %d" % (row["ticker"], strike, strike_index))
                    if (strike_index in error_list):
                        print("id in error list")
                        finished = True
                    elif (strike_index in received_list):
                        print("id has been received")
                        finished = True
                    else:
                        print("right ", right)
                        contract = tools.createContract(row["ticker"], "OPT", exp, strike, right) 
                        print(contract)
                        app.reqMarketDataType(market_data_type)
                        app.reqMktData(strike_index, contract, "101", False, False, [])
                        app.run()
                        restart()
            if (right == 'C'):
                print("displaying data for calls for %s" % (row["ticker"]))
            if (right == 'P'):
                print("displaying data for puts")
            for strike_index, row_ in temp_df.iterrows():
                if (row_["delta"] == None):
                    continue
                if (strike_index in error_list or abs(row_["delta"]) <= min_buy_wing_delta or abs(row_["delta"]) > .2):
                    temp_df.drop(strike_index, inplace=True)
            for strike_index, row_ in temp_df.iterrows():
                print(strike_index, row_)
            #at this point, should have all data for calls for this underlying. Do analysis/select strikes and determine number of contracts here before moving on to next underlying
            #sell leg rules: gamma less than .046, vega greater than .040, sub 20 delta, sub 20 theta (this can wiggle but must be sub 20 delta)
            send_order = Operations(temp_df, exp, account_size)
            spreads_dict = send_order.checkCriteria()
            #stop at first spread that satisfies margin impact
            print("looking for spreads")
            print(row["ticker"])
            sell_leg, buy_leg = 0, 1
            bid_, ask_, contract_ = 0, 1, 2
            print(spreads_dict)
            spreads = True
            for strike_index, (spread, values) in enumerate(spreads_dict.items()):
                print("showing spread/bid_ask/contract for %s" % (right))
                print(spread, values)
                legs = {}
                leg1 = tools.createContract(row["ticker"], "OPT", exp, float(spread.split(',')[sell_leg]), right)
                legs.update({leg1 : 0})
                leg2 = tools.createContract(row["ticker"], "OPT", exp, float(spread.split(',')[buy_leg]), right)
                legs.update({leg2 : 0})
                for leg, conid in legs.items():
                    print("leg check one: ", leg, "con id: ", conid)
                    received = False
                    while (not received):
                        leg__ = leg
                        app.reqContractDetails(request_id, leg)
                        app.run()
                        restart()
                        received = True
                        if (request_id not in contract_details):
                            print("foo")
                            received = False
                        request_id+=1
                    print("leg check two: ", leg, "con id: ", conid)
                error_list.clear()
                received_list.clear()
                contract_details.clear()
                for i in range(3):
                    if (values[bid_] != 0 and values[ask_] != 0):
                        break
                    elif (strike_index in error_list):
                        break
                    else:
                        print("showing legs dict before data requests")
                        for con, id_ in legs.items():
                            print(con, id_)
                        contract = tools.createContract(row["ticker"], "BAG", '', '', '')
                        exchange = tools.getExchange(row["ticker"])
                        leg1_combo = ComboLeg()
                        leg1_combo.conId = legs[leg1]
                        print("leg one con id: ", legs[leg1])
                        leg1_combo.ratio = 1
                        leg1_combo.action = "SELL"
                        leg1_combo.exchange = exchange
                        leg2_combo = ComboLeg()
                        leg2_combo.conId = legs[leg2]
                        leg2_combo.ratio = 1
                        leg2_combo.action = "BUY"
                        leg2_combo.exchange = exchange
                        contract.comboLegs = []
                        contract.comboLegs.append(leg1_combo)
                        contract.comboLegs.append(leg2_combo)
                        values[contract_] = contract
                        app.reqMarketDataType(market_data_type)
                        print("displaying combo leg contract: ", contract)
                        app.reqMktData(request_id, contract, "", False, False, [])
                        app.run()
                        restart()
            #all acceptable spreads should have market data
            for spread, value in spreads_dict.items():
                print(spread, " : ", value)
            error_list.clear()
            contract_details.clear()
            #check margin impact. spreads start from best to worst. select first spread that satisfies margin (less than or equal to max_margin)
            margin_impact = 0
            for spread, values in spreads_dict.items():
                current_margin_impact = margin_impact
                while (current_margin_impact == margin_impact):
                    app.reqIds(1)
                    app.run()
                    app.done = True
                    restart()
                    order = Order()
                    order.action = "BUY"
                    order.orderType = "LMT"
                    print("ask: ", values[ask_])
                    print("contract: ", values[contract_])
                    order.totalQuantity = send_order.findNumberOfContracts(abs(values[ask_]) * 100)
                    print("total number of contracts: ", order.totalQuantity)
                    order.lmtPrice = 0
                    order.whatIf = True
                    print("margin order id: ", order_id)
                    app.placeOrder(order_id, values[contract_], order)
                    app.run()
                    app.done = True
                    order_id+=1
                    restart()
                    print("current margin impact: ", margin_impact)
                    print("current spread: ", spread)
                print("spread bid: ", spread[bid_])
                if (margin_impact != 0 and margin_impact <= account_size/1.8 and spread[bid_] != 0): #1.8 because there should be some excess cash in the account
                    print("selected spread: ", spread, " number of contracts: ", order.totalQuantity)
                    row["num_contracts"] = order.totalQuantity
                    print("spread bid: ", values[bid_])
                    spread = spread.split(',')
                    if (right == 'C'):
                        row["call_bid"], row["call_ask"], row["call_contract"], row["expirations"] = spread[bid_], spread[ask_], values[contract_], exp
                    else:
                        row["put_bid"], row["put_ask"], row["put_contract"], row["expirations"]  = spread[bid_], spread[ask_], values[contract_], exp
                    break #this is the end of the spread search phase
    inner_end = time.time()
    inner_time_elapsed = inner_end = inner_start
    print("time elapsed for %s" % (row["ticker"]))

print("showing dataframe with bids/asks")
for index, row in contracts.iterrows():
    print(index, row)
outer_end = time.time()
outer_time_elapsed = outer_end - outer_start
print("total time elapsed: %.2f min" % (outer_time_elapsed/60))


#start monitoring chosen spread. #as of now, leaving dataframe, but there will always be only one row

try:
    position_size = contracts.loc[0, ["num_contracts"]].values[0]
    if (row["direction"] == "call"):
        strike = float(contracts.loc[0, ["call_bid"]].values[0])
        contracts.loc[0, ["call_ask"]] = None
        expiration = contracts.loc[0, ["expirations"]].values[0]
        spread_contract = contracts.loc[0, ["call_contract"]].values[0]
        right = 'C'
    else:
        strike = float(contracts.loc[0, ["put_bid"]].values[0])
        contracts.loc[0, ["put_ask"]] = None
        expiration = contracts.loc[0, ["expirations"]].values[0]
        spread_contract = contracts.loc[0, ["put_contract"]].values[0]
        right = 'P'
except Exception as e: #no spread found
    print("no spread found")
    sys.exit(0)
    

sell_column = ""
if (right == 'C'):
    sell_column = "call_ask"
    buy_column = "call_bid"
else:
    sell_column = "put_ask"
    buy_column = "put_bid"

print("beginning monitoring")
#store updated prices in call and put ask
for i in range(len(contracts)): #store sell leg ask in ask column
    contracts[sell_column].values[0] = -11
monitoring = True
initial_premium = -11
percentage_against_entry = 0
while (monitoring):
    date = str(datetime.now())[11:16]
    if (date == "10:59" or date == "11:00"):
        print("out of time. exiting")
        monitoring = False
        break
    for index, row in contracts.iterrows(): #if we leave this system as one underlying per script, all of these loops will become unecessary
        #find percent difference between initial premium and current ask
        if (row[sell_column] != -11):
            if (initial_premium == -11):
                initial_premium = row[sell_column]
                print("initial premium: ", initial_premium, " call ask: ", row[sell_column])
                #all data aside from time of entry, time of exit, daily range, and IVR can be logged at this point
            percent_difference = round(tools.percentChange(initial_premium, row[sell_column]), 2)
            print("percent difference between initial premium and current premium: ", percent_difference)
            #if ((percent_difference < 0 and abs(percent_difference) >= percentage_against_entry) or date == "11:30"):
            if (abs(percent_difference) >= percentage_against_entry):
                #request bid for spread
                print("requesting spread bid")
                for i in range(len(contracts)): #store sell leg ask in ask column
                    contracts[buy_column].values[0] = -11 #sometimes TWS spits back -1, and can't use None with dataframe
                while (row[buy_column] == -11): #at this point, the buy column is the spread bid
                    app.reqMktData(index, spread_contract, "", False, False, [])
                    app.run()
                    restart()
                #send spread bid
                print("placing bed for spread")
                print("bid: ", row[buy_column])
                order = Order()
                order.action = "BUY"
                order.orderType = "LMT"
                order.totalQuantity = position_size
                order.lmtPrice = row[buy_column] - .10 #temporary - .10 for testing
                print("limit price: ", order.lmtPrice)
                order.transmit = True #TODO - orders require manual transmit even with flag set to True
                order.whatIf = False 
                app.placeOrder(order_id, spread_contract, order)
                app.run()
                app.done = True
                order_id+=1
                print("exiting loop")
                monitoring = False #end of script. At this point, either we have timed out, or an order has been sent
        contract = tools.createContract(row["ticker"], "OPT", expiration, strike, right)
        app.reqMktData(index, contract, '', False, False, [])
        app.run()
        restart()
