#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import trace
import logging
import os
import time
import itertools
import threading
import Queue
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


class interfaceProperties():
    def __init__(self, name, etype, epgs):
        self.name = name
        self.etype = etype
        self.epgs = epgs
    def __repr__(self):
        return self.name

class epgobj():
    def __init__(self, epg):
        self.epg = epg
        self.encapvlans = []
        self.internalvlans = []
    def __repr__(self):
        return self.epg

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    clear_screen()
    location_banner('Show EPGs to interface')
    while True:

        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print('\nSelect leaf(s): ')
        print('\r')
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
        #chosendestinterfaceobject = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
        leaf = chosenleafs
        vlanlist = pull_vlan_info_for_leaf(apic, cookie, leaf)
        epgvlanlist = [x.dn for x in vlanlist]
        interface_epg_pull(apic, leaf, vlanlist, leaf)
     #   interfacelist = [x['l1PhysIf']['attributes']['id'] for x in result]
     #   interfacelist = interface_vlan_to_epg(apic, cookie, leaf, interfacelist)
     #   #mport pdb; pdb.set_trace()
     #   for interface in interfacelist:
     #       for vlan in vlanlist:
     #           #import pdb; pdb.set_trace()
     #           if interface.epgs != []:
     #               for epg in interface.epgs:
     #                   if epg.epg == vlan.epgDn:
     #                       #import pdb; pdb.set_trace()
     #                       epg.encapvlans.append(vlan.encap)
     #                       epg.internalvlans.append(vlan.fabEncap)
     #   import pdb; pdb.set_trace()
             #  x,y = interfacelist
             #  if y != None:
             #  #import pdb; pdb.set_trace()
             #      if y == vlan.epgDn:
             #          pass
                    #for z in y:
                    #   if z == vlan.epgDn:
                    #        print('yes')

     #   for interface in sorted(interfacedictwithegps, key=lambda x: (x.split('/')[0],int(x.split('/')[-1]))):
     #       print(interface)
     #       #import pdb; pdb.set_trace()
     #      # if interfacedictwithegps[interface][1]
     #       x,y = interfacedictwithegps[interface]
     #       if y == None:
     #           print('\t{} {}'.format(x,y))
     #       else:
     #           #print('\t{}'.format(x))
     #           for yy in sorted(y):
     #               pass
     #               #print('\t\t{} | {} | {}'.format(yy[0],yy[1],yy[2]))
    


class vlanCktEp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        if self.name != '':
            return self.name
        else:
            return self.epgDn

def pull_vlan_info_for_leaf(apic, cookie, leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/vlanCktEp.json""".format(apic=apic, leaf=leaf[0])
    result = GetResponseData(url, cookie)
    vlanlist = [vlanCktEp(**x['vlanCktEp']['attributes']) for x in result]
    return vlanlist

#def pull_each_interface(leaf, interface, apic, q):
#    #url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json""".format(leaf=leaf,apic=apic)
#    epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf),apic=apic)
##url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
#    #import pdb; pdb.set_trace()
#    logger.info(epgurl)
#    #print(interface)
#    epgresult = GetResponseData(epgurl, cookie)
#    #print(epgresult)
#    logger.debug(epgresult)
#    #result = GetResponseData(url, cookie)
#    logger.info('complete')
#    q.put(epgresult)

#def displayepgs(result):
#
#    if result[0]['l1PhysIf']['attributes']['layer'] == 'Layer3':
#        #print(' L3 Interface\n')
#        return 'L3', None
#    if result[0]['l1PhysIf'].get('children'):
#        for int in result[0]['l1PhysIf']['children']:
#            interfaceepglist = []
#            for epgs in int['pconsCtrlrDeployCtx']['children']:
#                if 'LDevInst' in epgs['pconsResourceCtx']['attributes']['ctxDn']:
#                    return 'redirect', None
#                    #print(epgs['pconsResourceCtx']['attributes']['ctxDn'])
#                else:
#                    epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn']#.split('/')
#                #print(epgpath)
#                   # tenant = epgpath[1][3:]
#                   # app = epgpath[2][3:]
#                   # epg = epgpath[3][4:]
#                interfaceepglist.append(epgpath)
#            #import pdb; pdb.set_trace()
#            #return 'L2', (interfaceepglist)
#            return 'L2', interfaceepglist
#                    #print('\t{:10}{:15}{}'.format(tenant,app,epg))
#    else:
#        return 'L2', None

def pull_each_vlan(apic, leaf, vlan, q):
    url = """https://{apic}/api/mo/{vlan}.json?query-target=children&target-subtree-class=l2RsPathDomAtt""".format(apic=apic, vlan=vlan.dn)
    result = GetResponseData(url, cookie)
    q.put((vlan,result))

class interfacetoEpg():
    def __init__(self, interface):
        self.vlan = []
        self.interface = interface

def interface_epg_pull(apic,cookie, epgvlanlist, selectedleaf):
    leaf = selectedleaf
    #str(chosendestinterfaceobject[0]).replace('paths','nodes')
    #clear_screen()
    q = Queue.Queue()
    #leafs = leaf_selection(get_All_leafs(apic, cookie))
    threadlist = []
    leafinterfacelist = []
    interfacedictwithegps = {}
    for epgvlan in epgvlanlist:
        t = threading.Thread(target=pull_each_vlan, args=[apic, leaf[0], epgvlan, q])
        t.start()
        threadlist.append(t)
    resultlist = []
    for thread in threadlist:
        thread.join()
        resultlist.append(q.get())
    allinterfacesfound = set()
    interfaces_per_vlan = []
    vlanwith_allinterfacesfound = []
    for result in resultlist:
        for x in result[1]:
            if x.get('l2RsPathDomAtt'):
                allinterfacesfound.add(x['l2RsPathDomAtt']['attributes']['tDn'])
                interfaces_per_vlan.append(x['l2RsPathDomAtt']['attributes']['tDn'])
        vlanwith_allinterfacesfound.append((result[0], interfaces_per_vlan))
        interfaces_per_vlan = []
    interfacewith_allvlans = []
    addvlans = []
    for z in allinterfacesfound:
        for x in vlanwith_allinterfacesfound:
            #print(z,x)
           # print('\n\n')
            if z in x[1]:
                addvlans.append(x[0])
        interfacewith_allvlans.append((z, addvlans))
        addvlans = []
    for k in sorted(interfacewith_allvlans, key=lambda x: x[0]):
        print(k[0])
        for m in k[1]:
            print(m, m.fabEncap, m.pcTag, m.encap)
        print('\n\n')
    #allinterfacesfound = list(allinterfacesfound)
    import pdb; pdb.set_trace()
   # for x in allinterfacesfound:
   #     print(x, resultlist)
       # for v in resultlist:
       #     #print(x, v[1])
       #     if x in v[1].dn:
       #         print(x, v[0])
    #print(result[0].epgDn)
       # for x in result[1]:
       #     if x.get('l2RsPathDomAtt'):
       #         print(x['l2RsPathDomAtt']['attributes']['tDn'])
        #print('\n')
        #print(result[0]['l1PhysIf']['attributes']['id'])
     #   types, epgs = displayepgs(result)
     #   #print(epgs)
     #   if epgs == None:
     #       ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=[])
     #   else:
     #       epgslist = [epgobj(x) for x in epgs]
     #       ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=epgslist)
     #   leafinterfacelist.append(ee)
     #   #print(ee.__dict__)
     #   #interfacedictwithegps[result[0]['l1PhysIf']['attributes']['id']] = (types, epgs)

    #return leafinterfacelist

#def interface_epg_pull(import_apic,import_cookie, selectedleaf, interfacelist):
#    authcounter = 0
#    leaf = selectedleaf
#    #str(chosendestinterfaceobject[0]).replace('paths','nodes')
#    #clear_screen()
#    q = Queue.Queue()
#    #leafs = leaf_selection(get_All_leafs(apic, cookie))
#    threadlist = []
#    leafinterfacelist = []
#    interfacedictwithegps = {}
#    for interface in interfacelist:
#        t = threading.Thread(target=pull_each_interface, args=[leaf[0], interface, apic, q])
#        t.start()
#        threadlist.append(t)
#    resultlist = []
#    for thread in threadlist:
#        thread.join()
#        resultlist.append(q.get())
#    for result in resultlist:
#        #print('\n')
#        #print(result[0]['l1PhysIf']['attributes']['id'])
#        types, epgs = displayepgs(result)
#        #print(epgs)
#        if epgs == None:
#            ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=[])
#        else:
#            epgslist = [epgobj(x) for x in epgs]
#            ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=epgslist)
#        leafinterfacelist.append(ee)
#        #print(ee.__dict__)
#        #interfacedictwithegps[result[0]['l1PhysIf']['attributes']['id']] = (types, epgs)
#
#    return leafinterfacelist








