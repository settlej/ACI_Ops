#!/bin//python

#import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import os
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)

def retrieve_leaf_list():
    # Display available leafs beginning of script
    url = """https://localhost/api/node/mo/topology/pod-1.json?query-target=children&target-subtree-class=fabricNode&query-target-filter=and(wcard(fabricNode.id,"^1[0-9][0-9]"))"""
    logger.info(url)
    result = GetResponseData(url,cookie)
    #print(result)
    leafs = [leaf['fabricNode']['attributes']['id'] for leaf in result]
    #print('Available leafs to bounce ports...')
    return leafs

def displayepgs(result):
    print('\n{:10}{:15}{}'.format('Tenant','APP','EPG'))
    print('-'*40)
    #print(result)
    if result[0]['l1PhysIf']['attributes']['layer'] == 'Layer3':
        print('Layer 3 interface, no EPGs\n')
        return
    if result[0]['l1PhysIf'].get('children'):
        for int in result[0]['l1PhysIf']['children']:
            for epgs in int['pconsCtrlrDeployCtx']['children']:
                epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn'].split('/')
                #print(epgpath)
                tenant = epgpath[1][3:]
                app = epgpath[2][3:]
                epg = epgpath[3][4:]
                print('{:10}{:15}{}'.format(tenant,app,epg))
        print('\n')
    else:
        print('No Epgs found...\n')

def gatherandstoreinterfacesforleaf(leaf):
    url = """https://localhost/api/node/class/topology/pod-1/node-101/l1PhysIf.json"""
    logger.info(url)
    result = GetResponseData(url,cookie)
    listofinterfaces = [interface['l1PhysIf']['attributes']['id'] for interface in result]
    return listofinterfaces

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    fex = False
    clear_screen()
    print("\n1.) Physical interface\n" + 
            "2.) Port-channel/vPC\n")
    int_type = raw_input("What is the interface type?: ")
    if int_type == '1':
        listleafs = retrieve_leaf_list()
        print('\nAvailable Leafs\n' + '-'*12)
        for leaf in sorted(listleafs):
            print(leaf)#Leaf' + ' Leaf'.join(leafs))
        print('\r')
        while True:
            leaf = raw_input("What is leaf number?: ")
            if leaf in listleafs:
                break
            else:
                print('\x1b[41;1mInvalid or leaf does not exist...try again\x1b[0m\n')
        availableinterfaces = gatherandstoreinterfacesforleaf(leaf)
        while True:
            if fex == True:
                interface = raw_input("What is the interface? (format: ethxxx/x/x): ")
            else:
                interface = raw_input("What is the interface? (format: ethx/x): ")
            if interface in availableinterfaces:
                break
            else:
                print('\x1b[41;1mInvalid or interface does not exist...try again\x1b[0m\n')
        
        url = """https://localhost/api/node/mo/topology/pod-1/node-{leaf}/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(leaf=leaf,interface=interface)
        logger.info(url)
        result = GetResponseData(url,cookie)
        displayepgs(result)
    elif int_type == 2:
        pass
    else:
        pass




