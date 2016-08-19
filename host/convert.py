#! /usr/bin/python
import numpy
import sys

print_values = 0

def convert(a):

    pins = ('B10', 'B12', 'C13', 'B14', 'C11', 'D11', 'F10', 'E13', # DI0..7
            'B15', 'C15', 'D14', 'E15', 'F15', 'G14', 'H15', 'J14', # DId0..7
            'K12', 'L12', 'M13', 'J11', 'J13', 'G12', 'H13', 'F12', # DQ0..7
            'T14', 'R14', 'R15', 'P15', 'N14', 'M15', 'L14', 'K15') # DQd0..7

    pin_rev = { pins[i] : i for i in range(len(pins)) }

    if 0:
        # Orded by pins
        order = [
            [ 'B10', 'C11', 'B12', 'C13', 'F10', 'B14', 'D11', 'E13' ],
            [ 'B15', 'F12', 'D14', 'C15', 'E15', 'F15', 'G14', 'H15' ],
            [ 'G12', 'H13', 'J11', 'J13', 'K12', 'J14', 'K15', 'N14' ],
            [ 'M15', 'L14', 'P15', 'R15', 'R14', 'T14', 'L12', 'M13' ],
            ]

    elif 0:
        # Orded by pins, inverted
        order = [
            [ 'B10', 'c11', 'B12', 'C13', 'F10', 'b14', 'D11', 'E13' ],
            [ 'B15', 'f12', 'd14', 'C15', 'E15', 'F15', 'G14', 'h15' ],
            [ 'g12', 'H13', 'J11', 'J13', 'K12', 'J14', 'K15', 'n14' ],
            [ 'M15', 'l14', 'P15', 'R15', 'R14', 't14', 'L12', 'M13' ],
            ]

    elif 0:
        # Orderd by frequency
        order = [
            [ 'E13', 'F10', 'D11', 'c11', 'P15', 'K12', 'B10', 'L12' ],
            [ 'f12', 'H13', 'g12', 'F15', 'b14', 'B15', 'R15', 'R14' ],
            [ 'J14', 'h15', 'G14', 'J13', 'E15', 'M13', 't14', 'C13' ],
            [ 'K15', 'l14', 'M15', 'n14', 'J11', 'd14', 'C15', 'B12' ],
            ]

    elif 0:
        # Two channels, all high bits in the first two sets
        order = [
            [ 'E13', 'F10', 'D11', 'c11', 'E15', 'd14', 'B10', 'C13' ],
            [ 'f12', 'h15', 'G14', 'F15', 'b14', 'B15', 'C15', 'B12' ],
            [ 'J14', 'H13', 'g12', 'J13', 'P15', 'M13', 't14', 'L12' ],
            [ 'K15', 'l14', 'M15', 'n14', 'J11', 'K12', 'R15', 'R14' ],
            ]

    elif 0:
        # Two channels, all high bits in the first two sets, manual fix
        order = [
            [ 'E13', 'F10', 'D11', 'c11', 'b14', 'd14', 'B10', 'C13' ],
            [ 'J14', 'h15', 'G14', 'F15', 'E15', 'B15', 'C15', 'B12' ],
            [ 'f12', 'H13', 'g12', 'J13', 'J11', 'M13', 't14', 'L12' ],
            [ 'K15', 'l14', 'M15', 'n14', 'P15', 'K12', 'R15', 'R14' ],
            ]

    elif 1:
        order = [
            [ 'J14', 'h15', 'G14', 'F15', 'E15', 'd14', 'C15', 'B15' ], # DId
            [ 'E13', 'F10', 'D11', 'c11', 'b14', 'C13', 'B12', 'B10' ], # DI
            [ 'K15', 'l14', 'M15', 'n14', 'P15', 'R15', 'R14', 't14' ], # DQd
            [ 'f12', 'H13', 'g12', 'J13', 'J11', 'M13', 'L12', 'K12' ], # DQ
            ]

    if 0:
        forder = [val for sublist in order for val in sublist]
        print "forder", forder
        for i in range(32):
            if pins[i].lower() in forder:
                a ^= (1<<i)

    if 0:
        vand = 0xffffffff
        vor = 0
        changes = [ 0 for _ in range(32) ]
        last = a[0]
        for v in a[310:330]:
        # for v in a:
            vand &= v
            vor |= v
            t = last ^ v
            for i in range(32):
                if t & (1<<i):
                    changes[i] += 1
            last = v

        print "# and", hex(vand)
        for o in order:
            for p in o:
                if vand & (1<<pin_rev[p.upper()]):
                    print p,
            print

        print "# or", hex(vor)
        for o in order:
            for p in o:
                if not vor & (1<<pin_rev[p.upper()]):
                    print p,
            print

        print "# changes", sorted(zip(changes, pins))
        l = None
        for n, name in sorted(zip(changes, pins)):
            if l != n:
                print
                print n,
                l = n
            print name,
        print

    if 0:
        o2 = []
        for o in order:
            c2 = []
            for ci in range(len(o)):
                if ci == 0:
                    c2.append(o[ci])
                elif o[ci].isupper():
                    c2.append(o[ci].lower())
                else:
                    c2.append(o[ci].upper())
            o2.append(c2)

        order = o2

    if 0:
        ba = []
        samples = [ [] for _ in range(4) ]
        for i in range(len(a)):
            for o in range(len(order)):
                v = 0
                if print_values:
                    print "#", i,
                for p in range(len(order[o])):
                    v <<= 1
                    b = (a[i] >> pin_rev[order[o][p].upper()]) & 1
                    if print_values:
                        print "%-3s" % order[o][p], b,
                    v |= b
                if print_values:
                    print
                if print_values:
                    print v
                samples[o].append(v)
            # print
            # print

    else:
        samples = [
            (a >> 8) & 0xff,
            (a >> 0) & 0xff,
            (a >> 24) & 0xff,
            (a >> 16) & 0xff,
            ]

    return samples

def display(samples):
    import os
    import matplotlib.pyplot as plt

    fig = plt.figure(1, figsize = (8, 6))

    for i, (c, m) in enumerate([ ('r','.'), ('g','.'), ('b','.'), ('m','.') ]):
        plt.plot(numpy.array(range(len(samples[i]))) + 0.5 * (i & 1), samples[i],
                 color = c, marker = m, linestyle = '')

    plt.show()

def save(fn, samples):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig = plt.figure(1, figsize = (8, 6))

    for i, (c, m) in enumerate([ ('r','.'), ('g','.'), ('b','.'), ('m','.') ]):
        plt.plot(numpy.array(range(len(samples[i]))) + 0.5 * (i & 1), samples[i],
                 color = c, marker = m, linestyle = '')

    plt.tight_layout()

    fig.savefig(fn, dpi = 90)

def main():
    if 0:
        a = []
        for l in open(sys.argv[1]):
            l = l.strip()
            if not l or l.startswith('#'):
                continue
            parts = l.split()
            a.append(int(parts[1], 0))

        a = numpy.array(a)
        print "#", a

    else:
        a = numpy.loadtxt(sys.argv[1], dtype = numpy.uint32, delimiter = ' ')

    samples = convert(a[:1000])

    if 'DISPLAY' in os.environ:
        display(samples)
    else:
        save('plot.png', samples)

if __name__ == '__main__':
    import os

    if not sys.argv[0]:
        if 0:
            os.environ['DISPLAY'] = ':0'
        sys.argv = [ '', '../capture.txt' ]

    main()
