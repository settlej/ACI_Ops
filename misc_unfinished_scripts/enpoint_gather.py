#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os
import ipaddress


def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-trig", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

class epmMacEp():
    def __init__(self, addr=None, ifId=None, name=None,
                 pcTag=None, dn=None, flags=None, iplist=[], ipobjectlist=[]):
        self.addr = addr
        self.ifId = ifId
        self.name = name
        self.pcTag = pcTag
        self.dn = dn
        self.flags = flags
        self.iplist = iplist
        self.ipobjectlist = ipobjectlist
    def __repr__(self):
        return self.dn
    def __getitem__(self, addr):
        if addr in self.addr:
            return self.addr
        else:
            return None

class epmRsMacEpToIpEpAtt():
    def __init__(self, forceResolve=None, tDn=None, ipaddr=None,
                 state=None):
        self.forceResolve = forceResolve
        self.tDn = tDn
        self.ipaddr = ipaddr
        self.state = state
    def __repr__(self):
        return self.tDn
    def __getitem__(self, ip):
        if ip in self.ipaddr:
            return self.ipaddr
        else:
            return None


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
    def __getitem__(self, mac):
        if mac in self.mac:
            return self.mac
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


def gether_epm_fullinfo(result):
    eplist = []
    iplist = []
    ipobjectlist = []
    for ep in result:
        addr = ep['epmMacEp']['attributes']['addr']
        ifId = ep['epmMacEp']['attributes']['ifId']
        pcTag = ep['epmMacEp']['attributes']['pcTag']
        dn = ep['epmMacEp']['attributes']['dn']
        flags = ep['epmMacEp']['attributes']['flags']
        name = ep['epmMacEp']['attributes']['name']
        if ep['epmMacEp'].get('children'):
            for ip in ep['epmMacEp']['children']:
                if ip.get('epmRsMacEpToIpEpAtt') and ip['epmRsMacEpToIpEpAtt']['attributes']['state'] == 'formed':
                    tDn = ip['epmRsMacEpToIpEpAtt']['attributes']['tDn']
                    state = ip['epmRsMacEpToIpEpAtt']['attributes']['state']
                    ipaddr = re.search(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', ip['epmRsMacEpToIpEpAtt']['attributes']['tDn'])
                    if ipaddr:
                        iplist.append(ipaddr.group())
                    forceResolve = ip['epmRsMacEpToIpEpAtt']['attributes']['forceResolve']
                    ipobjectlist.append(epmRsMacEpToIpEpAtt(forceResolve=forceResolve, 
                                                            tDn=tDn, ipaddr=ipaddr, state=state))
        eplist.append(epmMacEp(addr=addr,ifId=ifId, name=name, pcTag=pcTag, 
                      dn=dn, flags=flags, iplist=iplist, ipobjectlist=ipobjectlist))
        iplist = []
        ipobjectlist = []
    return eplist


#def gather_fvCEp_fullinfo(result):
#    ipobjectlist
#    for ep in result:
#        mac = ep['fvCEp']['attributes']['mac']
#        name = ep['fvCEp']['attributes']['name']
#        encap = ep['fvCEp']['attributes']['encap']
#        lcC = ep['fvCEp']['attributes']['lcC']
#        dn = ep['fvCEp']['attributes']['dn']
#        if ep['fvCEp'].get('children'):
#            for ip in ep['fvCEp']['children']:
#                if ip.get('fvRsCEpToPathEp') and ip['fvRsCEpToPathEp']['attributes']['state'] == 'formed':
#                    tDn = ip['fvRsCEpToPathEp']['attributes']['tDn']
#                    state = ip['fvRsCEpToPathEp']['attributes']['state']
#                    ipaddr = re.search(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', ip['fvRsCEpToPathEp']['attributes']['tDn'])
#                    if ipaddr:
#                        iplist.append(ipaddr.group())
#                    forceResolve = ip['fvRsCEpToPathEp']['attributes']['forceResolve']
#                    ipobjectlist.append(fvRsCEpToPathEp(forceResolve=forceResolve, 
#                                                            tDn=tDn, ipaddr=ipaddr, state=state))
#        eplist.append(fvCEp(mac=mac,ifId=ifId, name=name, encap=encap, lcC=lcC,
#                      dn=dn, flags=flags, iplist=iplist, ipobjectlist=ipobjectlist))
#        iplist = []
#        ipobjectlist = []
#    return eplist

if __name__ == '__main__':
    get_Cookie()
    url = """https://localhost/api/class/fvCEp.json?rsp-subtree=full"""
    result, totalamount = GetResponseData(url)
    ce_list = gather_fvCEp_fullinfo(result)
    for ce in ce_list:
        print(ce)
        print(ce.ip)
        print(ce.encap)
        print(ce.fvRsVm)
        print(ce.fvRsCEpToPathEp)
#mac=mac, name=name, encap=encap,
#                 lcC=lcC, dn=dn, fvRsVm=fvRsVmobject, fvRsCEpToPathEp=fvRsCEpToPathEpobject, 
#                 ip=ip, fvRsHyper=fvRsHyperobject, fvIPlist=[]))
#    #url = """https://localhost/api/class/epmMacEp.json?rsp-subtree=full"""
    #result, totalamount = GetResponseData(url)
    #eplist = gether_epm_fullinfo(result)
    #for endpoint in eplist:
    #    print(endpoint.addr)
    #    for ip in endpoint.iplist:
    #        print(ip)




#https://192.168.255.2/api/class/epmMacEp.json?rsp-subtree=full
# leaf directly https://192.168.255.101/api/class/epmMacEp.json?rsp-subtree=full