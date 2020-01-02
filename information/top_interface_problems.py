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

class interface():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.name = '/'.join(self.affected.split('/')[4:-1])[6:-1]
        self.leaf = self.affected.split('/')[2]
        self.pod = self.affected.split('/')[1]
    def __repr__(self):
        return self.name

class rmonIf():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.name = '/'.join(self.dn.split('/')[4:-1])[6:-1]
        self.leaf = self.dn.split('/')[2]
        self.pod = self.dn.split('/')[1]
    def __repr__(self):
        return self.dn

class eqpt():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.name = '/'.join(self.dn.split('/')[4:-1])[6:-1]
        self.leaf = self.dn.split('/')[2]
        self.pod = self.dn.split('/')[1]
    def __repr__(self):
        return self.dn

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    #clear_screen()
    #location_banner('Top Interface Problems')
    while True:
        clear_screen()
        location_banner('Top Interface Counters')
        url = """https://{apic}/api/class/rmonIfIn.json?order-by=rmonIfIn.errors|desc&page=0&page-size=30&query-target-filter=and(wcard(rmonIfIn.dn,"phys-"),lt(rmonIfIn.errors,"1"))""".format(apic=apic)
        result = GetResponseData(url, cookie)
        rmoifinlist = [rmonIf(x['rmonIfIn']['attributes']) for x in result]
        print('*' * 20)
        print("Top 30 Input Errors")
        print('*' * 20)
        for x in rmoifinlist:
            print("{} {} {}: {}".format( x.pod, x.leaf, x.name, x.errors))
            #print(x.pod, x.leaf, x.name, x.errors)
        #for x in result:
        #    print(x['rmonIfIn']['attributes']['dn'],x['rmonIfIn']['attributes']['errors'])
        url = """https://{apic}/api/class/rmonIfOut.json?order-by=rmonIfOut.errors|desc&page=0&page-size=30&query-target-filter=and(wcard(rmonIfOut.dn,"phys-"),lt(rmonIfOut.errors,"1"))""".format(apic=apic)
        result = GetResponseData(url, cookie)
        rmoifoutlist = [rmonIf(x['rmonIfOut']['attributes']) for x in result]
        counter = 0
        print('\x1b[7;32H{}'.format('*' * 20))
        print("\x1b[8;32HTop 30 Output Errors")
        print('\x1b[9;32H{}'.format('*' * 20))
        for x in rmoifoutlist:
            print("\x1b[{};32H{} {} {}: {}".format(10 + counter, x.pod, x.leaf, x.name, x.errors))
            counter += 1
        url = """https://192.168.255.2/api/class/eqptEgrTotal5min.json?order-by=eqptEgrTotal5min.bytesRate|desc&page=0&page-size=30query-target-filter=not(wcard(eqptEgrTotal5min.dn,"po")))"""
        result = GetResponseData(url, cookie)
        eqptoutlist = [eqpt(x['eqptEgrTotal5min']['attributes']) for x in result]
        counter = 0
        print('\x1b[7;65H{}'.format('*' * 28))
        print("\x1b[8;65HTop 30 Output (bps) Rate")
        print('\x1b[9;65H{}'.format('*' * 28))
        for x in eqptoutlist:
            print("\x1b[{};65H{} {} {}: {}".format(10 + counter, x.pod, x.leaf, x.name, round(float(x.bytesRate),2) * 8))
            counter += 1
        url = """https://192.168.255.2/api/class/eqptIngrTotal5min.json?order-by=eqptIngrTotal5min.bytesRate|desc&page=0&page-size=30"""
        result = GetResponseData(url, cookie)
        eqptinlist = [eqpt(x['eqptIngrTotal5min']['attributes']) for x in result]
        counter = 0
        print('\x1b[7;105H{}'.format('*' * 28))
        print("\x1b[8;105HTop 30 Input (bps) Rate")
        print('\x1b[9;105H{}'.format('*' * 28))
        for x in eqptinlist:
            #import pdb; pdb.set_trace()
            print("\x1b[{};105H{} {} {}: {}".format(10 + counter, x.pod, x.leaf, x.name, (round(float(x.bytesRate),2) * 8) ))
            counter += 1
    #    url = """https://192.168.255.2/api/node/class/eventRecord.json?order-by=eventRecord.created|desc&page=0&page-size=60&query-target-filter=or(eq(eventRecord.code,"E4205125"),eq(eventRecord.code,"E4215671"))""".format(apic=apic)
    #    result = GetResponseData(url, cookie)
    # #   for x in result:
    #    interfacelist = [interface(x['eventRecord']['attributes']) for x in result]
    #    for x in interfacelist:
    #        print("{} {} {}: {}".format(x.pod, x.leaf, x.name, x.descr))
            #import pdb; pdb.set_trace()
      #      print(x['eventRecord']['attributes']['affected'],x['eventRecord']['attributes']['descr'])

        custom_raw_input('#Press Enter to continue...')
