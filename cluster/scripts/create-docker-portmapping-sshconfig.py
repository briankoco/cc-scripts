#!/usr/bin/env python

import getopt
import os
import sys
import json

def usage(argv, exit=None):
    print >> sys.stderr, "Usage %s [OPTIONS] <cluster info JSON> <ssh config (out)>" % argv[0]
    print >> sys.stderr, "  -h (--help)  : print help and exit"
    print >> sys.stderr, "  -p (--port=) : ssh port (default:2222)"
    if exit is not None:
        sys.exit(exit)

def parse_cmd_line(argc, argv):
    opts = []
    args = []
    port = 2222

    try:
        opts, args = getopt.getopt(
            argv[1:],
            "hp:",
            ["help", "port="])
    except getopt.GetoptError, err:
        print >> sys.stderr, err
        usage(argv, exit=1)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(argv, exit=0)

        elif o in ("-p", "--port"):
            port = int(a)

        else:
            usage(argv, exit=1)

    if len(args) != 2:
        usage(argv, exit=1)

    return port, args[0], args[1]

def main(argc, argv, envp):
    port, cluster_info, ssh_config = parse_cmd_line(argc, argv)

    with open(cluster_info, "r") as f:
        data = json.load(f)["info"]

    with open(ssh_config, "w") as f:
        f.write(
            '\n'.join(["Host %s\n\tPort %d" % (node['host_ip'], port)\
            for node in data])
        )

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    envp = os.environ
    sys.exit(main(argc, argv, envp))
