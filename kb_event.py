#!/usr/bin/python
import struct
import time
import sys

"""
FORMAT represents the format used by linux kernel input event struct
See https://github.com/torvalds/linux/blob/v5.5-rc5/include/uapi/linux/input.h#L28
Stands for: long int, long int, unsigned short, unsigned short, unsigned int
"""
EV_FORMAT = 'llHHI'
JS_FORMAT = 'lhBB'

FORMAT = JS_FORMAT
EVENT_SIZE = struct.calcsize(FORMAT)

class Listener():
	def __init__(self, ev_type, code, value, func):
		self.ev_type = ev_type
		self.code = code
		self.value = value
		self.func = func

class InputDevice():
	def __init__(self, dev_path, debug=False):
		self.dev_path = dev_path

		#open file in binary mode
		self.dev_file = open(dev_path, "rb")
		self.event = self.dev_file.read(EVENT_SIZE)

		self.listeners = {}

		self.listener_index = 0

		self.debug = debug

	def register(self, ev_type, code, value, func):
		self.listeners[self.listener_index] = Listener(ev_type, code, value, func)
		self.listener_index += 1

		return self.listener_index

	def unregister(self, index):
		self.listeners.pop(index)

	def listen(self):
		if self.event:
		    # for keyboard events 
		    #(tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, self.event)

		    # for joystick events
		    tv_sec = 0
		    (tv_usec, value, ev_type, code) = struct.unpack(FORMAT, self.event)

		    if ev_type != 0 or code != 0 or value != 0:

		    	for i, listener in self.listeners.items():
		    		if listener.ev_type == ev_type:
		    			if listener.code == code:
		    				if listener.value == value:
		    					listener.func()

		    	if self.debug:
		        	print("Event type %u, code %u, value %u at %d.%d" % \
		            	(ev_type, code, value, tv_sec, tv_usec))
		    else:
		        # Events with code, type and value == 0 are "separator" events
		        pass
		        #print("===========================================")

		    self.event = self.dev_file.read(EVENT_SIZE)
		else:
			self.dev_file.close()
