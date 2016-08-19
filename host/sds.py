#! /usr/bin/python
import os
import sys
import numpy
import time
from subprocess import Popen, PIPE
import random

GPA = tuple([ 0 + i for i in range(32) ])
GPB = tuple([ 32 + i for i in range(16) ])
GPC = tuple([ 64 + i for i in range(16) ])
GPD = tuple([ 96 + i for i in range(16) ])
GPE = tuple([ 128 + i for i in range(16) ])
GPF = tuple([ 160 + i for i in range(16) ])
GPH = tuple([ 224 + i for i in range(16) ])

class SDS(object):
    def __init__(self, host):
        self.p = Popen([ 'ssh', host, './sds-server' ],
                       stdin = PIPE, stdout = PIPE, stderr = sys.stderr)

        self.fi = self.p.stdout
        self.fo = self.p.stdin

        self.verbose = False

    def read_regs(self, addr, count):
        cmd = 'read_fpga 0x%x %u' % (addr, count)
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

        a = numpy.zeros(count, dtype = numpy.uint32)
        for i in range(count):
            s = self.fi.readline()
            a[i] = int(s, 0)

        return a

    def read_reg(self, addr):
        return self.read_regs(addr, 1)[0]

    def write_regs(self, addr, data):
        cmd = 'write_fpga 0x%x %s' % (addr, ' '.join([ '0x%x' % v for v in data ]))
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

    def write_reg(self, addr, value):
        self.write_regs(addr, [ value ])

    def read_soc_regs(self, addr, count):
        cmd = 'read_soc 0x%x %u' % (addr, count)
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

        a = numpy.zeros(count, dtype = numpy.uint32)
        for i in range(count):
            s = self.fi.readline()
            a[i] = int(s, 0)

        return a

    def read_soc_reg(self, addr):
        return self.read_soc_regs(addr, 1)[0]

    def write_soc_regs(self, addr, data):
        cmd = 'write_soc 0x%x %s' % (addr, ' '.join([ '0x%x' % v for v in data ]))
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

    def write_soc_reg(self, addr, value):
        self.write_soc_regs(addr, [ value ])

    def read_ddr(self, addr, count):
        cmd = 'read_ddr 0x%x %u' % (addr, count)
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

        a = numpy.zeros(count, dtype = numpy.uint32)
        for i in range(count):
            s = self.fi.readline()
            a[i] = int(s, 0)

        return a

    def write_ddr(self, addr, data):
        cmd = 'write_ddr 0x%x %s' % (addr, ' '.join([ '0x%x' % v for v in data ]))
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

    def set_gpio(self, pin, value):
        cmd = 'set_gpio %u %u' % (pin, value)
        if self.verbose:
            print cmd
        self.fo.write(cmd + '\n')
        self.fo.flush()

    def atten(self, channel, value):
        assert channel >= 0 and channel < 2
        assert value >= 0 and value < 2

        if channel:
            a = GPE[1]
            b = GPH[12]
        else:
            a = GPA[15]
            b = GPA[1]

        self.set_gpio(a, 1 - value)
        self.set_gpio(b, value)

    def acdc(self, channel, value):
        assert channel >= 0 and channel < 2
        assert value >= 0 and value < 2

        if channel:
            a = GPD[8]
        else:
            a = GPA[0]

        self.set_gpio(a, value)

    def mux(self, channel, value):
        assert channel >= 0 and channel < 2
        assert value >= 0 and value < 4

        if channel:
            a0 = GPH[9]
            a1 = GPH[11]
        else:
            a0 = GPC[5]
            a1 = GPC[6]

        self.set_gpio(a0, value & 1)
        self.set_gpio(a1, (value & 2) >> 1)

    def odd_relay(self, value):
        assert value >= 0 and value < 2
        self.set_gpio(GPE[3], value)

    def ext_relay(self, value):
        assert value >= 0 and value < 2
        self.set_gpio(GPC[7], value)

    def shifter(self, cs, bits, value, cpol = 0, cpha = 0, pulse = 0):
        assert cpol >= 0 and cpol < 2
        assert cpha >= 0 and cpha < 2
        assert pulse >= 0 and pulse < 2
        assert cs >= 0 and pulse < 6
        assert bits >= 0 and bits <= 32
        data = [ value,
                 bits | (cpha<<8) | (cpol<<9) | (pulse<<10) | (1<<16<<cs) ]
        self.write_regs(0x210, data)
        time.sleep(0.1)

    def bu2506(self, channel, value):
        assert channel >= 0 and channel < 16
        assert value >= 0 and value < 1024
        v = channel | (value << 4)
        v2 = 0
        for i in range(14):
            v2 <<= 1
            if v & (1<<i):
                v2 |= 1
        if self.verbose:
            print "bu2506 0x%04x 0x%04x" % (v, v2)
        self.shifter(0, 14, v2, pulse = 1)

    def adf4360(self, value):
        self.shifter(1, 24, value, pulse = 1)

    def adc08d500(self, value):
        self.shifter(2, 32, value, cpol = 1, cpha = 1)

    def lmh6518(self, channel, value):
        assert channel >= 0 and channel < 2
        if channel:
            self.shifter(4, 24, value)
        else:
            self.shifter(3, 24, value)

    def dac8532(self, channel, value):
        assert channel >= 0 and channel < 2
        assert value >= 0 and value < 65536
        if channel:
            base = 0x100000
        else:
            base = 0x240000
        self.shifter(5, 24, base | value, cpha = 1)

    def capture(self, count):
        self.write_reg(0x230, 0)
        self.write_reg(0x230, 1)
        time.sleep(0.1)
        data0 = self.read_regs(0x4000, count)
        data1 = self.read_regs(0x6000, count)

        data = numpy.dstack((data0, data1))[0].reshape(len(data0)+len(data1))

        print data0
        print data1
        print data

        return data

    def mig_reset(self):
        self.write_soc_reg(0x200, 1)
        print "ctrl 0x%08x" % self.read_soc_reg(0x200)
        self.write_soc_reg(0x200, 0)
        print "ctrl 0x%08x" % self.read_soc_reg(0x200)
        time.sleep(0.1)
        print "ctrl 0x%08x" % self.read_soc_reg(0x200)
        print

    def mig_capture(self, count):
        self.mig_reset()
        self.write_reg(0x230, 0)
        self.write_reg(0x230, 1)
        time.sleep(0.1)

        data = self.read_ddr(0, count)

        if 0:
            data2 = self.read_ddr(0, count)
            assert all(data == data2)

        print "capture_status 0x%08x" % self.read_reg(0x230)

        s = numpy.reshape(data, (len(data) / 64, 2, 32))
        s0 = numpy.reshape(s[:,0,:], len(data)/2)
        s1 = numpy.reshape(s[:,1,:], len(data)/2)

        # I need to to this to make the offsets align, I need to think
        # a bit about why this happens.
        if 1:
            s0 = s0[:-2]
            s1 = s1[2:]

        print len(s0)
        print len(s1)

        data = numpy.reshape(numpy.dstack((s0, s1)), len(s0)+len(s1))

        return data

    def soc(self, count):
        """Get a SoC bus trace"""

        self.write_reg(0x231, 0)
        self.write_reg(0x231, 1)
        time.sleep(0.1)

        # Single Data Rate (SDR) signals
        sdr0 = self.read_regs(0x2000, count)
        sdr1 = sdr0
        sdr = numpy.dstack((sdr1, sdr0))[0].reshape(len(sdr0)+len(sdr1))

        print sdr0
        print sdr1
        print sdr

        # Registered copies of SDR signals
        reg0 = self.read_regs(0x2000, count)
        reg1 = reg0
        reg = numpy.dstack((reg1, reg0))[0].reshape(len(reg0)+len(reg1))

        print reg0
        print reg1
        print reg

        # Double Data Rate DDR signals
        ddr0 = self.read_regs(0x3000, count)
        ddr1 = self.read_regs(0x3800, count)
        ddr = numpy.dstack((ddr1, ddr0))[0].reshape(len(ddr0)+len(ddr1))

        print ddr0
        print ddr1
        print ddr

        return sdr, reg, ddr

    def set_red_led(self, value):
        self.set_gpio(GPF[3], value)

    def set_green_led(self, value):
        assert value >= 0 and value <= 1
        v = self.read_soc_reg(0x108)
        if value:
            v |= (1<<0)
        else:
            v &= ~(1<<0)
        self.write_soc_reg(0x108, v)

    def set_white_led(self, value):
        assert value >= 0 and value <= 1
        v = self.read_soc_reg(0x108)
        if value:
            v |= (1<<1)
        else:
            v &= ~(1<<1)
        self.write_soc_reg(0x108, v)

    def fp_init(self):
        v = self.read_soc_reg(0x100)
        v |= 1
        self.write_soc_reg(0x100, v)
        time.sleep(0.1)
        v &= ~1
        self.write_soc_reg(0x100, v)

def decode_mig_status(v):
    print "dram status  0x%08x" % v
    print "cmd_full     %u" % ((v >> 25) & 1)
    print "cmd_empty    %u" % ((v >> 24) & 1)
    print "wr_underrun  %u" % ((v >> 23) & 1)
    print "wr_error     %u" % ((v >> 22) & 1)
    print "wr_full      %u" % ((v >> 21) & 1)
    print "wr_empty     %u" % ((v >> 20) & 1)
    print "wr_count     %u" % ((v >> 12) & 0x7f)
    print "rd_overflow  %u" % ((v >> 11) & 1)
    print "rd_error     %u" % ((v >> 10) & 1)
    print "rd_full      %u" % ((v >> 9) & 1)
    print "rd_empty     %u" % ((v >> 8) & 1)
    print "rd_count     %u" % ((v >> 0) & 0x7f)
    print

def main():
    sds = SDS('sds')

    # sds.capture(16)

    if 1:
        print "counts 0x%08x" % sds.read_soc_reg(0x212)
        decode_mig_status(sds.read_soc_reg(0x211))

    if 1:
        print "Reset"
        sds.write_soc_reg(0x200, 1)
        print "ctrl 0x%08x" % sds.read_soc_reg(0x200)
        sds.write_soc_reg(0x200, 0)
        print "ctrl 0x%08x" % sds.read_soc_reg(0x200)
        time.sleep(0.1)
        print "ctrl 0x%08x" % sds.read_soc_reg(0x200)
        print

    decode_mig_status(sds.read_soc_reg(0x211))

    n = 3
    o = 10
    if 1:
        print "write to FIFO"
        for i in range(n):
            sds.write_soc_reg(0x218, 0xf00f0000 + i)
            time.sleep(0.1)
        print "counts 0x%08x" % sds.read_soc_reg(0x212)
        decode_mig_status(sds.read_soc_reg(0x211))

        print "write to DDR"
        sds.write_soc_reg(0x210, o | ((n-1)<<24) | (0<<30))
        time.sleep(0.1)
        print "counts 0x%08x" % sds.read_soc_reg(0x212)
        decode_mig_status(sds.read_soc_reg(0x211))

    sds.write_ddr(20, [ 0xdeadbeef, 0xfeedf00f ])

    n = 31
    o = 0
    if 1:
        print "read from DDR"
        sds.write_soc_reg(0x210, o | ((n-1)<<24) | (1<<30))
        time.sleep(0.1)
        print "counts 0x%08x" % sds.read_soc_reg(0x212)
        decode_mig_status(sds.read_soc_reg(0x211))

        print "read from FIFO"
        for i in range(n):
            print "rd %2d -> 0x%08x" % (i, sds.read_soc_reg(0x218))
        time.sleep(0.1)
        print "counts 0x%08x" % sds.read_soc_reg(0x212)
        decode_mig_status(sds.read_soc_reg(0x211))

    data = sds.read_ddr(0, 32)
    for i in range(len(data)):
        print "%2d -> 0x%08x" % (i, data[i])

    n = 0x100
    o = 0x100
    wr_data = [ random.randrange(1<<32) for _ in range(n) ]
    sds.write_ddr(o, wr_data)
    rd_data = sds.read_ddr(o, n)

    assert all(wr_data == rd_data)

if __name__ == '__main__':
    main()
