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
        refresh = custom_raw_input("Return to fault list? [y=default|n]:  ") or 'y'
        if refresh[0].lower() == 'y':
            return True
        elif refresh[0].lower() == 'n':
            return False
        else:
            continue

def gatheranddisplayrecentfaults():
    while True:
        clear_screen()
        current_time = get_APIC_clock(apic,cookie)
        print("Current time = " + current_time)
        url = """https://{apic}/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"))&order-by=faultInfo.lastTransition|desc&page=0&page-size=100""".format(apic=apic)
        logger.info(url)
        result = GetResponseData(url,cookie,timeout=60)
        print('\n{:>5}   {:26}{:20}{:18}{:18}{}'.format('#','Time','Time Difference', 'Type','Fault-State','Fault Summary'))
        print('-'*175)
        faultdict = {}
        for num,fault in enumerate(result,1):
            if fault.get('faultInst'):
                faultdescr = fault['faultInst']['attributes']['descr'].split()
                faultdescr = ' '.join(faultdescr)
                if len(faultdescr) > 120:
                     summaryfaultdescr = faultdescr[:112] + '...'
                else:
                    summaryfaultdescr = faultdescr
                faultlastTransition = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
                faulttype = fault['faultInst']['attributes']['type']
                faultstate = fault['faultInst']['attributes']['lc']
                faultdn = fault['faultInst']['attributes']['dn']
                diff_time = time_difference(current_time, faultlastTransition[:-6])
                faultdict[num] = [faultlastTransition[:-6],faulttype,faultstate,faultdn,faultdescr]
                print('{:5}.) {:26}{:20}{:18}{:18}{}'.format(num,faultlastTransition[:-6],diff_time,faulttype,faultstate,summaryfaultdescr))
            else:
                faultdescr = fault['faultDelegate']['attributes']['descr'].split()
                faultdescr = ' '.join(faultdescr)
                if len(faultdescr) > 120:
                     summaryfaultdescr = faultdescr[:112] + '...'
                else:
                    summaryfaultdescr = faultdescr
                faultlastTransition = ' '.join(fault['faultDelegate']['attributes']['lastTransition'].split('T'))
                faulttype = fault['faultDelegate']['attributes']['type']
                faultstate = fault['faultDelegate']['attributes']['lc']
                faultdn = fault['faultDelegate']['attributes']['dn']
                diff_time = time_difference(current_time, faultlastTransition[:-6])
                faultdict[num] = [faultlastTransition[:-6],faulttype,faultstate,faultdn,faultdescr]
                print('{:5}.) {:26}{:20}{:18}{:18}{}'.format(num,faultlastTransition[:-6],diff_time,faulttype,faultstate,summaryfaultdescr))
        while True:
            moredetails = custom_raw_input("\nMore details, select number [refresh=Blank and Enter]:  ")
            if moredetails == '':
                break
            if moredetails.isdigit() and faultdict.get(int(moredetails)):
                break
            else:
                print('\x1b[41;1mInvalid, number does not exist...try again\x1b[0m\n') 
        if moredetails == '':
            continue
        diff_time = time_difference(current_time, faultdict[int(moredetails)][0])
        print('\n\n{:26}{:20}{:18}{:18}{}'.format('Time','Time Difference', 'Type','Fault-State','Object-Affected'))
        print('-'*120)
        print('{:26}{:20}{:18}{:18}{}\n'.format(faultdict[int(moredetails)][0],diff_time, faultdict[int(moredetails)][1],faultdict[int(moredetails)][2],'/'.join(str(faultdict[int(moredetails)][3]).split('/')[:-1])))
        print('Fault Details')
        print('-'*15)
        print(faultdict[int(moredetails)][4])
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
    gatheranddisplayrecentfaults()

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
