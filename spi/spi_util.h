#include <stdint.h>

struct SpiParam {
	uint8_t mode;
	uint8_t bits;
	uint32_t speed;
	uint16_t delay;
};

int do_transfer(const char* device, 
				struct SpiParam param,
				char* instr,
				uint8_t* rx,
				int verbose);