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


def shutinterfaces(interfaces, apic, cookie):
    queue = Queue.Queue()
    interfacelist = []
    interfacelist2 =[]
    for interface in interfaces:
        t = threading.Thread(target=postshut, args=(interface,queue, apic, cookie,))
        t.start()
        interfacelist.append(t)
    for t in interfacelist:
        t.join()
        interfacelist2.append(queue.get())
    for x in sorted(interfacelist2):
        print(x)

def postshut(interface,queue, apic, cookie):
        url = 'https://{apic}/api/node/mo/uni/fabric/outofsvc.json'.format(apic=apic)
        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a normal interface
        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"{interface}","lc":"blacklist"}},"children":[]}}}}'""".format(interface=interface)
        result, error =  PostandGetResponseData(url, data, cookie)
        if result == []:
            queue.put('[Complete] shut ' + interface.name)

def noshutinterfaces(interfaces, apic, cookie):
    queue = Queue.Queue()
    interfacelist = []
    interfacelist2 =[]
    for interface in interfaces:
        t = threading.Thread(target=postnoshut, args=(interface,queue, apic, cookie,))
        t.start()
        interfacelist.append(t)
    for t in interfacelist:
        t.join()
        interfacelist2.append(queue.get())
    for x in sorted(interfacelist2):
        print(x)

def postnoshut(interface,queue, apic, cookie):
        url = 'https://{apic}/api/node/mo/uni/fabric/outofsvc.json'.format(apic=apic)
        # data is the 'POST' data sent in the REST call to delete object from 'blacklist' (no shut)
        data = """'{{"fabricRsOosPath":{{"attributes":{{"dn":"uni/fabric/outofsvc/rsoosPath-[{interface}]","status":"deleted"}},"children":[]}}}}'""".format(interface=interface)
        result, error =  PostandGetResponseData(url, data, cookie)
        if result == []:
            queue.put('[Complete] no shut ' + interface.name)


def main(import_apic, import_cookie):
    while True:
        cookie = import_cookie
        apic = import_apic
        allepglist = get_All_EGPs(apic,cookie)
        allpclist = get_All_PCs(apic,cookie)
        allvpclist = get_All_vPCs(apic,cookie)
        all_leaflist = get_All_leafs(apic,cookie)
        clear_screen()
        location_banner('Shut and No Shut interfaces')
        selection = interface_menu()
    
        if selection == '1':
            returnedlist = physical_selection(all_leaflist, apic, cookie)
            print('\r')
            while True:
                option = custom_raw_input(
                    ("Would you like to do?\n\
                        \n1.) shut\
                        \n2.) no shut\
                        \n3.) bounce \n\
                        \nSelect a number: "))
                if option == '1':
                    print('\n')
                    shutinterfaces(returnedlist, apic, cookie)
                    break
                elif option == '2':
                    print('\n')
                    noshutinterfaces(returnedlist, apic, cookie)
                    break
                elif option == '3':
                    print('\n')
                    shutinterfaces(returnedlist, apic, cookie)
                    noshutinterfaces(returnedlist, apic, cookie)
                    break
                else:
                    print('\n\x1b[1;31;40mInvalid option, please try again...\x1b[0m\n')
                    continue
            custom_raw_input('\n#Press enter to continue...')
        elif selection == '2':
            returnedlist = port_channel_selection(allpclist)
            print('\r')
            option = custom_raw_input(
                    ("Would you like to do?\n\
                        \n1.) shut\
                        \n2.) no shut\
                        \n3.) bounce \n\
                        \nSelect a number: "))
            if option == '1':
                print('\n')
                shutinterfaces(returnedlist, apic, cookie)
            elif option == '2':
                print('\n')
                noshutinterfaces(returnedlist, apic, cookie)
            else:
                print('\n')
                shutinterfaces(returnedlist, apic, cookie)
                noshutinterfaces(returnedlist, apic, cookie)
            custom_raw_input('\n#Press enter to continue...')

        elif selection == '3':
            returnedlist = port_channel_selection(allvpclist)
            print('\r')
            option = custom_raw_input(
                    ("Would you like to do?\n\
                        \n1.) shut\
                        \n2.) no shut\
                        \n3.) bounce \n\
                        \nSelect a number: "))
            if option == '1':
                print('\n')
                shutinterfaces(returnedlist, apic, cookie)
            elif option == '2':
                print('\n')
                noshutinterfaces(returnedlist, apic, cookie)
            else:
                print('\n')
                shutinterfaces(returnedlist, apic, cookie)
                noshutinterfaces(returnedlist, apic, cookie)
            custom_raw_input('\n#Press enter to continue...')

