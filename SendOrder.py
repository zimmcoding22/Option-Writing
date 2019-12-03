import pandas as pd
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.order import (OrderComboLeg, Order)


class SendOrder():

    gamma, theta, vega, sell_leg_bid, buy_leg_ask = .056, .300, .030, .30, .18
    #gamma, theta, vega, sell_leg_bid, buy_leg_ask = .046, .300, .040, .30, .18
    ask_ = 1
    
    def __init__(self, option_chain, expiration, account_size):
        self.option_chain = option_chain
        self.expiration = expiration
        self.account_size = account_size
        self.checkCriteria()

    #return list of acceptable spreads. returns empty list if none are suitable
    def checkCriteria(self):
        print("inside check criteria")
        spreads = {}
        sell_leg = 0, 0
        #sell leg
        for index, row in self.option_chain.iterrows():
            print(row["vega"], row["gamma"], row["theta"], row["bid"])
            if (row["bid"] is None or row["bid"] is -1):
                continue
            if (row["bid"] > self.sell_leg_bid and row["vega"] >= self.vega and row["gamma"] <= self.gamma and abs(row["theta"]) <= self.theta):
                sell_leg = row["strike"]
                #buy leg
                for index, row in self.option_chain[::-1].iterrows():
                    if (row["ask"] < self.buy_leg_ask):
                        spreads.update({str(sell_leg) + ', ' + str(row["strike"]) : [0, 0, 0]})
        print("displaying spread dict being returned in sendOrder")
        print(spreads)
        return(spreads)

            
    def findNumberOfContracts(self, ask):
        max_risk = self.account_size * .005 #risking half percent with this strategy to allow for up to 2 positions
        stop_loss = .20
        position_size = max_risk/stop_loss
        premium = ask * .25 + ask
        num_contracts = int(position_size/premium)
        print("number of contracts needed to risk %.2f: %d" % (max_risk, num_contracts))
        return(num_contracts)
            

   
 
