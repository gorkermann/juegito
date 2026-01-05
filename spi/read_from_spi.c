#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

// smaller than spi_util.c, but doesn't work
// not sure why (7/1/2022)

int main(int argc, char **argv)
{

	char rdata[2];
	int ctrl = 0;
	int fd;
	int n;
	char device[15] = "/dev/spidev0.1";

	fd = open(device, O_RDWR);
	if (fd < 0) {
		printf("Failed to open pipe %s\n", device);
		return 0;
	} else {
		printf("opened %s\n", device);
	}	
	printf("fd = %i\n", fd);
	write(fd, "00", 2);
	ctrl = read(fd, rdata, 2);
	if (ctrl == -1) {
	  perror("read");
	  exit(EXIT_FAILURE);
	}
	rdata[ctrl] = '\0'; // read() doesn't add a trailing 0
 	printf("control: %d\n", ctrl);	
	printf("entered data: %d %d\n", rdata[0], rdata[1]);

	close(fd);

	return 0;
}
