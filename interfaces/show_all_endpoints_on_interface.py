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
from collections import namedtuple
import interfaces.switchpreviewutil as switchpreviewutil
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


class vlanCktEp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.tenant = self.epgDn.split('/')[1].replace('tn-','')
        self.app = lambda x : '/'.join(self.epgDn.split('/')[2:]) if 'LDevInst' in self.epgDn.split('/')[2] else self.epgDn.split('/')[2].replace('ap-','')
        self.epg = '/'.join(self.epgDn.split('/')[3:]).replace('epg-','')
    def __repr__(self):
        if self.name != '':
            return self.name
        else:
            return self.epgDn

class epmMacEp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.ip = []
    def __repr__(self):
        return self.addr
#class fvCEp():
#    def __init__(self, mac=None, name=None, encap=None,
#                 lcC=None, dn=None, fvRsVm=None, fvRsHyper=None,
#                 fvRsCEpToPathEp=None, ip=None, fvIplist=[]):
#        self.mac = mac
#        self.name = name
#        self.encap = encap
#        self.dn = dn
#        self.lcC = lcC
#        self.fvRsVm = fvRsVm
#        self.fvRsHyper = fvRsHyper
#        self.ip = ip
#        #self.iplist = iplist
#        self.fvIplist = fvIplist
#        self.fvRsCEpToPathEp = fvRsCEpToPathEp
#    def __repr__(self):
#        return self.dn
#    def __getitem__(self, mac):
#        if mac in self.mac:
#            return self.mac
#        else:
#            return None
#    def showips(self):
#        iplist = [fvIP.addr for fvIP in self.fvIplist]
#        return ', '.join(iplist)


#class fvIp():
#    def __init__(self, addr=None, rn=None,fvReportingNodes=None):
#        self.addr = addr
#        self.rn = rn
#        self.fvReportingNodes = fvReportingNodes
#    def __repr__(self):
#        return self.addr
#    def __getitem__(self, addr):
#        if addr in self.addr:
#            return self.addr
#        else:
#            return None
#
#class fvRsCEpToPathEp():
#    def __init__(self, tDn=None, lcC=None, fvReportingNodes=[], forceResolve=None):
#        self.lcC = lcC #shows location it learned if 'vmm' vmm knows it cause vmware, 'vmm,learned' means vmware and switch knows, if just 'learned' not vmm source 
#        self.tDn = tDn # location of learned interface "topology/pod-1/paths-102/extpaths-112/pathep-[eth1/25]" example
#        self.fvReportingNodes = fvReportingNodes # looks like port-channels use fvReportingNode api class (describes leafs where ep is discovered)
#        self.forceResolve = forceResolve
#    def __repr__(self):
#        return self.tDn
#
#class fvRsVm():
#    def __init__(self, state=None, tDn=None, dn=None):
#        self.state = state
#        self.dn = dn
#        self.tDn = tDn #internal vm name to lookup vmware vm name
#    def __repr__(self):
#        return self.tDn
#
#class fvRsHyper():
#    def __init__(self, state=None, tDn=None):
#        self.state = state
#        self.tDn = tDn  #hyperviser internal name to look up vmware host name
#    def __repr__(self):
#        return self.tDn

def gather_epmMacEp_fullinfo(macpullresult):
    epmMacEplist = []
    for mac in macpullresult:
        epmMacEpObj = epmMacEp(**mac['epmMacEp']['attributes'])
        if mac['epmMacEp'].get('children'):
            for child in mac['epmMacEp']['children']:
                epmMacEpObj.ip.append(child['epmRsMacEpToIpEpAtt']['attributes']['tDn'].split('/')[-1][4:-1])
        #import pdb; pdb.set_trace()
        epmMacEpObj.tenant_vrf = mac['epmMacEp']['attributes']['dn'].split('/')[4]
        epmMacEpObj.bd = mac['epmMacEp']['attributes']['dn'].split('/')[5]
        epmMacEpObj.encap = mac['epmMacEp']['attributes']['dn'].split('/')[6]
        epmMacEpObj.bd_encap = epmMacEpObj.bd + '/' + epmMacEpObj.encap
        epmMacEpObj.po_interfaces = []
        #epmMacEpObj.shortname = None
        #epmMacEpObj.ethname = None
        epmMacEplist.append(epmMacEpObj)
        #print(epmMacEpObj)
    return epmMacEplist

#def gather_fvCEp_fullinfo(result):
#    eplist = []
#    fvRsVmobject = None
#    fvRsCEpToPathEpobject = None
#    fvRsHyperobject = None
#    fvIplist = []
#    for ep in result:
#        fvReportingNodes = []
#        mac = ep['fvCEp']['attributes']['mac']
#        name = ep['fvCEp']['attributes']['name']
#        encap = ep['fvCEp']['attributes']['encap']
#        lcC = ep['fvCEp']['attributes']['lcC']
#        dn = ep['fvCEp']['attributes']['dn']
#        ip = ep['fvCEp']['attributes']['ip']
#        if ep['fvCEp'].get('children'):
#            for ceptopath in ep['fvCEp']['children']:
#                if ceptopath.get('fvRsCEpToPathEp') and ceptopath['fvRsCEpToPathEp']['attributes']['state'] == 'formed':
#                    fvRsCEpToPathEp_tDn = ceptopath['fvRsCEpToPathEp']['attributes']['tDn']
#                    fvRsCEpToPathEp_lcC = ceptopath['fvRsCEpToPathEp']['attributes']['lcC']
#                    fvRsCEpToPathEp_forceResolve = ceptopath['fvRsCEpToPathEp']['attributes']['forceResolve']
#                    fvRsCEpToPathEpobject = fvRsCEpToPathEp(forceResolve=fvRsCEpToPathEp_forceResolve, 
#                                                            tDn=fvRsCEpToPathEp_tDn, lcC=fvRsCEpToPathEp_lcC)
#                elif ceptopath.get('fvIp'):
#                    fvIp_addr = ceptopath['fvIp']['attributes']['addr']
#                    fvIp_rn = ceptopath['fvIp']['attributes']['rn']
#                    if ceptopath['fvIp'].get('children'):
#                        fvReportingNodes = [node['fvReportingNode']['attributes']['rn'] for node in ceptopath['fvIp']['children'] if node.get('fvReportingNode')]
#                    else:
#                        fvReportingNodes = None
#                    fvIplist.append(fvIp(addr=fvIp_addr, rn=fvIp_rn,
#                                        fvReportingNodes=fvReportingNodes))
#                elif ceptopath.get('fvRsVm') and ceptopath['fvRsVm']['attributes']['state'] == 'formed':
#                    fvRsVm_state = ceptopath['fvRsVm']['attributes']['state']
#                    fvRsVm_tDn = ceptopath['fvRsVm']['attributes']['tDn']
#                    fvRsVmobject = fvRsVm(state=fvRsVm_state,
#                                            tDn=fvRsVm_tDn)
#                elif ceptopath.get('fvRsHyper') and ceptopath['fvRsHyper']['attributes']['state'] == 'formed':
#                    fvRsHyper_state = ceptopath['fvRsHyper']['attributes']['state']
#                    fvRsHyper_tDn = ceptopath['fvRsHyper']['attributes']['tDn']
#                    fvRsHyperobject = fvRsHyper(state=fvRsHyper_state,
#                                                tDn=fvRsHyper_tDn)
#        eplist.append(fvCEp(mac=mac, name=name, encap=encap,
#                                lcC=lcC, dn=dn, fvRsVm=fvRsVmobject, fvRsCEpToPathEp=fvRsCEpToPathEpobject, 
#                                ip=ip, fvRsHyper=fvRsHyperobject, fvIplist=fvIplist))
#        fvIplist = []
#    return eplist


#def mac_path_function():
#    url = """https://{apic}/api/node/class/topology/pod-1/node-101/fvCEp.json?rsp-subtree=full&target-subtree-class=fvCEp,fvRsCEpToPathEp""".format(apic=apic)
#    logger.info(url)
#    result = GetResponseData(url,cookie)
#    fvCEplist = gather_fvCEp_fullinfo(result)
#    return fvCEplist

class pcAggrIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.id

def gather_pclist(result):
    polist = []
    for pc in result:
        currentpcagg = pcAggrIf(**pc['pcAggrIf']['attributes'])
        if pc['pcAggrIf'].get('children'):
            for ethpmAggrif in  pc['pcAggrIf']['children']:
                activephys = ethpmAggrif['ethpmAggrIf']['attributes']['activeMbrs'].split(',')
                currentpcagg.activephys = filter(lambda x: x != 'unspecified', activephys)
        polist.append(currentpcagg)
    return polist

def pull_vlan_info_for_leaf(chosenleafs):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/vlanCktEp.json""".format(apic=apic, leaf=chosenleafs[0])
    logger.info(url)
    result = GetResponseData(url, cookie)
    vlanlist = [vlanCktEp(**x['vlanCktEp']['attributes']) for x in result]
   # import pdb; pdb.set_trace()
    return vlanlist

def pull_bd_info_for_leaf(chosenleafs):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l2BD.json""".format(apic=apic, leaf=chosenleafs[0])
    logger.info(url)
    result = GetResponseData(url, cookie)
    bdlist = [l2BD(**x['l2BD']['attributes']) for x in result]
    return bdlist

def pull_mac_and_ip(chosenleafs):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/epmMacEp.json?rsp-subtree=full""".format(apic=apic, leaf=chosenleafs[0])
    logger.info(url)
    result = GetResponseData(url,cookie)
    epmMacEplist = gather_epmMacEp_fullinfo(result)
    return epmMacEplist

def pull_port_channel_info(chosenleafs):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/pcAggrIf.json?rsp-subtree-class=ethpmAggrIf&rsp-subtree=children""".format(apic=apic, leaf=chosenleafs[0])
    logger.info(url)
    result = GetResponseData(url,cookie)
    pclist = gather_pclist(result)
    return pclist

def pull_all_nonvpc_port_channel_info():
    url = """https://{apic}/api/node/class/pcAggrIf.json?rsp-subtree-class=ethpmAggrIf&rsp-subtree=children""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    pclist = gather_pclist(result)
    return pclist

def get_column_sizes(objlist, *args):
    templist = []
    for column in args:
        nestedlist = False
        c_objlist = filter(lambda x: hasattr(x, column), objlist)
        if c_objlist == [] or c_objlist == None:
            import pdb; pdb.set_trace()
        currentcolumnmaxobj = max(c_objlist, key=lambda x: len(getattr(x, column)))
        if type(getattr(currentcolumnmaxobj, column)) == list:
            currentcolumnmaxobj = max(c_objlist, key=lambda x: len(','.join(getattr(x, column))))
            #import pdb; pdb.set_trace()
            #rowlistmax = 0
            #for row in currentcolumnmaxobj.ip:
            #    import pdb; pdb.set_trace()
            #    currentlistmax = len(row)
            #    if currentlistmax == rowlistmax:
            #        continue
            #    elif currentlistmax > rowlistmax:
            #        rowlistmax = len(row)
            #    elif currentlistmax < rowlistmax:
            #        rowlistmax = len(row)
            #    else:
            #        rowlistmax = len(row)
            insidelistmax = len(','.join(currentcolumnmaxobj.ip))
            #for insideobj in getattr(currentcolumnmaxobj, column):
            #insidelistmaxobj = max(columnlist, key=lambda x: len(str(x)))
            #import pdb; pdb.set_trace()
            nestedlist = True
        if nestedlist:
            templist.append(insidelistmax)
            #templist.append((column, insidelistmax))
        else:
            templist.append( len(getattr(currentcolumnmaxobj, column)))
            #templist.append((column, len(getattr(currentcolumnmaxobj, column))))
        #import pdb; pdb.set_trace()
    #columnsizes = namedtuple('columnsizes', ','.join(*args))
    #import pdb; pdb.set_trace()
    return templist

class endpoint():
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return ';'.join((self.addr,self.ifId,self.encap))

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    allepglist = get_All_EGPs(apic,cookie)
    allpclist = get_All_PCs(apic,cookie)
    allvpclist = get_All_vPCs(apic,cookie)
    all_leaflist = get_All_leafs(apic,cookie)
    url = """https://{apic}/api/node/class/fvBD.json""".format(apic=apic)
    logger.info(url)
    bdresult = GetResponseData(url, cookie)
    if all_leaflist == []:
        print('\x1b[1;31;40mFailed to retrieve active leafs, make sure leafs are operational...\x1b[0m')
        custom_raw_input('\n#Press enter to continue...')
        return
    while True:
        clear_screen()
        location_banner('Show Endpoints on Interface')
        #selection = interface_menu()
        try:
            #if selection == '1':
                print("\nSelect leaf(s): ")
                print("\r")
                while True:
                    chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
                    if len(chosenleafs) > 1:
                        print('\n\x1b[1;31;40mOnce leaf supported at this time, please try again...\x1b[0m')
                        print('\r')
                    else:
                        break
                switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
               # import pdb; pdb.set_trace()
                returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
                #import pdb; pdb.set_trace()
                #returnedlist = physical_selection(all_leaflist, apic, cookie)
                #interface =  interfacelist[0].name
                #interfacelist = physical_selection(all_leaflist, allepglist)
                #print(returnedlist)
                #custom_raw_input('#Press enter to continue...')
                epmMacEplist = pull_mac_and_ip(chosenleafs)
                epmMacEplist = [x for x in epmMacEplist if 'tunnel' not in x.ifId]
                if epmMacEplist == []:
                    print('\n\x1b[1;31;40mNo Endpoints found on interfaces\x1b[0m\n')
                    custom_raw_input('#Press Enter to continue...')
                    continue
                else:
                    polist = pull_port_channel_info(chosenleafs)
                    for po in polist:
                        for epmmacep in epmMacEplist:
                            if po.id == epmmacep.ifId:
                                epmmacep.physlocation = po.activephys
                    #print(chosenleafs)
                    vlanlist = pull_vlan_info_for_leaf(chosenleafs)
                    for x in epmMacEplist:
                        found = False
                        for vlan in vlanlist:
                            #rint(x.bd_encap, vlan.dn)
                            #if x.encap == 'db-ep':
                            #    #import pdb; pdb.set_trace()
                            #    #if x.bd in vlan.dn:
                            #    
                            #    print(x.bd, vlan.tenant, vlan.encap, vlan.name, vlan.dn, vlan.epgDn)
                                #x.foundvlan = vlan.name
                            if x.bd_encap in vlan.dn:
                                x.foundvlan = vlan.name
                                x.encap = x.encap.replace('vlan-[','')[:-1]
                                found = True
                        if not found:
                            bdfound = False
                            for v in bdresult:
                                bd = x.bd[x.bd.rfind('[')+1:-1].replace('vxlan-','')
                                if bd in v['fvBD']['attributes']['seg']:
                                    x.foundvlan = v['fvBD']['attributes']['dn'].replace('tn-','')[4:]
                                    x.encap = ''
                                    bdfound = True
                            if bdfound == False:
                                x.foundvlan = ''
                                    #print('hit')
            
                            #url = """https://{apic}/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.mac,"{addr}")""".format(apic=apic,addr=x.addr)
                            #result = GetResponseData(url, cookie)
                            #x.foundvlan = ':'.join(result[0]['fvCEp']['attributes']['dn'].split('/')[1:4]).replace('tn-','').replace('ap-','').replace('epg-','')
                                    
            
                    macsfound = 0
                    desiredlist = map(lambda x: x.dn, returnedlist)
                    endpointlist = []
                    #print(len(epmMacEplist))
                    for macep in epmMacEplist:
                        if hasattr(macep, 'physlocation'):
                            for location in macep.physlocation:
                              #  import pdb; pdb.set_trace()
                                #for port in macep.activephys:
                                ethname = location
                                if ethname.count('/') > 1:
                                    shortname = ''.join(ethname.split('/')[-2:])
                                else:
                                    shortname = ethname[ethname.rfind('/')+1:]
                                endpointlist.append(endpoint(ethname=ethname,shortname=shortname,**macep.__dict__))
                        else:
                            ethname = macep.ifId
                            if ethname.count('/') > 1:
                                shortname = ''.join(ethname.split('/')[-3:]).replace('eth','')
                            else:
                                shortname = ethname[ethname.rfind('/')+1:]
                            endpointlist.append(endpoint(ethname=ethname,shortname=shortname,**macep.__dict__))
                    filteredlist = []
                    for endp in endpointlist:
                        if endp.ethname.count('/') > 1:
                            localethname = 'eth' + '/'.join(endp.ethname.split('/')[-2:])
                            expaths = endp.ethname.split('/')[0][3:]
                            topology = ('/'.join(endp.dn.split('/')[:3]) + '/extpaths-' + expaths + '/pathep-[' + localethname + ']').replace('node-','paths-')
                        else:
                            topology = ('/'.join(endp.dn.split('/')[:3]) + '/pathep-[' + endp.ethname + ']').replace('node-','paths-')
                        if topology in desiredlist:
                            filteredlist.append(endp)
                    columnwidthfind = ('ethname','addr','foundvlan','encap','ifId','ip')
                    sizes = get_column_sizes(filteredlist, *columnwidthfind)
                    print('{:{inter}}  {:{mac}}  {:{epg}}  {:{encap}}  {:{po}}  {:{ip}}'.format('Interface', 'MAC', 'EPG', 'Encap', 'Po #', 'IP',inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
                    print('{:-<{inter}}  {:-<{mac}}  {:-<{epg}}  {:-<{encap}}  {:-<{po}}  {:-<{ip}}'.format('', '', '', '', '', '',inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
                    #import pdb; pdb.set_trace()
                    for ep in sorted(filteredlist, key=lambda x : int(x.shortname)):
                        if 'po' in ep.ifId:
                            macsfound += 1
                            print('{:{inter}}  {:{mac}}  {:{epg}}  {:{encap}}  {:{po}}  {:{ip}}'.format(ep.ethname,ep.addr,ep.foundvlan,ep.encap,ep.ifId,','.join(ep.ip),inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
                        else:
                            macsfound += 1
                            print('{:{inter}}  {:{mac}}  {:{epg}}  {:{encap}}  {:{po}}  {:{ip}}'.format(ep.ethname,ep.addr,ep.foundvlan,ep.encap,'',','.join(ep.ip),inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
                    if macsfound == 0 and selection == '1':
                        print("No endpoints found!\n\n**If this interface is part of a PC or VPC on interface please search using interface type pc/vpc")
                        #import pdb; pdb.set_trace()
                        raw_input('\n#Press enter to continue...')
                    elif macsfound == 0:
                        print("No endpoints found!")
                        raw_input('\n#Press enter to continue...')
                    elif macsfound == 1:
                        print('\nFound {} endpoint.\n'.format(macsfound))
                        raw_input('\n#Press enter to continue...')
                    else:
                        print('\nFound {} endpoint.\n'.format(macsfound))
                        raw_input('\n#Press enter to continue...')
                   #     raw_input('\nFound {} endpoints.\n\n#Press enter to return...'.format(macsfound))

            #elif selection == '2':
            #    returnedlist = port_channel_selection(allpclist)
            #    pclist = pull_all_nonvpc_port_channel_info()
            #    #pclistname = map(lambda x: str(x.name), pclist)
            #    pcnamelist = map(lambda x: str(x.name), returnedlist)
            #    filteredlist = [x for x in pclist if str(x.name) in pcnamelist]
            #    import pdb; pdb.set_trace()
#
            #    #print(returnedlist)
            #    #epmMacEplist = pull_mac_and_ip(chosenleafs)
            #    #epmMacEplist = [x for x in epmMacEplist if 'tunnel' not in x.ifId]
            #    #if epmMacEplist == []:
            #    #    print('\n\x1b[1;31;40mNo Endpoints found on interfaces\x1b[0m\n')
            #    #    custom_raw_input('#Press Enter to continue...')
            #    #    continue
            #    #else:
            #    #    polist = pull_port_channel_info(chosenleafs)
            #    #    for po in polist:
            #    #        for epmmacep in epmMacEplist:
            #    #            if po.id == epmmacep.ifId:
            #    #                epmmacep.physlocation = po.activephys
            #    #    #print(chosenleafs)
            #    #    vlanlist = pull_vlan_info_for_leaf(chosenleafs)
            #    #    for x in epmMacEplist:
            #    #        found = False
            #    #        for vlan in vlanlist:
            #    #            #rint(x.bd_encap, vlan.dn)
            #    #            #if x.encap == 'db-ep':
            #    #            #    #import pdb; pdb.set_trace()
            #    #            #    #if x.bd in vlan.dn:
            #    #            #    
            #    #            #    print(x.bd, vlan.tenant, vlan.encap, vlan.name, vlan.dn, vlan.epgDn)
            #    #                #x.foundvlan = vlan.name
            #    #            if x.bd_encap in vlan.dn:
            #    #                x.foundvlan = vlan.name
            #    #                x.encap = x.encap.replace('vlan-[','')[:-1]
            #    #                found = True
            #    #        if not found:
            #    #            bdfound = False
            #    #            for v in bdresult:
            #    #                bd = x.bd[x.bd.rfind('[')+1:-1].replace('vxlan-','')
            #    #                if bd in v['fvBD']['attributes']['seg']:
            #    #                    x.foundvlan = v['fvBD']['attributes']['dn'].replace('tn-','')[4:]
            #    #                    x.encap = ''
            #    #                    bdfound = True
            #    #            if bdfound == False:
            #    #                x.foundvlan = ''
            #    #                    #print('hit')
            ##
            #    #            #url = """https://{apic}/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.mac,"{addr}")""".format(apic=apic,addr=x.addr)
            #    #            #result = GetResponseData(url, cookie)
            #    #            #x.foundvlan = ':'.join(result[0]['fvCEp']['attributes']['dn'].split('/')[1:4]).replace('tn-','').replace('ap-','').replace('epg-','')
            #    #                    
            ##
            #    #    macsfound = 0
            #    #    import pdb; pdb.set_trace()
            #    #    desiredlist = map(lambda x: x.dn, returnedlist)
            #    #    endpointlist = []
            #    #    #print(len(epmMacEplist))
            #    #    for macep in epmMacEplist:
            #    #        if hasattr(macep, 'physlocation'):
            #    #            for location in macep.physlocation:
            #    #              #  import pdb; pdb.set_trace()
            #    #                #for port in macep.activephys:
            #    #                ethname = location
            #    #                if ethname.count('/') > 1:
            #    #                    shortname = ''.join(ethname.split('/')[-2:])
            #    #                else:
            #    #                    shortname = ethname[ethname.rfind('/')+1:]
            #    #                endpointlist.append(endpoint(ethname=ethname,shortname=shortname,**macep.__dict__))
            #    #        else:
            #    #            ethname = macep.ifId
            #    #            if ethname.count('/') > 1:
            #    #                shortname = ''.join(ethname.split('/')[-3:]).replace('eth','')
            #    #            else:
            #    #                shortname = ethname[ethname.rfind('/')+1:]
            #    #            endpointlist.append(endpoint(ethname=ethname,shortname=shortname,**macep.__dict__))
            #    #    filteredlist = []
            #    #    for endp in endpointlist:
            #    #        if endp.ethname.count('/') > 1:
            #    #            localethname = 'eth' + '/'.join(endp.ethname.split('/')[-2:])
            #    #            expaths = endp.ethname.split('/')[0][3:]
            #    #            topology = ('/'.join(endp.dn.split('/')[:3]) + '/extpaths-' + expaths + '/pathep-[' + localethname + ']').replace('node-','paths-')
            #    #        else:
            #    #            topology = ('/'.join(endp.dn.split('/')[:3]) + '/pathep-[' + endp.ethname + ']').replace('node-','paths-')
            #    #        if topology in desiredlist:
            #    #            filteredlist.append(endp)
            #    #    columnwidthfind = ('ethname','addr','foundvlan','encap','ifId','ip')
            #    #    sizes = get_column_sizes(filteredlist, *columnwidthfind)
            #    #    print('{:{inter}}  {:{mac}}  {:{epg}}  {:{encap}}  {:{po}}  {:{ip}}'.format('Interface', 'MAC', 'EPG', 'Encap', 'Po #', 'IP',inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
            #    #    print('{:-<{inter}}  {:-<{mac}}  {:-<{epg}}  {:-<{encap}}  {:-<{po}}  {:-<{ip}}'.format('', '', '', '', '', '',inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
            #    #    #import pdb; pdb.set_trace()
            #    #    for ep in sorted(filteredlist, key=lambda x : int(x.shortname)):
            #    #        if 'po' in ep.ifId:
            #    #            macsfound += 1
            #    #            print('{:{inter}}  {:{mac}}  {:{epg}}  {:{encap}}  {:{po}}  {:{ip}}'.format(ep.ethname,ep.addr,ep.foundvlan,ep.encap,ep.ifId,','.join(ep.ip),inter=sizes[0]+4,mac=sizes[1],epg=sizes[2],encap=sizes[3],po=sizes[4],ip=sizes[5]))
            #    #    if macsfound == 0 and selection == '1':
            #    #        print("No endpoints found!\n\n**If this interface is part of a PC or VPC on interface please search using interface type pc/vpc")
            #    #        #import pdb; pdb.set_trace()
            #    #        raw_input('\n#Press enter to continue...')
            #    #    elif macsfound == 0:
            #    #        print("No endpoints found!")
            #    #        raw_input('\n#Press enter to continue...')
            #    #    elif macsfound == 1:
            #    #        print('\nFound {} endpoint.\n'.format(macsfound))
            #    #        raw_input('\n#Press enter to continue...')
            #    #    else:
            #    #        print('\nFound {} endpoint.\n'.format(macsfound))
            #    #        raw_input('\n#Press enter to continue...')
            #    #   #     raw_input('\nFound {} endpoints.\n\n#Press enter to return...'.format(macsfound))
            #elif selection == '3':
            #    returnedlist = port_channel_selection(allvpclist)
            #    #print(returnedlist)
        except Exception as e:
            print(e)
            raw_input('Completed. Press enter to return....')


    
          #  macsfound = 0
          #  print('{:20}  {:15}  {:25}  {}'.format('MAC', 'Last IP', 'All Live IPs', 'EPG'))
          #  print('---------------------------------------------------------------------------')
          #  for x in fvCEplist:
          #      #print('\t', x.fvRsCEpToPathEp, interfacelist[0])
          #      if str(x.fvRsCEpToPathEp) == str(returnedlist[0]):
          #          print("{:20}  {:15}  {:25}  {}".format(x.mac,x.ip,x.fvIplist,x.dn[x.dn.find('/')+1:x.dn.rfind('/')]))
          #          macsfound +=1
          #  if macsfound == 0 and selection == '1':
          #      print("No endpoints found!\n\n**If this interface is part of a PC or VPC on interface please search using interface type pc/vpc")
          #      import pdb; pdb.set_trace()
          #      raw_input('\n\n#Press enter to return')
          #  elif macsfound == 0:
          #      print("No endpoints found!")
          #      raw_input('\n\n#Press enter to return')
          #  else:
          #      raw_input('\nFound {} endpoints.\n\n #Press enter to return...'.format(macsfound))
    #def     main():
    #        get_Cookie()
    #        mac_path_function()
    
    