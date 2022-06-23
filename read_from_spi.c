#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char **argv)
{

	char rdata[2];
	int ctrl = 0;
	int fd;
	int n;
	char device[15] = "/dev/spidev1.1";

	fd = open(device, O_RDWR);
	if (fd < 0) {
		printf("Failed to open pipe %s\n", device);
		return 0;
	} else {
		printf("opened %s\n", device);
	}	
	printf("fd = %i\n", fd);

	ctrl = read(fd, rdata, sizeof(rdata) - 1);
	if (ctrl == -1) {
	  perror("read");
	  exit(EXIT_FAILURE);
	}
	rdata[ctrl] = '\0'; // read() doesn't add a trailing 0
	printf("entered data: %s", rdata);

	close(fd);


	return 0;
}