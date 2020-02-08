#!/bin//python

from __future__ import print_function
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

def pull_each_vlan(apic, leaf, vlan, q):
    url = """https://{apic}/api/mo/{vlan}.json?query-target=children&target-subtree-class=l2RsPathDomAtt""".format(apic=apic, vlan=vlan.dn)
    result = GetResponseData(url, cookie)
    q.put((vlan,result))

class interfacetoEpg():
    def __init__(self, interface):
        self.vlan = []
        self.interface = interface

class l2RsPathDomAtt():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return self.dn

def interface_grouping(resultlist, finaldict):
    for epg in resultlist:
        for interface in epg[1]:
            currentinterface = interface['l2RsPathDomAtt']['attributes']['tDn']
            if not finaldict.get(currentinterface):
                finaldict[currentinterface] = [(l2RsPathDomAtt(interface['l2RsPathDomAtt']['attributes']),epg[0])]
            else:
                finaldict[currentinterface].append((l2RsPathDomAtt(interface['l2RsPathDomAtt']['attributes']),epg[0]))

def interface_epg_pull(apic,cookie, epgvlanlist, selectedleaf):
    leaf = selectedleaf
    q = Queue.Queue()
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
    finaldict = {}
    interface_grouping(resultlist, finaldict)
    #for result in resultlist:
    #    print(result[0], result[1])
    #    print('\n\n\n')
    #    for x in result[1]:
    #        if x.get('l2RsPathDomAtt'):
    #            allinterfacesfound.add(l2RsPathDomAtt(x['l2RsPathDomAtt']['attributes']) )
    #            interfaces_per_vlan.append(l2RsPathDomAtt(x['l2RsPathDomAtt']['attributes']) ) ########################
    #    vlanwith_allinterfacesfound.append((result[0], interfaces_per_vlan))
    #    interfaces_per_vlan = []
    #import pdb; pdb.set_trace()
    #interfacewith_allvlans = []
    #addvlans = []
    #allinterfacesfound = list(allinterfacesfound)
    #for z in allinterfacesfound:
    #    for x in vlanwith_allinterfacesfound:
    #        #print(z.tDn,x)
    #       # print('\n\n')
    #        if z in map(str,x[1]):
    #            addvlans.append(x[0])
    #    interfacewith_allvlans.append((z, addvlans))
    #    addvlans = []
    ##import pdb; pdb.set_trace()
    #eth_interfaces = [x for x in interfacewith_allvlans if x[0].tDn.count('/') != 7 and 'eth' in x[0].tDn]
    #fex_interfaces = [x for x in interfacewith_allvlans if x[0].tDn.count('/') == 7 and 'eth' in x[0].tDn]
    #po_interfaces = [x for x in interfacewith_allvlans if not 'eth' in x[0].tDn]
    ##import pdb; pdb.set_trace()
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/pcAggrIf.json""".format(apic=apic,leaf=leaf[0])
    #import pdb; pdb.set_trace()
    result = GetResponseData(url,cookie)
    podict = {}
    for pointerface in result:
        podict[pointerface['pcAggrIf']['attributes']['id']] = pointerface['pcAggrIf']['attributes']['name']
    eth_interfaces = {x:y for x,y in finaldict.items() if x.count('/') != 7 and 'eth' in x}
    fex_interfaces = {x:y for x,y in finaldict.items() if x.count('/') == 7 and 'eth' in x}
    po_interfaces = {x:y for x,y in finaldict.items() if not 'eth' in x}
    #import pdb; pdb.set_trace()

    epglist = []
    interfacecolumn = []
    encaplist =[]
    for k,v in sorted(eth_interfaces.items(), key=lambda x: int(x[0].split('/')[-1][:-1])):
        leftlocation = k.find('[')
        interfacecolumn.append(k[leftlocation+1:-1]) 
       # print('  {:16}|'.format(k[leftlocation+1:-1]), end='')
        for num,m in enumerate(v):
            encaplist.append(m[1].encap)
            epglist.append(m[1])
    for k,v in sorted(fex_interfaces.items(), key=lambda x: int(x[0].split('/')[-1][:-1])):
        leftlocation = k.find('[')
        interfacecolumn.append(k[leftlocation+1:-1])
        #print('  {:16}|'.format(k[leftlocation+1:-1]), end='')
        for num,m in enumerate(v):
            encaplist.append(m[1].encap)
            epglist.append(m[1])
    for k,v in sorted(po_interfaces.items(), key=lambda x: int(x[0].split('[po')[-1][:-1])):
        leftlocation = k.find('[')
        po_name = podict[k[leftlocation+1:-1]]
        interfacecolumn.append(po_name)
       # print('  {:16}|'.format(po_name), end='')
        for num,m in enumerate(v):
            encaplist.append(m[1].encap)
            epglist.append(m[1])

    headers = ('Interface','Vlan/Vxlan','Type','EPG')
    columns = (interfacecolumn,encaplist,epglist)
    columns = filter(None, columns)
    sizes = get_column_sizes(list(columns), minimum=5, baseminimum=headers,alreadysorted=True)
    print('  {:{interfname}} | {:{vlansize}} | {:^8} | {:{epgsize}}'.format('Interface','Vlan/Vxlan','Type','EPG',interfname=sizes[0],vlansize=sizes[1],epgsize=sizes[-1])) 
    print('  {:-<{interfname}}-|-{:-<{vlansize}}-|-{:-^8}-|-{:-<{epgsize}}'.format('','','','',interfname=sizes[0],vlansize=sizes[1],epgsize=sizes[-1]))
    for k,v in sorted(eth_interfaces.items(), key=lambda x: int(x[0].split('/')[-1][:-1])):
        leftlocation = k.find('[')
        print('  {:{interfname}} |'.format(k[leftlocation+1:-1], interfname=sizes[0]), end='')
        for num,m in enumerate(v):
            if num == 0:
                if m[0].type == 'regular':
                    print(' {:{vlansize}} | {:^8} | {}'.format(m[1].encap, 'tagged', m[1],vlansize=sizes[1]))
                if m[0].type == 'native':
                    print(' {:{vlansize}} | {:^8} | {}'.format(m[1].encap, 'UNTAGGED', m[1],vlansize=sizes[1]))
            else:
                if m[0].type == 'regular':
                    print('  {:{interfname}}   {:{vlansize}} | {:^8} | {}'.format('',m[1].encap, 'tagged', m[1],interfname=sizes[0],vlansize=sizes[1]))
                if m[0].type == 'native':
                    print('  {:{interfname}}   {:{vlansize}} | {:^8} | {}'.format('',m[1].encap, 'UNTAGGED', m[1],interfname=sizes[0],vlansize=sizes[1]))

        #print('')

    for k,v in sorted(fex_interfaces.items(), key=lambda x: int(x[0].split('/')[-1][:-1])):
        leftlocation = k.find('[')
        print('  {:{interfname}} |'.format(k[leftlocation+1:-1], interfname=sizes[0]), end='')
        for num,m in enumerate(v):
            if num == 0:
                if m[0].type == 'regular':
                    print(' {:{vlansize}} | {:^8} | {}'.format(m[1].encap, 'tagged', m[1],vlansize=sizes[1]))
                if m[0].type == 'native':
                    print(' {:{vlansize}} | {:^8} | {}'.format(m[1].encap, 'UNTAGGED', m[1],vlansize=sizes[1]))
            else:
                if m[0].type == 'regular':
                    print('  {:{interfname}}   {:{vlansize}} | {:^8} | {}'.format('',m[1].encap, 'tagged', m[1],interfname=sizes[0],vlansize=sizes[1]))
                if m[0].type == 'native':
                    print('  {:{interfname}}   {:{vlansize}} | {:^8} | {}'.format('',m[1].encap, 'UNTAGGED', m[1],interfname=sizes[0],vlansize=sizes[1]))

        #print("")
    for k,v in sorted(po_interfaces.items(), key=lambda x: int(x[0].split('[po')[-1][:-1])):
        leftlocation = k.find('[')
        po_name = podict[k[leftlocation+1:-1]]
        print('  {:{interfname}} |'.format(po_name, interfname=sizes[0]), end='')
        for num,m in enumerate(v):
            if num == 0:
                if m[0].type == 'regular':
                    print(' {:{vlansize}} | {:^8} | {}'.format(m[1].encap, 'tagged', m[1],vlansize=sizes[1]))
                if m[0].type == 'native':
                    print(' {:{vlansize}} | {:^8} | {}'.format(m[1].encap, 'UNTAGGED', m[1],vlansize=sizes[1]))
            else:
                if m[0].type == 'regular':
                    print('  {:{interfname}}   {:{vlansize}} | {:^8} | {}'.format('',m[1].encap, 'tagged', m[1],interfname=sizes[0],vlansize=sizes[1]))
                if m[0].type == 'native':
                    print('  {:{interfname}}   {:{vlansize}} | {:^8} | {}'.format('',m[1].encap, 'UNTAGGED', m[1],interfname=sizes[0],vlansize=sizes[1]))


       # print('')

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:
        clear_screen()
        location_banner('Show EPGs to interface')
        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print('\nSelect leaf(s): ')
        print('\r')
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        for leaf in chosenleafs:

            switchpreviewutil.main(apic,cookie,[leaf], purpose='port_switching')
            vlanlist = pull_vlan_info_for_leaf(apic, cookie, [leaf])
            epgvlanlist = [x.dn for x in vlanlist]
            interface_epg_pull(apic,cookie, vlanlist, [leaf])
            custom_raw_input('Continue...')








