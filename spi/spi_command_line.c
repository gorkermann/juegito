#include <stdio.h> // printf
#include <stdlib.h> // exit

#include <getopt.h> // getopt_long

#include <linux/spi/spidev.h>

#include "spi_util.h"

struct SpiParam param = {
	0, // mode
	8, // bits
	500000, // speed
	0 // delay
};

const char *device = "/dev/spidev0.1";
char* instr_g = NULL;

void print_usage(const char *prog) {
	printf("Usage: %s [-DsbdlHOLC3]\n", prog);
	puts("  -D --device   device to use (default /dev/spidev1.1)\n"
	     "  -s --speed    max speed (Hz)\n"
	     "  -d --delay    delay (usec)\n"
	     "  -b --bpw      bits per word \n"
	     "  -l --loop     loopback\n"
	     "  -H --cpha     clock phase\n"
	     "  -O --cpol     clock polarity\n"
	     "  -L --lsb      least significant bit first\n"
	     "  -C --cs-high  chip select active high\n"
	     "  -3 --3wire    SI/SO signals shared\n");
	exit(1);
}

void parse_opts(int argc, char *argv[]) {
	while (1) {
		static const struct option lopts[] = {
			{ "device",  1, 0, 'D' },
			{ "speed",   1, 0, 's' },
			{ "delay",   1, 0, 'd' },
			{ "bpw",     1, 0, 'b' },
			{ "loop",    0, 0, 'l' },
			{ "cpha",    0, 0, 'H' },
			{ "cpol",    0, 0, 'O' },
			{ "lsb",     0, 0, 'L' },
			{ "cs-high", 0, 0, 'C' },
			{ "3wire",   0, 0, '3' },
			{ "no-cs",   0, 0, 'N' },
			{ "ready",   0, 0, 'R' },
			{ NULL, 0, 0, 0 },
		};
		int c;

		c = getopt_long(argc, argv, "D:s:d:b:i:lHOLC3NR", lopts, NULL);

		if (c == -1)
			break;

		switch (c) {
		case 'D':
			device = optarg;
			break;
		case 's':
			param.speed = atoi(optarg);
			break;
		case 'd':
			param.delay = atoi(optarg);
			break;
		case 'b':
			param.bits = atoi(optarg);
			break;
		case 'i':
			instr_g = optarg; 			
			break;
		case 'l':
			param.mode |= SPI_LOOP;
			break;
		case 'H':
			param.mode |= SPI_CPHA;
			break;
		case 'O':
			param.mode |= SPI_CPOL;
			break;
		case 'L':
			param.mode |= SPI_LSB_FIRST;
			break;
		case 'C':
			param.mode |= SPI_CS_HIGH;
			break;
		case '3':
			param.mode |= SPI_3WIRE;
			break;
		case 'N':
			param.mode |= SPI_NO_CS;
			break;
		case 'R':
			param.mode |= SPI_READY;
			break;
		default:
			print_usage(argv[0]);
			break;
		}
	}
}

int main(int argc, char *argv[]) {
	parse_opts(argc, argv);
	return do_transfer(device, param, instr_g, NULL, 1);
}