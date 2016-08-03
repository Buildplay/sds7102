#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <assert.h>
#include <time.h>

#include <arpa/inet.h>

/* this table must match the table in _sds7102.py */
static const char *names[] = {
    /* bank2 */
    "N11",

    "Ref",                      /* 10MHz reference clock */

    "Tr1", "Tr2",               /* Triggers */
    "Vd1", "Vd2", "Hd1", "Hd2", /* Vertical Sync, Horizonal Sync */
    "AC",                       /* AC Trigger */

    "Prb",                      /* Probe compensation output */
    "Ext",                      /* External trigger output */

    "SCL", "SDA",               /* AT88SC I2C SCL and SDA */

    "R11"                       /* CCLK */
};

#define COUNT (sizeof(names) / sizeof(*names) + 5)

int main()
{
    uint32_t buf[COUNT];
    uint32_t last[COUNT];
    int fd;
    int r;
    int i;
    struct timespec ts0, ts;

    for (i = 0; i < COUNT; i++)
	last[i] = 0;

    while (1)
    {
	clock_gettime(CLOCK_MONOTONIC, &ts0);

	fd = open("/dev/regs", O_RDWR);
	assert(fd >= 0);
	buf[0] = htonl((0 << 1) | 1);
	r = write(fd, buf, 4);
	printf("write -> %d\n", r);
	assert(r == 4);
	r = read(fd, buf, sizeof(buf));
	printf("read -> %d\n", r);
	assert(r == sizeof(buf));

	if (1)
	{
	    for (i = 0; i < COUNT; i++)
	    {
		buf[i] = ntohl(buf[i]);
		if (0)		/* gray decoder */
		{
		    uint32_t b = buf[i] >> 31;
		    buf[i] &= (1u<<31)-1;
		    buf[i] = buf[i] ^ (buf[i] >> 16);
		    buf[i] = buf[i] ^ (buf[i] >> 8);
		    buf[i] = buf[i] ^ (buf[i] >> 4);
		    buf[i] = buf[i] ^ (buf[i] >> 2);
		    buf[i] = buf[i] ^ (buf[i] >> 1);
		    buf[i] |= (b << 31);
		}
	    }
	}

	for (i = 0; i < COUNT; i++)
	{
	    uint32_t v = buf[i];

	    if (!(i % 5))
	    {
		if (i)
		    printf("\n");
		printf("%3u", i);
	    }
	    if (0)
		printf(" %08x", v);
	    else
	    {
		unsigned delta = (v - last[i]) & ((1u<<31)-1);

		if (i < sizeof(names) / sizeof(*names))
		    printf("  %-3s", names[i]);
		else
		    printf("  %-3s", "-");

		if (delta >= 1E9)
		    printf(" %5.1fG", delta / 1E9);
		else if (delta >= 1E6)
		    printf(" %5.1fM", delta / 1E6);
		else if (delta >= 1E3)
		    printf(" %5.1fk", delta / 1E3);
		else
		    printf("  %5d", delta);

		printf(" %c", v & (1u<<31) ? '^' : 'v');
	    }

	    last[i] = v;
	}
	printf("\n");
	fflush(stdout);

	usleep(300000);
	close(fd);

	do
	{
	    usleep(1000);
	    clock_gettime(CLOCK_MONOTONIC, &ts);
	}
	while (((ts.tv_sec - ts0.tv_sec) * 1000000000 +
		(ts.tv_nsec - ts0.tv_nsec)) < 1000000000);
    }
}

