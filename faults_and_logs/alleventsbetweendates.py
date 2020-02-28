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
import trace
import getpass
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


def ask_refresh():
    while True:
        refresh = custom_raw_input("Return to event list? [y=default|n]:  ") or 'y'
        if refresh[0].lower() == 'y':
            return True
        elif refresh[0].lower() == 'n':
            return False
        else:
            continue

def get_and_seperate_dates():
    userdatefailure = False
    futuredate = False
    while True:
        if userdatefailure == True:
            clear_screen()
        current_time = get_APIC_clock(apic,cookie)
        print("Current time = " + current_time)
        print("\nBetween Dates (Oldest -> Latest) \n\n[Format: yyyy-mm-ddThh:mm:ss - yyyy-mm-ddThh:mm:ss ]\n\n")
        if userdatefailure == True:
            print("\x1b[1;37;41mIncorrect Date/Format, Please try again\x1b[0m\n\n")
            if futuredate == True:
                print("\x1b[1;37;41mCan't pull future logs... \x1b[0m\n\n")
                futuredate = False
        dates = custom_raw_input("[Example: 2019-07-02T00:16:05 - 2019-07-02T10:16:05]: ")
        # regex to verify spacing and catch most date/format problems that will inhibit parsing
        if not re.search(r'^20[0-9]{2}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2} - 20[0-9]{2}\-[0-9]{2}\-[0-9]{2}T[0-9]{2}\:[0-9]{2}\:[0-9]{2}$', dates):
            userdatefailure = True
            continue
        # remove the 'T' for easy logic 
        dates = dates.replace('T', ' ')
        oldandnewdatesseperated = dates.split(' - ')
        try:
            # Cheap way to verify dates are a real date format, if execption error is raised then restart dates question
            datetime.datetime.strptime(oldandnewdatesseperated[0], '%Y-%m-%d %H:%M:%S')
            datetime.datetime.strptime(oldandnewdatesseperated[1], '%Y-%m-%d %H:%M:%S')
        except:
            userdatefailure = True
            continue
        # verify first date is not older than the second date specified
        if oldandnewdatesseperated[0] > oldandnewdatesseperated[1]:
            userdatefailure = True
            continue
        if oldandnewdatesseperated[1] > current_time:
            userdatefailure = True
            futuredate = True
            continue
            
        allseperated = [time.split(' ') for time in oldandnewdatesseperated]
        date1 = allseperated[0][0]
        time1 = allseperated[0][1]
        date2 = allseperated[1][0]
        time2 = allseperated[1][1]
        return date1,time1,date2,time2

class eventObject():
    def __init__(self, ftype=None, created=None, lastTransition=None, user=None, code=None, dn=None, descr=None, summarydescr=None, changeset=None, state=None, trig=None):
        self.created = created
        self.lastTransition = lastTransition
        self.summarydescr = summarydescr
        self.descr = descr
        self.ftype = ftype
        self.user = user
        self.code = code
        self.dn = dn
        self.changeset = changeset
        self.state = state
        self.trig = trig
    def __repr__(self):
        return self.lastTransition
    def __getitem__(self, code):
        if self.code == code:
            return self.code
        else:
            return None


def faultgather(faultresult):
    listfault = []
    faultdict = {}
    for num,fault in enumerate(faultresult,1):
        if fault.get('faultInst'):
            faultdescr = fault['faultInst']['attributes']['descr'].split()
            faultdescr = ' '.join(faultdescr)
            if len(faultdescr) > 120:
                 summaryfaultdescr = faultdescr[:120] + '...'
            else:
                summaryfaultdescr = faultdescr
            faultlastTransition = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            faultchangeset = fault['faultInst']['attributes']['changeSet']
            faulttype = fault['faultInst']['attributes']['type']
            faultcreated = fault['faultInst']['attributes']['created']
            faultstate = fault['faultInst']['attributes']['lc']
            faultdn = fault['faultInst']['attributes']['dn']
            faultdict[num] = [faultlastTransition[:-6],faulttype,faultstate,faultdn,faultdescr]
            listfault.append(eventObject(ftype='fault', created=faultcreated[:-6], lastTransition=faultlastTransition[:-6],
                             user=None, code=None, dn=faultdn, descr=faultdescr, summarydescr=summaryfaultdescr,
                             changeset=faultchangeset, state=faultstate, trig=None))
        else:
            faultdescr = fault['faultDelegate']['attributes']['descr'].split()
            faultdescr = ' '.join(faultdescr)
            if len(faultdescr) > 120:
                 summaryfaultdescr = faultdescr[:120] + '...'
            else:
                summaryfaultdescr = faultdescr
            faultlastTransition = ' '.join(fault['faultDelegate']['attributes']['lastTransition'].split('T'))
            faultchangeset = fault['faultDelegate']['attributes']['changeSet']
            faulttype = fault['faultDelegate']['attributes']['type']
            faultcreated = fault['faultDelegate']['attributes']['created']
            faultstate = fault['faultDelegate']['attributes']['lc']
            faultdn = fault['faultDelegate']['attributes']['dn']
            faultdict[num] = [faultlastTransition[:-6],faulttype,faultstate,faultdn,faultdescr]
            listfault.append(eventObject(ftype='faultd', created=faultcreated[:-6], lastTransition=faultlastTransition[:-6],
                             user=None, code=None, dn=faultdn, descr=faultdescr, summarydescr=summaryfaultdescr,
                             changeset=faultchangeset, state=faultstate, trig=None))
    return listfault

def auditgather(auditresult):
    listfault = []
    for audit in auditresult: 
        if audit.get('aaaModLR'):
            auditdescr = audit['aaaModLR']['attributes']['descr'].split()
            auditdescr = ' '.join(auditdescr)
            if len(auditdescr) > 120:
                 summaryauditdescr = auditdescr[:120] + '...'
            else:
                summaryauditdescr = auditdescr
            auditcreated = ' '.join(audit['aaaModLR']['attributes']['created'].split('T'))
            audittrig = audit['aaaModLR']['attributes']['trig']
            audituser = audit['aaaModLR']['attributes']['user']
            auditdn = audit['aaaModLR']['attributes']['dn']
            listfault.append(eventObject(ftype='audit', created=auditcreated[:-6], lastTransition=auditcreated[:-6],
                             user=audituser, code=None, dn=auditdn, descr=auditdescr, summarydescr=summaryauditdescr,
                             changeset=None, state=None, trig=audittrig))
    return listfault

def eventgather(eventresult):
    listfault = []
    for event in eventresult:
        if event.get('eventRecord'):
            eventdescr = event['eventRecord']['attributes']['descr'].split()
            eventdescr = ' '.join(eventdescr)
            if len(eventdescr) > 120:
                summaryeventdescr = eventdescr[:120] + '...'
            else:
                summaryeventdescr = eventdescr
            eventcreated = ' '.join(event['eventRecord']['attributes']['created'].split('T'))
            eventtrig = event['eventRecord']['attributes']['trig']
            eventuser = event['eventRecord']['attributes']['user']
            eventdn = event['eventRecord']['attributes']['dn']
            if 'eth' in eventdn and not 'extpaths' in eventdn:
                if re.search(r'node-[0-9]{1,3}', eventdn):
                    leaf = re.search(r'node-[0-9]{1,3}', eventdn).group()
                else:
                    leaf = 'unknown'
                leaf = leaf.replace('node', 'leaf')
                if re.search(r'eth.*\/[0-9]{1,3}\]', eventdn):
                    interface = re.search(r'eth.*\/[0-9]{1,3}\]', eventdn).group()
                else:
                    interface = 'unknown'
            elif re.search(r'po[0-9]*\]', eventdn):
                leaf = re.search(r'node-[0-9]{1,3}', eventdn).group()
                leaf = leaf.replace('node', 'leaf')
                interface = re.search(r'po[0-9]*\]', eventdn).group()
            listfault.append(eventObject(ftype='event', created=eventcreated[:-6], lastTransition=eventcreated[:-6],
                             user=eventuser, code=None, dn=eventdn, descr=eventdescr, summarydescr=summaryeventdescr,
                             changeset=None, state=None, trig=eventtrig))
    return listfault

def gather_and_display_related_events(apic,cookie):
    while True:
        clear_screen()
        date1,time1,date2,time2 = get_and_seperate_dates()
        print('\nGathering Audit Logs...')
        url = """https://{apic}/api//class/aaaModLR.json?query-target-filter=and(gt(aaaModLR.created,"{}T{}"),lt(aaaModLR.created,"{}T{}"))&order-by=aaaModLR.created|desc""".format(date1,time1,date2,time2,apic=apic)
        logger.info(url)
        auditresult = GetResponseData(url,cookie, timeout=60)
        list1 = auditgather(auditresult)
        print('Gathering Fault Logs...')
        url = """https://{apic}/api/node/class/faultInfo.json?query-target-filter=and(gt(faultInfo.created,"{}T{}"),lt(faultInfo.created,"{}T{}"))&order-by=faultInfo.lastTransition|desc""".format(date1,time1,date2,time2,apic=apic)
        logger.info(url)
        faultresult = GetResponseData(url,cookie, timeout=60)
        list2 = faultgather(faultresult)
        print('Gathering Event Logs...\n')
        logger.info(url)
        url = """https://{apic}/api/node/class/eventRecord.json?query-target-filter=and(gt(eventRecord.created,"{}T{}"),lt(eventRecord.created,"{}T{}"))&order-by=eventRecord.created|desc""".format(date1,time1,date2,time2,apic=apic)
        eventresult = GetResponseData(url,cookie, timeout=60)
        list3 = eventgather(eventresult)
        print('{:6}{:8}{:26}{:10}{:18}{}'.format('Order','Type', 'Date & Time ', 'User','Fault-State','Summary Description'))
        print('-'*140)
        listall = list1 + list2 + list3
        lista = sorted(listall, key=lambda event: event.lastTransition, reverse=True)
        eventdict = {}
        for num,event in enumerate(lista,1):
            if event.ftype == 'event':
                eventdict[num] = event
                print('{:6}\x1b[2;30;43m{:8}\x1b[0m{:26}{:10}{:18}{}'.format(str(num) + '.)', event.ftype,event.lastTransition,event.user,event.state,event.summarydescr))
            elif event.ftype == 'fault' or event.ftype == 'faultd':
                eventdict[num] = event
                print('{:6}\x1b[1;33;44m{:8}\x1b[0m{:26}{:10}{:18}{}'.format(str(num) + '.)', event.ftype,event.lastTransition,event.user,event.state,event.summarydescr))
            elif event.ftype == 'audit':
                eventdict[num] = event
                print('{:6}\x1b[6;30;41m{:8}\x1b[0m{:26}{:10}{:18}{}'.format(str(num) + '.)', event.ftype,event.lastTransition,event.user,event.state,event.summarydescr))
        while True:
            while True:
                ask = custom_raw_input("\nMore details, select number [New Dates Search=Blank and Enter]:  ")
                if ask == '':
                    break
                elif ask.isdigit() and int(ask) > 0 and int(ask) <= len(eventdict):
                    ask = int(ask)
                    break
            if ask == '':
                break
            print('\n\n{:8}{:26}{:26}{:20}{:18}{:18}{}'.format('Type','Time Created', 'Time Modified', 'User','State','Object-Affected',''))
            print('-'*120)
            print('{:8}{:26}{:26}{:20}{:18}{:18}{}\n'.format(eventdict[ask].ftype,eventdict[ask].created,eventdict[ask].lastTransition, eventdict[ask].user,eventdict[ask].state,eventdict[ask].dn, ''))
            print('Changed info (Only for Faults)')
            print('-'*25)
            print(eventdict[ask].changeset)
            print('\r')
            print('Event Details')
            print('-'*15)
            print(eventdict[ask].descr)
            print('\n')
        

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    gather_and_display_related_events(apic,cookie)

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
