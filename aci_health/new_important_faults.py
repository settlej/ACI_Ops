#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os
import datetime

def getToken(host):
    ssl._create_default_https_context = ssl._create_unverified_context
    user = 'admin'
    pwd = 'ciscopsdt'
    url = "https://{host}/api/aaaLogin.json".format(host=host)
    payload = '{"aaaUser":{"attributes":{"name":"%(user)s","pwd":"%(pwd)s"}}}' % {"pwd":pwd,"user":user}
    request = urllib2.Request(url, data=payload)
    response = urllib2.urlopen(request)
    token = json.loads(response.read())
    global cookie
    cookie = token["imdata"][0]["aaaLogin"]["attributes"]["token"]
    return cookie


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

def displaycurrenttime():
    currenttime = datetime.datetime.now()
    return str(currenttime)[:-3]

def time_difference(fault_time):
    currenttime = datetime.datetime.now()
    ref_fault_time = datetime.datetime.strptime(fault_time, '%Y-%m-%d %H:%M:%S.%f')
    return str(currenttime - ref_fault_time)[:-7]

def faultSummary(host, cookie):
    url = ("""https://{host}/api/node/class/faultSummary.json?query-target-filter=and(not(wcard(faultSummary.dn,%22__ui_%22)),and())""" + \
          """&order-by=faultSummary.severity|desc&page=0&page-size=100""").format(host=host)
    print(url)
    result, totalcount = GetResponseData(url)
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

    print('\t{}.) Exit'.format(str(len(orderedlist)+1)))
    orderedlist.append('Exit')
    print('\n')
    selected = raw_input('Which fault?:  ')
    faultselected = (orderedlist[int(selected)-1])
    if faultselected is orderedlist[-1]:
        print('Exiting program...\n')
        exit()
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

def get_fault_results(host, cookie, code):
    url = ("""https://{host}/api/node/class/faultInfo.json?query-target-filter=and(ne(faultInfo.severity,"cleared"),""" + 
          """eq(faultInfo.code,"{code}"))&order-by=faultInfo.lastTransition|Desc&page=0&order-by=faultInfo.lastTransition|Desc&page-size=100""").format(host=host,code=code.code)
    result, totalcount = GetResponseData(url)
    code.results = result
    code.amount = totalcount
    return code


def detail_ospf_faults(listdetail,host):
    print('\n')
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Leaf', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        lc = fault['faultInst']['attributes']['lc']
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]{0,3}', fault['faultInst']['attributes']['dn'])
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,controller.group(), lc,descr))
    print('\n')
def detail_switch_availability_status_faults(listdetail,host):
    print('\n')
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Leaf', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        device = re.search(r'[nN]ode [0-9]{1,3}', descr).group()
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,device, lc,descr))
    print('\n')
def detail_access_inter_faults(listdetail, host):
    print('\n{:26}{:20}{:10}{:15}{:18}{:18}{}'.format('Time', 'Time Diff','Switch','Interface','Port-Channel', 'State', 'Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
        leaf = re.search(r'leaf[0-9]{3}', fault['faultInst']['attributes']['descr'])
        lc = fault['faultInst']['attributes']['lc']
        description = ' '.join(fault['faultInst']['attributes']['descr'].split())
        #print(description_short)
        usedlocation =  description.find('used')
        description_final = description[:usedlocation - 2] 
        if 'po' in interface.group():
            poName = retrievePortChannelName(host, interface.group(), leaf.group())
            print('{:26}{:20}{:10}{:15}{:18}{:18}{}'.format(timestamp[:-6],diff_time, leaf.group(), interface.group(), poName, lc, description_final))
        else:
            print('{:26}{:20}{:10}{:15}{:18}{:18}{}'.format(timestamp[:-6],diff_time, leaf.group(), interface.group(), '', lc,  description_final))
    print('\n')
def detail_leaf_spine_uplink_faults(listdetail,host):
    print('\n')
    print("{:26}{:20}{:12}{:12}{:18}{}".format('Time', 'Time Diff','Leaf','Interface', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]{0,3}', fault['faultInst']['attributes']['dn'])
        interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
        print("{:26}{:20}{:12}{:12}{:18}{}".format(timestamp[:-6],diff_time,controller.group(), interface.group(), lc,descr))
    print('\n')
def detail_vpc_full_faults(listdetail,host):
    print('\n{:26}{:20}{:10}{:15}{:18}{:18}{}'.format('Time', 'Time Diff','Switch','Interface','Port-Channel', 'State', 'Description'))
    print('-'*120)
    for fault in listdetail:
        if fault.get('faultInst'):
            timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            diff_time = time_difference(timestamp[:-6])
            descr = fault['faultInst']['attributes']['descr']
            #interface = re.search(r'\[.*\]', fault['faultInst']['attributes']['dn'])
            #leaf = re.search(r'leaf[0-9]{3}', fault['faultInst']['attributes']['descr'])
            lc = fault['faultInst']['attributes']['lc']
            print('{:26}{:20}{:10}{:18}{}'.format(timestamp[:-6],diff_time, '', lc, descr))
    print('\n')
def detail_vpc_part_faults(listdetail,host):
    print("\n{:26}{:20}{:15}{:18}{}".format('Time', 'Time Diff','Leaf', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        if fault.get('faultInst'):
            dn = fault['faultInst']['attributes']['dn'] 
            dn = dn.split('/')[2]
            descr = fault['faultInst']['attributes']['descr']   
            changeSet = fault['faultInst']['attributes']['changeSet']
            timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            diff_time = time_difference(timestamp[:-6])
            lc = fault['faultInst']['attributes']['lc']
            print("{:26}{:20}{:15}{:18}{:18}{}".format(timestamp[:23],dn,lc,descr,'changeSet: ' + changeSet))
    print('\n')
def detail_apic_replica_faults(listdetail,host):
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Controller', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'controller [0-9]', fault['faultInst']['attributes']['descr'])
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,controller.group()[-1],lc,descr))
    print('\n')
def detail_apic_health_faults(listdetail,host):
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff','Controller', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        controller = re.search(r'[nN]ode-[0-9]', fault['faultInst']['attributes']['dn'])
        print("{:26}{:20}{:^12}{:18}{}".format(timestamp[:-6],diff_time,controller.group()[-1],lc,descr))
    print('\n')
def detail_ntp_faults(listdetail,host):
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff', 'Device', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('node', 'leaf')
        else:
            node = node.group().replace('node', 'APIC')
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,node,lc,descr))
    print('\n')
def detail_vcenter_reachable(listdetail,host):
    print("{:26}{:20}{:18}{}".format('Time', 'Time Diff', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        if fault.get('faultInst'):
            timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
            diff_time = time_difference(timestamp[:-6])
            descr = fault['faultInst']['attributes']['descr']
            lc = fault['faultInst']['attributes']['lc']
        elif fault.get('faultDelegate'):
            timestamp = ' '.join(fault['faultDelegate']['attributes']['lastTransition'].split('T'))
            diff_time = time_difference(timestamp[:-6])
            descr = fault['faultDelegate']['attributes']['descr']
            lc = fault['faultDelegate']['attributes']['lc']
        if len(descr) > 80:
            print("{:26}{:20}{:18}{}".format(timestamp[:-6],diff_time,lc,descr))
            print('\n')
        else:
            print("{:26}{:20}{:18}{}".format(timestamp[:-6],diff_time,lc,descr))

    print('\n')
def detail_phys_apic_port_faults(listdetail,host):
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff', 'Device', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('Node', 'leaf')
        else:
            node = node.group().replace('Node', 'APIC')
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,node,lc,descr))
    print('\n')
def detail_port_channel_neighbor_faults(listdetail,host):
    print("{:26}{:20}{:25}{:18}{}".format('Time', 'Time Diff','Description', 'State','Path'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        #interface = re.search(r'pod-1.*\]agg', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:20}{:25}{:18}{}".format(timestamp[:-6],diff_time,lc,descr, dn))
    print('\n')
def detail_missing_psu_faults(listdetail,host):
    print("{:26}{:20}{:18}{:12}{:12}{}".format('Time', 'Time Diff', 'State','Device', 'PSU Slot', 'Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        node = re.search(r'node-[0-9]{1,3}', dn)
        psu = re.search(r'psuslot-[0-9]{1,3}', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:20}{:18}{:12}{:12}{}".format(timestamp[:-6],diff_time,lc,node.group(),psu.group(),descr))
    print('\n')
def detail_shutdown_psu_faults(listdetail,host):
    print("{:26}{:20}{:18}{:12}{:12}{}".format('Time', 'Time Diff', 'State','Device','PSU Slot','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        dn = fault['faultInst']['attributes']['dn']
        node = re.search(r'node-[0-9]{1,3}', dn)
        psu = re.search(r'psuslot-[0-9]{1,3}', dn)
        lc = fault['faultInst']['attributes']['lc']
        print("{:26}{:20}{:18}{:12}{:12}{}".format(timestamp[:-6],diff_time,lc,node.group(),psu.group(),descr))
    print('\n')
def detail_failed_psu_faults(listdetail,host):
    print("{:26}{:20}{:12}{:18}{}".format('Time', 'Time Diff', 'Device', 'State','Description'))
    print('-'*120)
    for fault in listdetail:
        timestamp = ' '.join(fault['faultInst']['attributes']['lastTransition'].split('T'))
        diff_time = time_difference(timestamp[:-6])
        descr = fault['faultInst']['attributes']['descr']
        lc = fault['faultInst']['attributes']['lc']
        node = re.search(r'[nN]ode [0-9]{1,3}', descr)
        if len(node.group()) == 8:
            node = node.group().replace('Node', 'leaf')
        else:
            node = node.group().replace('Node', 'APIC')
        print("{:26}{:20}{:12}{:18}{}".format(timestamp[:-6],diff_time,node,lc,descr))
    print('\n')

def retrievePortChannelName(host, PoNum, leaf):
    url = """https://{host}/api/node/mo/topology/pod-1/node-{leaf}/sys/aggr-{PoNum}/rtaccBndlGrpToAggrIf.json""".format(host=host,leaf=leaf[4:],PoNum=PoNum)
    result = GetResponseData(url)
    poresult = result[0][0][u"pcRtAccBndlGrpToAggrIf"][u"attributes"][u'tDn']
    poposition = result[0][0][u"pcRtAccBndlGrpToAggrIf"][u"attributes"][u'tDn'].rfind('accbundle-')
    poName = poresult[poposition+10:]
    return poName

def getCookie():
    with open('/.aci/.sessions/.token', 'r') as f:
        global cookie
        cookie = f.read()
        return cookie


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
    



def askmoreDetail(host):
    while True:
        listdetail = []
        faultdict = {}
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
            complete_refresh = askrefresh(detail_ospf_faults, OSPF_fault_check)
        elif faultdict[userselected][0]['fault-type'] == 'Leaf/Spine(s) are Down':
            detail_switch_availability_status_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_switch_availability_status_faults, is_Leaf_Spine_Down)
        elif faultdict[userselected][0]['fault-type'] == 'Server ports Down':
            detail_access_inter_faults(faultdict[userselected],host)
            complete_refresh = askrefresh(detail_access_inter_faults, is_Leaf_interface_Down)
        elif faultdict[userselected][0]['fault-type'] == 'Switch UPLINK':
            detail_leaf_spine_uplink_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_leaf_spine_uplink_faults, is_Leaf_uplink_Down)
        elif faultdict[userselected][0]['fault-type'] == 'vPC Fully Down':
            detail_vpc_full_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_vpc_full_faults, is_VPC_interface_fully_down)
        elif faultdict[userselected][0]['fault-type'] == 'VPC Partialty DOWN':
            detail_vpc_part_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_vpc_part_faults, is_VPC_paritally_down)
        elif faultdict[userselected][0]['fault-type'] == 'APIC Database Replication':
            detail_apic_replica_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_apic_replica_faults, APIC_replica_issues)
        elif faultdict[userselected][0]['fault-type'] == 'APIC HEALTH':
            detail_apic_health_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_apic_health_faults, APIC_Health_issues)
        elif faultdict[userselected][0]['fault-type'] == 'APIC Phys Port issues':
            detail_phys_apic_port_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_phys_apic_port_faults, is_APIC_physical_ports_down)
        elif faultdict[userselected][0]['fault-type'] == 'NTP issues':
            detail_ntp_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_ntp_faults, is_NTP_issues)
        elif faultdict[userselected][0]['fault-type'] == "APIC can't reach VCenter":
            detail_vcenter_reachable(faultdict[userselected])
            complete_refresh = askrefresh(detail_vcenter_reachable, is_VCENTER_reachable)
        elif faultdict[userselected][0]['fault-type'] == 'vPC/PC Connection issues':
            detail_port_channel_neighbor_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_port_channel_neighbor_faults, is_Port_Channel_Neighbor_fail)
        elif faultdict[userselected][0]['fault-type'] == 'Missing Power Supply':
            detail_missing_psu_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_missing_psu_faults, is_Missing_PowerSupply)
        elif faultdict[userselected][0]['fault-type'] == 'Unused/Shutdown Power Supply':
            detail_shutdown_psu_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_shutdown_psu_faults, is_PowerSupply_shutdown)
        elif faultdict[userselected][0]['fault-type'] == 'Failed Power Supply':
            detail_failed_psu_faults(faultdict[userselected])
            complete_refresh = askrefresh(detail_failed_psu_faults, is_PowerSupply_failure)

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

        
def refreshloop(detail_function, fault, host, cookie):
    print('\r')
    print('Current Time = ' + displaycurrenttime())            
    while True:
        get_fault_results(host, cookie, fault)
        detail_function(fault.results,host)
        if fault.results == []:
            print("No Faults, all have been resolved...\n")
        ask = raw_input('Would you like to refresh? [y|n]:  ')
        if ask[0].lower() == 'y' and not ask == '':
            print('\r')
            print('Current Time = ' + displaycurrenttime())            

            continue
        else:
            return


def localOrRemote():
    if os.path.isfile('a/.aci/.sessions/.token'):
        host = "localhost"
        cookie = getCookie(host)
        return host, cookie
    else:
        host = raw_input("Enter IP address or FQDN of APIC: ")
        cookie = getToken(host)
        return host, cookie


def main():
    unauthenticated = False
    host, cookie = localOrRemote()

    while True:
        try:
            if unauthenticated:
                os.system('clear')
                print('Authentication Token timed out...restarting program')
            else:
                os.system('clear')
            unauthenticated = False
            ordered, objectdict = faultSummary(host, cookie)
            displayfaultSummary(objectdict)
            faultselected = displayfaultSummaryandSelection(ordered)
            fault = get_fault_results(host, cookie, faultselected)
            if fault.code == 'F1385': #OSPFrefreshloop                    
                refreshloop(detail_ospf_faults, fault, host, cookie)
            elif fault.code == 'F1543': # Leaf/Spine Down
                refreshloop(detail_switch_availability_status_faults, fault, host, cookie)
            elif fault.code == 'F1394': # Uplinks
                refreshloop(detail_leaf_spine_uplink_faults, fault, host, cookie)
            elif fault.code == 'F0532': # Server ports
                refreshloop(detail_access_inter_faults, fault, host, cookie)
            elif fault.code == 'F1296': # vPC full down
                refreshloop(detail_vpc_full_faults, fault, host, cookie)
            elif fault.code == 'F2705': # vPC half down
                refreshloop(detail_vpc_part_faults, fault, host, cookie)
            elif fault.code == 'F0600': # vPC connection issues
                refreshloop(detail_port_channel_neighbor_faults, fault, host, cookie)
            elif fault.code == 'F1574': # NTP
                refreshloop(detail_ntp_faults, fault, host, cookie)
            elif fault.code == 'F0130': # APIC can't reach VCENTER
                refreshloop(detail_vcenter_reachable, fault, host, cookie)
            elif fault.code == 'F1262': # Database APIC
                refreshloop(detail_apic_replica_faults, fault, host, cookie)
            elif fault.code == 'F0321': # H:ealth APIC
                refreshloop(detail_apic_health_faults, fault, host, cookie)
            elif fault.code == 'F0103': # apic interfaces
                refreshloop(detail_phys_apic_port_faults, fault, host, cookie)
            elif fault.code == 'F0413': # missing psu
                refreshloop(detail_missing_psu_faults, fault, host, cookie)
            elif fault.code == 'F1451': # shutdown psu
                refreshloop(detail_shutdown_psu_faults, fault, host, cookie)
            elif fault.code == 'F1940': # failed psu
                refreshloop(detail_failed_psu_faults, fault, host, cookie)

            
        except urllib2.HTTPError as e:
            unauthenticated = True
            pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
    
