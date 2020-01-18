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
import getpass
import threading
import Queue
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

class faultobject():
    def __init__(self, faultstring='', code='', amount=0, order=None, results=None):
        self.faultstring = faultstring
        self.code = code
        self.amount = amount
        self.order = order
        self.results = results
    def __repr__(self):
        return self.code
    def __getitem__(self, code):
        if self.code == code:
            return self.code
        else:
            return None

def faultSummary(apic, cookie):
    url = ("""https://{apic}/api/node/class/faultSummary.json?query-target-filter=and(not(wcard(faultSummary.dn,%22__ui_%22)),and())""" + \
          """&order-by=faultSummary.severity|desc&page=0&page-size=100""").format(apic=apic)
    logger.info(url)
    result = GetResponseData(url, cookie)
    #print(result)
    reduced_fault_summary_dict = {}
    neededfaults = ['F1385', # OSPF
                    'F1543', # Leaf/Spine Down
                    'F1394', # Uplinks
                    'F0532', # Server ports
                    'F1296', # vPC full down
                    'F2705', # vPC half down
                    'F0600', # vPC connection issues
                    'F1574', # NTP
                    'F0130', # APIC can't reach VCenter
                    'F1262', # Database APIC
                    'F0321', # Health APIC
                    'F0103', # apic inter
                    'F0413', # missing psu
                    'F1451', # shutdown psu
                    'F1940'] # failed psu

    orderedfilteredfaultlist = []
    for fault in result:
        if fault['faultSummary']['attributes']['code'] in neededfaults:
            key = fault['faultSummary']['attributes']['code']
            value = fault['faultSummary']['attributes']['count']
            reduced_fault_summary_dict[key] = value
            # needed to create an object to sort by 'order'
            foundobject = faultobject(code=fault['faultSummary']['attributes']['code'])
            foundobject.amount = fault['faultSummary']['attributes']['count']
            foundobject.order = neededfaults.index(fault['faultSummary']['attributes']['code'])
            orderedfilteredfaultlist.append(foundobject)
    orderedfilteredfaultlist = sorted(orderedfilteredfaultlist, key=lambda fault: fault.order)
    return orderedfilteredfaultlist, reduced_fault_summary_dict

def displayfaultSummaryandSelection(orderedlist):
    faultstringdict = { 'F1385':'OSPF peer issues',
                        'F1543':'Leaf/Spine(s) are Down',
                        'F1394':'Leaf uplinks are Down',
                        'F0532':'Server ports Down',
                        'F1296':'vPC Fully Down',
                        'F2705':'vPC Half Down',
                        'F0600':'vPC/PC Connection issues',
                        'F1574':'NTP issues',
                        'F0130':"APIC can't reach VCenter",
                        'F1262':'Database issues on APIC',
                        'F0321':'APIC Health issues',
                        'F0103':'APIC Physical Port issues',
                        'F0413':'Missing Power Supply',
                        'F1451':'Unused/Shutdown Power Supply',
                        'F1940':'Failed Power Supply'
                        }

    print('\n')
    for num,fault in enumerate(orderedlist,1):
        fault.faultstring = faultstringdict[fault.code]
        print('\t{}.) {}'.format(num,fault.faultstring))

    #print('\t{}.) Exit'.format(str(len(orderedlist)+1)))
    #orderedlist.append('Exit')
    print('\n')
    while True:
        selected = custom_raw_input('Which fault?:  ')
        if selected.isdigit() and (int(selected) > 0 and int(selected) < len(orderedlist)+1):
            break
        else:
            print('\n\x1b[1;31;40mInvalid entry...please try again\x1b[0m\n') 
    faultselected = (orderedlist[int(selected)-1])
    #if faultselected is orderedlist[-1]:
    #    print('Exiting program...\n')
    #    exit()
    return faultselected

def displayfaultSummary(summarylist):
    fabricfaultstring = ""
    apicfaultstring = ""
    powerfaultstring = ""
    #print('\n{:<50}{}'.format('','# of Faults'))
    print('-'*62)
    print('\r')
    listoffoundfalts = []
    fabricfaultstring += '{:.<45}{}\n'.format('Checking OSPF peer issues',summarylist.get('F1385', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking if Leaf/Spine(s) are Down',summarylist.get('F1543', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking if Leaf uplinks are Down',summarylist.get('F1394', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking for Server ports Down',summarylist.get('F0532', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking for vPC Fully Down',summarylist.get('F1296', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking for vPC Half Down',summarylist.get('F2705', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking for vPC/PC Connection issues',summarylist.get('F0600', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking NTP issues',summarylist.get('F1574', 'None'))
    fabricfaultstring += '{:.<45}{}\n'.format('Checking APIC to VCenter connection issues',summarylist.get('F0130','None'))
    apicfaultstring += '{:.<45}{}\n'.format('Checking for Database issues on APIC',summarylist.get('F1262', 'None'))
    apicfaultstring += '{:.<45}{}\n'.format('Checking for APIC Health issues',summarylist.get('F0321', 'None'))
    apicfaultstring += '{:.<45}{}\n'.format('Checking APIC Physical Port issues',summarylist.get('F0103', 'None'))
    powerfaultstring += '{:.<45}{}\n'.format('Checking Missing Power Supply',summarylist.get('F0413', 'None'))
    powerfaultstring += '{:.<45}{}\n'.format('Checking Unused/Shutdown Power Supply',summarylist.get('F1451', 'None'))
    powerfaultstring += '{:.<45}{}\n'.format('Checking Failed Power Supply',summarylist.get('F1940', 'None'))
    
    listoffaultgroups = [('Fabric:',fabricfaultstring.split('\n')), ('APIC:',apicfaultstring.split('\n')), ('PSU:',powerfaultstring.split('\n'))]
    for group in listoffaultgroups:
        print(group[0])
        for faults in group[1]:
            print('\t'+ faults)
    print('-'*62)

def get_fault_results(apic, cookie, code):
    url = ("""https://{apic}/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" +
          """eq(faultInfo.code,"{code}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""").format(apic=apic,code=code.code)
    logger.info(url)
    result = GetResponseData(url, cookie)
    code.results = result
    code.amount 
    return code


def detail_ospf_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print('\n')
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Leaf', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        lc = fault['faultInst']['attributes']['lc']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]{0,3}', fault['faultInst']['attributes']['dn'])
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,controller.group(), lc,descr))
    print('\n')
def detail_switch_availability_status_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print('\n')
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Leaf', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        device = re.search(r'[nN]ode [0-9]{1,3}', descr).group()
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,device, lc,descr))
    print('\n')
def detail_access_inter_faults(listdetail, apic=None):
    current_time = get_APIC_clock(apic,cookie)
    #import pdb; pdb.set_trace()
    print('\r')
    print('Current Time = ' + current_time)
    print('\n{:7}{:26}{:20}{:10}{:15}{:20}{:17}{}'.format('','Time', 'Time Diff','Device','Interface','Port-Channel', 'State', 'Description'))
    print('-'*130)
    tablestring = ''
    for num,fault in enumerate(listdetail,1):
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(current_time,timestamp[:-6])
        interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
        leaf = re.search(r'(node [0-9]{3})|(node-[0-9]{3})', fault['faultInst']['attributes']['dn'])
        if leaf == None:
            leaf = re.search(r'leaf[0-9]{3}', fault['faultInst']['attributes']['dn'])
        logger.debug('{} {} {}'.format(current_time,timestamp,interface.group()))
        lc = fault['faultInst']['attributes']['lc'][:15]
        description = ' '.join(fault['faultInst']['attributes']['descr'].split())
        #print(description_short)
        usedlocation =  description.find('used')
        description_final = description[:usedlocation - 2] 
        que = Queue.Queue()
        polisting = []
        if 'po' in interface.group():
            t = threading.Thread(target=retrievePortChannelName, args=(apic, cookie, interface.group(), leaf.group(), que))
            t.start()
            polisting.append(t)
        else:
            if leaf == None or interface == None:
                import pdb; pdb.set_trace()
            tablestring += '{:4}.) {:26}{:20}{:10}{:15}{:20}{:17}{}\n'.format(num,timestamp[:-6],diff_time, leaf.group(), interface.group(), '', lc,  description_final)
        for t in polisting:
            t.join()
            po = que.get()
            logger.debug('{} {}'.format(fault, diff_time))
            tablestring += '{:4}.) {:26}{:20}{:10}{:15}{:20}{:17}{}\n'.format(num,timestamp[:-6],diff_time, leaf.group(), interface.group(), po[:19], lc, description_final)
    #import pdb; pdb.set_trace()
    print(tablestring)
    print('\n')
    while True:
        refresh = False
        while True:
            moredetails = custom_raw_input("More details, select number [default=No]:  ")
            if moredetails == '':
                break
            if moredetails.isdigit() and int(moredetails) <= len(listdetail) and int(moredetails) > 0:
                break
            else:
                print('\x1b[41;1mInvalid, number does not exist...try again\x1b[0m\n') 
        if moredetails == '':
            print('')
            return
           # refresh = True
        if refresh:
            print('')
            break
        timestamp = ' '.join(listdetail[int(moredetails)-1]['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(current_time,timestamp[:-6])
        print('\n\n{:26}{:20}{:7}{:30}{}\n'.format('Time','Time Difference', 'Code','Cause','Object-Affected'))
        print('-'*120)
        print('\x1b[1;33;40m{:26}{:20}{:7}{:30}{}'.format(' '.join(listdetail[int(moredetails)-1]['faultInst']['attributes']['lastTransition'].split('T'))[:-7],diff_time, listdetail[int(moredetails)-1]['faultInst']['attributes']['code'],listdetail[int(moredetails)-1]['faultInst']['attributes']['cause'],'/'.join(str(listdetail[int(moredetails)-1]['faultInst']['attributes']['dn']).split('/')[:-1])))
        print('')
        print('\x1b[0mEvent Details')
        print('-'*15)
        print('\x1b[1;33;40m' + listdetail[int(moredetails)-1]['faultInst']['attributes']['descr'])
        print('')
        print('\x1b[0mEvent ChangeSet')
        print('-'*15)
        print('\x1b[1;33;40m' + listdetail[int(moredetails)-1]['faultInst']['attributes']['changeSet'] + '\x1b[0m')
        print('\n')
        #refresh = askrefresh()
        #if refresh == True:
        #    continue
        #else:
        #    print('\nEnding Program...\n')
        #    break
    refresh = False
def detail_leaf_spine_uplink_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print('\n')
    print("{:26}{:20}{:12}{:12}{:18}{}".format('Time', 'Time Diff','Device','Interface', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]{0,3}', fault['faultInst']['attributes']['dn'])
        interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
        print("{:26}{:20}{:12}{:12}{:18}{}".format(timestamp[:-6],diff_time,controller.group(), interface.group(), lc,descr))
    print('\n')
def detail_vpc_full_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print('\n{:26}{:20}{:18}{}'.format('Time', 'Time Diff','State','Description'))
    print('-'*120)
    for fault in listdetail:
        if fault.get('faultInst'):
            timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            logger.debug('{} {}'.format(current_time,timestamp))
            diff_time = time_difference(current_time,timestamp[:-6])
            descr = fault['faultInst']['attributes']['descr']
            #interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
            #leaf = re.search(r'leaf[0-9]{3}', fault['faultInst']['attributes']['descr'])
            lc = fault['faultInst']['attributes']['lc']
            print('{:26}{:20}{:18}{}'.format(timestamp[:-6],diff_time, lc, descr))
    print('\n')
def detail_vpc_part_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("\n{:26}{:20}{:15}{:18}{}".format('Time', 'Time Diff', 'State','Device','Description'))
    print('-'*120)
    for fault in listdetail:
        if fault.get('faultInst'):
            dn = fault['faultInst']['attributes']['dn'] 
            dn = dn.split('/')[2]
            descr = fault['faultInst']['attributes']['descr']   
            changeSet = fault['faultInst']['attributes']['changeSet']
            timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            logger.debug('{} {}'.format(current_time,timestamp))
            diff_time = time_difference(current_time,timestamp[:-6])
            lc = fault['faultInst']['attributes']['lc']
            print("{:26}{:20}{:15}{:18}{}".format(timestamp[:23],diff_time,lc,dn,descr))#,'changeSet: ' + changeSet))
    print('\n')
def detail_apic_replica_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Controller', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'controller [0-9]', fault['faultInst']['attributes']['descr'])
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,controller.group()[-1],lc,descr))
    print('\n')
def detail_apic_health_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Controller', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]', fault['faultInst']['attributes']['dn'])
        print("{:26}{:20}{:^12}{:18}{}".format(timestamp[:-6],diff_time,controller.group()[-1],lc,descr))
    print('\n')
def detail_ntp_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff', 'Device', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('node', 'leaf')
        else:
            node = node.group().replace('node', 'APIC')
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,node,lc,descr))
    print('\n')
def detail_vcenter_reachable(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:18}{}".format('Time', 'Time Diff', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        if fault.get('faultInst'):
            timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            logger.debug('{} {}'.format(current_time,timestamp))
            diff_time = time_difference(current_time,timestamp[:-6])
            descr = fault['faultInst']['attributes']['descr']
            lc = fault['faultInst']['attributes']['lc']
        elif fault.get('faultDelegate'):
            timestamp = ' '.join(fault['faultDelegate']['attributes']['lastTransition'].split('T'))
            logger.debug('{} {}'.format(current_time,timestamp))
            diff_time = time_difference(current_time,timestamp[:-6])
            descr = fault['faultDelegate']['attributes']['descr']
            lc = fault['faultDelegate']['attributes']['lc']
        if len(descr) > 80:
            print("{:26}{:20}{:18}{}".format(timestamp[:-6],diff_time,lc,descr))
            print('\n')
        else:
            print("{:26}{:20}{:18}{}".format(timestamp[:-6],diff_time,lc,descr))
    print('\n')
def detail_phys_apic_port_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff', 'Device', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('Node', 'leaf')
        else:
            node = node.group().replace('Node', 'APIC')
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,node,lc,descr))
    print('\n')
def detail_port_channel_neighbor_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:18}{:28}{}".format('Time', 'Time Diff', 'State','Path','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        descr = ' '.join(descr.split())
        dn = fault['faultInst']['attributes']['dn']
        dn = dn[:dn.find('/aggrmbrif')].replace('topology/', '').replace('sys/','').replace('/phys-', '')
        #interface = re.search(r'pod-1.*\]agg', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:20}{:18}{:28}{}".format(timestamp[:-6],diff_time,lc, dn,descr))
    print('\n')
def detail_missing_psu_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:18}{:12}{:12}{}".format('Time', 'Time Diff', 'State','Device', 'PSU Slot', 'Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        node = re.search(r'node-[0-9]{1,3}', dn)
        psu = re.search(r'psuslot-[0-9]{1,3}', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:20}{:18}{:12}{:12}{}".format(timestamp[:-6],diff_time,lc,node.group(),psu.group(),descr))
    print('\n')
def detail_shutdown_psu_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:18}{:12}{:12}{}".format('Time', 'Time Diff', 'State','Device','PSU Slot','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        node = re.search(r'node-[0-9]{1,3}', dn)
        psu = re.search(r'psuslot-[0-9]{1,3}', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:20}{:18}{:12}{:12}{}".format(timestamp[:-6],diff_time,lc,node.group(),psu.group(),descr))
    print('\n')
def detail_failed_psu_faults(listdetail,apic=None):
    current_time = get_APIC_clock(apic,cookie)
    print('\r')
    print('Current Time = ' + current_time)
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff', 'Device', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        logger.debug('{} {}'.format(current_time,timestamp))
        diff_time = time_difference(current_time,timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('Node', 'leaf')
        else:
            node = node.group().replace('Node', 'APIC')
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,node,lc,descr))
    print('\n')
def retrievePortChannelName(apic, cookie, PoNum, leaf, que):
    #import pdb; pdb.set_trace()
    url = """https://{apic}/api/node/mo/topology/pod-1/node-{leaf}/sys/aggr-{PoNum}/rtaccBndlGrpToAggrIf.json""".format(apic=apic,leaf=leaf[5:].lstrip(),PoNum=PoNum)
    logger.info(url)
    result = GetResponseData(url, cookie)
    logger.debug(result)
    poresult = result[0][u"pcRtAccBndlGrpToAggrIf"][u"attributes"][u'tDn']
    poposition = result[0][u"pcRtAccBndlGrpToAggrIf"][u"attributes"][u'tDn'].rfind('accbundle-')
    poName = poresult[poposition+10:]
    que.put(poName)

def askrefresh(detail_function, is_function):
    while True:
        refresh = custom_raw_input("Would you like to refresh? [y/n]: ")
        if refresh.lower() == 'y' and refresh != '':
            result = is_function()
            if result == []:
                print("\nNo Faults Found (all faults are cleared)...\n")
                custom_raw_input("#Press enter to refresh fault list...")
                return 1
            else:
                detail_function(result[0]) 
        else:
            break
    clear_screen()
    return

        
def refreshloop(detail_function, fault, apic, cookie):
    refreshcount = 0      
    while True:
        if refreshcount == 5:
            cookie = refreshToken(apic, cookie)
            refreshcount = 0
        get_fault_results(apic, cookie, fault)
        detail_function(fault.results,apic)
        if fault.results == []:
            print("No Faults, all have been resolved...\n")
        ask = custom_raw_input('Would you like to refresh? [y=default|n]:  ') or 'y'
        if ask[0].lower() == 'y' and not ask == '':
            refreshcount +=1
            continue
        else:
            return


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    unauthenticated = False
    global current_time
    current_time = get_APIC_clock(apic,cookie)
    while True:
        clear_screen()
        ordered, objectdict = faultSummary(apic, cookie)
        displayfaultSummary(objectdict)
        faultselected = displayfaultSummaryandSelection(ordered)
        fault = get_fault_results(apic, cookie, faultselected)
        if fault.code == 'F1385': #OSPFrefreshloop                    
            refreshloop(detail_ospf_faults, fault, apic, cookie)
        elif fault.code == 'F1543': # Leaf/Spine Down
            refreshloop(detail_switch_availability_status_faults, fault, apic, cookie)
        elif fault.code == 'F1394': # Uplinks
            refreshloop(detail_leaf_spine_uplink_faults, fault, apic, cookie)
        elif fault.code == 'F0532': # Server ports
            refreshloop(detail_access_inter_faults, fault, apic, cookie)
        elif fault.code == 'F1296': # vPC full down
            refreshloop(detail_vpc_full_faults, fault, apic, cookie)
        elif fault.code == 'F2705': # vPC half down
            refreshloop(detail_vpc_part_faults, fault, apic, cookie)
        elif fault.code == 'F0600': # vPC connection issues
            refreshloop(detail_port_channel_neighbor_faults, fault, apic, cookie)
        elif fault.code == 'F1574': # NTP
            refreshloop(detail_ntp_faults, fault, apic, cookie)
        elif fault.code == 'F0130': # APIC can't reach VCENTER
            refreshloop(detail_vcenter_reachable, fault, apic, cookie)
        elif fault.code == 'F1262': # Database APIC
            refreshloop(detail_apic_replica_faults, fault, apic, cookie)
        elif fault.code == 'F0321': # Health APIC
            refreshloop(detail_apic_health_faults, fault, apic, cookie)
        elif fault.code == 'F0103': # apic interfaces
            refreshloop(detail_phys_apic_port_faults, fault, apic, cookie)
        elif fault.code == 'F0413': # missing psu
            refreshloop(detail_missing_psu_faults, fault, apic, cookie)
        elif fault.code == 'F1451': # shutdown psu
            refreshloop(detail_shutdown_psu_faults, fault, apic, cookie)
        elif fault.code == 'F1940': # failed psu
            refreshloop(detail_failed_psu_faults, fault, apic, cookie)
        cookie = refreshToken(apic, cookie)
