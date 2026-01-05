/*
 * SPI testing utility (using spidev driver)
 *
 * Copyright (c) 2007  MontaVista Software, Inc.
 * Copyright (c) 2007  Anton Vorontsov <avorontsov@ru.mvista.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License.
 *
 * Cross-compile with cross-gcc -I/path/to/cross-kernel/include
 */

#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>

#include <sys/ioctl.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>

#include "spi_util.h"

#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define MAX_BYTES 10 // workaround until I make a routine to count the number of bytes
					 // in the string
/*
static void pabort(const char *s) {
	perror(s);
	abort();
}*/

static int transfer(int fd, 
					struct SpiParam param,
					char* instr,
					uint8_t* output_buf,
					int verbose ) {
	if (instr == NULL) {
		printf("instruction has not been set\n");
		return -1;
	}

	if (verbose) {
		printf("instr: %s\n", instr);
	}

	// get bytes from input string
	int byte_count = 0;	

	uint8_t tx[MAX_BYTES] = {0, };
	uint8_t rx[MAX_BYTES] = {0, };

	char* byte = strtok(instr, " "); 	

	while (byte != NULL && byte_count < MAX_BYTES) {
		tx[byte_count] = strtol(byte, NULL, 16) % 0xFF;
		byte_count++;
		byte = strtok(NULL, " ");
	}

	// check size of output buffer, if present
	if (output_buf != NULL && ARRAY_SIZE(output_buf) < byte_count) {
		printf("size of rx buffer (%d) less than expected (%d)\n",
			   (int)ARRAY_SIZE(output_buf), byte_count);
		return -1;
	}

	// compose struct to transfer
	struct spi_ioc_transfer tr = {
		.tx_buf = (unsigned long)tx,
		.rx_buf = (unsigned long)rx,
	    .cs_change = 0,	
		.len = byte_count, 
		.delay_usecs = param.delay,
		.speed_hz = param.speed,
		.bits_per_word = param.bits,
	};

	int ret = ioctl(fd, SPI_IOC_MESSAGE(1), &tr);
	if (ret < 1) {
		printf("can't send spi message\n");
		return -1;
	}

	// copy receive buffer to output buffer
	if (output_buf != NULL) {
		for (ret = 0; ret < byte_count; ret++) {
			output_buf[ret] = rx[ret];
		}
	}

	if (verbose) {
		printf("Input:");	
		for (ret = 0; ret < byte_count; ret++) {
			if (!(ret % 6))
				puts("");
			printf("%.2X ", tx[ret]);
		}

		puts("\n");

		printf("Output:");
		for (ret = 0; ret < byte_count; ret++) {
			if (!(ret % 6))
				puts("");
			printf("%.2X ", rx[ret]);	
		}
		puts("");
	}

	return 0;
}

int do_transfer(const char* device, 
				struct SpiParam param,
				char* instr,
				uint8_t* output_buf,
				int verbose) {	
	int ret;
	int fd;

	fd = open(device, O_RDWR);
	if (fd < 0) {
		printf("can't open device\n");
		return -1;
	}

	/*
	 * spi mode
	 */
	ret = ioctl(fd, SPI_IOC_WR_MODE, &param.mode);
	if (ret == -1) {
		printf("can't set spi mode\n");
		return -1;
	}

	ret = ioctl(fd, SPI_IOC_RD_MODE, &param.mode);
	if (ret == -1) {
		printf("can't get spi mode\n");
		return -1;
	}

	/*
	 * bits per word
	 */
	ret = ioctl(fd, SPI_IOC_WR_BITS_PER_WORD, &param.bits);
	if (ret == -1) {
		printf("can't set bits per word\n");
		return -1;
	}

	ret = ioctl(fd, SPI_IOC_RD_BITS_PER_WORD, &param.bits);
	if (ret == -1) {
		perror("can't get bits per word\n");
		return -1;
	}

	/*
	 * max speed hz
	 */
	ret = ioctl(fd, SPI_IOC_WR_MAX_SPEED_HZ, &param.speed);
	if (ret == -1) {
		printf("can't set max speed hz\n");
		return -1;
	}

	ret = ioctl(fd, SPI_IOC_RD_MAX_SPEED_HZ, &param.speed);
	if (ret == -1) {
		printf("can't get max speed hz\n");
		return -1;
	}

	if (verbose) {
		printf("spi mode: %d\n", param.mode);
		printf("bits per word: %d\n", param.bits);
		printf("max speed: %d Hz (%d KHz)\n", param.speed, param.speed/1000);
	}

	if (transfer(fd, param, instr, output_buf, verbose)) {
		printf("unable to complete transfer\n");
		close(fd);
		return -1;
	}

	close(fd);
	return 0;
}
