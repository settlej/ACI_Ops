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


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    clear_screen()
    location_banner('Show interface counters and EPGs')
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
        interface_epg_pull(apic, cookie, leaf, interfacelist)


def pull_each_interface(leaf, interface, apic, q):
    #url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json""".format(leaf=leaf,apic=apic)
    epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf),apic=apic)
#url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
    #import pdb; pdb.set_trace()
    logger.info(epgurl)
    #print(interface)
    epgresult = GetResponseData(epgurl, cookie)
    #print(epgresult)
    logger.info(epgresult)
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
                    epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn'].split('/')
                #print(epgpath)
                    tenant = epgpath[1][3:]
                    app = epgpath[2][3:]
                    epg = epgpath[3][4:]
                    interfaceepglist.append((tenant,app,epg))
            return 'L2', (interfaceepglist)
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
    leafdictwithresults = []
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
        type, epgs = displayepgs(result)
        interfacedictwithegps[result[0]['l1PhysIf']['attributes']['id']] = (type, epgs)
    for interface in sorted(interfacedictwithegps, key=lambda x: int(x.split('/')[1])):
        print(interface)
        print('\t{}'.format(interfacedictwithegps[interface]))




