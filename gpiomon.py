#!/usr/bin/env python3

import signal
import sys
import time

import RPi.GPIO as GPIO

import add_button

class GpioPinSpec:
	def __init__(self, name, channel, direction):
		self.name = name
		self.channel = channel
		self.direction = direction

PIECON_0V2_GPIO = [
	GpioPinSpec('N_LEFT_CTLR', 6, GPIO.IN),
	GpioPinSpec('N_RIGHT_CTLR', 13, GPIO.IN),
	GpioPinSpec('N_DETECT', 26, GPIO.IN),
	GpioPinSpec('N_RESET_SW', 5, GPIO.IN)
]

JUEGITO_0V2_GPIO = {}

POLL_INTERVAL = 0.2 # seconds

pinout = None
unijoy = None

CTLR_MODE_ATTACHED = 1
CTLR_MODE_DETACHED = 2

ctlr_mode = CTLR_MODE_DETACHED

def signal_handler(sig, frame):
	GPIO.cleanup()
	sys.exit(0)

def update_ctlr_mode(button_state):
	global ctlr_mode

	# down
	if not button_state:
		if ctlr_mode == CTLR_MODE_DETACHED:						
			unijoy.update(CTLR_MODE_ATTACHED)

		ctlr_mode = CTLR_MODE_ATTACHED

	# up
	else:
		if ctlr_mode == CTLR_MODE_ATTACHED:						
			unijoy.update(CTLR_MODE_DETACHED)
					
		ctlr_mode = CTLR_MODE_DETACHED
	

def button_pressed_callback(channel):
	if pinout is not None:
		for pin in pinout:
			if pin.channel == channel:
				if pin.name == 'N_LEFT_CTLR':
					update_ctlr_mode(0)

def button_released_callback(channel):
	if pinout is not None:
		for pin in pinout:
			if pin.channel == channel:
				if pin.name == 'N_LEFT_CTLR':			
					update_ctlr_mode(1)

if __name__ == '__main__':
	GPIO.setmode(GPIO.BCM)

	pinout = PIECON_0V2_GPIO

	# init Unijoy in 1 player mode
	unijoy = add_button.Unijoy(CTLR_MODE_ATTACHED)

	for pin in pinout:
		GPIO.setup(pin.channel, pin.direction, pull_up_down=GPIO.PUD_UP)
		#GPIO.add_event_detect(pin.channel, GPIO.FALLING, 
		#	callback=button_pressed_callback, bouncetime=100)
		GPIO.add_event_detect(pin.channel, GPIO.RISING, 
			callback=button_released_callback, bouncetime=100)

	signal.signal(signal.SIGINT, signal_handler)
	
	while True:
		time.sleep(POLL_INTERVAL)

		update_ctlr_mode(GPIO.input(6))

	#signal.pause()
