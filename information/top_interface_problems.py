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
    location_banner('Top Interface Problems')
    while True:
        url = """https://{apic}/api/class/rmonIfIn.json?order-by=rmonIfIn.errors|desc&page=0&page-size=30""".format(apic=apic)
        result = GetResponseData(url, cookie)
        for x in result:
            print(x['rmonIfIn']['attributes']['dn'],x['rmonIfIn']['attributes']['errors'])
        url = """https://{apic}/api/class/rmonIfOut.json?order-by=rmonIfOut.errors|desc&page=0&page-size=30""".format(apic=apic)
        result = GetResponseData(url, cookie)
        for x in result:
            print(x['rmonIfOut']['attributes']['dn'],x['rmonIfOut']['attributes']['errors'])
        custom_raw_input('#Press Enter to continue...')