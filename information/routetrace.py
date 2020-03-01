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
import ipaddress
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)

def getallroutes(leaf,vrf,tenant):
    url = """https://{apic}/api/node/mo/topology/pod-1/node-{}/sys/uribv4/dom-{}:{}.json?rsp-subtree=full&query-target=subtree&target-subtree-class=uribv4Route""".format(leaf,vrf,tenant,apic=apic)
    result = GetResponseData(url,cookie)
    routelist = []
    for routes in result:
        routeprefix = routes['uribv4Route']['attributes']['prefix']
        subnetmask = routes['uribv4Route']['attributes']['prefixLength']
        dn = routes['uribv4Route']['attributes']['dn']
        vrf = dn[5:6].replace('dom-', '')
        if routes['uribv4Route'].get('children'):
            nexthopobjectlist = []
            for route in routes['uribv4Route']['children']:
                nexthopvrf = route['uribv4Nexthop']['attributes']['vrf']
                nexthopaddr = route['uribv4Nexthop']['attributes']['addr']
                nexthopif = route['uribv4Nexthop']['attributes']['if']
                nexthopstatus = route['uribv4Nexthop']['attributes']['active']
                nexthoptype = route['uribv4Nexthop']['attributes']['type']
                nexthoprouteType = route['uribv4Nexthop']['attributes']['routeType']
                #print(nexthopif,)
                nexthopobjectlist.append(nexthopObject(nexthopif=nexthopif, 
                    nexthopaddr=nexthopaddr, nexthopstatus=nexthopstatus, nexthoptype=nexthoptype,
                    nexthopvrf=nexthopvrf, nexthoprouteType=nexthoprouteType))
        routelist.append(routeObject(routeprefix=routeprefix, subnetmask=subnetmask, nexthoplist=nexthopobjectlist))
    return routelist

class nexthopObject():
    def __init__(self, nexthopif=None, nexthopaddr=None, nexthopstatus=None,
                 nexthoptype=None, nexthopvrf=None, nexthoprouteType=None):
        self.nexthopif = nexthopif
        self.nexthopaddr = nexthopaddr
        self.nexthopstatus = nexthopstatus
        self.nexthoptype = nexthoptype
        self.nexthopvrf = nexthopvrf
        self.nexthoprouteType = nexthoprouteType
    def __repr__(self):
        return self.nexthopaddr
    def __getitem__(self, route):
        if route in self.nexthopaddr:
            return self.nexthopaddr
        else:
            return None

class routeObject():
    def __init__(self, vrf=None, routeprefix=None, subnetmask=None, nexthoplist=[]):
        self.vrf = vrf
        self.routeprefix = routeprefix
        self.subnetmask = subnetmask
        self.nexthoplist = nexthoplist
    def __repr__(self):
        return self.routeprefix
    def __getitem__(self, route):
        if route in self.routeprefix:
            return self.routeprefix
        else:
            return None
    def add_nexthop(self, nexthoplistitem):
        self.nexthoplist.append(nexthoplistitem)

def allips():
    #get_Cookie()
    url = """https://{apic}/api//class/ipv4Addr.json""".format(apic=apic)
    return GetResponseData(url)

def iproutecheckfromleaf(leafnum=102, autocomplete=None):
    cidrcollection = {}
    if not autocomplete:
        askleaf = raw_input("What leaf [default=102] ") or leafnum
        asktenant = raw_input("what tenant [default=SI] ") or 'SI'
        askvrf = raw_input("What vrf [default=SI]: ") or 'SI'
        askipaddress = raw_input("Compair ip address to routing table: ")
    else: 
       askleaf = leafnum
       asktenant = autocomplete[1] 
       askvrf    = autocomplete[2] 
       askipaddress   = autocomplete[3] 
    routes= getallroutes(vrf=askvrf,leaf=askleaf,tenant=asktenant)
    ipv4addressresults, totalcount = allips()  #not used yet
    possible_route_matches = []
    for route in routes:
        if ipaddress.ip_address(unicode(askipaddress)) in ipaddress.ip_network(unicode(route.routeprefix)):
            possible_route_matches.append(route)
    if len(possible_route_matches) > 1:
        for network in possible_route_matches:
            slashlocation = network.routeprefix.find('/')
            cidr = network.routeprefix[slashlocation+1:]
            cidrcollection[cidr] = network
    elif len(possible_route_matches) == 1:
        network = possible_route_matches[0]
        slashlocation = network.routeprefix.find('/')
        cidr = network.routeprefix[slashlocation+1:]
        cidrcollection[cidr] = network
    maxcidr = max(cidrcollection)
    return cidrcollection[maxcidr], ipv4addressresults, (askleaf,asktenant,askvrf,askipaddress)
        #stringa += "{} {} {} {} {} ".format(route, route.nexthoplist[0].nexthopaddr,route.nexthoplist[0].nexthoptype, route.nexthoplist[0].nexthopif, route.nexthoplist[0].nexthoprouteType)
        #if 'recursive' in route.nexthoplist[0].nexthoptype:
        #    stringa += allnexthopIPs(route.nexthoplist[0].nexthopaddr, ipv4addressresults) + '\n'
        #else:
        #    stringa += '\n'
    #possible_route_matches = stringa.strip().split('\n')
#possible_route_matches = iproutecheckfromleaf()
#routestring = ""
#cidrcollection = {}
#if len(possible_route_matches) > 1:
#    for network in possible_route_matches:
#        slashlocation = network.routeprefix.find('/')
#        cidr = network.routeprefix[slashlocation+1:]
#        cidrcollection[cidr] = network
#elif len(possible_route_matches) == 1:
#    network = possible_route_matches[0]
#    slashlocation = network.routeprefix.find('/')
#    cidr = network.routeprefix[slashlocation+1:]
#    cidrcollection[cidr] = network
#
#maxcidr = max(cidrcollection)
#route = cidrcollection[maxcidr]

def allnexthopIPs(ip,ipv4addressresults):
    for route in ipv4addressresults:
        if route['ipv4Addr']['attributes']['addr'] == ip:
            return str(route['ipv4Addr']['attributes']['dn'].split('/')[2:3])


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    clear_screen()
    routestring = ""
    route, ipv4addressresults, askedresults = iproutecheckfromleaf()
    routestring+= "{} {} {} {} {} ".format(route, route.nexthoplist[0].nexthopaddr,route.nexthoplist[0].nexthoptype, route.nexthoplist[0].nexthopif, route.nexthoplist[0].nexthoprouteType)
    if 'recursive' in route.nexthoplist[0].nexthoptype:
        routestring += allnexthopIPs(route.nexthoplist[0].nexthopaddr, ipv4addressresults) 
    print(routestring)
    #import pdb; pdb.set_trace()


    results = allnexthopIPs(route.nexthoplist[0].nexthopaddr, ipv4addressresults)
    nexthopleafip = re.search(r"\d\d\d", results).group()
    route, ipv4addressresults, askedresults = iproutecheckfromleaf(nexthopleafip, autocomplete=askedresults)
    routestring = ""
    routestring+= "{} {} {} {} {} ".format(route, route.nexthoplist[0].nexthopaddr,route.nexthoplist[0].nexthoptype, route.nexthoplist[0].nexthopif, route.nexthoplist[0].nexthoprouteType)
    if 'recursive' in route.nexthoplist[0].nexthoptype:
        routestring += allnexthopIPs(route.nexthoplist[0].nexthopaddr, ipv4addressresults) 
    print(routestring)
    raw_input('.')