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

def askrefresh():
    while True:
        refresh = custom_raw_input("Return to admin list? [y=default|n]:  ") or 'y'
        if refresh[0].lower() == 'y':
            return True
        elif refresh[0].lower() == 'n':
            return False
        else:
            continue
    

def gatheranddisplayrecentadmins():
    while True:
        clear_screen()
        current_time = get_APIC_clock(apic,cookie)
        print("Current time = " + current_time)
        url = """https://{apic}/api/node/class/aaaModLR.json?query-target-filter=not(wcard(aaaModLR.dn,%22__ui_%22))&order-by=aaaModLR.created|desc&page=0&page-size=50""".format(apic=apic)
        logger.info(url)
        result = GetResponseData(url, cookie)
        print('\n{:>5}   {:26}{:20}{:18}{:18}{}'.format('#','Time','Time Difference', 'Type','User','admin Summary'))
        print('-'*175)
        admindict = {}
        for num,admin in enumerate(result,1):
            if admin.get('aaaModLR'):
                admindescr = admin['aaaModLR']['attributes']['descr'].split()
                admindescr = ' '.join(admindescr)
                if len(admindescr) > 120:
                     summaryadmindescr = admindescr[:120] + '...'
                else:
                    summaryadmindescr = admindescr
                admincreated = ' '.join(admin['aaaModLR']['attributes']['created'].split('T'))
                admintrig = admin['aaaModLR']['attributes']['trig']
                adminuser = admin['aaaModLR']['attributes']['user']
                admindn = admin['aaaModLR']['attributes']['dn']
                diff_time = time_difference(current_time,admincreated[:-6])
                admindict[num] = [admincreated[:-6],admintrig,adminuser,admindn,admindescr]
                print('{:5}.) {:26}{:20}{:18}{:18}{}'.format(num,admincreated[:-6],diff_time,admintrig,adminuser,summaryadmindescr))
        
        while True:
            moredetails = custom_raw_input("\nMore details, select number [refresh=Blank and Enter]:  ")
            if moredetails == '':
                break
            if moredetails.isdigit() and admindict.get(int(moredetails)):
                break
            else:
                print('\x1b[41;1mInvalid, number does not exist...try again\x1b[0m\n') 
        if moredetails == '':
            continue
        diff_time = time_difference(current_time,admindict[int(moredetails)][0])
        print('\n\n{:26}{:20}{:18}{:18}{}'.format('Time','Time Difference', 'Type','User','Object-Affected'))
        print('-'*120)
        print('{:26}{:20}{:18}{:18}{}\n'.format(admindict[int(moredetails)][0],diff_time, admindict[int(moredetails)][1],admindict[int(moredetails)][2],'/'.join(str(admindict[int(moredetails)][3]).split('/')[:-1])))
        print('admin Details')
        print('-'*15)
        print(admindict[int(moredetails)][4])
        print('\n\n')

        refresh = askrefresh()
        if refresh == True:
            continue
        else:
            print('\nEnding Program...\n')
            break
        


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    gatheranddisplayrecentadmins()

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
