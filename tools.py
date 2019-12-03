from datetime import datetime
from ibapi.contract import *

class Tools():

    def __init__(self):
        pass

    #returns number of days till expiration for selected option chain
    def findNumberOfDays(self, starting_date, ending_date):
        format_ = "%Y%m%d"
        self.start = datetime.strptime(starting_date, format_)
        self.end = datetime.strptime(ending_date, format_)
        self.delta = self.end - self.start
        return(self.delta.days)


    def createContract(self, ticker, sec_type, exp, strike, right):
        contract = Contract()
        exchange = self.getExchange(ticker)
        contract.symbol = ticker
        contract.exchange = exchange
        contract.primaryExch = exchange
        contract.currency = "USD"
        contract.secType = sec_type
        if (sec_type == "OPT"):
            contract.lastTradeDateOrContractMonth = exp
            contract.strike = strike
            contract.right = right
            contract.multiplier = 100
        return(contract)


    def getExchange(self, ticker):
        island, nyse = ["MSFT"], []
        if (ticker in island):
            return("ISLAND")
        elif (ticker in nyse):
            return("NYSE")
        else:
            return("SMART")


    #premium inflating is represented as a signed value
    def percentChange(self, previous, current):
        if (previous == 0 or current == 0):
            return(0)
        if (current > previous):
            self.change_percentage = ((current - previous)/previous) * 100 * -1
        else:
            self.change_percentage = ((previous - current)/previous) * 100 
        return(self.change_percentage)
