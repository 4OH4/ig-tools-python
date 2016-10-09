#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Run the IG Markets Streamer object
"""

import ig_streamer
import time
# import tickDB_sqlite as db
import tickDB_sqlite_ORM as db
# import tickDB_MySQL_AWS_ORM as db


import threading
import atexit

import pdb

def updateDB_handler(spacingTimeSecs = 30):
	# Call the update function, sleep in between, and watch for the stop signal
	t = threading.currentThread()
	while getattr(t, "do_run", True):
		updateDB()
		time.sleep(spacingTimeSecs)

def updateDB():
	# Flush the streamer tick buffer, and if there are
	# new ticks, write them to the main DB
	new_ticks = streamer.flushTickStack();
	if new_ticks:
		#pdb.set_trace()
		print('Adding:')
		for tick in new_ticks:
			print(tick.epic, tick.bid)
		db.add_ticks(new_ticks)
		print('...added to tick DB')
		new_ticks = None

def readSubscribeList(filename):
	text_file = open(filename, "r")
	lines = text_file.readlines()
	text_file.close()
	for i in range(len(lines)):		# iterate and remove comments and CR
		lines[i] = lines[i].partition('#')[0]
		lines[i] = lines[i].partition('\n')[0]
	lines = [line for line in lines if line != '']	 # Strip empty lines
	return(lines)

def shutdown():
	pdb.set_trace()
	updateDB()		# flush any ticks left in the buffer
	DBupdateThread.do_run = False	# set the execute flag on the thread to false, and update
	streamer.disconnect()
	
	
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
DBupdateThread = threading.Thread( target = updateDB_handler )
DBupdateThread.start()

# Set-up auto clean up in case of error
atexit.register(shutdown)

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
shutdown()
# db.commit_and_close()
#streamer.disconnect()