#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
IG Markets Stream API sample with Python
2015 FemtoTrader
"""

import sys
import traceback
import logging

from trading_ig import (IGService, IGStreamService)
from trading_ig.config import config
from trading_ig.lightstreamer import Subscription
import trading_ig.compat as compat

import datetime

import pdb

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class streamer(object):

    tickStack = list()
    accountStack = list()
    ig_stream_service = None

    def __init__(self, connect=True):        
        if connect:
            self.connect()

    # Connect to the IG Streaming API
    def connect(self,accountId=None):
        logger.debug("Connecting to IG Streaming API...")
        ig_service = IGService(config.username, config.password, config.api_key, config.acc_type)

        ig_stream_service = IGStreamService(ig_service)
        ig_session = ig_stream_service.create_session()
        if accountId is None:
            accountId = ig_session[u'accounts'][0][u'accountId']
        ig_stream_service.connect(accountId)

        self.ig_stream_service = ig_stream_service

    # Subscription listener: put new price tick in stack
    def on_prices_update(self, item_update):
        logger.info("{stock_name:<19}: Time {UPDATE_TIME:<8} - "
              "Bid {BID:>5} - Ask {OFFER:>5}".format(stock_name=item_update["name"], **item_update["values"]))
        self.tickStack.append(IGtick(item_update))

    # Subscription listener: put new account information in stack
    def on_account_update(self, balance_update):
        logger.info("balance: %s " % balance_update)
        self.accountStack.append(balance_update)

    # Output and clear the tick stack
    def flushTickStack(self):
        output = list(self.tickStack)
        self.tickStack.clear()
        return output

    # Add a listener using the epic name
    def addEpicListener(self, epicName):
        logger.debug("Adding epic listener...")
        # Make Subscription using MERGE mode
        subcription_prices = Subscription(
            mode="MERGE",
            items=['MARKET:'+epicName],
            fields=["UPDATE_TIME", "BID", "OFFER", "CHANGE", "MARKET_STATE"]
            ) 
        #'MARKET:CS.D.BITCOIN.TODAY.IP',
        #'MARKET:IX.D.FTSE.DAILY.IP'

        # Adding the "on_price_update" function to Subscription
        subcription_prices.addlistener(self.on_prices_update)
        # Registering the Subscription
        sub_key_prices = self.ig_stream_service.ls_client.subscribe(subcription_prices)

        logger.debug("Success")

    # Add a listener for account updates
    def addAccountListener(self, accountId):
        logger.debug("Adding account listener...")
        # Makie Subscription using MERGE mode
        subscription_account = Subscription(
            mode="MERGE",
            items=['ACCOUNT:'+accountId],
            fields=["AVAILABLE_CASH"],
            )

        # Adding the "on_balance_update" function to Subscription
        subscription_account.addlistener(on_account_update)
        # Registering the Subscription
        sub_key_account = self.ig_stream_service.ls_client.subscribe(subscription_account)

        logger.debug("Success")

    # Disconnect from the streaming service
    def disconnect(self):
        logger.debug("Disconnecting from streamer service...")
        self.ig_stream_service.disconnect()


class IGtick:
    # A single price, created with an item update object from the IG Streamping API

    epic = ''
    updateDate = ''
    updateTime = ''
    bid = None
    offer = None

    def __init__(self, item_update):
        self.epic = str(item_update["name"])
        self.updateDate = datetime.datetime.now().strftime("%Y%m%d")
        self.updateTime = str(item_update["values"]["UPDATE_TIME"])
        self.bid = float(item_update["values"]["BID"])
        self.offer = float(item_update["values"]["OFFER"])