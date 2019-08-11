#!/bin//python

import re
import readline
import urllib2
import json
import ssl


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
                 fvRsCEpToPathEp=None, ip=None, fvIPlist=[]):
        self.mac = mac
        self.name = name
        self.encap = encap
        self.dn = dn
        self.lcC = lcC
        self.fvRsVm = fvRsVm
        self.fvRsHyper = fvRsHyper
        self.ip = ip
        #self.iplist = iplist
        self.fvIPlist = fvIPlist
        self.fvRsCEpToPathEp = fvRsCEpToPathEp
    def __repr__(self):
        return self.dn
    def __getitem__(self, addr):
        if addr in self.addr:
            return self.addr
        else:
            return None

class fvIP():
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
    def __init__(self, state=None, tDn=None):
        self.state = state
        self.tDn = tDn #internal vm name to lookup vmware vm name
    def __repr__(self):
        return self.tDn

class fvRsHyper():
    def __init__(self, state=None, tDn=None):
        self.state = state
        self.tDn = tDn  #hyperviser internal name to look up vmware host name
    def __repr__(self):
        return self.tDn

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

def gather_fvCEp_fullinfo(result):
    fvIPlist = []
    eplist = []
    for ep in result:
        mac = ep['fvCEp']['attributes']['mac']
        name = ep['fvCEp']['attributes']['name']
        encap = ep['fvCEp']['attributes']['encap']
        lcC = ep['fvCEp']['attributes']['lcC']
        dn = ep['fvCEp']['attributes']['dn']
        ip = ep['fvCEp']['attributes']['ip']
        if ep['fvCEp'].get('children'):
            for ceptopath in ep['fvCEp']['children']:
                #print(ceptopath)
                if ceptopath.get('fvRsCEpToPathEp') and ceptopath['fvRsCEpToPathEp']['attributes']['state'] == 'formed':
                    fvRsCEpToPathEp_tDn = ceptopath['fvRsCEpToPathEp']['attributes']['tDn']
                    fvRsCEpToPathEp_lcC = ceptopath['fvRsCEpToPathEp']['attributes']['lcC']
                    fvRsCEpToPathEp_forceResolve = ceptopath['fvRsCEpToPathEp']['attributes']['forceResolve']
                    fvRsCEpToPathEpobject =(fvRsCEpToPathEp(forceResolve=fvRsCEpToPathEp_forceResolve, 
                                                            tDn=fvRsCEpToPathEp_tDn, lcC=fvRsCEpToPathEp_lcC))
                else:
                    fvRsCEpToPathEpobject = None
                if ceptopath.get('fvIP') and ceptopath['fvIP']['attributes']['state'] == 'formed':
                    fvIP_addr = ceptopath['fvIP']['attributes']['tDn']
                    fvIP_rn = ceptopath['fvIP']['attributes']['rn']
                    if ceptopath['fvIP'].get('children'):
                        fvReportingNodes = [node['fvReportingNode']['attributes']['rn'] for node in ceptopath['fvIP']['children']]
                    else:
                        fvReportingNodes = None
                    fvIPlist.append(fvIP(addr=fvIP_addr, rn=fvIP_rn,fvReportingNodes=fvReportingNodes))
                else:
                    fvIPlist = None
                if ceptopath.get('fvRsVm') and ceptopath['fvRsVm']['attributes']['state'] == 'formed':
                    fvRsVm_state = ceptopath['fvRsVm']['attributes']['state']
                    fvRsVm_tDn = ceptopath['fvRsVm']['attributes']['tDn']
                    fvRsVmobject = fvRsVm(state=fvRsVm_state,tDn=fvRsVm_tDn)
                else:
                    fvRsVmobject = None
                if ceptopath.get('fvRsHyper') and ceptopath['fvRsHyper']['attributes']['state'] == 'formed':
                    fvRsHyper_state = ceptopath['fvRsHyper']['attributes']['state']
                    fvRsHyper_tDn = ceptopath['fvRsHyper']['attributes']['tDn']
                    fvRsHyperobject = fvRsHyper(state=fvRsHyper_state,tDn=fvRsHyper_tDn)
                else:
                    fvRsHyperobject = None
        eplist.append(fvCEp(mac=mac, name=name, encap=encap,
                 lcC=lcC, dn=dn, fvRsVm=fvRsVmobject, fvRsCEpToPathEp=fvRsCEpToPathEpobject, 
                 ip=ip, fvRsHyper=fvRsHyperobject, fvIPlist=[]))
        iplist = []
        ipobjectlist = []
        fvreportingNodes = []
    return eplist


def findipaddress():
    ipaddr = raw_input("\nWhat is the ip address?: ")
    url = """https://localhost/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-include=required&rsp-subtree-filter=eq(fvIp.addr,"{}")""".format(ipaddr)
    result, totalcount = GetResponseData(url)
    epobject = gather_fvCEp_fullinfo(result)
    
    epobject = epobject[0]
    try:
        if totalcount == '0':
            print('\n')
            print("{:26}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
            print('-'*97)
            #print(troubleshootstring.format(result['troubleshootEpTransition']['attributes']['date'], result['troubleshootEpTransition']['attributes']['encap'], result['troubleshootEpTransition']['attributes']['ip'], result['troubleshootEpTransition']['attributes']['mac']))
            print('\x1b[41;1mNo "LIVE Endpoint" IP found...check event history\x1b[0m\n')
            print('\n')
            #print("{:35}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
            #print('-'*97)
            #('No current IP found...check event history\n')
        else:

            mac = result[0]['fvCEp']['attributes']['mac']
            encap = result[0]['fvCEp']['attributes']['encap']
            dn = result[0]['fvCEp']['attributes']['dn']
            
            dnpath = dn.split('/')[:4]
            dnpath = '/'.join(dnpath)
            print('\n')
            print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address", "Path"))
            print('-'*115)
            print("{:26}\t{:15}\t{:18}\t{:20}\t{}".format("Current", encap, "Ip Address", mac, dn))
        #url2 = """https://localhost/api/node/mo/uni/tn-SI/ap-APP-ISE/epg-EPG-VL10-ISE/cep-{}.json?query-target=subtree&target-subtree-class=fvCEp,fvRsCEpToPathEp,fvRsHyper,fvRsToNic,fvRsToVm""".format(mac)
        #result2, totalcount2 = GetResponseData(url2)
        #result2['f']
            url3 = """https://localhost/mqapi2/troubleshoot.eptracker.json?ep={}/cep-{}""".format(dnpath,mac)
        #print(url3)
            result3, totalcount3 = GetResponseData(url3)
            #print(result3)
     #   print('\n')
     #   print("{:35}\t{:15}\t{:18}\t{}".format("Date", "encap-vlan", "Ip Address", "Mac Address"))
     #   print('-'*97)
     #   if totalcount3 == '0':
     #       #troubleshootstring = "{:35}\t{:15}\t{:18}\t{}"
            #print(troubleshootstring.format(x['troubleshootEpTransition']['attributes']['date'], x['troubleshootEpTransition']['attributes']['encap'], x['troubleshootEpTransition']['attributes']['ip'], x['troubleshootEpTransition']['attributes']['mac']))
            #print('No current IP found...check event history\n')
            for x in result3:
                troubleshootstring = "{:26}\t{:15}\t{:18}\t{:20}\t{}"
                print(troubleshootstring.format(x['troubleshootEpTransition']['attributes']['date'][:-6], x['troubleshootEpTransition']['attributes']['encap'], x['troubleshootEpTransition']['attributes']['ip'], x['troubleshootEpTransition']['attributes']['mac'], x['troubleshootEpTransition']['attributes']['path']) )
    except Exception as e:
        print(e)
    history = raw_input("\nWould you like to see event history of {}? [y/n]: ".format(ipaddr))
    if history != '' and history.lower() == 'y':
        return ipaddr
    else:
        return


def scrollevents(ipaddr):
    #event record code E4209236 is "ip detached event"

    url = """https://localhost/api/node/class/eventRecord.json?query-target-filter=and(eq(eventRecord.code,"E4209236"))&query-target-filter=and(wcard(eventRecord.descr,"{ipaddr}$"))&order-by=eventRecord.created|desc&page=0&page-size=30""".format(ipaddr=ipaddr)
    result, totalcount = GetResponseData(url)
    print('\n')
    if totalcount == '0':
        print("{:.<45}0\n".format("Searching Event Records"))
    else:
        print("{:.<45}Found {} Events\n".format("Searching Event Records",totalcount))
       
    print("{:26}{:12}".format('Time','Description', ))
    print('-'*90)
    if totalcount == '0':
        print("\x1b[41;1mNo event history found for IP {}\x1b[0m\n\n".format(ipaddr))
        return
    for event in result:
        timestamp = event['eventRecord']['attributes']['created']
        descr = event['eventRecord']['attributes']['descr']
        dn = event['eventRecord']['attributes']['dn']
        mac = re.search(r'cep-.{17}', dn)
        #controller = re.search(r'node-[0-9]', event['eventRecord']['attributes']['dn'])
        print("{:26}{:^12}  [{}]".format(timestamp[:-6],descr,'mac: ' + mac.group()[4:]))
        
def main():
    ipaddr = findipaddress()
    if ipaddr:
        scrollevents(ipaddr)