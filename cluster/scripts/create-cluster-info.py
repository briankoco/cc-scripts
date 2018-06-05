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
    print >> sys.stderr, "  -o (--nova-like=<o>)    : generate entries for host entries that contain <o>"
    print >> sys.stderr, "  -e (--neutron-like=<o>) : generate entries for VM entries that contain <o>"
    print >> sys.stderr, "  -p (--passthrough-net)  : generate guest IP addresses on a private 192.168.0.x network"
    print >> sys.stderr, "  -s (--single-host=<s>)  : put all VM entries on a single host <s>"
    if exit is not None:
        sys.exit(exit)


def parse_cmd_line(argc, argv):
    opts = []
    args = []
    nova_like = None
    neutron_like = None
    passthrough_net = False
    host = None

    try:
        opts, args = getopt.getopt(argv[1:], "ho:e:ps:", 
            ["help, nova-like=", "neutron-like=", "passthrough-net", "single-host="])
    except getopt.GetoptError:
        usage(argv, exit=1)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage(argv, exit=0)

        elif o in ("-o", "--nova-like"):
            nova_like = a

        elif o in ("-e", "--neutron-like"):
            neutron_like = a

        elif o in ("-p", "--passthrough-net"):
            passthrough_net = True

        elif o in ("-s", "--single-host"):
            host = a

        else:
            usage(argv, exit=-1)

    if len(args) != 1:
        usage(argv, exit=-1)

    if nova_like is None:
        print >> sys.stderr, "--nova_like is required"
        return -1

    if passthrough_net:
        if host is not None:
            print >> sys.stderr, "Cannot specify both --passthrough-net and --single-host"
            return -1
    else:
        if neutron_like is None:
            print >> sys.stderr, "Must specify at least one of --passthrough-net and/or --neutro-like"
            return -1

    return nova_like, neutron_like, passthrough_net, host, args[0]

def get_host_mac_address(host_ip_address, ports):
    for p in ports:
        for ip in p["fixed_ips"]:
            if ip["ip_address"] == host_ip_address:
                return p["mac_address"]

    return None


# A very crude assumption here is that "nic 2" on each machine has a MAC
# address that is +2 "greater than" the NIC that we can actually see via
# neutron

# 2 edge cases:
#   (1) for values less than 0x10, we need to prepend a '0':
#       e.g., 0x0f instead of 0xf
#
#   (2) for values greater than 0xfd, need to add 1 to the second to last hex
#       

def inc_hex_val(address_list, index, val):
    old_val = int(address_list[index], 16)
    new_val = old_val + val

    if new_val >= 0x100:
        new_val %= 0x100
        address_list[:] = inc_hex_val(address_list, index - 1, 1)

    address_list[index] = hex(new_val)[2:]

    if new_val < 0xf:
        address_list[index] = '0' + address_list[index]

    return address_list

def get_guest_mac_address_from_host(host_mac_address):
    return ":".join(inc_hex_val(host_mac_address.split(":"), -1, 2))

def main(argc, argv, envp):
    nova_like, neutron_like, passthrough_net, host, out_file = parse_cmd_line(argc, argv)

    # Get Openstack stuff
    try:
        auth_url = envp['OS_AUTH_URL']
        username = envp['OS_USERNAME']
        password = envp['OS_PASSWORD']
        project_name = envp['OS_PROJECT_NAME']
    except KeyError:
        print >> sys.stderr, "You must source your OpenStack configuration file first"
        return -2

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
    valid_hosts = sorted([h for h in hosts if h.status == "ACTIVE" and (nova_like is None or nova_like in h.name)], key=lambda h: h.name)

    if neutron_like:
        valid_guests = sorted([g for g in [p for p in ports if neutron_like in p['name']]], key=lambda g: g['name'])

    _dict = []


    # First check: whether we want a single host or multiple hosts
    if host is None:
        # Algorithm: get list of nova hosts and neutron ports
        # Walk though in tandem until one or the other runs out.
        
        off = 0

        #for h,g in zip(valid_hosts, valid_guests)

        for off, h in enumerate(valid_hosts):
            host_network = h.networks['sharednet1'][0]
            host_name    = h.name
            host_mac     = get_host_mac_address(host_network, ports)

            guest_virt_mac = None
            guest_phys_mac = None

            # If user specified neuron ports, get guest info from them
            if neutron_like:
                g = valid_guests[off]
                ips = g['fixed_ips']
                assert len(ips) == 1

                #guest_name = g['name']
                guest_dynamic_network = ips[0]['ip_address']
                guest_virt_mac = g['mac_address']

            else:
                # guest_name = "vm-%d" % off
                guest_dynamic_network = None
                guest_virt_mac = None

            guest_name = "vm-%d" % off

            if passthrough_net:
                guest_static_network = "192.168.0.%d" % (2 + off)
                guest_phys_mac = get_guest_mac_address_from_host(host_mac)

            entry = {
                'host_hostname'    : host_name,
                'host_ip'          : host_network,
                'guest_hostname'   : guest_name,
                'guest_id'         : off,
            }

            if guest_dynamic_network is not None:
                entry.update({
                    'guest_dynamic_ip' : guest_dynamic_network,
                    'guest_virt_mac'   : guest_virt_mac
                })

            if guest_static_network is not None: 
                entry.update({
                    'guest_static_ip' : guest_static_network,
                    'guest_phys_mac'  : guest_phys_mac
                })

            _dict.append(entry)

            # guest_mac, guest_hostname, guest_ip <--- used by guest static IP setup
            # guest_hostname, guest_ip <--- used by guest DHCP setup

            # TODO: change guest static IP setup to use 'guest_static_ip' and 'guest_phys_mac'
            # TODO: change guest DHCP setup to use 'guest_dynamic_ip'
    else:
        # Just get all guests and put them on a single host
        _h = None
        for h in valid_hosts:
            if h.name == host:
                _h = h
                break
        else:
            print >> sys.stderr, "Could not find hostname %s in list of nova hosts" % host
            return -2

        host_network = h.networks['sharednet1'][0]
        host_name    = h.name

        for off, g in enumerate(valid_guests):
            ips = g['fixed_ips']
            assert len(ips) == 1

            guest_name = g['name']
            guest_network = ips[0]['ip_address']
            guest_mac = g['mac_address']

            _dict.append({
                'host_hostname'    : host_name,
                'host_ip'          : host_network,
                'guest_hostname'   : guest_name,
                'guest_dynamic_ip' : guest_network,
                'guest_virt_mac'   : guest_mac,
                'guest_id'         : off,
            })

    json_data = {
        "vms_per_host" : 1 if host is None else off+1,
        "info" : _dict
    }

    with open(out_file, 'w') as f:
        json.dump(json_data, f, indent=4)


if __name__ == "__main__":
    argv = sys.argv
    argc = len(sys.argv)
    envp = os.environ
    sys.exit(main(argc, argv, envp))
