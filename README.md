# Daily-Option-Writing

Selling options intraday on liquid underlyings like BABA, FB, AAPL, etc.
This was initially done with naked options, but due to margin restrictions, it would have to be implemented with spreads.

I've attempted to automate this strategy, but it is difficult to get options data and run checks for more than a few underlyings in a 
timely enough fashion since strikes must be requested in individual slices.

main.py, operations.py, and tools.py are the system files.

native_api_multithreaded.py is an example of how data can be retrieved more quickly with threading and concurrent programming. This is a framework for a work around for the speed problem, but causes data pacing violations and requires paying for more market data

