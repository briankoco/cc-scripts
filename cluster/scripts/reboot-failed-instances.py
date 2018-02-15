#!/usr/bin/env python

import re
import os
import sys
import getopt
import json
import subprocess

from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client

def usage(argv, exit=None):
    print >> sys.stderr, "Usage: %s [OPTIONS] <Lease ID>" % argv[0]
    print >> sys.stderr, "  -h (--help)     : print help and exit"
    print >> sys.stderr, "  -o (--nova-like=<o>)    : only reboot instances with names that contain <o>"
    if exit is not None:
        sys.exit(exit)


def parse_cmd_line(argc, argv):
    opts = []
    args = []
    nova_like = None

    try:
        opts, args = getopt.getopt(argv[1:], "ho:", 
            ["help, nova-like="])
    except getopt.GetoptError:
        usage(argv, exit=1)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(argv, exit=0)

        elif o in ("-o", "--nova-like"):
            nova_like = a

        else:
            usage(argv, exit=1)

    if len(args) != 1:
        usage(argv, exit=1)

    return nova_like, args[0]

def reboot(server, lease_id):
    name = server.name
    server.delete()

    cmd = ["nova", "boot", "--flavor", "baremetal",
           "--image", "kvm-and-docker-2.3.2018",
           "--key-name", "pet-lab-2", 
           "--nic", "net-name=sharednet1",
           "--hint", "reservation=%s" % lease_id,
           "%s" % name]
    
    str_cmd = " ".join(cmd)
    print str_cmd
    os.system(str_cmd)

    print "sleep 30"
    os.system("sleep 30")


def main(argc, argv, envp):
    nova_like, lease_id = parse_cmd_line(argc, argv)

    # Get Openstack stuff
    try:
        auth_url = envp['OS_AUTH_URL']
        username = envp['OS_USERNAME']
        password = envp['OS_PASSWORD']
        project_name = envp['OS_PROJECT_NAME']
    except KeyError:
        print >> sys.stderr, "You must source your OpenStack configuration file first"
        return 2

    auth = identity.Password(auth_url=auth_url,
                          username=username,
                          password=password,
                          project_name=project_name)
#                          project_domain_id=project_domain_id,
#                          user_domain_id=user_domain_id)
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2.1", session=sess)

    # parse out hosts
    hosts        = nova.servers.list()
    valid_hosts  = sorted([h for h in hosts if nova_like is None or nova_like in h.name], key=lambda h: h.name)

    _dict = []

    for h in valid_hosts:
        if h.status == "ERROR":
            print 'Rebooting %s which is in an ERROR status' % h.name 
            reboot(h, lease_id)


if __name__ == "__main__":
    argv = sys.argv
    argc = len(sys.argv)
    envp = os.environ
    sys.exit(main(argc, argv, envp))
