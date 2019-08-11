#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def faultSummary():
    url = """https://localhost/api/node/class/faultSummary.json?query-target-filter=and(not(wcard(faultSummary.dn,%22__ui_%22)),and())""" + \
          """&order-by=faultSummary.severity|desc&page=0&page-size=100"""
    result, totalcount = GetResponseData(url)
    faultSummarydict = {}
    for fault in result:
        faultSummarydict[fault['faultSummary']['attributes']['code']]=fault['faultSummary']['attributes']['count']
    for fault in faultSummarydict:
        if fault == 'F1385':
            print('ospf {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F0532':
            print('leaf/spine uplink {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F1543':
            print('leaf/spine down {}'.format(faultSummarydict[fault]))
        elif fault == 'F1296':
            print('found vpc down ' + 'count = ' + faultSummarydict[fault])
    #result[]
    print(faultSummarydict)


def OSPF_fault_check():
    #F1385
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1385')
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking OSPF peer issues"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking OSPF peer issues",totalcount))
        result[0]['fault-type']='OSPF peer issues'
        return [result]
def is_Leaf_Spine_Down():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1543')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking if Leaf/Spine(s) are Down"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking if Leaf/Spine(s) are Down",totalcount))
        result[0]['fault-type']='Leaf/Spine(s) are Down'
        return [result]
def is_Leaf_interface_Down():
    #F0532
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F0532')
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking for Server ports Down"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking for Server ports Down",totalcount))
        result[0]['fault-type']='Server ports Down'
        return [result]
def is_Leaf_uplink_Down():
    #F1394
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1394')
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking if Leaf uplinks are Down"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking if Leaf uplinks are Down",totalcount))
        result[0]['fault-type']='Switch UPLINK'
        return [result]
def is_VPC_interface_fully_down():
    #F1296
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1296')
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking for vPC Fully Down "))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking for vPC Fully Down",totalcount))
        result[0]['fault-type']='vPC Fully Down'
        return [result]
def is_VPC_paritally_down():
    #F2705
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F2705')
    #print(url)
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking for vPC Half Down"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking for vPC Half Down",totalcount))
        result[0]['fault-type']='VPC Partialty DOWN'
        return [result]
def APIC_replica_issues():
    #F1262
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1262')
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking for Database issues on APIC"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking for Database issues on APIC",totalcount))
        result[0]['fault-type']='APIC Database Replication'
        return [result]
def APIC_Health_issues():
    #F0321
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F0321')
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking for APIC Health issues"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking for APIC Health issues",totalcount))
        result[0]['fault-type']='APIC HEALTH'
        return [result]

##########
def is_APIC_physical_ports_down():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F0103')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking APIC Physical Port issues"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking APIC Physical Port issues",totalcount))
        result[0]['fault-type']='APIC Phys Port issues'
        return [result]
def is_NTP_issues():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1574')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking NTP issues"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking NTP issues",totalcount))
        result[0]['fault-type']='NTP issues'
        return [result]
def is_Port_Channel_Neighbor_fail():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F0600')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking for vPC/PC Connection issues"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking for vPC/PC Connection issues",totalcount))
        result[0]['fault-type']='vPC/PC Connection issues'
        return [result]
def is_Missing_PowerSupply():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F0413')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking Missing Power Supply"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking Missing Power Supply",totalcount))
        result[0]['fault-type']='Missing Power Supply'
        return [result]
def is_PowerSupply_shutdown():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1451')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking Unused/Shutdown Power Supply"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking Unused/Shutdown Power Supply",totalcount))
        result[0]['fault-type']='Unused/Shutdown Power Supply'
        return [result]
def is_PowerSupply_failure():
    url = """https://localhost/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + \
          """eq(faultInfo.code,"{}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""".format('F1940')
    result, totalcount = GetResponseData(url)
    #F1543
    if totalcount == '0':
        print("\t{:.<45}None".format("Checking Failed Power Supply"))
        return []
    else:
        print("\t{:.<45}Found {} faults".format("Checking Failed Power Supply",totalcount))
        result[0]['fault-type']='Failed Power Supply'
        return [result]



def detail_ospf_faults(listdetail):
    print('\n')
    print("{:26}{:12}{:18}{}".format('Time','Leaf', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]{0,3}', fault['faultInst']['attributes']['dn'])
        print("{:26}{:12}{:18}{}".format(timestamp[:-6],controller.group(), lc,descr))
    print('\n')
def detail_switch_availability_status_faults(listdetail):
    print('\n')
    print("{:26}{:12}{:18}{}".format('Time','Leaf', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        device = re.search(r'[nN]ode [0-9]{1,3}', descr).group()
        print("{:26}{:12}{:18}{}".format(timestamp[:-6],device, lc,descr))
    print('\n')

def detail_access_inter_faults(listdetail):
    print('\n{:26}{:10}{:15}{:18}{:18}{}'.format('Time','Switch','Interface','Port-Channel', 'State', 'Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
        leaf = re.search(r'leaf[0-9]{3}', fault['faultInst']['attributes']['descr'])
        lc = fault['faultInst']['attributes']['lc']
        description = ' '.join(fault['faultInst']['attributes']['descr'].split())
        #print(description_short)
        usedlocation =  description.find('used')
        description_final = description[:usedlocation - 2] 
        if 'po' in interface.group():
            poName = retrievePortChannelName(interface.group(), leaf.group())
            print('{:26}{:10}{:15}{:18}{:18}{}'.format(timestamp[:-6], leaf.group(), interface.group(), poName, lc, description_final))
        else:
            print('{:26}{:10}{:15}{:18}{:18}{}'.format(timestamp[:-6], leaf.group(), interface.group(), '', lc,  description_final))
    print('\n')
def detail_leaf_spine_uplink_faults(listdetail):
    print('\n')
    print("{:26}{:12}{:12}{:18}{}".format('Time','Leaf','Interface', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]{0,3}', fault['faultInst']['attributes']['dn'])
        interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
        print("{:26}{:12}{:12}{:18}{}".format(timestamp[:-6],controller.group(), interface.group(), lc,descr))
    print('\n')
def detail_vpc_full_faults(listdetail):
    print('\n{:26}{:10}{:15}{:18}{:18}{}'.format('Time','Switch','Interface','Port-Channel', 'State', 'Description'))
    print('-'*90)
    for fault in listdetail:
        if fault.get('faultInst'):
            timestamp = fault['faultInst']['attributes']['lastTransition']
            descr = fault['faultInst']['attributes']['descr']
            #interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
            #leaf = re.search(r'leaf[0-9]{3}', fault['faultInst']['attributes']['descr'])
            lc = fault['faultInst']['attributes']['lc']
            print('{:26}{:10}{:18}{}'.format(timestamp[:-6], '', lc, descr))
    print('\n')
def detail_vpc_part_faults(listdetail):
    print("\n{:26}{:15}{:18}{}".format('Time','Leaf', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        if fault.get('faultInst'):
            dn = fault['faultInst']['attributes']['dn'] 
            dn = dn.split('/')[2]
            descr = fault['faultInst']['attributes']['descr']   
            changeSet = fault['faultInst']['attributes']['changeSet']
            timestamp = fault['faultInst']['attributes']['lastTransition']
            lc = fault['faultInst']['attributes']['lc']
            print("{:26}{:15}{:18}{:18}{}".format(timestamp[:23],dn,lc,descr,'changeSet: ' + changeSet))
    print('\n')
def detail_apic_replica_faults(listdetail):
    print("{:26}{:12}{:18}{}".format('Time','Controller', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'controller [0-9]', fault['faultInst']['attributes']['descr'])
        print("{:26}{:12}{:18}{}".format(timestamp[:-6],controller.group()[-1],lc,descr))
    print('\n')
def detail_apic_health_faults(listdetail):
    print("{:26}{:12}{:18}{}".format('Time','Controller', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]', fault['faultInst']['attributes']['dn'])
        print("{:26}{:^12}{:18}{}".format(timestamp[:-6],controller.group()[-1],lc,descr))
    print('\n')
def detail_ntp_faults(listdetail):
    print("{:26}{:12}{:18}{}".format('Time', 'Device', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('node', 'leaf')
        else:
            node = node.group().replace('node', 'APIC')
        print("{:26}{:12}{:18}{}".format(timestamp[:-6],node,lc,descr))
    print('\n')
def detail_phys_apic_port_faults(listdetail):
    print("{:26}{:12}{:18}{}".format('Time', 'Device', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('Node', 'leaf')
        else:
            node = node.group().replace('Node', 'APIC')
        print("{:26}{:12}{:18}{}".format(timestamp[:-6],node,lc,descr))
    print('\n')
def detail_port_channel_neighbor_faults(listdetail):
    print("{:26}{:25}{:18}{}".format('Time','Description', 'State','Path'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        #interface = re.search(r'pod-1.*\]agg', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:25}{:18}{}".format(timestamp[:-6],lc,descr, dn))
    print('\n')
def detail_missing_psu_faults(listdetail):
    print("{:26}{:18}{:12}{:12}{}".format('Time', 'State','Device', 'PSU Slot', 'Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        node = re.search(r'node-[0-9]{1,3}', dn)
        psu = re.search(r'psuslot-[0-9]{1,3}', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:18}{:12}{:12}{}".format(timestamp[:-6],lc,node.group(),psu.group(),descr))
    print('\n')
def detail_shutdown_psu_faults(listdetail):
    print("{:26}{:18}{:12}{:12}{}".format('Time', 'State','Device','PSU Slot','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        node = re.search(r'node-[0-9]{1,3}', dn)
        psu = re.search(r'psuslot-[0-9]{1,3}', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:18}{:12}{:12}{}".format(timestamp[:-6],lc,node.group(),psu.group(),descr))
    print('\n')
def detail_failed_psu_faults(listdetail):
    print("{:26}{:12}{:18}{}".format('Time', 'Device', 'State','Description'))
    print('-'*90)
    for fault in listdetail:
        timestamp = fault['faultInst']['attributes']['lastTransition']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('Node', 'leaf')
        else:
            node = node.group().replace('Node', 'APIC')
        print("{:26}{:12}{:18}{}".format(timestamp[:-6],node,lc,descr))
    print('\n')


def retrievePortChannelName(PoNum, leaf):
    url = """https://localhost/api/node/mo/topology/pod-1/node-{leaf}/sys/aggr-{PoNum}/rtaccBndlGrpToAggrIf.json""".format(leaf=leaf[4:],PoNum=PoNum)
    result = GetResponseData(url)
    poresult = result[0][0][u"pcRtAccBndlGrpToAggrIf"][u"attributes"][u'tDn']
    poposition = result[0][0][u"pcRtAccBndlGrpToAggrIf"][u"attributes"][u'tDn'].rfind('accbundle-')
    poName = poresult[poposition+10:]
    return poName

def getCookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()


def askrefresh(detail_function, is_function):
    while True:
        refresh = raw_input("Would you like to refresh? [y/n]: ")
        if refresh.lower() == 'y' and refresh != '':
            result = is_function()
            if result == []:
                print("\nNo Faults Found (all faults are cleared)...\n")
                raw_input("#Press enter to refresh fault list...")
                return 1
            else:
                detail_function(result[0]) 
        else:
            break
            
    os.system('clear')
    #print('\n')
    return
    


def askmoreDetail():
    while True:
        listdetail = collecting_all_faults()
        #answer = raw_input("Would you like more details? (y/n): ")
        #if answer.lower() == 'y':        
        faultdict = {}
        #availablefaultstringlist = ""

        for num,fault in enumerate(listdetail,0):
            print('\t{}.) {}'.format(num+1,fault[0]['fault-type']))
            #availablefaultstringlist += '\t{}.) {}\n'.format(num,fault[0]['fault-type'])
            faultdict[num+1]=fault
        faultdict[len(listdetail)+1]='exit'
        print('\t{}.) Exit'.format(str(len(listdetail)+1)))
        
        print('\t')
        while True:
            userselected = raw_input("Which fault?: ")
            if userselected.isdigit():
                userselected = int(userselected) 
                break
        if faultdict[userselected] == 'exit':
            exit()
        elif faultdict[userselected][0]['fault-type'] == 'OSPF peer issues':
            detail_ospf_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_ospf_faults, OSPF_fault_check)#[0] )
        elif faultdict[userselected][0]['fault-type'] == 'Leaf/Spine(s) are Down':
            detail_switch_availability_status_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_switch_availability_status_faults, is_Leaf_Spine_Down)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'Server ports Down':
            detail_access_inter_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_access_inter_faults, is_Leaf_interface_Down)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'Switch UPLINK':
            detail_leaf_spine_uplink_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_leaf_spine_uplink_faults, is_Leaf_uplink_Down)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'vPC Fully Down':
            detail_vpc_full_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_vpc_full_faults, is_VPC_interface_fully_down)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'VPC Partialty DOWN':
            detail_vpc_part_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_vpc_part_faults, is_VPC_paritally_down)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'APIC Database Replication':
            detail_apic_replica_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_apic_replica_faults, APIC_replica_issues)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'APIC HEALTH':
            detail_apic_health_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_apic_health_faults, APIC_Health_issues)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'APIC Phys Port issues':
            detail_phys_apic_port_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_phys_apic_port_faults, is_APIC_physical_ports_down)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'NTP issues':
            detail_ntp_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_ntp_faults, is_NTP_issues)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'vPC/PC Connection issues':
            detail_port_channel_neighbor_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_port_channel_neighbor_faults, is_Port_Channel_Neighbor_fail)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'Missing Power Supply':
            detail_missing_psu_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_missing_psu_faults, is_Missing_PowerSupply)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'Unused/Shutdown Power Supply':
            detail_shutdown_psu_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_shutdown_psu_faults, is_PowerSupply_shutdown)#[0])
        elif faultdict[userselected][0]['fault-type'] == 'Failed Power Supply':
            detail_failed_psu_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_failed_psu_faults, is_PowerSupply_failure)#[0])

        os.system('clear')
        print('\n')
        if complete_refresh == 1:
            return True
        #if answer.lower() == 'n':
        #    exitquestion = raw_input("\nWould you like to exit? [y/n]:  ")
        #    if exitquestion.lower() == 'y':
        #        exit()
        #    else:
        #        break

        
def collecting_all_faults():
    print('\n' + '-'*80 + '\n')
    print('Fabric:')
    ospfd = OSPF_fault_check()
    lsdownd = is_Leaf_Spine_Down()
    uplinkd = is_Leaf_uplink_Down()
    intdownd = is_Leaf_interface_Down()
    vpcdownd = is_VPC_interface_fully_down()
    vpcpartd = is_VPC_paritally_down()
    PoNeighbord = is_Port_Channel_Neighbor_fail()
    ntpd = is_NTP_issues()
    print('APIC: ')
    apicrepd = APIC_replica_issues()
    apichealthd = APIC_Health_issues()
    physapicportd = is_APIC_physical_ports_down()
    print('Power:')
    missingpsud = is_Missing_PowerSupply()
    shutdownpsud = is_PowerSupply_shutdown()
    failurepsud = is_PowerSupply_failure()
    print('\n' + '-'*80 + '\n')
    return ospfd + lsdownd +  uplinkd + intdownd  + vpcdownd + vpcpartd + PoNeighbord + ntpd +  apicrepd + apichealthd + physapicportd + missingpsud + shutdownpsud + failurepsud

def Main():
    unauthenticated = False
    while True:
        try:
            getCookie()
            faultSummary()
            if unauthenticated:
                #os.system('clear')
                print('Authentication Token timed out...restarting program')
            else:
                pass
                #os.system('clear')
            unauthenticated = False
            
            ##print('\n' + '-'*80 + '\n')
            ##print('Fabric:')
            ##ospfd = OSPF_fault_check()
            ##lsdownd = is_Leaf_Spine_Down()
            ##uplinkd = is_Leaf_uplink_Down()
            ##intdownd = is_Leaf_interface_Down()
            ##vpcdownd = is_VPC_interface_fully_down()
            ##vpcpartd = is_VPC_paritally_down()
            ##PoNeighbord = is_Port_Channel_Neighbor_fail()
            ##ntpd = is_NTP_issues()
            ##print('APIC: ')
            ##apicrepd = APIC_replica_issues()
            ##apichealthd = APIC_Health_issues()
            ##physapicportd = is_APIC_physical_ports_down()
            ##print('Power:')
            ##missingpsud = is_Missing_PowerSupply()
            ##shutdownpsud = is_PowerSupply_shutdown()
            ##failurepsud = is_PowerSupply_failure()
            ##print('\n' + '-'*80 + '\n')
            ##listdetail = ospfd + lsdownd +  uplinkd + intdownd  + vpcdownd + vpcpartd + PoNeighbord + ntpd +  apicrepd + apichealthd + physapicportd + missingpsud + shutdownpsud + failurepsud
            #print('debug1: ', len(unfilteredlist))
            #listdetail = list(filter(None, unfilteredlist)) 
            #print('debug2: ', listdetail)
            askmoreDetail()
            #if complete_refresh == True:
            #    continue
            #break
            #else:
            #    continue
            

        except urllib2.HTTPError as e:
            unauthenticated = True
            pass



Main()
