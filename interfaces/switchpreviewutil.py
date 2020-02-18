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
import itertools
import threading
import Queue
from collections import namedtuple
from localutils.custom_utils import *
import logging




def gather_l1PhysIf_info(result):
    listofinterfaces = []
    for interface in result:
        physinterface = l1PhysIf(**interface['l1PhysIf']['attributes'])
        listofinterfaces.append(physinterface)
    return listofinterfaces


def leaf_selection(all_leaflist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    #print(nodelist)
    nodelist.sort()
    print('\nAvailable leafs to choose from:\n')
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
       # try:
            asknode = custom_raw_input('\nWhat leaf(s): ')
            print('\r')
            returnedlist = parseandreturnsingelist(asknode, nodelist)
            if returnedlist == 'invalid':
                continue
            leaflist =  [nodelist[int(node)-1] for node in returnedlist]
            return leaflist

def parse_interfaces_state_layout(leafallinterfacesdict,leafs):
    #interface_output = ''
    nodeinterfacegrouping = []
    for leaf,leafinterlist in sorted(leafallinterfacesdict.items()):
        interfaces = gather_l1PhysIf_info(leafinterlist)
        #match_port_channels_to_interfaces(interfaces, leaf)
        interfacelist = []
        interfacelist2 = []
        for inter in interfaces:
            if inter.id.count('/') > 1:
                removed_eth = inter.id[3:]
                ethlist = removed_eth.split('/')
                inter['fex']=int(ethlist[0])
                inter['nodeid']='leaf{} fex{}'.format(str(leaf), str(ethlist[0]))
                inter['shortnum']=int(ethlist[2])
                interfacelist2.append(inter)
            else:
                inter['nodeid']='leaf{}'.format(str(leaf))
                inter['shortnum'] = int(inter.id[5:])
                interfacelist.append(inter)
                
        interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortnum)))
        interfacelist = sorted(interfacelist, key=lambda x: x.shortnum)
        interfacenewlist = interfacelist + interfacelist2
        for interface in interfacenewlist:
            if interface.adminSt == 'up':
                status = 'admin-up'
            elif interface.adminSt == 'down':
                status = 'admin-down'
            interface['portstatus'] = status
        nodeinterfacegrouping.append(interfacenewlist)
    #print(nodeinterfacegrouping)
    return nodeinterfacegrouping

def display_port_switchingSt(nodeinterfacegrouping):
    print('='*80)
    print('Green:EPGs Present, Black:No EPGs\n')
    for node in nodeinterfacegrouping:
        #print(node)
        #print('\n\n\n')
        groups = []
        uniquekeys = []
        data = node
        for k, g in itertools.groupby(data, lambda x:x.nodeid):
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        evenlist = []
        oddlist = []
        for group in groups:
            #if group[0].fex:
            print('{:^80}'.format(group[0].nodeid))
            for num,inters in enumerate(group):
                if num % 2:
                    evenlist.append(inters)
                else:
                    oddlist.append(inters)
            oddstring = ''
            for odd in oddlist:
                oddstring += odd.port_epgusage_color() + ' '
                #print odd.port_status_color(),
            print('{:^85}'.format(oddstring))
            evenstring = ''
            for even in evenlist:
                evenstring += even.port_epgusage_color() + ' '
            print('{:^85}'.format(evenstring))
            print('\n')
            oddlist = []
            evenlist = []
        groups = []
    print('='*80)
    print('')


def display_port_status(nodeinterfacegrouping):
    print('='*80)
    print('Green:Admin-UP, Black:Admin-DOWN\n')
    for node in nodeinterfacegrouping:
        #print(node)
        #print('\n\n\n')
        groups = []
        uniquekeys = []
        data = node
        for k, g in itertools.groupby(data, lambda x:x.nodeid):
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        evenlist = []
        oddlist = []
        for group in groups:
            #if group[0].fex:
            print('{:^80}'.format(group[0].nodeid))
            for num,inters in enumerate(group):
                if num % 2:
                    evenlist.append(inters)
                else:
                    oddlist.append(inters)
            oddstring = ''
            for odd in oddlist:
                oddstring += odd.port_adminstatus_color() + ' '
                #print odd.port_status_color(),
            print('{:^85}'.format(oddstring))
            evenstring = ''
            for even in evenlist:
                evenstring += even.port_adminstatus_color() + ' '
            print('{:^85}'.format(evenstring))
            print('\n')
            oddlist = []
            evenlist = []
        groups = []
    print('='*80)
    print('')

def display_port_custom(nodeinterfacegrouping, interfacelist): 
    for node in nodeinterfacegrouping:
        #print(node)
        #print('\n\n\n')
        groups = []
        uniquekeys = []
        data = node
        for k, g in itertools.groupby(data, lambda x:x.nodeid):
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        evenlist = []
        oddlist = []
        for group in groups:
            #if group[0].fex:
            print('{:^80}'.format(group[0].nodeid))
            for num,inters in enumerate(group):
                if num % 2:
                    evenlist.append(inters)
                else:
                    oddlist.append(inters)
            oddstring = ''
            for odd in oddlist:
               # import pdb; pdb.set_trace()
                oddstring += odd.custom_matched_port_color(interfacelist) + ' '
                #print odd.port_status_color(),
            #import pdb; pdb.set_trace()
            if len(oddlist) >= 27:
                print('{:^85}'.format(oddstring))
            elif len(oddlist) <= 12:
                print('{:31}{}'.format('',oddstring))
            else:
                print('{:5}{:^85}'.format('',oddstring))
            evenstring = ''
            for even in evenlist:
                evenstring += even.custom_matched_port_color(interfacelist) + ' '
            if len(evenlist) >= 27:
                print('{:^85}'.format(evenstring))
            elif len(evenlist) <= 12:
                print('{:31}{}'.format('',evenstring))
            else:
                print('{:5}{:^85}'.format('',evenstring))
            print('\r')
            oddlist = []
            evenlist = []
        groups = []
   # print('='*80)

def pull_leaf_state_interfaces(leaf, apic, q):
    url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json""".format(leaf=leaf,apic=apic)
    #import pdb; pdb.set_trace()
    logger.info(url)
    try:
        result = GetResponseData(url, cookie)
        logger.info('complete')
        q.put((leaf, result))
    except urllib2.HTTPError:
        logger.info('failed')
        q.put(('Failure','HTTPError'))

def main(import_apic,import_cookie, leafs, interfacelist=None, purpose='port_status'):
    #while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        #clear_screen()
        q = Queue.Queue()
        
        #leafs = leaf_selection(get_All_leafs(apic, cookie))

        threadlist = []
        leafdictwithresults = {}
        for leaf in leafs:
            t = threading.Thread(target=pull_leaf_state_interfaces, args=[leaf, apic ,q])
            t.start()
            threadlist.append(t)
        resultlist = []
        for thread in threadlist:
            thread.join()
            resultlist.append(q.get())
        for result in resultlist:
            if result[0] == 'Failure':
                raise KeyboardInterrupt
            leafdictwithresults[result[0]] = result[1]
    #leafallinterfacesdict = pull_leaf_interfaces(leafs
        nodeinterfacegrouping = parse_interfaces_state_layout(leafdictwithresults,leafs)
      #counter += 1  
   #clear_screen()
        if purpose == 'port_status':
            display_port_status(nodeinterfacegrouping)
        elif purpose == 'port_switching':
            display_port_switchingSt(nodeinterfacegrouping)
        elif purpose == 'custom':
            display_port_custom(nodeinterfacegrouping, interfacelist)
        #raw_input('')
        #Pre-pull for refresh
#        threadlist = []
#        leafdictwithresults = {}
#        for leaf in leafs:
#            t = threading.Thread(target=pull_leaf_interfaces, args=[leaf,q])
#            t.start()
#            threadlist.append(t)
#        resultlist = []
#        for thread in threadlist:
#            thread.join()
#            resultlist.append(q.get())
#        for result in resultlist:
#            leafdictwithresults[result[0]] = result[1]
#        nodeinterfacegrouping = print_interfaces_layout(leafdictwithresults,leafs)
#        authcounter += 1
#        if authcounter == 5:
#            refreshToken(apic,cookie)
#            authcounter = 0 
#        if action == 'a':
#            time.sleep(3)
#            continue
#        action = custom_raw_input("Options ('a' = auto refresh 3 sec, 'm' = manual refresh, 's' = int stats) default=[m]:")
#        if action == 'm':
#            continue
#        elif action == 's':
#            interfacesearch = custom_raw_input('interface (xxx ethx/x) [example: 101 eth1/1]: ')
#            leaf, interfacepull = interfacesearch.split()
#            showinterface.single_interface_pull(apic,cookie, leaf, interfacepull)
        #cookie = refreshToken(apic, cookie)
        #import pdb; pdb.set_trace()
