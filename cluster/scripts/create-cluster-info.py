#!/usr/bin/env python

import os
import sys
import getopt
import json

from keystoneauth1 import identity
from keystoneauth1 import session
from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client

def usage(argv, exit=None):
    print >> sys.stderr, "Usage: %s [OPTIONS] <output JSON file>" % argv[0]
    print >> sys.stderr, "  -h (--help)     : print help and exit"
    print >> sys.stderr, "  -o (--nova-like=<o>)    : only generate entries for host entries that contain <o>"
    print >> sys.stderr, "  -e (--neutron-like=<o>) : only generate entries for VM entries that contain <o>"
    print >> sys.stderr, "  -d (--disable-vms)      : only generate host entries"
    print >> sys.stderr, "  -s (--single-host=<s>)  : put all VM entries on a single host <s>"
    if exit is not None:
        sys.exit(exit)


def parse_cmd_line(argc, argv):
    opts = []
    args = []
    nova_like = None
    neutron_like = None
    host_only = False
    host = None

    try:
        opts, args = getopt.getopt(argv[1:], "ho:e:ds:", 
            ["help, nova-like=", "neutron-like=", "disable-vms", "single-host="])
    except getopt.GetoptError:
        usage(argv, exit=1)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(argv, exit=0)

        elif o in ("-o", "--nova-like"):
            nova_like = a

        elif o in ("-e", "--neutron-like"):
            neutron_like = a

        elif o in ("-d", "--disable-vms"):
            host_only = True

        elif o in ("-s", "--single-host"):
            host = a

        else:
            usage(argv, exit=1)

    if len(args) != 1:
        usage(argv, exit=1)

    return nova_like, neutron_like, host_only, host, args[0]


def main(argc, argv, envp):
    nova_like, neutron_like, host_only, host, out_file = parse_cmd_line(argc, argv)

    if host is not None:
        if host_only:
            print >> sys.stderr, "Cannot specify --disable-vms and --single-host"
            return 2

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
    neutron = neutron_client.Client(session=sess)
    nova = nova_client.Client("2.1", session=sess)

    hosts     = nova.servers.list()
    port_list = neutron.list_ports()
    ports     = port_list['ports']

    # parse out hosts and guests that match the keys and sort them by name
    valid_hosts  = sorted([h for h in             hosts if nova_like    is None or nova_like    in h.name],     key=lambda h: h.name)
    valid_guests = sorted([g for g in [p for p in ports if neutron_like is None or neutron_like in p['name']]], key=lambda g: g['name'])

    _dict = []

    if host is None:
        # Algorithm: get list of nova hosts and neutron ports
        # Walk though in tandem until one or the other runs out.
        
        off = 0

        if host_only:
            for h in valid_hosts:
                host_network = h.networks['sharednet1'][0]
                host_name    = h.name

                _dict.append({
                    'host_hostname'  : host_name,
                    'host_ip'        : host_network,
                })
        else:
            vm_id = 0
            for h, g in zip(valid_hosts, valid_guests):
                host_network = h.networks['sharednet1'][0]
                host_name    = h.name

                ips = g['fixed_ips']
                assert len(ips) == 1

                guest_name = g['name']
                guest_network = ips[0]['ip_address']
                guest_mac = g['mac_address']

                _dict.append({
                    'host_hostname'  : host_name,
                    'host_ip'        : host_network,
                    'guest_hostname' : guest_name,
                    'guest_ip'       : guest_network,
                    'guest_mac'      : guest_mac,
                    'guest_id'       : vm_id
                })

                vm_id += 1
    else:
        # Just get all guests and put them on a single host
        _h = None
        for h in valid_hosts:
            if h.name == host:
                _h = h
                break
        else:
            print >> sys.stderr, "Could not find hostname %s in list of nova hosts" % host
            return 2

        host_network = h.networks['sharednet1'][0]
        host_name    = h.name

        vm_id = 0
        for g in valid_guests:
            ips = g['fixed_ips']
            assert len(ips) == 1

            guest_name = g['name']
            guest_network = ips[0]['ip_address']
            guest_mac = g['mac_address']

            _dict.append({
                'host_hostname'  : host_name,
                'host_ip'        : host_network,
                'guest_hostname' : guest_name,
                'guest_ip'       : guest_network,
                'guest_mac'      : guest_mac,
                'guest_id'       : vm_id
            })

            vm_id += 1

    json_data = {
        "vms_per_host" : 1 if host is None else vm_id,
        "info" : _dict
    }

    with open(out_file, 'w') as f:
        json.dump(json_data, f, indent=4)


if __name__ == "__main__":
    argv = sys.argv
    argc = len(sys.argv)
    envp = os.environ
    sys.exit(main(argc, argv, envp))
