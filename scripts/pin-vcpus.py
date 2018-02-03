#!/usr/bin/env python

import os
import sys


CPUS_PER_VM = 2
NR_VMS = 24

for i in range(NR_VMS):
    for c in range(CPUS_PER_VM):
        j = i % 2
        cmd = 'virsh vcpupin --vcpu %d --cpulist %d varbench-%d' % (c, (i*2) - j + (c*2), i)
        print cmd
        os.system(cmd)
