#!/usr/bin/env python

import os
import sys

for i in range(48):
    name = 'varbench-%d' % i

    cmd = 'virsh destroy %s' % name
    os.system(cmd)

#    cmd = 'virsh undefine %s' % name
#    os.system(cmd)
