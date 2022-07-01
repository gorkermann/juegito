#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "spi_util.h"

void main(int argc, char* argv[]) {

 	char* s;	
 	struct SpiParam param = {
		0, // mode
		8, // bits
		500000, // speed
		0 // delay
	};
	
 	uint8_t output_buf[2]; 
 	int volume_percent = 0;

 	char* command;

	while(1) {

		// send two bytes to ADC, get two bytes back
	 	// need to recopy each time because something in do_transfer() writes
	 	// to the instruction string	
		strcpy(s, "0 0");	
		if (do_transfer("/dev/spidev1.1", param, s, output_buf)) {
			printf("failed to read volume level\n");
			break;
		}

		volume_percent = ((output_buf[0] << 4) + (output_buf[1] >> 4)) / 2.55;

		// set volume level
		FILE *fp; 	
		
		sprintf(command, "amixer sset Headphone %d%%", volume_percent);
		fp = popen(command, "r");
		if (!fp) {
			printf("failed to run amixer\n");
			break;
		}

		pclose(fp);

		sleep(1);
	}
}
