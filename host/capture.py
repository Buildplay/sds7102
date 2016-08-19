#! /usr/bin/python
import sds
import numpy
import sys
import time
import os

from sds import SDS, hd
from convert import convert, save, display

def main():
    sds = SDS(sys.argv[1])

    high = 1

    sds.odd_relay(1)
    sds.ext_relay(0)

    if high:
        sds.atten(0, 1)
    else:
        sds.atten(0, 1)

    sds.atten(1, 1)

    if 1:
        # Set the vertical shift for channel 1 and 2
        if high:
            sds.dac8532(0, 0x9150)
        else:
            sds.dac8532(0, 0x7800)
        sds.dac8532(1, 0x6c00)

    if 1:
        # Set the gain for channel 1 and 2
        if high:
            sds.lmh6518(0, 0xc1)
        else:
            sds.lmh6518(0, 0xc9)
        sds.lmh6518(1, 0xca)

    if 1:
        # Set the sampling frequency
        sds.adf4360(0x000000c9)	# R Counter Latch
        sds.adf4360(0x000fe100)	# Control Latch
        if 1:
            # 400 MHz
            sds.adf4360(0x0000fa02)	# N Counter Latch
        elif 0:
            # 480 MHz
            sds.adf4360(0x00012c02)	# N Counter Latch
        else:
            # 500.8 MHz
            sds.adf4360(0x00013902)	# N Counter Latch

    if 1:
        # Set up the ADC
        sds.adc08d500(0x001b89ff)
        sds.adc08d500(0x001a007f)
        sds.adc08d500(0x001dffff)
        sds.adc08d500(0x001effff)

        sds.adc08d500(0x001389ff)
        sds.adc08d500(0x0012007f)
        sds.adc08d500(0x001dffff)
        sds.adc08d500(0x001effff)

    if 1:
        # This selects 2 channels instead of 1 combined
        sds.adc08d500(0x001d3fff)

    if 1:
        # Set the trigger levels
        sds.bu2506(1, 0x295)
        sds.bu2506(2, 0x295)

    if 1:
        sds.write_soc_reg(0x230, 0)
        time.sleep(0.1)

        sds.mig_reset()
        time.sleep(0.1)

        if 0:
            sds.write_ddr(0, [0xaaaaaaaa] * 512)
        else:
            sds.write_ddr(0, [0x55555555] * 512)

    if 0:
        data = sds.capture(1024)
    else:
        n = 256
        n *= 1024
        data = sds.mig_capture(256 * 1024, synthetic = 0)

    hd(data[:256])

    data.tofile('capture.bin')

    samples = convert(data)

    if 'DISPLAY' in os.environ:
        display(samples)
    else:
        save('plot.png', samples)

if __name__ == '__main__':
    if not sys.argv[0]:
        sys.argv = [ '', 'sds' ]

    main()
