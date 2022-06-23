import fnctl
import sys

if __name__ == '__main__':
	if len(sys.arv) < 2:
		print(
			"Usage: %s /dev/input/eventN\n"
			"Where X = input device number\n"
			% argv[0]
		)
	
	with open(sys.argv[1], 'r'):
		version = fnctl.ioctl(fd, 0x01);
		device_id = fnctl.ioctl(fd, 0x02); 
		device_name = fnctl.ioctl(fd, 0x06);

		fprintf(stderr,
			"Name	  : %s\n"
			"Version   : %d.%d.%d\n"
			"ID		: Bus=%04x Vendor=%04x Product=%04x Version=%04x\n"
			"----------\n"
			,
			device_name,

			version >> 16,
			(version >> 8) & 0xff,
			version & 0xff,

			device_id[ID_BUS],
			device_id[ID_VENDOR],
			device_id[ID_PRODUCT],
			device_id[ID_VERSION]
		);