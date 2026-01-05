#!/usr/bin/env python2

import os
import shutil
import signal
import subprocess
import sys
import time

import RPi.GPIO as GPIO

import add_button
import kb_event

## RPi GPIO events

class GpioPinSpec:
	def __init__(self, name, channel, direction):
		self.name = name
		self.channel = channel
		self.direction = direction

PIECON_0V2_GPIO = {
	# controller presence detection (10k pullup on each) 
	# NOT USED
	'N_LEFT_CTLR': GpioPinSpec('N_LEFT_CTLR', 6, GPIO.IN),
	'N_RIGHT_CTLR': GpioPinSpec('N_RIGHT_CTLR', 13, GPIO.IN),
	
	# this is the same as N_RIGHT_CTLR, but renamed for clarity
	'N_CTLR_MODE': GpioPinSpec('N_CTLR_MODE', 13, GPIO.IN),

	# cartridge presence detection (10k pullup)
	'N_DETECT': GpioPinSpec('N_DETECT', 26, GPIO.IN),
	
	# reset switch (10k pullup)
	'N_RESET_SW': GpioPinSpec('N_RESET_SW', 5, GPIO.IN)
}
POLL_INTERVAL = 0.2 # seconds

pinout = None
unijoy = None

CTLR_MODE_ATTACHED = 1
CTLR_MODE_DETACHED = 2

ctlr_mode = CTLR_MODE_DETACHED

MODE_NAME = ['', 'CTLR_MODE_ATTACHED', 'CTLR_MODE_DETACHED']

emulator_process = None

## Joystick Events
JS_EVENT_BUTTON = 1
JS_EVENT_AXIS = 2

BTN_B = 0
BTN_SELECT = 2
BTN_START = 3
BTN_A = 4

BTNVAL_UP = 0
BTNVAL_DOWN = 1

AXIS_HORIZ = 0
AXIS_VERT = 1

## Keyboard Events
#RAPHNET_BUTTONS = {}
#RAPHNET_BUTTONS['A'] = 292 # A
#RAPHNET_BUTTONS['B'] = 288 # B
#RAPHNET_BUTTONS['START'] = 291 # Start
#RAPHNET_BUTTONS['SELECT'] = 290 # Select

## ROM control
ROM_DIR = '/home/pi/roms'
current_rom_index = 0
rom_names = []
current_rom_path = ''

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


def set_ctlr_attached():
	if emulator_is_running():
		return

	set_ctlr_mode(CTLR_MODE_ATTACHED)

def set_ctlr_detached():
	if emulator_is_running():
		return

	set_ctlr_mode(CTLR_MODE_DETACHED)

def copy_file(source, target):
	shutil.copyfile(source, target)
	print 'cp ' + source + ' ' + target

def set_ctlr_mode(mode):
	global ctlr_mode

	attached_config = '/home/pi/configs/attached.cfg'
	detached_config = '/home/pi/configs/detached.cfg'
	target_file = '/home/pi/configs/retroarch.cfg'

	ctlr_mode = mode

	if ctlr_mode == CTLR_MODE_ATTACHED:
		copy_file(attached_config, target_file)
	elif ctlr_mode == CTLR_MODE_DETACHED:
		copy_file(detached_config, target_file)
	else:
		print 'set_ctlr_mode: unknown mode %s' % ctlr_mode

	print 'set controller mode: %s' % MODE_NAME[mode]


def load_prev_rom():
	global current_rom_index

	if emulator_is_running():
		return

	current_rom_index -= 1
	if current_rom_index < 0:
		current_rom_index = len(rom_names) - 1

	load_rom(current_rom_index)

def load_next_rom():
	global current_rom_index

	if emulator_is_running():
		return

	current_rom_index += 1
	if current_rom_index >= len(rom_names):
		current_rom_index = 0

	load_rom(current_rom_index)

def load_rom(index):
	global current_rom_path

	current_rom_path = ROM_DIR + '/' + rom_names[index]
	print 'current rom: %s' % current_rom_path


def reset_emulator(channel):
	global emulator_process

	emulator_cmd = '/home/pi/run_current.sh'

	retroarch_path = '/opt/retropie/emulators/retroarch/bin/retroarch'
	emulator_path = '/opt/retropie/libretrocores/lr-quicknes/quicknes_libretro.so'
	config_path = '/home/pi/configs/retroarch.cfg'
	emulator_cmd = '%s -L %s --config %s \"%s\"' % (retroarch_path, emulator_path, config_path, current_rom_path)

	if emulator_process is not None:
		try:
			os.killpg(os.getpgid(emulator_process.pid), signal.SIGTERM)
		except OSError:
			pass

		print 'terminated emulator'

	print 'command: %s' % emulator_cmd
	emulator_process = subprocess.Popen(emulator_cmd, shell=True, preexec_fn=os.setsid)

def emulator_is_running():
	global emulator_process

	# emulator_process=None means it hasn't run yet
	# emulator_process.poll()=None means it is running and hasn't terminated
	return (emulator_process is not None and
		emulator_process.poll() is None)

if __name__ == '__main__':
	print 'started monitor'

	GPIO.setmode(GPIO.BCM)

	pinout = PIECON_0V2_GPIO

	# init Unijoy in 1 player mode
	#unijoy = add_button.Unijoy(CTLR_MODE_ATTACHED)

	p2_ctlr = kb_event.InputDevice('/dev/input/js1')
	p2_ctlr.register(JS_EVENT_BUTTON, BTN_A, BTNVAL_DOWN, set_ctlr_attached)
	p2_ctlr.register(JS_EVENT_BUTTON, BTN_B, BTNVAL_DOWN, set_ctlr_detached) 

	p2_ctlr.register(JS_EVENT_AXIS, AXIS_HORIZ, -32767, load_prev_rom)
	p2_ctlr.register(JS_EVENT_AXIS, AXIS_HORIZ, 32767, load_next_rom)

	rom_names = filter(lambda x: x[-4:] == '.nes', os.listdir(ROM_DIR))

	if len(rom_names) == 0:
		print 'WARNING: no roms found'
	else:
		current_rom_index = 0
		load_rom(current_rom_index)

	for pin in pinout:
		pass
		#GPIO.setup(pin.channel, pin.direction, pull_up_down=GPIO.PUD_UP)
		#GPIO.add_event_detect(pin.channel, GPIO.FALLING, 
		#	callback=button_pressed_callback, bouncetime=100)
		#GPIO.add_event_detect(pin.channel, GPIO.RISING, 
		#	callback=button_released_callback, bouncetime=100)

	# reset switch
	pin = pinout['N_RESET_SW']
	GPIO.setup(pin.channel, pin.direction, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(pin.channel, GPIO.FALLING,
		callback=reset_emulator, bouncetime=100)

	signal.signal(signal.SIGINT, signal_handler)
	
	while True:
		time.sleep(POLL_INTERVAL)

		p2_ctlr.listen()

		#update_ctlr_mode(GPIO.input(6))

	#signal.pause()
