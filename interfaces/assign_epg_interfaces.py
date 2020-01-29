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
import datetime
import itertools
#import trace
#import pdb
import threading
import Queue
from collections import namedtuple
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


def parseandreturnsingelist2(liststring, collectionlist):
    try:
        rangelist = []
        singlelist = []
        seperated_list = liststring.split(',')
        for x in seperated_list:
            if '-' in x:
                rangelist.append(x)
            else:
                singlelist.append(int(x))
        if len(rangelist) >= 1:
            for foundrange in rangelist:
                tempsplit = foundrange.split('-')
                for i in xrange(int(tempsplit[0]), int(tempsplit[1])+1):
                    singlelist.append(int(i))
   #     print(sorted(singlelist))
        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
            return 'invalid'
        return list(set(singlelist)) 
    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'

def vlan_and_url_generating(chosenepgs,choseninterfaceobjectlist, apic, epg_type):
    urllist = []
    confirmationlist = []
    for epg in sorted(chosenepgs):
        url = """https://{apic}/api/node/mo/{}.json""".format(epg,apic=apic)
        logger.info(url)
        print("\nProvide a vlan number for epg: {}".format(epgformater(epg)))
        while True:
            try:
                vlan = custom_raw_input('vlan number [1-3899]: ')
                print('\r')
                if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
                   break
                else:
                    print('Invalid vlan number')
            except ValueError:
                continue
        for interface in sorted(choseninterfaceobjectlist):
            if epg_type == 'trunk_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","instrImedcy":"immediate",\
                     "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface.dn,vlan=vlan)
            elif epg_type == 'access_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","mode":"native","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface.dn,vlan=vlan)
            elif epg_type == 'untagged_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","mode":"untagged","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface.dn,vlan=vlan)
            urlmodify = namedtuple('urlmodify', ('url', 'interface', 'data'))
            urllist.append(urlmodify(url, interface, data))
        confirmationlist.append((choseninterfaceobjectlist,epg, vlan))
    return urllist, confirmationlist

def add_egps_to_interfaces(urllist, interfacetype, cookie):
    queue = Queue.Queue()
    threadlist = []
    queuelist = []
    for url in urllist:
        t = threading.Thread(target=submit_add_post_request, args=(url,interfacetype,queue, cookie))
        t.daemon = True
        #t.setDaemon(True)
        t.start()
        threadlist.append(t)
    for t in threadlist:
        t.join()
        queuelist.append(queue.get())
    for q in sorted(queuelist):
        print(q)

def submit_add_post_request(url,interfacetype,queue, cookie):
    result, error = PostandGetResponseData(url.url, url.data, cookie)
    logger.info(result)
    logger.info(error)
    shorturl = url.url[30:-5]
    if error == None and result == []:
        finalresult = '\x1b[1;32;40mSuccess!\x1b[0m -- Added ' + shorturl + ' > ' + str(url.interface)
        queue.put(finalresult)
        logger.debug('{} modify: {}'.format(interfacetype, finalresult))
    elif result == 'invalid':
        logger.error('{} modify: {}'.format(interfacetype, error))
        interfacepath = re.search(r'\[.*\]', error)
        if 'already exists' in error:
            queue.put('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + ' > ' + url.interface.dn + '\t -- EPG already on Interface ')# + interfacepath.group())    
        else:
            queue.put('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + '\t -- ' + error)
    else:
        logger.error('{} modify: {}'.format(interfacetype, error))
        print(error)

def interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="Physical"):
    while True:
        print('What is the inteface epg mode?:\n\n'
              + '**Use either 1 for trunks ports and 2 for normal access ports\n\n' 
              + '1.) Trunk\n'
              + '2.) Access\n'
              + '3.) Untagged\n')
        askepgtype = custom_raw_input("Which mode? [default=1]: ") or '1'
        if askepgtype == '1':
            epg_type = 'trunk_port'
            break
        elif askepgtype == '2':
            epg_type = 'access_port'
            break
        elif askepgtype == '3':
            epg_type = 'untagged_port'
            break
        else:
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue
        
    urllist, confirmationlist =  vlan_and_url_generating(chosenepgs,choseninterfaceobjectlist, apic, epg_type)
    print('')
    print('Please Confirm deployment:\n')
    for confirm in confirmationlist:
        print('{epg} with vlan {vlan}'.format(epg=confirm[1],vlan=confirm[2]))
        for interface in confirm[0]:
            print('{}'.format(interface))
        print('')
    while True:
        verify = custom_raw_input('Continue? [y|n]: ')
        if verify == '':
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue
        elif verify[0].lower() == 'y':
            break
        elif verify[0].lower() == 'n':
            raise KeyboardInterrupt
        else:
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue    
    add_egps_to_interfaces(urllist, type, cookie)

def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        allepglist = get_All_EGPs(apic,cookie)
        allpclist = get_All_PCs(apic,cookie)
        allvpclist = get_All_vPCs(apic,cookie)
        all_leaflist = get_All_leafs(apic,cookie)
        clear_screen()
        location_banner('Adding EPGs')
        selection = interface_menu()
    
        if selection == '1':
            chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
            switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
            returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)

            #returnedlist = physical_selection(all_leaflist, apic, cookie)
            #import pdb; pdb.set_trace()
            chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(returnedlist, allepglist)
            #import pdb; pdb.set_trace()
            interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic)
            print('\r')
            custom_raw_input('#Press enter to continue...')
        elif selection == '2':
            returnedlist = port_channel_selection(allpclist)
            chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(returnedlist, allepglist)
            interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="Port-Channel")
            #port_channel_selection(allpclist,allepglist)
            print('\r')
            custom_raw_input('#Press enter to continue...')
        elif selection == '3':
            returnedlist = port_channel_selection(allvpclist)
            chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(returnedlist, allepglist)
            interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="vPort-Channel")
            print('\r')
            custom_raw_input('#Press enter to continue...')
        
