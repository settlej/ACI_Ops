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
import time
import itertools
import ipaddress
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger(__name__)
logger.setLevel(logging.CRITICAL)

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

class fvCEp():
    def __init__(self, mac=None, name=None, encap=None,
                 lcC=None, dn=None, fvRsVm=None, fvRsHyper=None,
                 fvRsCEpToPathEp=None, ip=None, fvIplist=[]):
        self.mac = mac
        self.name = name
        self.encap = encap
        self.dn = dn
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
                        fvReportingNodes = [node['fvReportingNode']['attributes']['rn'] for node in ceptopath['fvIp']['children'] if node.get('fvReportingNode')]
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
        fvIplist = []
    return eplist


def mac_path_function():
    url = """https://{apic}/api/node/class/fvCEp.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp""".format(apic=apic)
    result = GetResponseData(url,cookie)
    fvCEplist = gather_fvCEp_fullinfo(result)
    return fvCEplist


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    allepglist = get_All_EGPs(apic,cookie)
    allpclist = get_All_PCs(apic,cookie)
    allvpclist = get_All_vPCs(apic,cookie)
    all_leaflist = get_All_leafs(apic,cookie)
    if all_leaflist == []:
        print('\x1b[1;31;40mFailed to retrieve active leafs, make sure leafs are operational...\x1b[0m')
        custom_raw_input('\n#Press enter to continue...')
        return
    while True:
        clear_screen()
        location_banner('Show Endpoints on Interface')
        selection = interface_menu()
        try:
            if selection == '1':
                print("\nSelect leaf(s): ")
                print("\r")
                returnedlist = physical_selection(all_leaflist, apic, cookie)
                #interface =  interfacelist[0].name
                #interfacelist = physical_selection(all_leaflist, allepglist)
                #print(returnedlist)
                #custom_raw_input('#Press enter to continue...')
            elif selection == '2':
                returnedlist = port_channel_selection(allpclist)
                #print(returnedlist)
                #custom_raw_input('#Press enter to continue...')
            elif selection == '3':
                returnedlist = port_channel_selection(allvpclist)
                #print(returnedlist)
        except Exception as e:
            print(e)
            raw_input('Completed. Press enter to return....')

            #custom_raw_input('#Press enter to continue...')

        #all_leaflist = get_All_leafs()
        fvCEplist = mac_path_function()
        #import pdb; pdb.set_trace()
   #     if fvCEplist == []:
        macsfound = 0
        print('{:20}  {:15}  {:25}  {}'.format('MAC', 'Last IP', 'All Live IPs', 'EPG'))
        print('---------------------------------------------------------------------------')
        for x in fvCEplist:
            #print('\t', x.fvRsCEpToPathEp, interfacelist[0])
            if str(x.fvRsCEpToPathEp) == str(returnedlist[0]):
                print("{:20}  {:15}  {:25}  {}".format(x.mac,x.ip,x.fvIplist,x.dn[x.dn.find('/')+1:x.dn.rfind('/')]))
                macsfound +=1
        if macsfound == 0 and selection == '1':
            print("No endpoints found!\n\n**If this interface is part of a PC or VPC on interface please search using interface type pc/vpc")
            raw_input('\n\n#Press enter to return')
        elif macsfound == 0:
            print("No endpoints found!")
            raw_input('\n\n#Press enter to return')
        else:
            raw_input('\nFound {} endpoints.\n\n #Press enter to return...'.format(macsfound))
#def     main():
#        get_Cookie()
#        mac_path_function()

