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

class static_route():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.nexthoplist = []
    def add_nexthop(self, nhAddr, pref):
        self.nexthoplist.append((nhAddr, pref))
    def __repr__(self):
        return self.ip

class Tenant():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.vrflist = []
        self.l3outlist = []
    def __repr__(self):
        return self.name
class localvrf():
    def __init__(self, name, **kwargs):
        self.name = name
        self.l3outlist = []
        #self.static_route = []
    def __repr__(self):
        return self.name
class l3outobj():
    def __init__(self, name, **kwargs):
        self.__dict__.update(kwargs)
        self.name = name
        self.vrf = None
        self.static_routelist = []
    def __repr__(self):
        return self.name

def gather_Tenants():
    #url = """https://{apic}/api/node/class/fvTenant.json?rsp-subtree=children&rsp-subtree-class=fvCtx""".format(apic=apic)
    url = """https://{apic}/api/node/class/fvTenant.json?rsp-subtree=full&rsp-subtree-class=fvCtx,l3extOut""".format(apic=apic)
    result = GetResponseData(url, cookie)
    tenantlist = []
    #l3outlist = []
    static_route_list = []
    for tenant in result:
        tenantObj = Tenant(**tenant['fvTenant']['attributes'])
        if tenant['fvTenant'].get('children'):
            for vrf in tenant['fvTenant']['children']:
                if vrf.get('fvCtx'):
                  #  print(vrf['fvCtx']['attributes']['rn'])
                    tenantObj.vrflist.append(localvrf(name=vrf['fvCtx']['attributes']['rn']))
                if vrf.get('l3extOut') and vrf['l3extOut'].get('children'):
                        currentl3outobj = l3outobj(name=vrf['l3extOut']['attributes']['name'], tenant=tenant['fvTenant']['attributes']['name'])
                        for l3 in vrf['l3extOut']['children']:
                            if l3.get('l3extRsEctx'):
                                vrfname = l3['l3extRsEctx']['attributes']['tDn']
                                l3outobj.vrf = localvrf(name=vrfname, vrf=vrfname)
                            if l3.get('l3extLNodeP') and l3['l3extLNodeP'].get('children'):
                                    for l3ext in l3['l3extLNodeP']['children']:
                                       # print('hit5')
                                        if l3ext.get('l3extRsNodeL3OutAtt') and l3ext['l3extRsNodeL3OutAtt'].get('children'):
                                            vrf = location = l3ext['l3extRsNodeL3OutAtt']['attributes']['tDn']
                                            location = l3ext['l3extRsNodeL3OutAtt']['attributes']['tDn']
                                            location = '/'.join(location.split('/')[1:])
                                            for iproute in l3ext['l3extRsNodeL3OutAtt']['children']:
                                                if iproute.get('ipRouteP') and iproute['ipRouteP'].get('children'):
                                                    ipRoute = iproute['ipRouteP']['attributes']['ip']
                                                    staticr = static_route(vrf=vrfname, **iproute['ipRouteP']['attributes'])
                                                    #import pdb; pdb.set_trace()
                                                    for nh in iproute['ipRouteP']['children']:
                                                        staticr.add_nexthop(nhAddr=nh['ipNexthopP']['attributes']['nhAddr'],pref=nh['ipNexthopP']['attributes']['pref'])
                                                    currentl3outobj.static_routelist.append((location, staticr))
                        tenantObj.l3outlist.append(currentl3outobj)
                        del currentl3outobj
                #if l3outlist:
                #   pass
                   # for ten in tenantlist
        #import pdb; pdb.set_trace()

        tenantlist.append(tenantObj)
    for tenant in tenantlist:
        print(tenant)
        for vrf in tenant.vrflist:
            #print(tenant.l3outlist)
            l3outlistvrf = map(lambda x: x.vrf, tenant.l3outlist)
            import pdb; pdb.set_trace()
            print(l3outlistvrf, repr(vrf))
            if repr(vrf) in l3outlistvrf:
                print('\tfound')
       # for l3out in tenant.l3outlist:
       #     import pdb; pdb.set_trace()
       #     vrflistname = map(lambda x: x.name, tenant.vrflist)
       #     print('\t' + repr(vrflistname))
       #     print('\t' + repr(l3out.vrf))
       #     if l3out.vrf in vrflistname:
       #         print(l3out.vrf, tenant.vrflist)
    import pdb; pdb.set_trace()
   # import pdb; pdb.set_trace()

#def get_all_static_routes():
#    url = """https://{apic}/api/node/class/ipRouteP.json?rsp-subtree=full""".format(apic=apic)
#    results = GetResponseData(url,cookie)
#    staticrlist = []
#    for iproute in results:
#        #print(iproute)
#        print(iproute)
#        path = iproute['ipRouteP']['attributes']['dn'].split('/')
#        tenant = path[1]
#        l3out = path[2]
#        location = re.search(r'rsnodeL3OutAtt-\[.*\]',iproute['ipRouteP']['attributes']['dn']).group()
#        location = location.replace('rsnodeL3OutAtt-', '').replace('[', '').replace(']','')
#        location = '/'.join(location.split('/')[1:-2])
#       # iiproute = re.search(r'rt-\[.*\]',iproute['ipRouteP']['attributes']['dn']).group()#.replace('rt-','')
#        ipRoute = iproute['ipRouteP']['attributes']['ip']
#        #import pdb; pdb.set_trace()
#        staticr = static_route(path=path,tenant=tenant,l3out=l3out,location=location,iproute=ipRoute)
#        if iproute['ipRouteP'].get('children'):
#            for nh in iproute['ipRouteP']['children']:
#               # import pdb; pdb.set_trace()
#                staticr.add_nexthop(nh['ipNexthopP']['attributes']['nhAddr'],nh['ipNexthopP']['attributes']['pref'])
#        staticrlist.append(staticr)
#    for route in staticrlist:
#        print(route.tenant,route.l3out,route.location,route.iproute,route.nexthoplist)
#        #print(tenant, l3out, location, route)
#        #print(iproute['ipRouteP']['attributes']['descr'], iproute['ipRouteP']['attributes']['ip'], iproute['ipRouteP']['attributes']['pref'])

def main(import_apic,import_cookie):
    global apic 
    global cookie 
    apic = import_apic
    cookie = import_cookie
   # get_all_static_routes()
    gather_Tenants()
    raw_input()
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
#def get_all_l3extRsNodeL3OutAtt():
#    url = """https://{apic}/api/node/class/l3extRsNodeL3OutAtt.json""".format(apic=apic)
#    results = GetResponseData(url,cookie)
#    nodelist = []
#    for result in results:
#        node = result['l3extRsNodeL3OutAtt']['attributes']['tDn']
#        #print(node)
#        dn = result['l3extRsNodeL3OutAtt']['attributes']['dn']
#        #print(dn)
#        Node = namedtuple('Node', ['node', 'dn'])
#        nodelist.append(Node(node=node,dn=dn))
#    return nodelist
#
#def main(import_apic,import_cookie):
#    global apic
#    global cookie
#    cookie = import_cookie
#    apic = import_apic
#    clear_screen()
#    nodelist = get_all_l3extRsNodeL3OutAtt()
#    noderoutelist = []
#    for node in nodelist:
#        url = """https://{apic}/api/node/mo/{node}.json?query-target=children&target-subtree-class=ipRouteP""".format(apic=apic,node=node.dn)
#        result = GetResponseData(url,cookie)
#        noderoutelist.append((node.node, result))
#        for iproute in result:
#            print(iproute['ipRouteP']['attributes']['descr'], iproute['ipRouteP']['attributes']['ip'])
#    print(noderoutelist)
#    #import pdb; pdb.set_trace()
#   # for node in nodelist:
#   #     url = """https://{apic}/api/node/class/l3extRsNodeL3OutAtt.json""".format(apic=apic)
#   #     result = GetResponseData(url)
#    #results = get_all_static_routes()
#    #parse_static_route_dn(results)
#    raw_input()