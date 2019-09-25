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
import os
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
c_handler.setLevel(logging.WARNING)
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

# custom data class to contain all layers relating to endpoint json representation
# as well as parsed and easy callable feilds based on names. 
class fvCEp():
    def __init__(self, mac=None, name=None, encap=None,
                 lcC=None, dn=None, fvRsVm=None, fvRsHyper=None,
                 fvRsCEpToPathEp=None, ip=None, fvIplist=[]):
        self.mac = mac
        self.name = name
        self.encap = encap
        self.dn = dn
        self.epg = ('|'.join(self.dn.split('/')[1:-1])).replace('tn-', '').replace('ap-', '').replace('epg-', '')
        self.lcC = lcC
        self.fvRsVm = fvRsVm
        self.fvRsHyper = fvRsHyper
        self.ip = ip
        #self.iplist = iplist
        self.fvIplist = fvIplist
        self.fvRsCEpToPathEp = fvRsCEpToPathEp
    def __repr__(self):
        return self.dn
    def __getitem__(self, mac):
        if mac in self.mac:
            return self.mac
        else:
            return None
    def showips(self):
        iplist = [fvIP.addr for fvIP in self.fvIplist]
        return ', '.join(iplist)


class fvIp():
    def __init__(self, addr=None, rn=None,fvReportingNodes=None):
        self.addr = addr
        self.rn = rn
        self.fvReportingNodes = fvReportingNodes
    def __repr__(self):
        return self.addr
    def __getitem__(self, addr):
        if addr in self.addr:
            return self.addr
        else:
            return None

class fvRsCEpToPathEp():
    def __init__(self, tDn=None, lcC=None, fvReportingNodes=[], forceResolve=None):
        self.lcC = lcC #shows location it learned if 'vmm' vmm knows it cause vmware, 'vmm,learned' means vmware and switch knows, if just 'learned' not vmm source 
        self.tDn = tDn # location of learned interface "topology/pod-1/paths-102/extpaths-112/pathep-[eth1/25]" example
        self.fvReportingNodes = fvReportingNodes # looks like port-channels use fvReportingNode api class (describes leafs where ep is discovered)
        self.forceResolve = forceResolve
    def __repr__(self):
        return self.tDn

class fvRsVm():
    def __init__(self, state=None, tDn=None, dn=None):
        self.state = state
        self.dn = dn
        self.tDn = tDn #internal vm name to lookup vmware vm name
    def __repr__(self):
        return self.tDn

class fvRsHyper():
    def __init__(self, state=None, tDn=None):
        self.state = state
        self.tDn = tDn  #hyperviser internal name to look up vmware host name
    def __repr__(self):
        return self.tDn



#>>>>>>compVm is for every vm known by vcenter not just VMs using vmware intergration resources


class compVm():
    def __init__(self, state=None, dn=None, name=None, guid=None, host_rn_reference=None, compVNiclist=[]):
        self.state = state
        self.dn = dn
        self.name = name
        self.guid = guid
        self.compVNiclist = compVNiclist
        self.host_rn_reference = host_rn_reference
        #self.tDn = tDn #internal vm name to lookup vmware vm name
    def __repr__(self):
        return self.dn


class compVNic():
    def __init__(self, operSt=None, name=None, ip=None, mac=None, adapterType=None, compRsDlPol=None, compEpPConn=None):
        self.operSt = operSt
        self.name = name
        self.ip = ip
        self.mac = mac
       # self.fvRsVmobject = fvRsVmobject
        self.adapterType = adapterType
        self.compRsDlPol = compRsDlPol
        self.compEpPConn = compEpPConn
        #self.tDn = tDn #internal vm name to lookup vmware vm name
    def __repr__(self):
        return self.name

class compRsDlPol():
    def __init__(self, tDn=None):
        self.tDn = tDn
    def __repr__(self):
        return self.tDn

class compEpPConn():
    def __init__(self, epgPKey=None, encap=None, hostDn=None, portDn=None):
        self.epgPKey = epgPKey
        self.encap = encap
        self.hostDn = hostDn
        self.portDn = portDn
        #self.tDn = tDn #internal vm name to lookup vmware vm name
    def __repr__(self):
        return self.epgPKey

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

def gather_fvCEp_fullinfo(result):
    eplist = []
    fvRsVmobject = None
    fvRsCEpToPathEpobject = None
    fvRsHyperobject = None
    fvIplist = []
    fvRsCEpToPathEplist = []
    for ep in result:
        fvReportingNodes = []
        mac = ep['fvCEp']['attributes']['mac']
        name = ep['fvCEp']['attributes']['name']
        encap = ep['fvCEp']['attributes']['encap']
        lcC = ep['fvCEp']['attributes']['lcC']
        dn = ep['fvCEp']['attributes']['dn']
        ip = ep['fvCEp']['attributes']['ip']
        if ep['fvCEp'].get('children'):
            for ceptopath in ep['fvCEp']['children']:
                if ceptopath.get('fvRsCEpToPathEp')  and ceptopath['fvRsCEpToPathEp']['attributes']['state'] == 'formed':
                    fvRsCEpToPathEp_tDn = ceptopath['fvRsCEpToPathEp']['attributes']['tDn']
                    fvRsCEpToPathEp_lcC = ceptopath['fvRsCEpToPathEp']['attributes']['lcC']
                    fvRsCEpToPathEp_forceResolve = ceptopath['fvRsCEpToPathEp']['attributes']['forceResolve']
                    fvRsCEpToPathEplist.append(fvRsCEpToPathEp(forceResolve=fvRsCEpToPathEp_forceResolve, 
                                                            tDn=fvRsCEpToPathEp_tDn, lcC=fvRsCEpToPathEp_lcC))
    
                elif ceptopath.get('fvIp'):
                    fvIp_addr = ceptopath['fvIp']['attributes']['addr']
                    fvIp_rn = ceptopath['fvIp']['attributes']['rn']
                    if ceptopath['fvIp'].get('children'):
                        fvReportingNodes = [node['fvReportingNode']['attributes']['rn'] for node in ceptopath['fvIp']['children']]
                    else:
                        fvReportingNodes = None
                    fvIplist.append(fvIp(addr=fvIp_addr, rn=fvIp_rn,
                                        fvReportingNodes=fvReportingNodes))
                elif ceptopath.get('fvRsVm') and ceptopath['fvRsVm']['attributes']['state'] == 'formed':
                    fvRsVm_state = ceptopath['fvRsVm']['attributes']['state']
                    fvRsVm_tDn = ceptopath['fvRsVm']['attributes']['tDn']
                    fvRsVmobject = fvRsVm(state=fvRsVm_state,
                                            tDn=fvRsVm_tDn)
                elif ceptopath.get('fvRsHyper') and ceptopath['fvRsHyper']['attributes']['state'] == 'formed':
                    fvRsHyper_state = ceptopath['fvRsHyper']['attributes']['state']
                    fvRsHyper_tDn = ceptopath['fvRsHyper']['attributes']['tDn']
                    fvRsHyperobject = fvRsHyper(state=fvRsHyper_state,
                                                tDn=fvRsHyper_tDn)
            # VMware learned endpoints have multiple fvRsCEpToPathEp 
        if len(fvRsCEpToPathEplist) > 1:
            for path in fvRsCEpToPathEplist:
                if 'learned' in path.lcC:
                    fvRsCEpToPathEpobject = path
        elif len(fvRsCEpToPathEplist) == 1:
            fvRsCEpToPathEpobject = fvRsCEpToPathEplist[0]
        else:
            fvRsCEpToPathEpobject = None
        eplist.append(fvCEp(mac=mac, name=name, encap=encap,
                                lcC=lcC, dn=dn, fvRsVm=fvRsVmobject, fvRsCEpToPathEp=fvRsCEpToPathEpobject, 
                                ip=ip, fvRsHyper=fvRsHyperobject, fvIplist=fvIplist))
    return eplist

def readable_dnpath(dnpath):
    dnpath = dnpath.replace('[', '').replace(']', '').replace('topology/', '')
    if "/protpaths-" in dnpath and '/pathep-' in dnpath:
        dnpath = dnpath.replace('protpaths','leafs').replace('pathep','vpc')
        slashamount = dnpath.count('/') 
        dnpath = dnpath.replace('/', ', ', slashamount) # replace all / except
    elif "/protpaths-" in dnpath and "/extpaths-" in dnpath and '/pathep-' in dnpath:
        dnpath = dnpath.replace('protpaths','leaf').replace('extpaths', 'fex').replace('pathep-','')
        slashamount = dnpath.count('/') 
        dnpath = dnpath.replace('/', ', ', slashamount-1) # replace all / except
    elif "/paths-" in dnpath and "/extpaths-" in dnpath and '/pathep-' in dnpath:
        dnpath = dnpath.replace('extpaths','fex').replace('paths','leaf').replace('pathep-','')
        slashamount = dnpath.count('/') 
        dnpath = dnpath.replace('/', ', ', slashamount-1) # replace all / except
    elif "/paths-" in dnpath and '/pathep-' in dnpath:
        dnpath = dnpath.replace('paths','leaf').replace('pathep-','')
        slashamount = dnpath.count('/') 
        dnpath = dnpath.replace('/', ', ', slashamount-1) # replace all / except
    return dnpath


def display_live_history_info(ipaddressEP, totalcount):
    url = """https://{apic}/mqapi2/troubleshoot.eptracker.json?ep={}&order-by=troubleshootEpTransition.date|desc""".format(ipaddressEP.dn,apic=apic)
    logger.info(str(url))
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print('No current IP history found...check event history\n')
    else:
        for historyep in result:
            dnpath = historyep['troubleshootEpTransition']['attributes']['path']
            dnpath = readable_dnpath(dnpath)
            troubleshootstring = "{:26}\t{:15}\t{:18}\t{:20}\t{}"
            print(troubleshootstring.format(historyep['troubleshootEpTransition']['attributes']['date'][:-6], 
                historyep['troubleshootEpTransition']['attributes']['encap'], historyep['troubleshootEpTransition']['attributes']['ip'],
                historyep['troubleshootEpTransition']['attributes']['mac'], dnpath))

def gather_compVM_info(result):
    host_rn_reference = None
    local_compRsDlPol = None
    local_compEpPConn = None
    vniclist = []
    result = result[0]
    compVMstate = result['compVm']['attributes']['state']
    compVMdn = result['compVm']['attributes']['dn']
    compVMname = result['compVm']['attributes']['name']
    compVMguid = result['compVm']['attributes']['guid']
    if result['compVm'].get('children'):
        for child in result['compVm']['children']:
            if child.get('compRsHv'):
                host_rn_reference = child['compRsHv']['attributes']['tDn']
            elif child.get('compVNic'):
                vnicname =  child['compVNic']['attributes']['name']
                vnicoperSt = child['compVNic']['attributes']['operSt']
                vnicip =  child['compVNic']['attributes']['ip']
                vnicmac =  child['compVNic']['attributes']['mac']
                vnicadapterType =  child['compVNic']['attributes']['adapterType']
                current_compVNicObject = compVNic(name=vnicname,
                                                    mac=vnicmac,
                                                    operSt=vnicoperSt,
                                                    ip=vnicip,
                                                    adapterType=vnicadapterType)
                if child['compVNic'].get('children'):
                    for object in child['compVNic']['children']:
                        if object.get('compRsDlPol'):
                            local_compRsDlPol = compRsDlPol(tDn=object['compRsDlPol']['attributes']['tDn'])
                        elif object.get('compEpPConn'):
                            local_compEpPConn = compEpPConn(epgPKey=object['compEpPConn']['attributes']['epgPKey'],
                                                            encap=object['compEpPConn']['attributes']['encap'],
                                                            portDn=object['compEpPConn']['attributes']['portDn'],
                                                            hostDn=object['compEpPConn']['attributes']['hostDn'])
                            #print(local_compEpPConn)
                        current_compVNicObject.compRsDlPol = local_compRsDlPol
                        current_compVNicObject.compEpPConn = local_compEpPConn

                vniclist.append(current_compVNicObject)
    compVMObject = compVm(state=compVMstate,
                          dn=compVMdn,
                          name=compVMname,
                          guid=compVMguid,
                          compVNiclist=vniclist,
                          host_rn_reference=host_rn_reference)
    return compVMObject
    

def eventhistory(address):
    #event record code E4209236 is "ip detached event"
    if len(address) == 17:
        url = """https://{apic}/api/node/class/eventRecord.json?query-target-filter=and(eq(eventRecord.code,"E4209236"))&query-target-filter=and(wcard(eventRecord.dn,"cep-{address}"))&order-by=eventRecord.created|desc&page=0&page-size=30""".format(address=address,apic=apic)
        logger.info(url)
    elif len(address) >= 7 and len(address) <= 15 :
        url = """https://{apic}/api/node/class/eventRecord.json?query-target-filter=and(eq(eventRecord.code,"E4209236"))&query-target-filter=and(wcard(eventRecord.descr,"{address}$"))&order-by=eventRecord.created|desc&page=0&page-size=30""".format(address=address,apic=apic)
        logger.info(url)
    result, totalcount = GetResponseData(url)
    print('\n')
    if totalcount == '0':
        print("{:.<45}0\n".format("Searching Event Records"))
    else:
        print("{:.<45}Found {} Events\n".format("Searching Event Records",totalcount))
    print("{:26}{:12}".format('Time','Description', ))
    print('-'*90)
    if totalcount == '0':
        print("\x1b[41;1mNo event history logs found for {}\x1b[0m\n\n".format(address))
        return
    for event in result:
        timestamp = event['eventRecord']['attributes']['created']
        descr = event['eventRecord']['attributes']['descr']
        dn = event['eventRecord']['attributes']['dn']
        macfound = re.search(r'cep-.{17}', dn)
        if macfound == None:
            macfound = 'No Mac Found'
        else:
            macfound = macfound.group()[4:]
        print("{:26}{:^12}  [{}]".format(timestamp[:-6],descr,'mac: ' + macfound))


def display_vm_information(endpointobject, compVm):
        if endpointobject.fvRsVm:
            vmhostname = '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m'
            if endpointobject.fvRsHyper:
                url = """https://{apic}/api/node/mo/{}.json""".format(endpointobject.fvRsHyper.tDn,apic=apic)
                logger.info(url)
                result, totalcount = GetResponseData(url)
                vmhostname = result[0]["compHv"]["attributes"]["name"]
                url = """https://{apic}/api/node/mo/{}.json""".format(endpointobject.fvRsVm.tDn,apic=apic)
                logger.info(url)
                result, totalcount = GetResponseData(url)
                vmname = result[0]["compVm"]["attributes"]["name"]
                vmpowerstate = result[0]["compVm"]["attributes"]["state"]
                if vmhostname == '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m':
                    print("{:96}vm_name = {:18}\n{:96}{:18}\n".format('',vmname,'',vmhostname))#,vmstate))
                else:
                    if vmpowerstate == 'poweredOff':
                        print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n{:96}State = \x1b[1;31;40m{:18}\x1b[0m\n".format('',vmname,'',vmhostname,'',vmpowerstate))#,vmstate))
                    else:
                        print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n{:96}State = {:18}\n".format('',vmname,'',vmhostname,'',vmpowerstate))#,vmstate))
            else:
                if vmhostname == '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m':
                    print("{:96}{:18}\n{:96}{:18}\n".format('','','',vmhostname))

def find_and_display_current_location_info(macEP, totalcount, compVm=None):
    dnpath = macEP.fvRsCEpToPathEp.tDn
    dnpath = readable_dnpath(dnpath)
    print('\n')
    # Account for mac addresses that have mulitple ip addresses, need to display all IPs if possible.
    if macEP.fvIplist == []:
        #print('he')
        print("{:^115}".format('EPG = \x1b[1;33;40m ' + macEP.epg + ' \x1b[0m\n'))
        print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
        print('-'*115)
        print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", macEP.encap, macEP.ip, macEP.mac, dnpath))
        display_vm_information(macEP, compVm)
    else:
        for ipadd in macEP.fvIplist:
            print("{:^115}".format('EPG = \x1b[1;33;40m ' + macEP.epg + ' \x1b[0m\n'))
            print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
            print('-'*115)
            print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", macEP.encap, ipadd.addr, macEP.mac, dnpath))
            display_vm_information(macEP, compVm)



def vm_search_function(vm_name):
    url = """https://{apic}/api/node/class/compVm.json?query-target-filter=and(eq(compVm.name,"{}"))""".format(vm_name,apic=apic)
    logger.info(url)
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print('\n')
        print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
        print('-'*97)
        print('\x1b[41;1mNo "LIVE Endpoint" VM found...check event history\x1b[0m\n')
        print('\n')
    else:
        url = """https://{apic}/api/node/class/fvRsVm.json""".format(apic=apic)
        logger.info(url)
        fvRsVm_result, totalcount = GetResponseData(url)
        fvRsVmlist = []
        for vm in fvRsVm_result:
            vmstate = vm['fvRsVm']['attributes']['state']
            if vmstate == 'formed':
                vmdn = vm['fvRsVm']['attributes']['dn']
                vmtDn = vm['fvRsVm']['attributes']['tDn']
                fvRsVmlist.append(fvRsVm(state=vmstate,dn=vmdn,tDn=vmtDn))
        compVm_dn = result[0]['compVm']['attributes']['dn']
        url = """https://{apic}/api/mo/{}.json?rsp-subtree=full""".format(compVm_dn, apic=apic)
        logger.info(url)
        result, totalcount = GetResponseData(url)
        compVM = gather_compVM_info(result)
        k = filter(lambda x: x in  fvRsVmlist, compVM.compVNiclist)
        if len(compVM.compVNiclist) == 1:
            mac_path_function(compVM.compVNiclist[0].mac, compVM=compVM)
            return compVM.compVNiclist[0].mac
        else:
            compVM.compVNiclist = sorted(compVM.compVNiclist, key=lambda x: x.name)
            print('\n')
            print("{} interfaces:".format(vm_name))
            print('-'*30)
            for num,vnic in enumerate(compVM.compVNiclist,1):
                if vnic.ip == '0.0.0.0':
                    print("{}.) VNIC = {} | MAC = {}".format(num,vnic.name,vnic.mac))         
                else:
                    print("{}.) VNIC = {} | MAC = {} | IP = {}".format(num,vnic.name,vnic.mac,vnic.ip))         
            while True:
                pickednum = custom_raw_input("\nWhich interface? ")
                if pickednum.isdigit() and (int(pickednum) > 0 and int(pickednum) <= len(compVM.compVNiclist)):
                    break
                else:
                    continue
            mac_path_function(compVM.compVNiclist[int(pickednum)-1].mac, compVM=compVM)
            return compVM.compVNiclist[int(pickednum)-1].mac


def mac_path_function(mac, compVM=None):
    epglist =[]
    url = """https://{apic}/api/node/class/fvCEp.json?rsp-subtree=full&query-target-filter=eq(fvCEp.mac,"{}")""".format(mac,apic=apic)
    logger.info(url)
    result, totalcount = GetResponseData(url)
    if totalcount == '0' and compVM:
        print('\n')
        url = """https://{apic}/api/node/mo/{}.json""".format(compVM.host_rn_reference,apic=apic)
        logger.info(url)
        result, totalcount = GetResponseData(url)
        for vminterface in compVM.compVNiclist:
            if vminterface.mac == mac:
                print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
                print('-'*97)
                print('\x1b[41;1mMAC not found on Fabric....\x1b[0m\n')
                print("Nic not using portgroup deployed by ACI\n")
                print("Helpful info:\n\tHost: {}\t VM Status: {}\tvnic_status: {}\tvnic_ip: {}".format(result[0]['compHv']['attributes']['name'],
                                                                                                compVM.state,vminterface.operSt ,vminterface.ip))
        print('\n')
    elif totalcount == '0':
        print('\n')
        print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
        print('-'*97)
        print('\x1b[41;1mNo "LIVE Endpoint" MAC found...check event history\x1b[0m\n')
        print('\n')
    else:
        fvCEplist = gather_fvCEp_fullinfo(result)
        for fvCEp in fvCEplist:
            url = """https://{apic}/api/node/mo/{}.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(fvCEp.dn,apic=apic)
            logger.info(url)
            result, totalcount = GetResponseData(url)
            completefvCEplist = gather_fvCEp_fullinfo(result)
            #Display current endpoint info
            find_and_display_current_location_info(completefvCEplist[0], totalcount,compVM)
            #Display current known endpoint history
        if len(fvCEplist) > 1:
            print('\n')
            for num,x in enumerate(fvCEplist,1):
                x = '|'.join(x.dn.split('/')[1:-1])
                print("{}.) {}".format(num,x))
            while True:
                ask = custom_raw_input("\nWhich number (MAC lives in multiple EPGs)?: ")
                if ask.isdigit() and (int(ask) > 0 and int(ask) <= len(fvCEplist)):
                    break
                else:
                    continue
            print('\n[History]')
            display_live_history_info(fvCEplist[int(ask)-1], totalcount)
            return fvCEplist[int(ask)-1]
        else:
            print('\n[History]')
            display_live_history_info(completefvCEplist[0], totalcount)
            return completefvCEplist[0]


def ip_path_function(ipaddr):
    totalcount2 = 1
    url = """https://{apic}/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&rsp-subtree-filter=eq(fvIp.addr,"{}")""".format(ipaddr,apic=apic)
    logger.info(url)
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        url = """https://{apic}/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&query-target-filter=eq(fvCEp.ip,"{}")""".format(ipaddr,apic=apic)
        logger.info(url)
        result, totalcount2 = GetResponseData(url)
    if totalcount2 == '0' :
        print('\n')
        print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
        print('-'*97)
        print('\x1b[41;1mNo "LIVE Endpoint" IP found...check event history\x1b[0m\n')
        print('\n')
    else:
        fvCEplist = gather_fvCEp_fullinfo(result)
        for fvCEp in fvCEplist:
            url = """https://{apic}/api/node/mo/{}.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(fvCEp.dn,apic=apic)
            logger.info(url)
            result, totalcount = GetResponseData(url)
           # print(result)
            completefvCEplist = gather_fvCEp_fullinfo(result)
            #Display current endpoint info
            find_and_display_current_location_info(completefvCEplist[0], totalcount)
            #Display current known endpoint history
        print('\n[History]')
        display_live_history_info(completefvCEplist[0], totalcount)



def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:
        clear_screen()
        search = custom_raw_input("\nWhat is the IP, MAC, or VM name?: ")
        if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", search.lower()):
            endpoint = search.upper()
            mac_path_function(endpoint)
        elif re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",search):
            endpoint = search
            ip_path_function(endpoint)
        else:
            endpoint = search
            endpoint = vm_search_function(endpoint)
        while True:
            history = custom_raw_input("\nWould you like to search event logs for {}? [y|n=default]: ".format(endpoint)) or 'n'
            if history != '' and history[0].lower() == 'y':
                eventhistory(endpoint)
                raw_input('#Press enter to continue...')
                break
            elif history[0].lower() == 'n':
                endpoint = None
                break
            else:
                print("\n\x1b[1;37;41mInvalid option, Please try again\x1b[0m\n")
                continue
     

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print('\nExiting...\n')
        exit()
