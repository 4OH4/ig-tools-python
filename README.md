# ig-tools-python

Tool set for automated trading with IG Markets. It uses the trading_ig package, ig-markets-api-python-library by femtotrader, and the IG Markets API. 

This was primarily a project to help me move to Python (from MATLAB) and to Git (from SVN), and do a bit more with Docker and AWS. This code is being used by myself, but doesn't go through a big release process and isn't unit tested at the moment. Numbered versions should be functional though.


## v0.1 - May 2016

### ig_streamer.py 
Object that connects to the IG Markets Streaming API and subscribes to price information updates on key markets (EPICs). Tick data is stored into a local store for extraction when required. Reads the subscribeList.txt file to get the list of EPICs.

### setup_streamer.py
Creates and starts the ig_streamer object.

### trading_ig_config.default.py
This needs to contain the configuration details for an active IG Markets account. This file is normally part of the trading_ig package, although is used by parts of ig-tools-python. Fill out with account details, and rename to 'trading_ig_config.py'