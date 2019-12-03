# Daily-Option-Writing
Uses Interactive Brokers native python api framework, build 9.73

Selling options intraday on liquid underlyings like BABA, FB, AAPL, etc.
This was initially done with naked options, but due to margin restrictions, it would have to be implemented with credit spreads.

I've attempted to automate this strategy, but it is difficult to get options data and run checks for more than a few underlyings in a 
timely enough fashion since strikes must be requested in individual slices.

main.py, operations.py, and tools.py are the system files.

native_api_multithreaded.py is an example of how data can be retrieved more quickly with threading and concurrent programming. This is a framework for a work around for the speed problem, but causes data pacing violations and requires paying for more market data

The dataset in the included csv file displays recorded results for roughly 6 months of trading. 

naked_options_writing_analysis.py takes each feature, finds the median, and asseses the win rates for trades above and below. naked_options_writing_expectancy.py attempts to understand future results.
