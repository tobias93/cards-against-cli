#!/usr/bin/env python3
"""
Handles the service announcement of the Cards against Cli Server.

Debugging command: (linux, requires avahi) (A similar command should be available using bonjour on mac)
> avahi-browse --resolve "_cac._tcp"

Use the environment variable CAC_LISTEN_INTERFACES to control, 
on which interface(s) the service should be announced.
Example:
export CAC_ANNOUNCE_INTERFACES=lo,wlp4s0

"""

from zeroconf import ServiceInfo, Zeroconf
import socket
import logging
import netifaces
import os

_logger = logging.getLogger(__name__)


def start_announcing_on_if(server_name, interface, address, port):
    _logger.info(
        f"Starting to announce server  named '{server_name}' via {interface} as {address}:{port}.")
    service = ServiceInfo("_cac._tcp.local.",
                          f"{server_name}._cac._tcp.local.",
                          socket.inet_aton(address), port,
                          properties=dict(name=server_name))
    zeroconf = Zeroconf(interfaces=[address])
    zeroconf.register_service(service)
    return zeroconf, service


def stop_announcing_on_if(zeroconf, service, iface):
    _logger.info(f"Unregistering service on {iface}...")
    zeroconf.unregister_service(service)
    zeroconf.close()


def stop_announcing(announcers):
    for zeroconf, service, iface in announcers:
        stop_announcing_on_if(zeroconf, service, iface)


def start_announcing(server_name, port):
    # announce on all interfaces
    ifaces = get_interfaces()
    result = []
    for iface, addr in ifaces.items():
        zeroconf, service = start_announcing_on_if(server_name, iface, addr, port)
        result.append((zeroconf, service, iface))
    return result


def get_interfaces():

    # get the list of interfaces
    ifaces = netifaces.interfaces()
    
    # get the address for each interface
    result = dict()
    for iface in ifaces:
        addr = get_address_for_interface(iface)
        if addr:
            result[iface] = addr

    if "CAC_ANNOUNCE_INTERFACES" in os.environ:
        iface_whitelist = os.environ["CAC_ANNOUNCE_INTERFACES"].split(',')
        result = {iface:addr for iface, addr in result.items() if iface in iface_whitelist and iface!=""}

    return result


def get_address_for_interface(iface):
    addrs = netifaces.ifaddresses(iface)

    # currently, the python zeroconf implementation does only support ipv4 :-(
    # however, the server still 
    addr_family = netifaces.AF_INET
    if addr_family in addrs:
        inet_addrs = addrs[netifaces.AF_INET]
        for inet_addr in inet_addrs:
            if "addr" in inet_addr:
                return inet_addr["addr"]
    return None
