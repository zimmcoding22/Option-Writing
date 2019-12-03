import pandas as pd
import numpy as np
from time import sleep

data = pd.read_csv("naked_options_database.csv", delim_whitespace=True, header=None)
data.columns = (["Date", "Underlying", "OpeningGap", "AverageEntry", "AverageExit", "Share Price",
                 "Strike", "Right", "Volume", "OpenInterest", "Delta", "Gamma", "Theta", "Vega",
                 "InitialPremium", "DTE", "TimeOfEntry", "DayHighLow", "IVR", "VIX"])


def dollar_gain_loss(multiple_one, multiple_two):
    gain_loss = 0
    change = round(percentChange(row["AverageEntry"], row["AverageExit"]), 0)
    if (float(row["InitialPremium"]) < .4):
        gain_loss+=(float(row["AverageEntry"]) * change) * multiple_one
    elif (float(row["InitialPremium"]) < .7 and float(row["InitialPremium"]) > .4):
        gain_loss+=(float(row["AverageEntry"]) * change) * multiple_two
    else:
        gain_loss+=(float(row["AverageEntry"]) * change)
    return(gain_loss)

def percentChange(previous, current):
    if (previous == 0 or current == 0):
        return(0)
    if (current > previous):
        change_percentage = ((current - previous)/previous) * 100 * -1
    else:
        change_percentage = ((previous - current)/previous) * 100 
    return(change_percentage)


final_dollar_amount, wins, losses, dollar_wins, dollar_losses = 0, 0, 0, 0, 0
for index, row in data.iterrows():
    entries = str(row["TimeOfEntry"])
    entries = entries.split('/')
    if (len(entries) == 1):
        dollars_collected = dollar_gain_loss(3, 2)
        if (dollars_collected > 0):
            dollar_wins+=dollars_collected
        elif (dollars_collected < 0):
            dollar_losses+=abs(dollars_collected)
        else:

            
            pass
        final_dollar_amount+=dollars_collected
    else:
        dollars_collected = dollar_gain_loss(6, 4)
        if (dollars_collected > 0):
            dollar_wins+=dollars_collected
        elif (dollars_collected < 0):
            dollar_losses+=abs(dollars_collected)
        else:
            pass
        final_dollar_amount+=dollars_collected
    if (round(percentChange(row["AverageEntry"], row["AverageExit"]), 0) > 0):
        wins+=1
    elif (round(percentChange(row["AverageEntry"], row["AverageExit"]), 0) < 0):
        losses+=1
    else:
        pass

num_trades = len(data)
risk_reward_ratio = (dollar_wins/num_trades)/(dollar_losses/num_trades)
average_win, average_loss = dollar_wins/num_trades, dollar_losses/num_trades
win_rate = round((wins/(wins + losses)) * 100, 2)
loss_rate = round(100 - win_rate, 2)
print("average dollar gain: %.2f average dollar loss: %.2f" % (average_win, average_loss))
print("risk reward ratio: %.2f" % (risk_reward_ratio))
print("win rate: %.2f: " % (win_rate))
print("expectancy: %.2f" % (((win_rate/100) * risk_reward_ratio) - ((loss_rate/100) * 1)))
print("approx dollars gained so far: %.2f" % (final_dollar_amount))


pd.options.display.float_format = '{:,.2f}'.format
#print(data.corr())
