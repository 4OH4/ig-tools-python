#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Run the IG Markets Streamer object
"""

import ig_streamer
import time
import tickDB_sqlite as db

import threading

import pdb

def updateDB(spacingTimeSecs = 30):
	# Flush the streamer tick buffer, and if there are
	# new ticks, write them to the main DB
	while True:
		new_ticks = streamer.flushTickStack();
		if new_ticks:
			#pdb.set_trace()
			for tick in new_ticks:
				print(tick.epic, tick.bid)
				db.add_tick(tick)
				print('...added to tick DB')
			new_ticks = None
			db.commit()
		time.sleep(spacingTimeSecs)

def readSubscribeList(filename):
	text_file = open(filename, "r")
	lines = text_file.readlines()
	text_file.close()
	for i in range(len(lines)):		# iterate and remove comments and CR
		lines[i] = lines[i].partition('#')[0]
		lines[i] = lines[i].partition('\n')[0]
	lines = [line for line in lines if line != '']	 # Strip empty lines
	return(lines)


## Create the tick streamer object
streamer = ig_streamer.streamer()
streamer.setName('IG_Streamer')
streamer.start()	# Start method from the Thread object, calls streamer.run()

time.sleep(5)	# This was necessary to avoid a strange clash, streamer not ready

# Initialise the database connection
db.init()

# Subscribe to the required epics
subscribeList = readSubscribeList("subscribeList.txt")
streamer.refreshEpicSubscriptions(subscribeList)

# streamer.addEpicListener('CS.D.BITCOIN.TODAY.IP')
# streamer.addEpicListener('IX.D.FTSE.DAILY.IP')

# Start the DB updater function on a separate thread
threading.Thread( target = updateDB ).start()

exitFlag = False
while not exitFlag:
	time.sleep(5)
	print("Select:")
	print("1. Refresh subscribe list from file")
	print("2. Add epic manually")
	print("3. Unsubscribe epic manually")
	print("4. Exit")
	userInput = int(input('Choose 1-4 and press enter:\n'))
	if userInput == 1:
		subscribeList = readSubscribeList("subscribeList.txt")
		streamer.refreshEpicSubscriptions(subscribeList)
	elif userInput == 2:
		userInput = input('Enter epic name:')
		streamer.addEpicListener(userInput)
	elif userInput == 3:
		userInput = input('Enter epic name:')
		streamer.unsubscribeEpicListener(userInput)
	elif userInput == 4:
		exitFlag = True

# Clean up
db.commit_and_close()
streamer.disconnect()