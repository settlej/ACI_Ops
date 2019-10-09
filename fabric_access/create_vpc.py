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
logger.setLevel(logging.DEBUG)

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

def create_infraNodeP(aps_name, apic, cookie, interfaces):
    
    url = """url: https://{apic}/api/node/mo/uni/infra/accportprof-Switch101-102_Profile_ifselector/hports-{aps_name}-typ-range.json""".format(apic=apic,aps_name=aps_name)
    data= """{"infraHPortS":{"attributes":
                                {"name":"{aps_name}","status":"created,modified"},
                                    "children":[
                                        {"infraPortBlk":{"attributes":
                                                            {"fromPort":"{first_interfacenum}","toPort":"{last_interfacenum}","name":"block2","status":"created,modified"},"children":[]}},
                                        {"infraRsAccBaseGrp":{"attributes":
                                                            {"status":"created,modified"},"children":[]}}]}}""".format(aps_name=aps_name,first_interfacenum=first_interfacenum,last_interfacenum=last_interfacenum)

class leafprofile():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
#def interface_range():
#    raw_interfaces = custom_raw_input('Interface range for VPC [example: 1/1-8 or 1/1,1/3]: ')
#    parseandreturnsingelist(raw_input,interfacelist)
def display_and_select_leafselector(apic,cookie):
    url = """https://{apic}/api/node/mo/uni/infra.json?target-subtree-class=infraFexP,infraAccPortP&query-target=subtree""".format(apic=apic)
    result = GetResponseData(url,cookie)
    logger.debug(result)
    leafprofilelist = []
    fexprofilelist = []
    for profile in result:
        #import pdb; pdb.set_trace()
        if profile.get('infraAccPortP'):
            #print('{}.) {}'.format(num,profile['infraAccPortP']['attributes']['name']))
            leafprofilelist.append(leafprofile(**profile['infraAccPortP']['attributes']))
        elif profile.get('infraFexP'):
            #print('{}.) {}'.format(num,profile['infraFexP']['attributes']['name']))
            fexprofilelist.append(leafprofile(**profile['infraFexP']['attributes']))
    #print(leafprofilelist)
    print('LEAF___')
    for type in leafprofilelist:
        print(type.name)
    print('FEX____')
    for type in fexprofilelist:
        print(type.name)

def ask_vPC_location(all_leaflist, apic, cookie):
    return physical_leaf_selection(all_leaflist, apic, cookie)

def ask_vPC_name():
    while True:
        vpcname = custom_raw_input('Name for new vPC [example: 101-102_ENC01_VPC5]: ')
        askconfirm = custom_raw_input('"{}" Coninue? [Y]: ') or 'Y'
        if askconfirm.upper().strip().lstrip() == 'Y':
            return vpcname
        else:
            continue

def main(import_apic,import_cookie):
#    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Creating VPC')
        ##all_leaflist = get_All_leafs(apic,cookie)
        ##chosenleafs = ask_vPC_location(all_leaflist, apic, cookie)
        ##switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_status')
        #returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
        #vpcname = ask_vPC_name()
        display_and_select_leafselector(apic,cookie)
        raw_input()