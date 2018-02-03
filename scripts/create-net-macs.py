#!/usr/bin/env python

import os
import sys

def dec_to_hex(nr):
    if nr > 255:
        print >> sys.stderr, "Error: too many VMS"
        sys.exit(1)

    elif nr > 15:
        base = ''

    else:
        base = '0'

    return base + hex(nr)[2:]


def dec_to_ip(nr):
    return 10 + nr

st = "<dhcp>\n"
st += "\t<range start='192.168.122.100' end='192.168.122.254'/>\n"

for i in range(48):
    st += "\t<host mac='de:ad:be:ef:00:%s' ip='192.168.122.%d'/>\n" % (dec_to_hex(i), dec_to_ip(i))

st += "</dhcp>\n"

print st
