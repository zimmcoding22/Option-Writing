#python queries to analyze data set

import numpy as np
import pandas as pd
from time import sleep
import re
from matplotlib import pyplot as plt
from datetime import datetime

df = pd.read_csv("naked_options_database.csv", delim_whitespace=True, header=None)
df.columns = ["date", "underlying", "opening_gap", "average_entry", "average_exit", "share_price", "strike",
           "right", "volume", "open_interest", "delta", "gamma", "theta", "vega", "initial_premium",
           "dte", "entry_time", "high_low", "ivr", "vix"]

#this function accounts for the fact that a higher premium is a loss
def percentChange(previous, current):
    if (previous == 0 or current == 0):
        return(0)
    if (current > previous):
        change_percentage = ((current - previous)/previous) * 100 * -1
    else:
        change_percentage = ((previous - current)/previous) * 100 
    return(change_percentage)

def winRates(column, split_range):
    above_wins, below_wins = 0, 0
    above_total, below_total = 0, 0
    for index, row in df.iterrows():
        if (row[column] == "None"):
            continue
        position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
        if (float(row[column]) >= split_range):
            if (position_change > 0):
                above_wins+=1
                above_total+=1
            else:
                above_total+=1
        else:
            if (position_change > 0):
                below_wins+=1
                below_total+=1
            else:
                below_total+=1
    above_win_rate = (above_wins/above_total) * 100
    below_win_rate = (below_wins/below_total) * 100
    print("win rate for %s above %.3f: %.2f percent out of %d trades" % (column, split_range, above_win_rate, above_total))
    print("win rate for %s below %.3f: %.2f percent out of %d trades" % (column, split_range, below_win_rate, below_total))
    
##for index, row in df.iterrows():
##    print(index, row)

#example query
##gain_loss_actual = []
##for index, row in df.iterrows():
##    gain_loss_actual.append(int(round(percentChange(row["average_entry"], row["average_exit"]), 0)))
##
##actual_total = 0
##for num in gain_loss_actual:
##    actual_total+=num
##print("percentage points gained/lost: %d" % (actual_total))

#most positions enter earlier in the morning, but there is an assumption that the daily range is the same as the range starting from our entry poin
#percentage change from average exit to low of daily range
exit_to_low_percentages = []
win_loss_percentages = []
for index, row in df.iterrows():
    change = round(percentChange(row["average_entry"], row["average_exit"]), 0)
    if (row["high_low"] == "None" or row["average_exit"] == "None" or change <= 0):
        continue
    low = str(row["high_low"])
    low = low.split('/')
    low = float(low[1])
    exit_ = row["average_exit"]
    exit_to_low_percentages.append(round(percentChange(exit_, low) * -1, 0))
total = 0
for value in exit_to_low_percentages:
    total+=value
print("average percentage change from exit to daily range low for winners: %.2f" %(total/len(exit_to_low_percentages)))

          
#find average percentage between entry and daily high for both winners and losers
high_winners, high_losers, high_combined = [], [], []
low_winners, low_losers, low_combined = [], [], []
num_trades = 0
for index, row in df.iterrows():
    if (row["high_low"] == "None" or row["average_exit"] == "None" or ('/' in row["entry_time"])):
        continue
    high_low = str(row["high_low"])
    high_low = high_low.split('/')
    high = float(high_low[0])
    low = float(high_low[1])
    high_percentage = abs(percentChange(row["average_entry"], high))
    low_percentage = abs(percentChange(row["average_entry"], low))
    #omit outliers based on histogram
    if (high_percentage < 400):
        high_combined.append(high_percentage)
        low_combined.append(low_percentage)
    if (percentChange(row["average_entry"], row["average_exit"]) >= 0 and high_percentage < 300):
        high_winners.append(high_percentage)
        low_winners.append(low_percentage)
    if (percentChange(row["average_entry"], row["average_exit"]) < 0 and high_percentage < 300):
        high_losers.append(high_percentage)
        low_losers.append(low_percentage)
    num_trades+=1
print("num trades: ", num_trades)
winners_total = 0
for win in high_winners:
    winners_total+=win
losers_total = 0
for loss in high_losers:
    losers_total+=loss
combined_total = 0
for trade in high_combined:
    combined_total+=trade
print("average percent difference from average entry to high of the day for winners: %.2f" % (winners_total/len(high_winners)))
print("average percent difference from average entry to high of the day for losers: %.2f" % (losers_total/len(high_losers)))
print("average percent difference from average entry to high of the day for combined: %.2f" % (combined_total/len(high_combined)))
winners_total = 0
for win in low_winners:
    winners_total+=win
losers_total = 0
for loss in low_losers:
    losers_total+=loss
combined_total = 0
for trade in low_combined:
    combined_total+=trade
print("average percent difference from average entry to low of the day for winners: %.2f" % (winners_total/len(low_winners)))
print("average percent difference from average entry to low of the day for losers: %.2f" % (losers_total/len(low_losers)))
print("average percent difference from average entry to low of the day for combined: %.2f" % (combined_total/len(low_combined)))
#combined_winners_losers = winners + losers
#plt.hist(combined_winners_losers)
#plt.title("combined")
#plt.show()
plt.hist(high_winners)
plt.title("winners")
#plt.show()
##plt.hist(losers)
##plt.title("losers")
##plt.show()
#call vs put win rate
calls, puts = 0, 0
call_wins, put_wins = 0, 0
for index, row in df.iterrows():
    if (row["right"] == 'C'):
        if (percentChange(row["average_entry"], row["average_exit"]) > 0):
            calls+=1
            call_wins+=1
        else:
            calls+=1
    if (row["right"] == 'P'):
        if (percentChange(row["average_entry"], row["average_exit"]) > 0):
            puts+=1
            put_wins+=1
        else:
            puts+=1
print("call win rate: %.2f out of %d trades" % ((call_wins/calls) * 100, calls))
print("put win rate: %.2f out of %d trades" % ((put_wins/puts) * 100, puts))     


#greek win rates
print("ranges split by the median")
winRates("gamma", .046)
winRates("theta", .195)
winRates("vega", .041)
winRates("delta", .169)
winRates("dte", 4)#greater than or equal to 3
winRates("ivr", 31)
winRates("average_entry", .67)
winRates("vix", 16)

#win rate for one unit vs two
one_unit_total, one_unit_wins = 0, 0
two_unit_total, two_unit_wins = 0, 0
slash = '/'
target_names = ["BABA", "AAPL", "GS", "NVDA", "TSLA", "FB"]
for index, row in df.iterrows():
    if (row["underlying"] in target_names):
        position_change = percentChange(row["average_entry"], row["average_exit"])
        if (slash in row["entry_time"]):
            if (position_change > 0):
                two_unit_total+=1
                two_unit_wins+=1
            else:
                two_unit_total+=1
        else:
            if (position_change > 0):
                one_unit_total+=1
                one_unit_wins+=1
            else:
                one_unit_total+=1
one_unit_win_rate = (one_unit_wins/one_unit_total) * 100
two_unit_win_rate = (two_unit_wins/two_unit_total) * 100
print("one unit win rate: %.2f percent out of %d trades" % (one_unit_win_rate, one_unit_total))
print("two unit win rate: %.2f percent out of %d trades" % (two_unit_win_rate, two_unit_total))

gamma_vega_total, gamma_vega_wins = 0, 0
for index, row in df.iterrows():
    if (row["gamma"] == "None"):
        continue
    position_change = percentChange(row["average_entry"], row["average_exit"])
    if (float(row["gamma"]) <= .048 and float(row["vega"]) >= .040 and float(row["delta"]) <= .168):
        if (position_change > 0):
            gamma_vega_total+=1
            gamma_vega_wins+=1
        else:
            gamma_vega_total+=1
gamma_vega_win_rate = (gamma_vega_wins/gamma_vega_total) * 100
print("gamma vega delta win rate: %.2f percent out of %d trades" % (gamma_vega_win_rate, gamma_vega_total))

#find average % difference between share price and strike
average_total, average_sum = 0, 0
for index, row in df.iterrows():
    if (row["share_price"] == "None" or row["strike"] == "None"):
        continue
    average_total+=1
    average_sum+=abs(percentChange(float(row["share_price"]), float(row["strike"])))
average_percentage = average_sum/average_total
print("average percent difference from initial share price to strike price: %.2f" % (average_percentage))
#win rate by range
above_total, above_wins = 0, 0
below_total, below_wins = 0, 0
split_range = 2.78
for index, row in df.iterrows():
    if (row["share_price"] == "None" or row["strike"] == "None"):
        continue
    position_change = percentChange(row["average_entry"], row["average_exit"])
    share_strike_difference = abs(percentChange(float(row["share_price"]), float(row["strike"])))
    if (share_strike_difference > split_range):
        if (position_change > 0):
            above_total+=1
            above_wins+=1
        else:
            above_total+=1
    else:
        if (position_change > 0):
            below_total+=1
            below_wins+=1
        else:
            below_total+=1
above_win_rate = above_wins/above_total * 100
below_win_rate = below_wins/below_total * 100
print("win rate for strikes %.2f percent above the initial share price: %.2f out of %d trades" % (split_range, above_win_rate, above_total))
print("win rate for strikes %.2f percent below the initial share price: %.2f out of %d trades" % (split_range, below_win_rate, below_total))

#percentage of wins with 2 units that went above a certain amount
total_wins, total_wins_above_target = 0, 0
range_ = 40
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None"):
        continue
    position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
    slash = '/'
    if (slash in row["entry_time"]):
        if (position_change > 0):
            if (position_change > range_):
                total_wins+=1
                total_wins_above_target+=1
            else:
                total_wins+=1
above_target_win_rate = total_wins_above_target/total_wins * 100
print("percentage of wins with 2 units that made over %d percent: %.2f" % (range_, above_target_win_rate))
            
#win rate by time of entry
median = 59
above_total, above_wins = 0, 0
below_total, below_wins = 0, 0
start_time, format_ = "09:30", "%H:%M"
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None"):
        continue
    position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
    slash, entry_time = '/', row["entry_time"]
    if (slash in row["entry_time"]):
        entries = row["entry_time"].split('/')
        entry_time = entries[1]
    tdelta = datetime.strptime(entry_time, format_) - datetime.strptime(start_time, format_)
    minutes_from_entry = tdelta.seconds/60
    if (minutes_from_entry >= median):
        if (position_change > 0):
            above_total+=1
            above_wins+=1
        else:
            above_total+=1
    else:
        if (position_change > 0):
            below_total+=1
            below_wins+=1
        else:
            below_total+=1

above_win_rate = above_wins/above_total * 100
below_win_rate = below_wins/below_total * 100          
print("win rate for entries that were more than %d minutes after the open: %.2f out of %d trades" % (median, above_win_rate, above_total))
print("win rate for entries that were less than %d minutes after the open: %.2f out of %d trades" % (median, below_win_rate, below_total))

#win rate assuming right was in the direction of the opening gap (gapped down and wrote puts and vice versa)
right_direction_total, wrong_direction_total = 0, 0
right_direction_wins, wrong_direction_wins = 0, 0
small_gap_wins, big_gap_wins, small_gap_total, big_gap_total = 0, 0, 0, 0
gap_divider = .7
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None" or row["opening_gap"] == "None"):
        continue
    position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
    #if is in the right direction
    if ((row["opening_gap"] > 0 and row["right"] == 'C') or (row["opening_gap"] < 0 and row["right"] == 'p')):
        right_direction_total+=1
        if (position_change > 0):
            right_direction_wins+=1
    else:
        wrong_direction_total+=1
        if (position_change > 0):
            wrong_direction_wins+=1
            if (abs(row["opening_gap"]) <= gap_divider):
                small_gap_wins+=1
                small_gap_total+=1
            if (abs(row["opening_gap"]) > gap_divider):
                big_gap_wins+=1
                big_gap_total+=1
        else:
            if (abs(row["opening_gap"]) <= gap_divider):
                small_gap_total+=1
            if (abs(row["opening_gap"]) > gap_divider):
                big_gap_total+=1
            
right_direction_win_rate = right_direction_wins/right_direction_total * 100
wrong_direction_win_rate = wrong_direction_wins/wrong_direction_total * 100
small_gap_win_rate = small_gap_wins/small_gap_total * 100
big_gap_win_rate = big_gap_wins/big_gap_total * 100
print("win rate for rights in the same direction as the opening gap: %.2f out of %d trades" % (right_direction_win_rate, right_direction_total))
print("win rate for rights in the opposite direction as the opening gap: %.2f out of %d trades" % (wrong_direction_win_rate, wrong_direction_total))
print("win rate for opening gaps that were less than or equal to %.2f percent that opened in the opposite direction: %.2f out of %d trades" % (gap_divider, small_gap_win_rate, small_gap_total))
print("win rate for opening gaps that were greater than %.2f percent that opened in the opposite direction: %.2f out of %d trades" % (gap_divider, big_gap_win_rate, big_gap_total))
#calculate number of instance of each ticker
unique_tickers = {}
for index, row in df.iterrows():
    if (row["underlying"] not in unique_tickers):
        unique_tickers.update({row["underlying"] : 0})
print("unique tickers and their number of instances")
for index, row in df.iterrows():
    unique_tickers[row["underlying"]]+=1
for ticker, count in unique_tickers.items():
    print(ticker, ': ', count)

#"BABA", "AAPL", "GS", "FB", "TSLA"
target_names = ["BABA", "AAPL", "GS", "NVDA", "TSLA", "FB"]
target_name_wins, target_name_total_trades = 0, 0
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None" or row["opening_gap"] == "None"):
        continue
    position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
    if (row["underlying"] in target_names):
        if (position_change > 0):
            target_name_wins+=1
        target_name_total_trades+=1
target_win_rate = round((target_name_wins/target_name_total_trades) * 100, 2)
print("win rate for target name trades: %.2f out of %d trades" % (target_win_rate, target_name_total_trades))

wins, total = 0, 0
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None" or row["opening_gap"] == "None"):
        continue
    position_change = percentChange(row["average_entry"], row["average_exit"])
    if (abs(position_change) < 10):
        continue
    if (position_change > 0):
        total+=1
        wins+=1
    else:
        total+=1       
win_rate = (wins/total) * 100
print("win rate: %.2f percent out of %d trades" % (win_rate, total))

call_above_count, call_below_count, put_above_count, put_below_count = 0, 0, 0, 0
call_above_wins, call_below_wins, put_above_wins, put_below_wins = 0, 0, 0, 0
split_range = 15
for index, row in df.iterrows():
    position_change = percentChange(row["average_entry"], row["average_exit"])
    if (row["right"] == 'C' and row["vix"] > split_range):
        if (position_change > 0):
            call_above_wins+=1
        call_above_count+=1
    if (row["right"] == 'C' and row["vix"] < split_range):
        if (position_change > 0):
            call_below_wins+=1
        call_below_count+=1
    if (row["right"] == 'P' and row["vix"] > split_range):
        if (position_change > 0):
            put_above_wins+=1
        put_above_count+=1
    if (row["right"] == 'P' and row["vix"] < split_range):
        if (position_change > 0):
            put_below_wins+=1
        put_below_count+=1
call_below_win_rate = (call_below_wins/call_below_count) * 100
call_above_win_rate = (call_above_wins/call_above_count) * 100
put_above_win_rate = (put_above_wins/put_above_count) * 100
put_below_win_rate = (put_below_wins/put_below_count) * 100
print("win rate for calls above %d: %.2f out of %d trades" % (split_range, call_above_win_rate, call_above_count))
print("win rate for calls below %d: %.2f out of %d trades" % (split_range, call_below_win_rate, call_below_count))
print("win rate for puts above %d: %.2f out of %d trades" % (split_range, put_above_win_rate, put_above_count))
print("win rate for puts below %d: %.2f out of %d trades" % (split_range, put_below_win_rate, put_below_count))

split_range = 81
above_wins, above_total, below_wins, below_total = 0, 0, 0, 0
volume_exceeding_total = 0
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None" or row["open_interest"] == "None" or row["volume"] == "None"):
        continue
    position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
    if (float(row["open_interest"]) > float(row["volume"])):
        difference = abs(percentChange(float(row["open_interest"]), float(row["volume"])))
        if (difference > split_range):
            if (position_change > 0):
                above_wins+=1
            above_total+=1
        else:
            if (position_change > 0):
                below_wins+=1
            below_total+=1
    else:
        volume_exceeding_total+=1
above_win_rate = (above_wins/above_total) * 100
below_win_rate = (below_wins/below_total) * 100
print("win rate for instances of open interest exceeding volume by more than %.2f percent out of %d trades: %.2f" % (split_range, above_total, above_win_rate))
print("win rate for instances of open interest exceeding volume by less than %.2f percent out of %d trades: %.2f" % (split_range, below_total, below_win_rate))
print("number of instances where volume exceeded open interest %d" % (volume_exceeding_total))

num_wins, win_sizes = 0, 0 
num_losses, loss_sizes = 0, 0
num_scratches = 0
for index, row in df.iterrows():
    if (row["average_entry"] == "None" or row["average_exit"] == "None" or row["open_interest"] == "None" or row["volume"] == "None"):
        continue
    position_change = percentChange(float(row["average_entry"]), float(row["average_exit"]))
    if (abs(position_change) < 5):
        num_scratches+=1
        continue
    if (position_change > 0):
        num_wins+=1
        win_sizes+=abs(position_change)
    else:
        num_losses+=1
        loss_sizes+=abs(position_change)
        
average_win_percentage = win_sizes/num_wins
average_loss_percentage = loss_sizes/num_losses
print("average win size: %.2f percent" % (average_win_percentage))
print("average loss size: %.2f percent" % (average_loss_percentage))
print("number of scratch trades: %d" % (num_scratches))








    

