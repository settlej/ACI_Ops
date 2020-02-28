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
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)
logger.setLevel(logging.INFO)

# Define logging handler for file and console logging.  Console logging can be desplayed during
# program run time, similar to print.  Program can display or write to log file if more debug 
# info needed.  DEBUG is lowest and will display all logging messages in program.  
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('aciops.log')
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


"""def removeepgs(interfaces):
    queue = Queue.Queue()
    interfacelist = []
    queueresultlist = []
    #interfacelist2 =[]
    for interface in interfaces:
        t = threading.Thread(target=postremove, args=(interface,queue,))
        t.start()
        interfacelist.append(t)
    for t in interfacelist:
        t.join()
        if not queue.empty():
            for epg in xrange(queue.qsize()):
                queueresultlist.append(queue.get())
    for interfaceresult in sorted(queueresultlist):
        print(interfaceresult)

def postremove(interface,queue):
    #import pdb; pdb.set_trace()
    for interface_epg in interface.epgfvRsPathAttlist:
        url = 'https://{apic}/api/node/mo/{rspathAtt}.json'.format(rspathAtt=interface_epg,apic=apic)
        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a normal interface
        data = """'{{"fvRsPathAtt":{{"attributes":{{"dn":"{rspathAtt}","status":"deleted"}},"children":[]}}}}'""".format(rspathAtt=interface_epg)
        logger.info(url)
        logger.info(data)
        #import pdb; pdb.set_trace()
        #print(data)
        result =  PostandGetResponseData(url, data, cookie)
        logger.debug(result)
        #print(result)
        if result[0] == []:
            #print(interface_epg[:interface_epg.find('rspathAtt')-1] + ' removed from ' + interface.name)
            queue.put(interface_epg[:interface_epg.find('rspathAtt')-1] + ' removed from ' + interface.name)
        else:
            queue.put('Failure -- ' + result[0])
"""
def removeepgs(interfaces):
    queue = Queue.Queue()
    interfacelist = []
    queueresultlist = []
    anyfailures = False
    #interfacelist2 =[]
    #import pdb; pdb.set_trace()
    for interface in interfaces:
        t = threading.Thread(target=postremove, args=(interface,queue,))
        t.start()
        interfacelist.append(t)
    for t in interfacelist:
        t.join()
        if not queue.empty():
            for epg in xrange(queue.qsize()):
                queueresultlist.append(queue.get())
    for interfaceresult in sorted(queueresultlist):
        if 'Failure' in interfaceresult:
            anyfailures = True
        print(interfaceresult)
    if anyfailures:
        return True
    else:
        return False

def postremove(interface_epg,queue):
    #import pdb; pdb.set_trace()
    interfacepath = interface_epg[interface_epg.find('rspathAtt')+11:-1]
    url = 'https://{apic}/api/node/mo/{rspathAtt}.json'.format(rspathAtt=interface_epg,apic=apic)
    # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a normal interface
    data = """'{{"fvRsPathAtt":{{"attributes":{{"dn":"{rspathAtt}","status":"deleted"}},"children":[]}}}}'""".format(rspathAtt=interface_epg)
    logger.info(url)
    logger.info(data)
    result =  PostandGetResponseData(url, data, cookie)
    logger.debug(result)
    if result[0] == []:
        removeendingrspathAtt = interface_epg.find('rspathAtt')-1
        queue.put('\x1b[1;32;40mSuccess!\x1b[0m -- Removed ' + interface_epg[:removeendingrspathAtt] + ' > ' + interfacepath)
    else:
        queue.put('\x1b[1;37;41mFailure!\x1b[0m -- ' + result[0])

def remove_all_epgs_every_interface(interfacelist, apic, cookie):
    print('\n')
    for interface in sorted(interfacelist, key=lambda x:x.dn):
        url = 'https://{apic}/api/node/class/fvRsPathAtt.json?query-target-filter=and(eq(fvRsPathAtt.tDn,"{interface}"))&order-by=fvRsPathAtt.modTs|desc'.format(interface=interface,apic=apic)
        logger.info(url)
        result = GetResponseData(url,cookie)
        logger.debug(result)
        if result == []:
            print('No static EPGs to remove for {}'.format(str(interface)))
        else:
            for epg in result:
                interface.epgfvRsPathAttlist.append(epg['fvRsPathAtt']['attributes']['dn'])
            failures = removeepgs(interface.epgfvRsPathAttlist)
            interface.epgfvRsPathAttlist = []
            if failures:
                print('Unable to remove some epgs on interface: {}'.format(str(interface)))
            else:
                print('Removal of static epgs on interface: {} [Complete]'.format(str(interface)))
    custom_raw_input('\n\n#Press enter to continue...')

def remove_selection_from_all_interfaces(interfacelist, apic, cookie):
    allepgsfoundlist = []
    interfaceswithoutepgs = []
    print('\n')
    for interface in interfacelist:
        url = 'https://{apic}/api/node/class/fvRsPathAtt.json?query-target-filter=and(eq(fvRsPathAtt.tDn,"{interface}"))&order-by=fvRsPathAtt.modTs|desc'.format(interface=interface,apic=apic)
        logger.info(url)
        result = GetResponseData(url,cookie)
        logger.debug(result)
        if result == []:
            interfaceswithoutepgs.append(interface)
        else:
            for epg in result:
                interface.epgfvRsPathAttlist.append(epg['fvRsPathAtt']['attributes']['dn'])
                allepgsfoundlist.append('/'.join(epg['fvRsPathAtt']['attributes']['dn'].split('/')[:4]))  
    allepgsfoundlist = sorted(list(set(allepgsfoundlist)))
    if allepgsfoundlist == []:
        empty_result = "No static EPGs found on any interfaces!"
        logger.info(empty_result)
        print('\n')
        print(empty_result)
        print('\n')
        custom_raw_input('#Press enter to continue...')
        return
    for num,epg in enumerate(allepgsfoundlist,1):
        print("{}.) {}".format(num,epgformater(epg)))
    selectedremovalepgs = custom_raw_input("\nWhich EPG(s) would you like to remove? [example 1 or 1,2 or 1-3,5]: ")
    removableegps = parseandreturnsingelist(selectedremovalepgs, allepgsfoundlist)
    filteredepglist = []
    for num in removableegps:
        filteredepglist.append(allepgsfoundlist[num-1])
    currentremovalegplist = []
    for interface in interfacelist:
        for epgfvRsPathAtt in interface.epgfvRsPathAttlist:
            for tDn in filteredepglist:
                if tDn in epgfvRsPathAtt:
                    currentremovalegplist.append(epgfvRsPathAtt)
    formatedconfirmationlist = []
    for epg in currentremovalegplist:
        epgandlocation = epg.split('/rspathAtt-')
        formatedepg = epgformater(epgandlocation[0])
        location = epgandlocation[1][1:-1]
        formatedconfirmationlist.append((formatedepg, location))
    groups = []
    uniquekeys = []
    for k, g in itertools.groupby(formatedconfirmationlist, lambda x:x[1]):
        groups.append(list(g))      # Store group iterator as a list
        uniquekeys.append(k)

    print('\n')
    print('Please Confirm Removeal:\n')
    for x in range(len(groups)):
        print(groups[x][0][1][9:].replace('paths','nodes'))
        for epgpath,interface in groups[x]:
            print('  Remove: {}'.format(epgpath))
    #import pdb; pdb.set_trace()
    while True:
        #import pdb; pdb.set_trace()
        verify = custom_raw_input('\nContinue removal of EPGs? [y|n]: ')
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
    print('\n')
    failures = removeepgs(currentremovalegplist)
    if failures:
        print('Unable to remove some epgs on interface: {}'.format(str(interface)))
    else:
        print('Removal of static epgs on interface: {} [Complete]'.format(str(interface)))
    raw_input("\n\n#Press enter to continue...")

def remove_per_interface(interfacelist, apic, cookie):
    for interface in interfacelist:
        url = 'https://{apic}/api/node/class/fvRsPathAtt.json?query-target-filter=and(eq(fvRsPathAtt.tDn,"{interface}"))&order-by=fvRsPathAtt.modTs|desc'.format(interface=interface,apic=apic)
        logger.info(url)
#              interface.getepgsurl = url
#          for interface in interfacelist:
#              t = 
        result, error = GetResponseData(url,cookie)
        logger.debug(result)
       # import pdb; pdb.set_trace()
        if result == []:
            print('No static EPGs to remove for {}'.format(str(interface)))
        else:
            for epg in result:
                interface.epgfvRsPathAttlist.append(epg['fvRsPathAtt']['attributes']['dn'])
            print('\n')
            #mport pdb; pdb.set_trace()
            removeepgs(interfacelist)
            interface.epgfvRsPathAttlist = []
            if error:
                print('Not unable to remove all selected egps on interface: {}'.format(str(interface)))
            else:
                print('Removal of static epgs on interface: {} [Complete]'.format(str(interface)))
    custom_raw_input('\n\n#Press enter to continue...')

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
        location_banner('Removing EPGs')

        selection = interface_menu()
    
        if selection == '1':
            chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
            switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
            interfacelist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)

            #interfacelist = physical_selection(all_leaflist, apic, cookie)
            #print(interfaces)
            print('What would you like to do for static EPGS on Port(s)?:\n\n'
                + '1.) Remove ALL EPGs\n'
                + '2.) Remove Selected from all interfaces\n')
                #+ '3.) Remove based on individual interface selection\n\n')
            while True:
                removaloption = custom_raw_input('Selection: ')
                if removaloption == '1':
                    while True:
                         verify = custom_raw_input('\nContinue removal of EPGs? [y|n]: ')
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
                    remove_all_epgs_every_interface(interfacelist, apic, cookie)
                    break
                elif removaloption == '2':
                    remove_selection_from_all_interfaces(interfacelist, apic, cookie)
                    break
                #elif removaloption == '3':
                #    remove_per_interface(interfacelist, apic, cookie)
                #    break
                else:
                    print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")

        elif selection == '2':
            interfacelist = port_channel_selection(allpclist)
            #print(interfaces)
            print('What would you like to do for static EPGS on Port(s)?:\n\n'
                + '1.) Remove ALL EPGs\n'
                + '2.) Remove Selected from all interfaces\n\n')
                #+ '3.) Remove based on individual interface selection\n\n')
            while True:
                removaloption = custom_raw_input('Selection: ')
                if removaloption == '1':
                    remove_all_epgs_every_interface(interfacelist, apic, cookie)
                    break
                elif removaloption == '2':
                    remove_selection_from_all_interfaces(interfacelist, apic, cookie)
                    break
                #elif removaloption == '3':
                #    remove_per_interface(interfacelist, apic, cookie)
                #    break
                else:
                    print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")

        elif selection == '3':
            interfacelist = port_channel_selection(allvpclist)
            print('What would you like to do for static EPGS on Port(s)?:\n\n'
                + '1.) Remove ALL EPGs\n'
                + '2.) Remove Selected from all interfaces\n\n')
                #+ '3.) Remove based on individual interface selection\n\n')
            while True:
                removaloption = custom_raw_input('Selection: ')
                if removaloption == '1':
                    remove_all_epgs_every_interface(interfacelist, apic, cookie)
                    break
                elif removaloption == '2':
                    remove_selection_from_all_interfaces(interfacelist, apic, cookie)
                    break
               # elif removaloption == '3':
               #     remove_per_interface(interfacelist, apic, cookie)
               #     break
                else:
                    print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")


