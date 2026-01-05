#!/usr/bin/env python2

import os
import sys

class Unijoy:
	def __init__(self, mode):
		# send commands to unijoy control file (see unijoy.c or README.md on github)
		self.ctl_file_path = '/sys/unijoy_ctl/merger'
		self.left_ctlr_id = None
		self.right_ctlr_id = None

		self.update(mode)

	def update(self, mode):
		## determing the ids of the controllers
		controller_ids = []
		merged_buttons = []
		merged_axes = []

		with os.popen('cat /sys/unijoy_ctl/merger') as output:
			for line in output:
				if not line or line[0] == '#':
					continue

				words = line.split(',')
				words = map(lambda x: x.strip(), words)

				if words[0] == 'device':
					device_id = int(words[1])
					device_status = words[2]		
					#device_axis_count = int(words[2])
					#device_button_count = int(words[3])
					device_name = words[5]

					if device_name.find('raph') == 0:
						controller_ids.append(device_id)
				if words[0] == 'map':
					if words[1] == 'BTN':
						merged_buttons.append(int(words[3]))
					elif words[1] == 'AXS':
						merged_axes.append(int(words[3]))
				else:
					continue

		if len(controller_ids) != 4:
			raise Exception('Expected 4 controllers, found %d' % len(controller_ids))

		## remove old configuration

		# P1 and P2 (where the controllers are physically wired) are usually assigned
		# the lowest device ids (not sure how consistent this is)
		controller_ids.sort()

		self.left_ctlr_id = controller_ids[0]
		self.right_ctlr_id = controller_ids[1]

		# remove all old input assignments
		for button_id in merged_buttons:
			os.popen('echo del_button %d > %s' % (button_id,  self.ctl_file_path))	

		for axis_id in merged_axes:
			os.popen('echo del_axis %d > %s' % (axis_id,  self.ctl_file_path))	


		## remove all other joystick /dev/input/eventXX entries
		target_dir = '/dev/input'

		inputs = os.listdir(target_dir)
		for device in inputs:
			path = os.path.join(target_dir, device)

			if os.path.isdir(path):
				continue

			joystick_str = os.popen(
				"udevadm info --query=property --name=%s | grep ID_INPUT_JOYSTICK=1" % path).read()
			
			if not joystick_str:
				continue

			serial_str = os.popen(
				"udevadm info --query=property --name=%s | grep ID_SERIAL=noserial" % path).read()

			if not serial_str:
				pass
				#print "remove %s (%s)" % (path, serial_str)
				#os.remove(path)


		## output new configuration
		# merge left and right controllers
		os.popen('echo merge %d > %s' % (self.left_ctlr_id,  self.ctl_file_path))
		os.popen('echo merge %d > %s' % (self.right_ctlr_id, self.ctl_file_path))

		# add buttons
		if mode == 1:
			self.apply_attached_config()
		elif mode == 2:
			self.apply_detached_config()
		else:
			raise Exception('Unknown controller configuration: %d') % mode

		os.popen('echo refresh > %s' % self.ctl_file_path)


	def apply_attached_config(self):
		print('attached config');

		# left controller (P1 Dpad, Start)
		dest = (self.left_ctlr_id, self.ctl_file_path)
		os.popen('echo add_axis   %d 0 1 > %s' % dest) # Left/Right
		os.popen('echo add_axis   %d 1 0 1 > %s' % dest) # Up/Down
		os.popen('echo add_button %d 0 5 > %s' % dest) # B
		os.popen('echo add_button %d 2 2 > %s' % dest) # Select
		os.popen('echo add_button %d 3 8 > %s' % dest) # Start
		os.popen('echo add_button %d 4 9 > %s' % dest) # A

		# right controller (P1 A, B, Select)
		dest = (self.right_ctlr_id, self.ctl_file_path)
		os.popen('echo add_axis   %d 0 3 > %s' % dest) # Left/Right
		os.popen('echo add_axis   %d 1 2 1 > %s' % dest) # Up/Down
		os.popen('echo add_button %d 0 0 > %s' % dest) # B
		os.popen('echo add_button %d 2 7 > %s' % dest) # Select
		os.popen('echo add_button %d 3 3 > %s' % dest) # Start
		os.popen('echo add_button %d 4 4 > %s' % dest) # A

	def apply_detached_config(self):
		print('detached config');

		# left controller (P1 standard)
		dest = (self.left_ctlr_id, self.ctl_file_path)
		os.popen('echo add_axis   %d 0 0 > %s' % dest) # Left/Right
		os.popen('echo add_axis   %d 1 1 > %s' % dest) # Up/Down
		os.popen('echo add_button %d 0 0 > %s' % dest) # B
		os.popen('echo add_button %d 2 2 > %s' % dest) # Select
		os.popen('echo add_button %d 3 3 > %s' % dest) # Start
		os.popen('echo add_button %d 4 4 > %s' % dest) # A

		# right controller (P2 standard)
		dest = (self.right_ctlr_id, self.ctl_file_path)
		os.popen('echo add_axis   %d 0 2 > %s' % dest) # Left/Right
		os.popen('echo add_axis   %d 1 3 > %s' % dest) # Up/Down
		os.popen('echo add_button %d 0 5 > %s' % dest) # B
		os.popen('echo add_button %d 2 7 > %s' % dest) # Select
		os.popen('echo add_button %d 3 8 > %s' % dest) # Start
		os.popen('echo add_button %d 4 9 > %s' % dest) # A
	
if __name__ == '__main__':
	ctlr_mode = 1

	if len(sys.argv) >= 2:
		ctlr_mode = int(sys.argv[1])

	unijoy = Unijoy(ctlr_mode)
