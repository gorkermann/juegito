#include <math.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "spi_util.h"

void main(int argc, char* argv[]) {

 	char s[10];
 	struct SpiParam param = {
		4, // mode
		8, // bits
		500000, // speed
		0 // delay
	};

 	uint8_t output_buf[2];

	int last_change_dir = 0; // -1, 0, 1
	int slider_percent = -1; // slider position
 	int volume_percent = -1; // volume, derived from slider position

 	char command[50];

	while(1) {

		// read from ADC
		//
		// send two bytes to ADC, get two bytes back
	 	// need to recopy each time because something in do_transfer() writes
	 	// to the instruction string
		strcpy(s, "0 0");
		if (do_transfer("/dev/spidev0.1", param, s, output_buf, 0)) {
			printf("failed to read volume level\n");
			break;
		}

		// get percent from binary
		int val_percent = ((output_buf[0] << 4) + (output_buf[1] >> 4)) / 2.55;

		// round to nearest multiple of 5
		val_percent = floor((val_percent + 5) / 10.0) * 10;

		// set volume level
		if (slider_percent < 0 ||
		    abs(slider_percent - val_percent) > 3) {
			slider_percent = val_percent;

			// 0 -> 0
			// 25 -> 50
			// 50 -> 71
			// 75 -> 87
			// 100 -> 100
			volume_percent = 10 * sqrt(slider_percent);

			FILE *fp;

			sprintf(command, "amixer sset Headphone %d%%", volume_percent);
			fp = popen(command, "r");
			if (!fp) {
				printf("failed to run amixer\n");
				break;
			}

			printf("%s\n", command);

			pclose(fp);
		}

		sleep(1);
	}
}
