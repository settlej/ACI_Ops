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
    def __str__(self):
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
    def __str__(self):
        return self.name
class l3outobj():
    def __init__(self, name, **kwargs):
        self.__dict__.update(kwargs)
        self.name = name
        self.vrf = None
        self.static_routelist = []
    def __repr__(self):
        return self.name

class l3outandsubnet():
    def __init__(self, dn, **kwargs):
        self.__dict__.update(kwargs)
        self.dn = dn
        self.static_routelist = []
    def __repr__(self):
        return self.dn

def addressInNetwork(ip, net):
   import socket,struct
   ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.') ]), 16)
   netstr, bits = net.split('/')
   netaddr = int(''.join([ '%02x' % int(x) for x in netstr.split('.') ]), 16)
   mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
   return (ipaddr & mask) == (netaddr & mask)

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
                                currentl3outobj.vrf = vrfname#, vrf=vrfname)
                            if l3.get('l3extLNodeP') and l3['l3extLNodeP'].get('children'):
                                    for l3ext in l3['l3extLNodeP']['children']:
                                       # print('hit5')
                                        if l3ext.get('l3extRsNodeL3OutAtt') and l3ext['l3extRsNodeL3OutAtt'].get('children'):
                                            #vrf = location = l3ext['l3extRsNodeL3OutAtt']['attributes']['tDn']
                                            #import pdb; pdb.set_trace()
                                            location = l3ext['l3extRsNodeL3OutAtt']['attributes']['tDn']
                                            location = '/'.join(location.split('/')[1:])
                                            for iproute in l3ext['l3extRsNodeL3OutAtt']['children']:
                                                if iproute.get('ipRouteP') and iproute['ipRouteP'].get('children'):
                                                    #ipRoute = iproute['ipRouteP']['attributes']['ip']
                                                    staticr = static_route(vrf=vrfname, **iproute['ipRouteP']['attributes'])
                                                    #import pdb; pdb.set_trace()
                                                    if iproute['ipRouteP'].get('children'):
                                                        for nh in iproute['ipRouteP']['children']:
                                                            staticr.add_nexthop(nhAddr=nh['ipNexthopP']['attributes']['nhAddr'],pref=nh['ipNexthopP']['attributes']['pref'])
                                                        currentl3outobj.static_routelist.append((location, staticr))
                        tenantObj.l3outlist.append(currentl3outobj)
                            #import pdb; pdb.set_trace()
                        del currentl3outobj
                #if l3outlist:
                #   pass
                   # for ten in tenantlist
        #import pdb; pdb.set_trace()

        tenantlist.append(tenantObj)
    return tenantlist

def display_static_routes(tenantlist):
    longesttenantname = len(max(tenantlist, key=lambda x: len(x.name)).name)
    longestl3outname = 0
    longestvrfname = 0 
    for tenant in tenantlist:
        if len(tenant.vrflist) != 0:
            currentvrflength = len(max(tenant.vrflist, key=lambda x: len(x.name)).name)
        else:
            currentvrflength = 0
        if currentvrflength > longestvrfname:
            longestvrfname = len(max(tenant.vrflist, key=lambda x: len(x.name)).name)
       
        if len(tenant.l3outlist) != 0:
            #import pdb; pdb.set_trace()
            currentl3outlength = len(max(tenant.l3outlist, key=lambda x: len(x.name)).name)
        else:
            currentl3outlength = 0
        if currentl3outlength > longestl3outname:
            longestl3outname = len(max(tenant.l3outlist, key=lambda x: len(x.name)).name)
            #import pdb; pdb.set_trace()
    #import pdb; pdb.set_trace()
    tenantwidth = longesttenantname
    vrfwidth = longestvrfname
    l3width = longestl3outname
    #import pdb; pdb.set_trace()
    columnstring = ''
    columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | {:39} {:4}   | {:18}   {:11} | {}\n'.format('Tenant','VRF','L3out','Static Routes ','Pref','Next Hop', 'NH Pref','Description', tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
    columnstring += ('{:=>{width}}\n'.format('=',width=tenantwidth + vrfwidth + l3width + 104))
    for tenant in tenantlist:
        if tenant != tenantlist[0]:
           #columnstring += '\n'
            columnstring += ('{:->{width}}\n'.format('-',width=tenantwidth + vrfwidth + l3width + 104))
        columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | \n'.format(tenant,'','', l3width=l3width,tenantwidth=tenantwidth,vrfwidth=vrfwidth))
        #columnstring += ('{:{tenantwidth}}'.format(tenant,tenantwidth=tenantwidth))
        for vrf in tenant.vrflist:
            columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} |\n'.format('',vrf.name[4:],'',tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
            for l3out in tenant.l3outlist:
                vrf.l3outlist = []
                #import pdb; pdb.set_trace()
               # columnstring += (vrf.name, l3out, l3out.static_routelist)
                if vrf.name in l3out.vrf:
                    vrf.l3outlist.append(l3out)
                    if len(l3out.static_routelist) >= 1:
                        columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | Static Routes: {numroutes}\n'.format('','',vrf.l3outlist[-1], numroutes=len(l3out.static_routelist),l3width=l3width,tenantwidth=tenantwidth,vrfwidth=vrfwidth))
                        #', '.join(map(str, l3out.static_routelist[0]))))
                        for num,route in enumerate(l3out.static_routelist,1):
                            #import pdb; pdb.set_trace()
                            if route[1].nexthoplist:
                                columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | {}.) {:35}   {:4}   {:18}   {:11}   {}\n'.format('','','',num,', '.join(map(str, route)),route[1].pref,route[1].nexthoplist[0][0],route[1].nexthoplist[0][1],route[1].descr,tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
                            if len(route[1].nexthoplist) > 1:
                                for num2,routes in enumerate(route[1].nexthoplist[1:],1):
                                    columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | {}   {:36}   {:4}   {:18}   {:11}   {}\n'.format('','','','','','',route[1].nexthoplist[num2][0],route[1].nexthoplist[num2][1],'',tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
                                   #columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | {:29}   {}\n'.format('','','','',route[1].nexthoplist,tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width)) 
                    #elif len(l3out.static_routelist) == 1:
                    #    columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | Static Routes: 1\n'.format('','', vrf.l3outlist[-1],tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
                    #    for num,route in enumerate(l3out.static_routelist,1):
                    #        columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | {}.) {} pref:{} nh:{}  \n'.format('','','',num,', '.join(map(str, route)) , route[1].pref,route[1].nexthoplist,tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
                    else:
                        columnstring += ('{:{tenantwidth}} | {:{vrfwidth}} | {:{l3width}} | Static Routes: 0\n'.format('','', vrf.l3outlist[-1],tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
    columnstring += ('{:->{width}}\n'.format('-',width=tenantwidth + vrfwidth + l3width + 104))
    print(columnstring)

               # else: 
               #     print('{:{tenantwidth}}   {:{vrfwidth}}   {:{l3width}}   '.format('','', '',tenantwidth=tenantwidth,vrfwidth=vrfwidth,l3width=l3width))
                   # print('\t\tl3Out: {} '.format('None'))
                #import pdb; pdb.set_trace()
               # print('\t\t{}{}'.format(l3out.name, vrf.l3outlist))
            #print(tenant.vrflist)
           # print('\t\t'.format())
           # l3outlistvrf = map(lambda x: x.vrf, tenant.l3outlist)
        #import pdb; pdb.set_trace() 
          #  print(l3outlistvrf, repr(vrf))
          #  if repr(vrf) in l3outlistvrf:
          #      print('\tfound')
       # for l3out in tenant.l3outlist:
       #     import pdb; pdb.set_trace()
       #     vrflistname = map(lambda x: x.name, tenant.vrflist)
       #     print('\t' + repr(vrflistname))
       #     print('\t' + repr(l3out.vrf))
       #     if l3out.vrf in vrflistname:
       #         print(l3out.vrf, tenant.vrflist)
    #import pdb; pdb.set_trace()
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
def gather_l3out():
    url = """https://{apic}/api/node/class/l3extOut.json?&order-by=l3extOut.modTs|desc""".format(apic=apic)
    results = GetResponseData(url, cookie)
    l3outlist = [l3out['l3extOut']['attributes']['dn']for l3out in results]
    return l3outlist
def gather_l3out_nodes(returnoption='menu'):
    url = """https://{apic}/api/node/class/l3extRsNodeL3OutAtt.json?&order-by=l3extRsNodeL3OutAtt.modTs|desc&rsp-subtree=full""".format(apic=apic)
    results = GetResponseData(url, cookie)
    l3outnodeslist = []
    for l3out in results:
        l3outobj = l3outandsubnet(**l3out['l3extRsNodeL3OutAtt']['attributes'])
        if l3out['l3extRsNodeL3OutAtt'].get('children'):
            for iproute in l3out['l3extRsNodeL3OutAtt']['children']:
                if iproute.get('ipRouteP'):
                    staticr = static_route(**iproute['ipRouteP']['attributes'])
                    if iproute['ipRouteP'].get('children'):
                        for nh in iproute['ipRouteP']['children']:
                            staticr.add_nexthop(nhAddr=nh['ipNexthopP']['attributes']['nhAddr'],pref=nh['ipNexthopP']['attributes']['pref'])
                    l3outobj.static_routelist.append(staticr)
        if returnoption == 'menu':
            l3outnodeslist.append((l3out['l3extRsNodeL3OutAtt']['attributes']['tDn'],l3out['l3extRsNodeL3OutAtt']['attributes']['dn']))
        else:
            l3outnodeslist.append(l3outobj)
    return l3outnodeslist
#    l3outnodeslist = [(l3out['l3extRsNodeL3OutAtt']['attributes']['tDn'],l3out['l3extRsNodeL3OutAtt']['attributes']['dn']) for l3out in results]

def main(import_apic,import_cookie):
    global apic 
    global cookie 
    apic = import_apic
    cookie = import_cookie
    while True:
        clear_screen()
        location_banner('Show Static Routes')
       # get_all_static_routes()
        tenantlist = gather_Tenants()
        display_static_routes(tenantlist)
        print('\r')
        print('Static Route Menu: ')
        print('\n\t1.) Add Static route\n' + 
                '\t2.) Remove Static route\n' +
                '\t3.) Search IP in static routes\n')
        while True:
            ask = custom_raw_input('Select number:')
            if ask != '' and ask.isdigit() and int(ask) > 0 and int(ask) <= 3:
                break
            else:
                continue
        if ask == '1':
            l3outlist = gather_l3out()
            print('\nWhich L3Out will use static route?: \n')
            for num,l3out in enumerate(l3outlist,1):
                print("\t{}.) {}".format(num,l3out))
            print('\r')
            while True:
                ask = custom_raw_input('Select number: ')
                if ask != '' and ask.isdigit() and int(ask) > 0 and int(ask) <= len(l3outlist):
                    break
                else:
                    continue
            l3outdesired = l3outlist[int(ask)- 1]
            l3outnodeslist = gather_l3out_nodes(returnoption='menu')
            #import pdb; pdb.set_trace()
            l3outnodeslist = filter(lambda x: l3outdesired in x[1], l3outnodeslist)
            print('\nWhere would you like static route installed?: \n')
            for num,node in enumerate(sorted(l3outnodeslist),1):
                print("\t{}.) {}".format(num, node[0]))
            print('\r')
            while True:
                ask = custom_raw_input('Select number: ')
                if ask != '' and ask.isdigit() and int(ask) > 0 and int(ask) <= len(l3outnodeslist):
                    break
                else:
                    continue
            l3outlocation = l3outnodeslist[int(ask)-1]
            while True:
                ask = 's'
                #ask = custom_raw_input('\nStandard or Advanced static route: [a|s=default] :') or 's'
                if ask != '' and ask.isalpha and (ask == 'a' or ask == 's'):
                    break
                else:
                    continue
            if ask == 's':
                while True:
                    staticroute_ask = custom_raw_input('\nStatic route [format: x.x.x.x/x or x.x.x.x/xx]: ')
                    checktest = staticroute_ask.split('/')
                    if not re.search(r'(?:^|\b(?<!\.))(?:1?\d?\d|2[0-4]\d|25[0-5])(?:\.(?:1?\d?\d|2[0-4]\d|25[0-5])){3}(?=$|[^\w.])',checktest[0]):
                        print('\nx1b[1;31;40mInvalid format, Try again...\x1b[0m\n')
                        continue
                    if not '/' in staticroute_ask:
                        print('\nx1b[1;31;40mInvalid format, Try again...\x1b[0m\n')
                        continue
                    checktestsubnet = checktest[1]
                    if checktestsubnet.isdigit() and int(checktestsubnet) >= 8 and int(checktestsubnet) <= 32:
                        break
                    else:
                        print('\nx1b[1;31;40mInvalid format, Try again...\x1b[0m\n')
                        continue
                while True:
                    nexthopip = custom_raw_input('NextHop IP [format: x.x.x.x]: ')
                    if not re.search(r'(?:^|\b(?<!\.))(?:1?\d?\d|2[0-4]\d|25[0-5])(?:\.(?:1?\d?\d|2[0-4]\d|25[0-5])){3}(?=$|[^\w.])',nexthopip):
                        print('\nx1b[1;31;40mInvalid format, Try again...\x1b[0m\n')
                        continue
                    else:
                        break
                description = custom_raw_input('Static Description: ')
                while True:
                    askcontinue = custom_raw_input('\nAdd static route ' + staticroute_ask + ', Confirm?: [n]:' ) or 'n'
                    if askcontinue != '' and askcontinue[0].lower() == 'n':
                        print('\n\x1b[1;33;40mCancelled!\x1b[0m')
                        break
                    elif ask != '' and askcontinue[0].lower() == 'y':
                        nhstaticsubnet = nexthopip
                        staticipsubnet = staticroute_ask
                        url = """https://{apic}/api/node/mo/{l3OutAttpath}/rt-[{staticipsubnet}].json""".format(apic=apic,l3OutAttpath=l3outlocation[1],staticipsubnet=staticipsubnet)
                        data = ("""{{"ipRouteP":{{"attributes":{{"descr":"{description}","ip":"{staticipsubnet}","status":"created"}},"children":[""" +
                            """{{"ipNexthopP":{{"attributes":{{"nhAddr":"{nhstaticsubnet}","status":"created"}},"children":[""" +
                                """]}}}}]}}}}""").format(staticipsubnet=staticipsubnet,description=description,nhstaticsubnet=nhstaticsubnet)
                        result, error = PostandGetResponseData(url,data,cookie)
                        if error == None:
                            print('\n\x1b[1;32;40mSuccessfully added static route!\x1b[0m\n')
                            break
                        else:
                            print('\n\x1b[1;31;40mInvalid option, please try again...\x1b[0m')
                            continue  
                    else:
                        print('\n\x1b[1;31;40mInvalid option, please try again...\x1b[0m')
                        continue     
                raw_input('\nPress Enter to continue...')
 
        if ask == '2':
            l3outnodelist = gather_l3out_nodes(returnoption='obj')
            menulist = []
            longestl3outname = len(max(l3outnodelist, key=lambda x: len(x.dn.split('/')[2])).dn.split('/')[2])
            for l3out in l3outnodelist:
                #import pdb; pdb.set_trace()
                l3outname = l3out.dn.split('/')[2]
                l3outpath = l3out.dn
                l3location = l3out.dn[l3out.dn.rfind('[')+1:][:-1]
                if l3out.static_routelist:
                    #import pdb; pdb.set_trace()
                    for static_route in l3out.static_routelist:
                        l3statictuple = namedtuple('l3statictuple', 'l3outname location route dn')
                        l3outroute = l3statictuple(l3outname=l3outname[4:], location=l3location.replace('topology/',''), route=static_route, dn=l3outpath)
                        menulist.append(l3outroute)
            print('\r')
            print('\t# | {:{namewidth}} | {:15} | Static Route'.format('L3Out','Location',namewidth=longestl3outname))
            print('\t' + '-' * int(longestl3outname + 38))
            for num,item in enumerate(menulist,1):
                print("\t{}.) {:{namewidth}}  [{}]   {}".format(num,item.l3outname,item.location,item.route,namewidth=longestl3outname))   
            while True:
                ask = custom_raw_input('\nSelect number: ').strip().lstrip()
                if ask != '' and ask.isdigit() and int(ask) > 0 and int(ask) <= len(menulist):
                    break
                else:
                    continue
            while True:
                askcontinue = custom_raw_input('\nRemove ' + str(menulist[int(ask)-1].route) + '. Confirm?: [n]: ' ) or 'n'
                if askcontinue != '' and askcontinue[0].lower() == 'n':
                    break
                elif ask != '' and askcontinue[0].lower() == 'y':
                    url = """https://{apic}/api/node/mo/{rsnodel3outatt}/rt-[{staticipsubnet}].json""".format(apic=apic,rsnodel3outatt=menulist[int(ask)-1].dn,staticipsubnet=menulist[int(ask)-1].route)
                    data = """{"ipRouteP":{"attributes":{"status":"deleted"},"children":[]}}"""
                    result, error = PostandGetResponseData(url,data,cookie)
                    if error == None:
                        print('\n\x1b[1;32;40mSuccessfully removed static route\x1b[0m\n')
                    break
                else:
                    print('\n\x1b[1;31;40mInvalid option, please try again...\x1b[0m')
                    continue
            raw_input('\n Press Enter to continue...')
        if ask == '3':
            l3outnodelist = gather_l3out_nodes(returnoption='obj')
            while True:
                searchip = custom_raw_input('\nProvide ip or subnet to search if existing static route: ')
                #import pdb; pdb.set_trace()
                foundlist = []
                if '/' in searchip:
                    try:
                        searchsubnet = ipaddress.ip_network(unicode(searchip),strict=False)
                        #print(searchsubnet)
                    except ValueError:
                        print('\n\x1b[1;31;40mInvalid IP Address, try again...\x1b[0m')
                        continue
                    foundlist = []
                    for l3out in l3outnodelist:
                        #print(l3out.static_routelist)
                        for route in l3out.static_routelist:
#                        converedroutelist = map(unicode, l3out.static_routelist)
                            if searchsubnet.subnet_of(ipaddress.IPv4Network(route.ip,strict=False)):
                                foundlist.append((l3out,route))
                    if len(foundlist) > 1:
                        print('\nFound {} static subnets\n'.format(len(foundlist)))
                    for l3,route in sorted(foundlist, key=lambda x: (x[0].dn,x[0].tDn)):
                        print('\t{}  {}  {}'.format(('/'.join(l3.dn.split('/')[1:3])).replace('tn-','').replace('out-',''), l3.tDn, route.ip))
                        #foundlist.extend(filter(lambda x: searchsubnet.subnet_of(ipaddress.IPv4Network(x,strict=False)),converedroutelist))
                    #custom_raw_input('\nPress enter to continue...')
                    #import pdb; pdb.set_trace()
                else:
                    try:
                        searchip = ipaddress.IPv4Address(unicode(searchip))
                        #import pdb; pdb.set_trace()
                    except ValueError:
                        print('\n\x1b[1;31;40mInvalid IP subnet, try again...\x1b[0m')
                        continue
                    foundlist = []
                    for l3out in l3outnodelist:
                        #print(l3out.static_routelist)
                        for route in l3out.static_routelist:
#                        converedroutelist = map(unicode, l3out.static_routelist)
                            currentroute = ipaddress.IPv4Network(route.ip,strict=False)
                            if searchip in currentroute:
                                #if searchsubnet.subnet_of(ipaddress.IPv4Network(route.ip,strict=False)):
                                foundlist.append((l3out,route))
                    if len(foundlist) > 1:
                        print('\nFound {} static subnets\n'.format(len(foundlist)))
                    elif len(foundlist) == 1:
                        print('\r')
                        tenantvrflist = map(lambda x: '/'.join(x[0].dn.split('/')[1:3]).replace('tn-','').replace('out-',''), foundlist)
                        tenantvrfwidth = len(max(tenantvrflist))
                       # tenantvrf, l3outname = map(lambda, foundlist[0][0].dn.split('/')[1:3])
                       # tenantvrf = tenantvrf[3:]
                       # l3outname = l3outname[4:]
                       #import pdb; pdb.set_trace()
                    for l3,route in sorted(foundlist, key=lambda x: (x[0].dn,x[0].tDn)):
                        import pdb; pdb.set_trace()
                        print('\t{}/{} {}  {}'.format(l3out[0], l3out[1], l3outname, l3.tDn, route.ip))

#                    for l3,route in foundlist:
#                        print('/'.join(l3.dn.split('/')[1:3]), l3.tDn, route.ip)
                if not foundlist:
                    print('\n\x1b[1;31;40mNo subnets found!\x1b[0m')
                del foundlist
                custom_raw_input('\nPress enter to continue...')
                break
                    #for route in l3out.static_routelist:
                    #    currentroute = ipaddress.IPv4Address(unicode(route.ip))
                    #    searchsubnet.subnet_of(currentroute)
                    #    if addressInNetwork(searchip, route.ip):
                    #        print(route.ip)
                    

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