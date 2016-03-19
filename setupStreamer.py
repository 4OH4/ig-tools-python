#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
Run the IG Markets Streamer object
"""

import ig_streamer
import time

streamer = ig_streamer.streamer()

streamer.addEpicListener('CS.D.BITCOIN.TODAY.IP')

baseTime = time.time()
while True:
	
	while (time.time() - baseTime) < 10 :
		# Do stuff
		None

	print("Flushing buffer")
	new_ticks = streamer.flushTickStack();

	for tick in new_ticks:
		print(tick.epic, tick.bid)

	baseTime = time.time()

streamer.disconnect()