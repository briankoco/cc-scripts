#!/usr/bin/env python

import getopt
import os
import sys
import json

def usage(argv, exit=None):
    print >> sys.stderr, "Usage %s [OPTIONS] <cluster info JSON> <hostfile (out)>" % argv[0]
    print >> sys.stderr, "  -h (--help)  : print help and exit"
    print >> sys.stderr, "  -s (--slots) : number of MPI slots per node"
    print >> sys.stderr, "  -H (--Host)  : use Host IP addresses rather than guest"
    if exit is not None:
        sys.exit(exit)

def parse_cmd_line(argc, argv):
    opts = []
    args = []
    slots = 1
    host = False

    try:
        opts, args = getopt.getopt(
            argv[1:],
            "hs:H",
            ["help", "slots=", "Host"])
    except getopt.GetoptError, err:
        print >> sys.stderr, err
        usage(argv, exit=1)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(argv, exit=0)

        elif o in ("-s", "--slots"):
            slots = int(a)

        elif o in ("-H", "--Host"):
            host = True

        else:
            usage(argv, exit=1)

    if len(args) != 2:
        usage(argv, exit=1)

    return slots, host, args[0], args[1]

def main(argc, argv, envp):
    slots, host, cluster_info, hostfile = parse_cmd_line(argc, argv)

    with open(cluster_info, "r") as f:
        data = json.load(f)["info"]

    if host:
        ip_selector = 'host_ip'
    else:
        ip_selector = 'guest_ip'

    with open(hostfile, "w") as f:
        f.write(
            '\n'.join(["%s slots=%d max-slots=%d" % (node[ip_selector], slots, slots)\
            for node in data])
        )

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    envp = os.environ
    sys.exit(main(argc, argv, envp))
