#!/bin//python

from __future__ import print_function
import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import trace
import logging
import os
import time
import itertools
import threading
import Queue
#import ipaddress
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging
from multiprocessing.dummy import Pool as ThreadPool


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
        self.bd = None
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
    for aepg in result:
        for ep in aepg['fvAEPg']['children']:
            mac = ep['fvCEp']['attributes']['mac']
            name = ep['fvCEp']['attributes']['name']
            encap = ep['fvCEp']['attributes']['encap']
            lcC = ep['fvCEp']['attributes']['lcC']
            dn = ep['fvCEp']['attributes']['dn']
            ip = ep['fvCEp']['attributes']['ip']
            fvRsVmobject = None
            fvRsCEpToPathEpobject = None
            fvRsHyperobject = None
            if ep['fvCEp'].get('children'):
                for ceptopath in ep['fvCEp']['children']:
                    if ceptopath.get('fvIp'): #and ceptopath['fvIP']['attributes']['state'] == 'formed':
                        fvIP_addr = ceptopath['fvIp']['attributes']['addr']
                        fvIP_rn = ceptopath['fvIp']['attributes']['rn']
                        fvIPlist.append(fvIP(addr=fvIP_addr))#, rn=fvIP_rn,#fvReportingNodes=fvReportingNodes))
                    else:
                        fvIPlist = None
            eplist.append(fvCEp(mac=mac, encap=encap, ip=ip, dn=dn, fvIPlist=fvIPlist))
            fvIPlist = []
            iplist = []
            ipobjectlist = []
            fvreportingNodes = []
    return eplist

class fvBD():
    def __init__(self, name=None):
        self.name = name
        self.subnets = []
        self.epgs = []
    def __repr__(self):
        return self.name



def gather_BDs_with_Subnets():
    url = """https://{apic}/api/class/fvBD.json?rsp-subtree=full&rsp-subtree-class=fvSubnet,fvRtBd""".format(apic=apic)
    result = GetResponseData(url, cookie)
    bdlist = []
    for bd in result:
        bdobject = fvBD(bd['fvBD']['attributes']['dn'])
        if bd['fvBD'].get('children'):
            for fvsubnet in bd['fvBD']['children']:
                if fvsubnet.get('fvSubnet'):
                    bdobject.subnets.append(fvsubnet['fvSubnet']['attributes']['ip'])
                if fvsubnet.get('fvRtBd'):
                    bdobject.epgs.append(fvsubnet['fvRtBd']['attributes']['tDn'])
        bdlist.append(bdobject)
    return bdlist


def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Show IPs in BD')
    
        #for epg in 
        #url = """https://{apic}/api/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvIp""".format(apic=apic)
        #url = """https://192.168.255.2/api/node/mo/uni/tn-SI/ap-APP-AD/epg-EPG-VL11-AD.json?rsp-subtree=full&target-subtree-class=fvCEp"""
        #result = GetResponseData(url, cookie)
       # ce_list = gather_fvCEp_fullinfo(result)
        bdlist = gather_BDs_with_Subnets()
        resultlist = []
     #   for bd in bdlist:
     #       for epg in bd.epgs:
     #           url = """https://{apic}/api/node/mo/{epg}.json?rsp-subtree=children""".format(apic=apic,epg=epg)
     #           resultlist.append(GetResponseData(url, cookie))
     #           
     #   for result in resultlist:
     #       #import pdb; pdb.set_trace()
     #      # print(result)
     #       print('\n\n\n')
     #       for fvceps in result[0]['fvAEPg']['children']:
     #           #print(fvceps)
     #           if fvceps.get('fvCEp'):
     #               print(fvceps['fvCEp']['attributes']['name'],fvceps['fvCEp']['attributes']['ip'] )
     #              # for fvcep in fvceps.items():
     #              #     import pdb; pdb.set_trace()
     #              #     print(fvcep.__dict__)
     #                   #if fvcep.get('fvCEp'):
     #                   #    print(fvcep)
     #       #print(result[0]['fvAEPg']['children'][0]['fvCEp'])
     #       #import pdb; pdb.set_trace()
     #       #url = """https://{apic}/api/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvIp""".format(apic=apic)
     #       import pdb; pdb.set_trace()
     #   print('\n')
        print('  {:40}   | {}'.format('Bridge Domain','Subnet(s)'))
        print('  ' + '-' * 60)
        for num,bd in enumerate(bdlist, 1):
            if bd.subnets == []:
                print('  {:3}.) {:36} | {}'.format(num,bd, 'None'))
            else:
                print('  {:3}.) {:36} | {}'.format(num,bd, ', '.join(bd.subnets)))
        while True:
            desiredbd = custom_raw_input('\n  Show all IPs used in which BD?: ')
            if desiredbd.isdigit() and int(desiredbd) > 0 and int(desiredbd) <= len(bdlist):
                break
            else:
                print('\n  \x1b[1;31;40mInvalid option, please try again...\x1b[0m')
                continue
        print('\n')
        epglist = []
        eplist = []
        #for bd in bdlist:
        for epg in bdlist[int(desiredbd)-1].epgs:
            epglist.append(epg)
        pool = ThreadPool(10)
        #for bd in bdlist:
        #    for epg in bd.epgs:
        url = """https://{}/api/node/mo/{}.json?rsp-subtree=children"""
        #print(epglist)
        results = pool.map(lambda x : GetResponseData(url.format(apic,x), cookie), epglist)
       # for x in results:
       #     if x[1] is not None:
       #         print("Error", x[0], x[1])
        pool.close()
        pool.join()
        #import pdb; pdb.set_trace()
        for bd in results:
            for endpoint in bd:
               # import pdb; pdb.set_trace()
                if endpoint['fvAEPg'].get('children'):
                    for ep in endpoint['fvAEPg']['children']:
                        if ep.get('fvCEp'):
                            eplist.append((endpoint['fvAEPg']['attributes']['name'], ep['fvCEp']['attributes']['name'], ep['fvCEp']['attributes']['encap'], ep['fvCEp']['attributes']['ip']))
           #         print(endpoint)
          #          print('\n\n')
     #   for ce in ce_list:
     #       shortdn = '/'.join(ce.dn.split('/')[:-1])
     #       for x in bdlist:
     #           if shortdn in x.epgs:
     #              # print('yes')
     #               ce.bd = x
        try:
            #import pdb; pdb.set_trace()
            for num,ce in enumerate(sorted(eplist, key=lambda x: (int(x[3].split('.')[0]),int(x[3].split('.')[1]),int(x[3].split('.')[2]),int(x[3].split('.')[3]), x[0]))):
                print('  {:3}.) {:23} | {:20} | {:10} | {}'.format(num + 1,ce[0], ce[1], ce[2], ce[3]))
        except:
            import pdb; pdb.set_trace()
        
        ask = custom_raw_input("\n New Search [y]: ") or 'y'
        if ask != '' and ask[0].lower() == 'y':
            continue
        else:
            break










#https://192.168.255.2/api/node/mo/uni/tn-SI.json?query-target=children&target-subtree-class=fvBD&rsp-subtree=full&rsp-subtree-class=fvSubnet,fvRsCtx&subscription=yes&order-by=fvBD.name|