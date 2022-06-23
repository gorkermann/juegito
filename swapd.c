#include <stdio.h>
#include <stdlib.h>

#include <string.h>     /* strerror() */
#include <errno.h>      /* errno */

#include <fcntl.h>      /* open() */
#include <unistd.h>     /* close() */
#include <sys/ioctl.h>  /* ioctl() */

#include <linux/input.h>    /* EVIOCGVERSION ++ */

#define EV_BUF_SIZE 16

uint EV_TYPE_MASK = EV_KEY; 

int main(int argc, char *argv[]) {
    int fd, sz;
    unsigned i;

    /* A few examples of information to gather */
    unsigned version;
    unsigned short id[4];                   /* or use struct input_id */
    char name[256] = "N/A";

    struct input_event ev[EV_BUF_SIZE]; /* Read up to N events at a time */

    if (argc < 2) {
        fprintf(stderr,
            "Usage: %s /dev/input/eventN\n"
            "Where X = input device number\n",
            argv[0]
        );
        return EINVAL;
    }

    if ((fd = open(argv[1], O_RDONLY)) < 0) {
        fprintf(stderr,
            "ERR %d:\n"
            "Unable to open `%s'\n"
            "%s\n",
            errno, argv[1], strerror(errno)
        );
    }

    /* Error check here as well. */
    ioctl(fd, EVIOCGVERSION, &version);
    ioctl(fd, EVIOCGID, id); 
    ioctl(fd, EVIOCGNAME(sizeof(name)), name);

    fprintf(stderr,
        "Name      : %s\n"
        "Version   : %d.%d.%d\n"
        "ID        : Bus=%04x Vendor=%04x Product=%04x Version=%04x\n"
        "----------\n"
        ,
        name,

        version >> 16,
        (version >> 8) & 0xff,
        version & 0xff,

        id[ID_BUS],
        id[ID_VENDOR],
        id[ID_PRODUCT],
        id[ID_VERSION]
    );

    /* Loop. Read event file and parse result. */
    for (;;) {
        sz = read(fd, ev, sizeof(struct input_event) * EV_BUF_SIZE);

        if (sz < (int) sizeof(struct input_event)) {
            fprintf(stderr,
                "ERR %d:\n"
                "Reading of `%s' failed\n"
                "%s\n",
                errno, argv[1], strerror(errno)
            );
            goto fine;
        }

        /* Implement code to translate type, code and value */
        for (i = 0; i < sz / sizeof(struct input_event); ++i) {
            if (ev[i].type & EV_TYPE_MASK) {
                fprintf(stderr,
                    "%ld.%06ld: "
                    "type=%02x "
                    "code=%02x "
                    "value=%02x\n",
                    ev[i].time.tv_sec,
                    ev[i].time.tv_usec,
                    ev[i].type,
                    ev[i].code,
                    ev[i].value
                );

                if (ev[i].value == 0x01) {

                    // Z
                    if (ev[i].code == 0x2c) {
                        system("python add_button.py 1");
                    
                    // X
                    } else if (ev[i].code == 0x2d) {
                        system("python add_button.py 2");
                    }
                }
            }
        }
    }

fine:
    close(fd);

    return errno;
}