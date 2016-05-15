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
from threading import Thread

import pdb

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

class streamer(Thread):

    tickStack = list()  # list of recently streamed prices as IGtick objects
    accountStack = list()   # list of recently streamed account updates
    subcriptionKeyStore = {}    # dictionary of keys to subscribed epics
    ig_stream_service = None

    def __init__(self, connect=False):
        Thread.__init__(self)   # initialise thread   
        if connect:
            self.connect()

    def run(self):
        print("Starting streamer...")
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
        if epicName not in self.subcriptionKeyStore:
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
            
            # Store the subscription key under the epic name
            if sub_key_prices != 0:
                self.subcriptionKeyStore[epicName] = sub_key_prices
                logger.info("Successfully subscribed to epic: " + epicName)
                result = True
            else:            
                logger.warning("Failed to subscribe to epic: " + epicName)
                result = False
        else:
            # Already subscribed
            result = True
        return(result)

    # Remove a subscription for an epic
    def unsubscribeEpicListener(self, epicName):
        if epicName in self.subcriptionKeyStore.keys():
            subcriptionKey = self.subcriptionKeyStore[epicName]
            self.ig_stream_service.ls_client.unsubscribe(subcriptionKey)
            del(self.subcriptionKeyStore[epicName])
            logger.info("Successfully unsubscribed from epic: " + epicName)
            result = True
        else:            
            logger.warning("Failed to unsubscribe from epic: " + epicName)
            result = False
        return(result)

    # Update the subscriptions using a list of epics and remove any that aren't on there
    def refreshEpicSubscriptions(self,subscribeList):
        # add new subscriptions
        for epic in subscribeList:
            self.addEpicListener(epic)

        # unsubscribe to ones not on the list
        remove = list()
        for epic in self.subcriptionKeyStore.keys():
            if epic not in subscribeList:
                remove.append(epic)
        for epic in remove:     # dp this in two stages to avoid changing the keys inside the iterator loop
            self.unsubscribeEpicListener(epic)

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