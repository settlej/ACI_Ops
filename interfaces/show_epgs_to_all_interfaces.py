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
logger = logging.getLogger('aciops.' + __name__)

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
        url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json""".format(leaf=leaf[0],apic=apic)
        logger.info(url)
        result = GetResponseData(url, cookie)
        interfacelist = [x['l1PhysIf']['attributes']['id'] for x in result]
        #import pdb; pdb.set_trace()
        interfacelist = interface_epg_pull(apic, cookie, leaf, interfacelist)
        #import pdb; pdb.set_trace()
        vlanlist = pull_vlan_info_for_leaf(apic, cookie, leaf)
        #mport pdb; pdb.set_trace()
        for interface in interfacelist:
            for vlan in vlanlist:
                #import pdb; pdb.set_trace()
                if interface.epgs != []:
                    for epg in interface.epgs:
                        if epg.name == vlan.epgDn:
                            import pdb; pdb.set_trace()
                            epg.encapvlans.append(vlan.encap)
                            epg.internalvlans.append(vlan.fabEncap)
        import pdb; pdb.set_trace()
             #  x,y = interfacelist
             #  if y != None:
             #  #import pdb; pdb.set_trace()
             #      if y == vlan.epgDn:
             #          pass
                    #for z in y:
                    #   if z == vlan.epgDn:
                    #        print('yes')

        for interface in sorted(interfacedictwithegps, key=lambda x: (x.split('/')[0],int(x.split('/')[-1]))):
            print(interface)
            #import pdb; pdb.set_trace()
           # if interfacedictwithegps[interface][1]
            x,y = interfacedictwithegps[interface]
            if y == None:
                print('\t{} {}'.format(x,y))
            else:
                #print('\t{}'.format(x))
                for yy in sorted(y):
                    pass
                    #print('\t\t{} | {} | {}'.format(yy[0],yy[1],yy[2]))
    


class vlanCktEp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def pull_vlan_info_for_leaf(apic, cookie, leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/vlanCktEp.json""".format(apic=apic, leaf=leaf[0])
    result = GetResponseData(url, cookie)
    vlanlist = [vlanCktEp(**x['vlanCktEp']['attributes']) for x in result]
    return vlanlist

def pull_each_interface(leaf, interface, apic, q):
    #url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json""".format(leaf=leaf,apic=apic)
    epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf),apic=apic)
#url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
    #import pdb; pdb.set_trace()
    logger.info(epgurl)
    #print(interface)
    epgresult = GetResponseData(epgurl, cookie)
    #print(epgresult)
    logger.debug(epgresult)
    #result = GetResponseData(url, cookie)
    logger.info('complete')
    q.put(epgresult)

def displayepgs(result):

    if result[0]['l1PhysIf']['attributes']['layer'] == 'Layer3':
        #print(' L3 Interface\n')
        return 'L3', None
    if result[0]['l1PhysIf'].get('children'):
        for int in result[0]['l1PhysIf']['children']:
            interfaceepglist = []
            for epgs in int['pconsCtrlrDeployCtx']['children']:
                if 'LDevInst' in epgs['pconsResourceCtx']['attributes']['ctxDn']:
                    return 'redirect', None
                    #print(epgs['pconsResourceCtx']['attributes']['ctxDn'])
                else:
                    epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn']#.split('/')
                #print(epgpath)
                   # tenant = epgpath[1][3:]
                   # app = epgpath[2][3:]
                   # epg = epgpath[3][4:]
                interfaceepglist.append(epgpath)
            #import pdb; pdb.set_trace()
            #return 'L2', (interfaceepglist)
            return 'L2', interfaceepglist
                    #print('\t{:10}{:15}{}'.format(tenant,app,epg))
    else:
        return 'L2', None

def interface_epg_pull(import_apic,import_cookie, selectedleaf, interfacelist):
    authcounter = 0
    leaf = selectedleaf
    #str(chosendestinterfaceobject[0]).replace('paths','nodes')
    #clear_screen()
    q = Queue.Queue()
    #leafs = leaf_selection(get_All_leafs(apic, cookie))
    threadlist = []
    leafinterfacelist = []
    interfacedictwithegps = {}
    for interface in interfacelist:
        t = threading.Thread(target=pull_each_interface, args=[leaf[0], interface, apic, q])
        t.start()
        threadlist.append(t)
    resultlist = []
    for thread in threadlist:
        thread.join()
        resultlist.append(q.get())
    for result in resultlist:
        #print('\n')
        #print(result[0]['l1PhysIf']['attributes']['id'])
        types, epgs = displayepgs(result)
        #print(epgs)
        if epgs == None:
            ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=[])
        else:
            epgslist = [epgobj(x) for x in epgs]
            ee = interfaceProperties(name=result[0]['l1PhysIf']['attributes']['id'], etype=types, epgs=epgslist)
        leafinterfacelist.append(ee)
        #print(ee.__dict__)
        #interfacedictwithegps[result[0]['l1PhysIf']['attributes']['id']] = (types, epgs)

    return leafinterfacelist

                    #print('\t{}'.format(y[0], y))
    
       # print('\t{}'.format(interfacedictwithegps[interface]))




