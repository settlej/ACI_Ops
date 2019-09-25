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

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-trig", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

#def get_all_static_routes():
#    url = """https://{apic}/api/node/class/ipRouteP.json""".format(apic=apic)
##def get_static_routes(*tenants):
##    for tenant in tenants:
##        url = """https://{apic}/api/mo/ni/SI.json?target-subtree-class=l3extRsExtx&query-target-filter=eq(l3extRsEctx.tnFvCtxName,"SI")&query-target=subtree
#    results, totalcount = GetResponseData(url)
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
    results, totalcount = GetResponseData(url)
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
        result, totalamount = GetResponseData(url)
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