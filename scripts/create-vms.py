#!/usr/bin/env python

import os
import sys



CPUS_PER_VM = 2
NR_VMS = 24


# Replace
# (1) 'varbench-id' with 'varbench-$i'
# (2) 'de:ad:be:ef:00:00' with 'de:ad:be:ef:00:<id>'
# (3) 'varbench-baseimage.img' with 'varbench-$i.img'
# (4) '5900' with '5900+$id'
# (5) Pin vpcus/memory

def port(nr):
    return 5900 + nr

def dec_to_hex(nr):
    if nr > 255:
        print >> sys.stderr, "Error: too many VMS"
        sys.exit(1)

    elif nr > 15:
        base = ''

    else:
        base = '0'

    return base + hex(nr)[2:]
 
for i in range(NR_VMS):
    fname = 'varbench-%d.xml' % i

    cmd = 'cp base-cfg.xml %s' % fname
    os.system(cmd)

    # (1)
    cmd = 'sed -i "s/varbench-id/varbench-%d/g" %s' % (i, fname)
    os.system(cmd)

    # (2)
    cmd = 'sed -i "s/de\:ad\:be\:ef\:00\:00/de\:ad\:be\:ef\:00\:%s/g" % s' % (dec_to_hex(i), fname)
    os.system(cmd)

    # (3) 
    cmd = 'sed -i "s/varbench-baseimage/varbench-%d/g" %s' % (i, fname)
    os.system(cmd)

    # (4) 
    cmd = 'sed -i "s/5900/%d/g" %s' % (port(i), fname)
    os.system(cmd)

    # (5) Update vcpu/numa pinning
    j = i % 2
    for c in range(CPUS_PER_VM):
        cmd = 'sed -i "s/cpu%d/%d/g" %s' % (c, (i*2) - j + (c*2), fname)
        os.system(cmd)

    cmd = 'sed -i "s/nodeset0/%d/g" %s' % (0 if j == 0 else 1, fname)
    os.system(cmd)

    # create it
    cmd = 'virsh create %s' % fname
    os.system(cmd)
