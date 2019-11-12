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
import random
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

def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        url = """https://{apic}/api/node/class/topSystem.json""".format(apic=apic)
        result = GetResponseData(url, cookie)
        xlocation = 6
        ylocation = 3
        clear_screen()
        for node in sorted(result, key=lambda a: int(a['topSystem']['attributes']['id']) ):
            #if location == 4:
            #    location = 1
            print('*' * 133)
            a = ('{}'.format('\x1b[' + str(ylocation) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['podId'] + '\x1b[0m'))
            print(a)
            print('{}'.format('\x1b[' + str(ylocation+1) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['id'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+2) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['systemUpTime'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+3) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['currentTime'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+4) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['inbMgmtAddr'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+5) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['oobMgmtAddr'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+6) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['role'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+7) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['serial'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+8) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['version'] + '\x1b[0m'))
            print('{}'.format('\x1b[' + str(ylocation+9) + ';' + str(xlocation) + 'H' + node['topSystem']['attributes']['status'] + '\x1b[0m'))
            xlocation += 33
            if xlocation >= 133:
                ylocation += 12
                xlocation = 6
        break
    custom_raw_input('\nPress enter to continue...')