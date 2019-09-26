#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import os
import logging
import ipaddress
from collections import namedtuple
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

# Define logging handler for file and console logging.  Console logging can be desplayed during
# program run time, similar to print.  Program can display or write to log file if more debug 
# info needed.  DEBUG is lowest and will display all logging messages in program.  
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('file.log')
c_handler.setLevel(logging.CRITICAL)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers.  This creates custom logging format such as timestamp,
# module running, function, debug level, and custom text info (message) like print.
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the parent custom logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

#def get_all_static_routes():
#    url = """https://{apic}/api/node/class/ipRouteP.json""".format(apic=apic)
##def get_static_routes(*tenants):
##    for tenant in tenants:
##        url = """https://{apic}/api/mo/ni/SI.json?target-subtree-class=l3extRsExtx&query-target-filter=eq(l3extRsEctx.tnFvCtxName,"SI")&query-target=subtree
#    results = GetResponseData(url,cookie)
#    return results
#def parse_static_route_dn(results):
#    for entry in results:
#        print(entry)
#        path = entry['ipRouteP']['attributes']['dn'].split('/')
#        tenant = path[1]
#        l3out = path[2]
#        location = re.search(r'rsnodeL3OutAtt-\[.*\]/',entry['ipRouteP']['attributes']['dn']).group()
#        #location = path[4].replace('rsnodeL3OutAtt-', '').replace('[', '').replace(']','')
#        route = re.search(r'rt-\[.*\]',entry['ipRouteP']['attributes']['dn']).group()#.replace('rt-','')
#        print(tenant, l3out, location, route)
def get_all_l3extRsNodeL3OutAtt():
    url = """https://{apic}/api/node/class/l3extRsNodeL3OutAtt.json""".format(apic=apic)
    results = GetResponseData(url,cookie)
    nodelist = []
    for result in results:
        node = result['l3extRsNodeL3OutAtt']['attributes']['tDn']
        #print(node)
        dn = result['l3extRsNodeL3OutAtt']['attributes']['dn']
        #print(dn)
        Node = namedtuple('Node', ['node', 'dn'])
        nodelist.append(Node(node=node,dn=dn))
    return nodelist

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    clear_screen()
    nodelist = get_all_l3extRsNodeL3OutAtt()
    noderoutelist = []
    for node in nodelist:
        url = """https://{apic}/api/node/mo/{node}.json?query-target=children&target-subtree-class=ipRouteP""".format(apic=apic,node=node.dn)
        result = GetResponseData(url,cookie)
        noderoutelist.append((node.node, result))
        for iproute in result:
            print(iproute['ipRouteP']['attributes']['descr'], iproute['ipRouteP']['attributes']['ip'])
    print(noderoutelist)
    #import pdb; pdb.set_trace()
   # for node in nodelist:
   #     url = """https://{apic}/api/node/class/l3extRsNodeL3OutAtt.json""".format(apic=apic)
   #     result = GetResponseData(url)
    #results = get_all_static_routes()
    #parse_static_route_dn(results)
    raw_input()