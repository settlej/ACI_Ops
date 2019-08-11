#!/bin//python

import re
import readline
import urllib2
import json
import ssl
#import ipaddress
import trace
import pdb

ipaddr = None

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
    def __init__(self, state=None, name=None, ip=None, mac=None, adapterType=None, compRsDlPol=None, compEpPConn=None):
        self.state = state
        self.name = name
        self.ip = ip
        self.mac = mac
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
                if ceptopath.get('fvRsCEpToPathEp') and ceptopath['fvRsCEpToPathEp']['attributes']['state'] == 'formed':
                    fvRsCEpToPathEp_tDn = ceptopath['fvRsCEpToPathEp']['attributes']['tDn']
                    fvRsCEpToPathEp_lcC = ceptopath['fvRsCEpToPathEp']['attributes']['lcC']
                    fvRsCEpToPathEp_forceResolve = ceptopath['fvRsCEpToPathEp']['attributes']['forceResolve']
                    fvRsCEpToPathEpobject = fvRsCEpToPathEp(forceResolve=fvRsCEpToPathEp_forceResolve, 
                                                            tDn=fvRsCEpToPathEp_tDn, lcC=fvRsCEpToPathEp_lcC)
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
    try:
        #url2 = """https://localhost/api/node/mo/uni/tn-SI/ap-APP-ISE/epg-EPG-VL10-ISE/cep-{}.json?query-target=subtree&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(mac)
        #result2, totalcount2 = GetResponseData(url2)
        #result2['f']
        #ephistorydnformat = ipaddressEP.dn.split('/')[:4]
        #ephistorydnformat = '/'.join(ephistorydnformat)
        #print(ephistorydnformat)
        url = """https://localhost/mqapi2/troubleshoot.eptracker.json?ep={}&order-by=troubleshootEpTransition.date|desc""".format(ipaddressEP.dn)
        #print(url)
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
    except Exception as e:
        print(e)

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
                vnicip =  child['compVNic']['attributes']['ip']
                vnicmac =  child['compVNic']['attributes']['mac']
                vnicadapterType =  child['compVNic']['attributes']['adapterType']
                current_compVNicObject = compVNic(name=vnicname,
                                                    mac=vnicmac,
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
        #print('yes')
        url = """https://localhost/api/node/class/eventRecord.json?query-target-filter=and(eq(eventRecord.code,"E4209236"))&query-target-filter=and(wcard(eventRecord.dn,"cep-{address}"))&order-by=eventRecord.created|desc&page=0&page-size=30""".format(address=address)
        #print(url)
    elif len(address) >= 7 and len(address) <= 15 :
        url = """https://localhost/api/node/class/eventRecord.json?query-target-filter=and(eq(eventRecord.code,"E4209236"))&query-target-filter=and(wcard(eventRecord.descr,"{address}$"))&order-by=eventRecord.created|desc&page=0&page-size=30""".format(address=address)
    
    result, totalcount = GetResponseData(url)
    #print(result)
    print('\n')
    if totalcount == '0':
        print("{:.<45}0\n".format("Searching Event Records"))
    else:
        print("{:.<45}Found {} Events\n".format("Searching Event Records",totalcount))
       
    print("{:26}{:12}".format('Time','Description', ))
    print('-'*90)
    if totalcount == '0':
        print("\x1b[41;1mNo event history logs found for IP {}\x1b[0m\n\n".format(address))
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
        #controller = re.search(r'node-[0-9]', event['eventRecord']['attributes']['dn'])
        print("{:26}{:^12}  [{}]".format(timestamp[:-6],descr,'mac: ' + macfound))
        
def find_current_ep_info(ipaddressEP, totalcount):
    #print('totalcount')
    #print(totalcount)
    #mac = result[0]['fvCEp']['attributes']['mac']
    #encap = result[0]['fvCEp']['attributes']['encap']
    #dn = result[0]['fvCEp']['attributes']['dn']
    dnpath = ipaddressEP.fvRsCEpToPathEp.tDn
    dnpath = readable_dnpath(dnpath)
    #print('\n')
    print('\n')
    #for ipadd in ipaddressEP.fvIplist:
    print("{:^115}".format('EPG = \x1b[1;33;40m ' + ipaddressEP.epg + ' \x1b[0m\n'))
    print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
    print('-'*115)
    print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", ipaddressEP.encap, ipaddressEP.ip, ipaddressEP.mac, dnpath))
    if ipaddressEP.fvRsVm:
        try:
   #     print(vars(fvRsHyper))
            vmhostname = '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m'
            if ipaddressEP.fvRsHyper:
                url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsHyper.tDn)
                result, totalcount = GetResponseData(url)
                vmhostname = result[0]["compHv"]["attributes"]["name"]
            url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsVm.tDn)
            result, totalcount = GetResponseData(url)
            vmname = result[0]["compVm"]["attributes"]["name"]
            vmpowerstate = result[0]["compVm"]["attributes"]["state"]
            #vmstate = result[0]["compVm"]["attributes"]["state"]
            if vmhostname == '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m':
                print("{:96}vm_name = {:18}\n{:96}{:18}\n".format('',vmname,'',vmhostname))#,vmstate))
            else:
                print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n{:96}State = {:18}\n".format('',vmname,'',vmhostname,'',vmpowerstate))#,vmstate))
        except AttributeError as ae:
            pdb.set_trace()

def find_current_ep_info_via_MAC(ipaddressEP, totalcount):
    #print('totalcount')
    #print(totalcount)
    #mac = result[0]['fvCEp']['attributes']['mac']
    #encap = result[0]['fvCEp']['attributes']['encap']
    #dn = result[0]['fvCEp']['attributes']['dn']
    dnpath = ipaddressEP.fvRsCEpToPathEp.tDn
    dnpath = readable_dnpath(dnpath)
    #print('\n')
    print('\n')
    #print(ipaddressEP)
    epglistforhistorysearch = []
    #print(ipaddressEP.fvIplist)
    for ipadd in ipaddressEP.fvIplist:
        epglistforhistorysearch.append(ipaddressEP)
        print("{:^115}".format('EPG = \x1b[1;33;40m ' + ipaddressEP.epg + ' \x1b[0m\n'))
        print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
        print('-'*115)
        print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", ipaddressEP.encap, ipadd.addr, ipaddressEP.mac, dnpath))
        if ipaddressEP.fvRsVm:
            vmhostname = '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m'
            try:
   #         print(vars(fvRsHyper))
                
                if ipaddressEP.fvRsHyper:
                    url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsHyper.tDn)
                    result, totalcount = GetResponseData(url)
                    vmhostname = result[0]["compHv"]["attributes"]["name"]
                    #vmpowerstate = result[0]["compHv"]["attributes"]["state"]

                url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsVm.tDn)
                result, totalcount = GetResponseData(url)
              #  print(result[0])
                vmname = result[0]["compVm"]["attributes"]["name"]
                vmpowerstate = result[0]["compVm"]["attributes"]["state"]
                if vmhostname == '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m':
                    print("{:96}vm_name = {:18}\n{:96}{:18}\n".format('',vmname,'',vmhostname))#,vmstate))
                else:
                    print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n{:96}State = {:18}\n".format('',vmname,'',vmhostname,'',vmpowerstate))#,vmstate))

                    #print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n".format('',vmname,'',vmhostname))#,vmstate))
            except AttributeError as ae:
                pdb.set_trace()
    if ipaddressEP.fvIplist == []:
        print("{:^115}".format('EPG = \x1b[1;33;40m ' + ipaddressEP.epg + ' \x1b[0m\n'))
        print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
        print('-'*115)
        print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", ipaddressEP.encap, ipaddressEP.ip, ipaddressEP.mac, dnpath))
        if ipaddressEP.fvRsVm:
            try:
   #         print(vars(fvRsHyper))
                vmhostname = '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m'
                if ipaddressEP.fvRsHyper:
                    url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsHyper.tDn)
                    result, totalcount = GetResponseData(url)
                    vmhostname = result[0]["compHv"]["attributes"]["name"]
                url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsVm.tDn)
                result, totalcount = GetResponseData(url)
                vmname = result[0]["compVm"]["attributes"]["name"]
                vmpowerstate = result[0]["compVm"]["attributes"]["state"]

                #vmstate = result[0]["compVm"]["attributes"]["state"]
                if vmhostname == '\x1b[1;37;41m****OLD INFORMATION PHASING OUT****\x1b[0m':
                    print("{:96}vm_name = {:18}\n{:96}{:18}\n".format('',vmname,'',vmhostname))#,vmstate))
                else:

                    print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n{:96}State = {:18}\n".format('',vmname,'',vmhostname,'',vmpowerstate))#,vmstate))
            except AttributeError as ae:
                pdb.set_trace()
    return epglistforhistorysearch 

    #if len(ipaddressEP.fvIplist) != 0:
    #    print("{:^115}".format('EPG = \x1b[1;33;40m ' + ipaddressEP.epg + ' \x1b[0m\n'))
    #    print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
    #    print('-'*115)
    #    print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", ipaddressEP.encap, ipaddressEP.ip, ipaddressEP.mac, dnpath))
    #    if ipaddressEP.fvRsVm:
    #        print(vars(fvRsHyper))
    #        url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsHyper.tDn)
    #        result, totalcount = GetResponseData(url)
    #        vmhostname = result[0]["compHv"]["attributes"]["name"]
    #        url = """https://localhost/api/node/mo/{}.json""".format(ipaddressEP.fvRsVm.tDn)
    #        result, totalcount = GetResponseData(url)
    #        vmname = result[0]["compVm"]["attributes"]["name"]
    #        #vmstate = result[0]["compVm"]["attributes"]["state"]
    #        print("{:96}vm_name = {:18}\n{:96}Host = {:18}\n".format('',vmname,'',vmhostname))#,vmstate))
    #else:
    #    print("{:^115}".format('EPG = \x1b[1;33;40m ' + ipaddressEP.epg + ' \x1b[0m\n'))
    #    print("{:26}\t{:15}\t{:25}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
    #    print('-'*115)
    #    print("{:26}\t{:15}\t{:25}\t{:20}\t{}".format("Current", ipaddressEP.encap, ipaddressEP.showips(), ipaddressEP.mac, dnpath))
        

    

        #url = """https://localhost/api/class/fvCEp.json?rsp-subtree=full"""
    #result, totalcount = GetResponseData(url)
    #for x in result:
    #    if x['fvCEp'].get('children'):
    #        for z in x['fvCEp']['children']:
    #            if z.get('fvRsCEpToPathEp'):
    #                print(z['fvRsCEpToPathEp']['attributes']['tDn'])

def vm_search_function(vm_name):
    url = """https://localhost/api/node/class/compVm.json?query-target-filter=and(eq(compVm.name,"{}"))""".format(vm_name)
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print('\n')
        print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
        print('-'*97)
        print('\x1b[41;1mNo "LIVE Endpoint" VM found...check event history\x1b[0m\n')
        print('\n')
    else:
        vmlist = []
        compVm_dn = result[0]['compVm']['attributes']['dn']
        url = """https://localhost/api/node/class/fvRsVm.json?query-target-filter=or(eq(fvRsVm.tDn,"{}"))""".format(compVm_dn)
        result, totalcount = GetResponseData(url)


        #gather_compVM_info(result)
        if result != []:
            vmlist = []
            url = """https://localhost/api/mo/{}.json""".format(compVm_dn)
            result, totalcount = GetResponseData(url)
            compVm_dn = result[0]['compVm']['attributes']['dn']
##
         ##   print(result)
         ##   for vm in result:
         ##       vmlist.append(compVm(state=vm['compVm']['attributes']['state'],
         ##                           dn=vm['compVm']['attributes']['dn']))
##
         ##   querystring = ''
##
         ##   for vm in vmlist:
         ##       querystring += """,eq(fvCEp.dn,"{}")""".format(vm.dn)
         ##   print(querystring)
            #print(vmlist[0])
            #url = """https://localhost/api/mo/{}.json?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,""" \
            #      """fvRsToVm""".format(vmlist[0].dn)
            url = """https://localhost/api/mo/{}.json?rsp-subtree=full""".format(compVm_dn)
            #url = """https://localhost/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,""" \
            #      """fvRsToVm&query-target-filter=or({})""".format(querystring)
            #print(url)
            result, totalcount = GetResponseData(url)
            
            compVM = gather_compVM_info(result)
            if len(compVM.compVNiclist) == 1:
                mac_path_function(compVM.compVNiclist[0].mac)
            else:
                compVM.compVNiclist = sorted(compVM.compVNiclist, key=lambda x: x.name)
                print('\n')
                for num,j in enumerate(compVM.compVNiclist,1):
                    print(num,j.name,j.mac, j.ip)
                while True:
                    pickednum = raw_input("\nWhich interface? ")
                    if pickednum.isdigit() and (int(pickednum) > 0 and int(pickednum) <= len(compVM.compVNiclist)):
                        break
                    else:
                        continue
            print(kk.compVNiclist[int(pickednum)-1].mac)
            mac_path_function(kk.compVNiclist[int(pickednum)-1].mac)
        else:    
            for vm in result:
                print(vm)
                vmlist.append(fvRsVm(tDn=vm['fvRsVm']['attributes']['tDn'],
                                    state=vm['fvRsVm']['attributes']['state'],dn=vm['fvRsVm']['attributes']['dn']))

            querystring = """eq(fvCEp.dn, "{}")""".format(vmlist[0].dn[:-5])
            vmlistlen = len(vmlist)
            print(vmlist)
            if vmlistlen > 1:
                for vm in vmlist[1:]:
                    querystring += """,eq(fvCEp.dn, "{}")""".format(vm.dn[:-5])
                    print(querystring)
            url = """https://localhost/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,""" \
                  """fvRsToVm&query-target-filter=or({})""".format(querystring)
            print(url)
            result, totalcount = GetResponseData(url)
            CElist = gather_fvCEp_fullinfo(result)
            CEselectionDict = {}
            print(CElist)
            print('\n')
            if len(CElist) == 1:
                mac_path_function(CElist[0].mac)
            else:
                for num,ce in enumerate(CElist,1):
                    CEselectionDict[str(num)] = ce
                    print("{}.) {}  | MAC: {}  |  IP: {}".format(num,vm_name,ce.mac,ce.ip))
                epselection = raw_input("\nSelect VM [MAC|IP] for history lookup: ")
                mac_path_function(CEselectionDict[epselection].mac)


def mac_path_function(mac):
    epglist =[]
    url = """https://localhost/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.mac,"{}")""".format(mac)
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        print('\n')
        print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
        print('-'*97)
        print('\x1b[41;1mNo "LIVE Endpoint" MAC found...check event history\x1b[0m\n')
        print('\n')
    else:
        fvCEplist = gather_fvCEp_fullinfo(result)
        #print(fvCEplist)
        for fvCEp in fvCEplist:
            url = """https://localhost/api/node/mo/{}.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(fvCEp.dn)
            print(url)
            result, totalcount = GetResponseData(url)
            completefvCEplist = gather_fvCEp_fullinfo(result)
            #print(completefvCEplist)
            #Display current endpoint info
    
            epglistforhistorysearch = find_current_ep_info_via_MAC(completefvCEplist[0], totalcount)
            #Display current known endpoint history
            epglist.append(epglistforhistorysearch)
        
        
        epglist = list(set(epglist[0]))

        if len(epglist) > 1:
            #epglist = list(set(epglist[0]))
            for num,x in enumerate(epglist,1):
                print(num,x.dn)
            ask = raw_input("which number?: ")
            print('\n[History]')
            display_live_history_info(epglist[int(ask)-1], totalcount)
        else:
        #for x in epglist:
        #    x = list(set(x))
        #    print(x)
        
  #      print('here')
  #      print(completefvCEplist[0])
  #      print('end')
            print('\n[History]')
            display_live_history_info(completefvCEplist[0], totalcount)
    while True:
        history = raw_input("\nWould you like to search event logs for {}? [y|n=default]: ".format(mac)) or 'n'
        if history != '' and history[0].lower() == 'y':
            break #return ipaddressEP.ip
        elif history[0].lower() == 'n':
            mac = None
            break
        else:
            print("\n\x1b[1;37;41mInvalid option, Please try again\x1b[0m\n")
            continue
    if mac:
            eventhistory(mac)


def ip_path_function(ipaddr):
    totalcount2 = 1
    url = """https://localhost/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&rsp-subtree-filter=eq(fvIp.addr,"{}")""".format(ipaddr)
    result, totalcount = GetResponseData(url)
    if totalcount == '0':
        url = """https://localhost/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&query-target-filter=eq(fvCEp.ip,"{}")""".format(ipaddr)
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
            url = """https://localhost/api/node/mo/{}.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(fvCEp.dn)
            result, totalcount = GetResponseData(url)
           # print(result)
            completefvCEplist = gather_fvCEp_fullinfo(result)
            #Display current endpoint info
            find_current_ep_info(completefvCEplist[0], totalcount)
            #Display current known endpoint history
        print('\n[History]')
        display_live_history_info(completefvCEplist[0], totalcount)
    while True:
        history = raw_input("\nWould you like to search event logs for {}? [y|n=default]: ".format(ipaddr)) or 'n'
        if history != '' and history[0].lower() == 'y':
            break #return ipaddressEP.ip
        elif history[0].lower() == 'n':
            ipaddr = None
            break
        else:
            print("\n\x1b[1;37;41mInvalid option, Please try again\x1b[0m\n")
            continue
    if ipaddr:
            eventhistory(ipaddr)



def main():
    while True:
        get_Cookie()
        while True:
            search = raw_input("\nWhat is the IP, MAC, or VM name?: ")
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", search.lower()):
                mac = search.upper()
                mac_path_function(mac)
            elif re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",search):
                ipaddr = search
                ip_path_function(ipaddr)
            else:
                vm = search
                vm_search_function(vm)
            while True:
                again = raw_input("\nSearch another endpoint? [y|n=default] ") or "n"
                if again[0].lower() == 'y':
                    break
                elif again[0].lower() == 'n':
                    print("\nExiting...\n")
                    exit()
                else:
                    print("\n\x1b[1;37;41mInvalid option, Please try again\x1b[0m\n")
                    continue
        break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print('\nExiting...\n')
        exit()