#!/bin//python

from __future__ import print_function 
import re
try:
    import readline
except:
    pass
import urllib2
import time
import json
import ssl
import os
import datetime
import itertools
#import trace
#import pdb
import random
import threading
import Queue
from collections import namedtuple
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging
from operator import attrgetter
from collections import Counter
from multiprocessing.dummy import Pool as ThreadPool


# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)

class policy_group():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.policies = {}
    def __setitem__(self, k,v):
        setattr(self, k, v)
    def __repr__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return self


class l1PrioFlowCtrlP():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsQosEgressDppIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsLldpIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsMonPolIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsStpIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsQosIngressDppIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsL2PortSecurityCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsStormctrlIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsL3IfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsMacsecPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsDwdmIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsMcpIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsL2IfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsFcIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsQosSdIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsCoppIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsHIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsQosPfcIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsCdpIfPolCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self
class l1RsAttEntityPCons():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        if hasattr(self, 'tDn'):
            return self.tDn
        else:
            return self


#infraRsAttEntP
#infraRsCdpIfPol
#infraRsCoppIfPol
#infraRsLldpIfPol
#infraRsFcIfPol
#infraRsMcpIfPol
#infraRsMonIfInfraPol
#infraRsDwdmIfPol
#infraRsHIfPol
#infraRsL2IfPol
#infraRsL2PortAuthPol
#infraRsQosSdIfPol
#infraRsStpIfPol
#infraRsQosIngressDppIfPol
#infraRsQosPfcIfPol
#infraRtAccBaseGrp
#infraRsMacsecIfPol
#infraRsQosDppIfPol
#infraRsStormctrlIfPol
#infraRsQosEgressDppIfPol
#infraRsL2PortSecurityPol
#infraRsAttEntP,infraRsCdpIfPol,infraRsHIfPol,infraRsLldpIfPol,infraRsMonIfInfraPol
class policy_row():
    column_order = {
       'column1'  : 'infraRsAttEntP',
       'column2'  : 'infraRsCdpIfPol',
       #'column3'  : 'infraRsCoppIfPol',
       #'column4'  : 'l1RsDwdmIfPolCons',
       'column3'  : 'infraRsFcIfPol',
       'column4'  : 'infraRsHIfPol',
       #'column7'  : 'l1RsL2IfPolCons',
       #'column8'  : 'l1RsL2PortSecurityCons',
       #'column9'  : 'l1RsL3IfPolCons',
       'column5' : 'infraRsLldpIfPol',
       #'column11' : 'l1RsMacsecPolCons',
      # 'column7' : 'infraRsMcpIfPol',
       'column6' : 'infraRsMonIfInfraPol',
       #'column14' : 'l1RsQosEgressDppIfPolCons',
       #'column15' : 'l1RsQosIngressDppIfPolCons',
       #'column16' : 'l1RsQosPfcIfPolCons',
       #'column17' : 'l1RsQosSdIfPolCons',
       #'column18' : 'l1RsStormctrlIfPolCons',
       #'column19' : 'l1RsStpIfPolCons'
       }
    def __init__(self, obj):
        self.name = obj.name
        self.num = obj.num
        self.column1 = '' 
        self.column2 = ''
        self.column3 = ''
        self.column4 = ''
        self.column5 = ''
        self.column6 = ''
        self.column7 = ''
        self.column8 = ''
        self.column9 = ''
        self.column10 =''
        self.column11 =''
        self.column12 =''
        self.column13 =''
        self.column14 =''
        self.column15 =''
        self.column16 =''
        self.column17 =''
        self.column18 =''
        self.column19 =''
        for num, column in enumerate(sorted(obj.policies.items())):
            if policy_row.column_order.get('column' + str(num+1)):
                if obj.policies.get(policy_row.column_order['column' + str(num+1)]):
                    insideobj = obj.policies[policy_row.column_order['column' + str(num+1)]] 
                    if 'uni' in str(insideobj):
                        self['column' + str(num+1)] = str(insideobj)[str(insideobj).find('-')+1:]
                    else:
                        self['column' + str(num+1)] = str(insideobj)
    def __setitem__(self, k,v):
        setattr(self, k, v)
    def __getitem__(self,k):
        return getattr(self,k)

class infraNodeP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.infraRsAccPortPlist = []
        self.infraLeafSlist = []
        self.allleafs = None
        self.leafprofiles = []
        self.fexprofiles = []
    def gatherallleafs(self):
        infraranges = []
        for local_infraNodeBlk in self.infraLeafSlist:
            for x in local_infraNodeBlk.infraNodeBlklist:
                infraranges.extend(range(int(x.from_), int(x.to_) + 1))
        allranges = list(set(infraranges))
        self.allleafs = allranges
        infraranges = []
        allranges = []
    def __repr__(self):
        return self.dn

class infraAccPortP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.foundfex = []
        self.infraRtAccPortPlist = []
        self.infraHPortSlist = []
        self.allports = {1:[]}
    def __repr__(self):
        return self.dn

def gather_infraNodeP(apic,cookie):
    url = """https://{apic}/api/node/class/infraNodeP.json?rsp-subtree=full""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    infraNodePlist = []
    infraNodePdict = {}
    for infrnodep in result:
        tempNodeP = infraNodeP(**infrnodep['infraNodeP']['attributes'])
        if infrnodep['infraNodeP'].get('children'):
            for child in infrnodep['infraNodeP']['children']:
                if child.get('infraRsAccPortP'):
                    tempNodeP.infraRsAccPortPlist.append(infraRsAccPortP(**child['infraRsAccPortP']['attributes']))
                elif child.get('infraLeafS'):
                    tempinfraLeafS = infraLeafS(**child['infraLeafS']['attributes'])
                    if child['infraLeafS'].get('children'):
                        for blocks in child['infraLeafS']['children']:
                            tempinfraLeafS.infraNodeBlklist.append(infraNodeBlk(**blocks['infraNodeBlk']['attributes']))
                    tempNodeP.infraLeafSlist.append(tempinfraLeafS)
        tempNodeP.gatherallleafs()
        infraNodePlist.append(tempNodeP)
        infraNodePdict[tempNodeP.dn] = tempNodeP
    return infraNodePlist, infraNodePdict



def gather_infraAccPortP(apic,cookie,fexes):
    url = """https://{apic}/api/node/class/infraAccPortP.json?rsp-subtree=full""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    infraAccPortPlist = []
    for outerobject in result:
        tempAccp = infraAccPortP(**outerobject['infraAccPortP']['attributes'])
        if outerobject['infraAccPortP'].get('children'):
            for child in outerobject['infraAccPortP']['children']:
                if child.get('infraRtAccPortP'):
                    tempAccp.infraRtAccPortPlist.append(infraRtAccPortP(**child['infraRtAccPortP']['attributes']))
                elif child.get('infraHPortS'):
                    tempinfraaHPortS = infraHPortS(**child['infraHPortS']['attributes'])
                    if child['infraHPortS'].get('children'):
                        for blocks in child['infraHPortS']['children']:
                            if blocks.get('infraRsAccBaseGrp'):
                                tempinfraaHPortS.infraRsAccBaseGrp = infraRsAccBaseGrp(**blocks['infraRsAccBaseGrp']['attributes'])
                                if blocks['infraRsAccBaseGrp']['attributes']['tCl'] == "infraFexBndlGrp":
                                    fexbndlgrppath = blocks['infraRsAccBaseGrp']['attributes']['tDn']# (ending) -> -> Fexp/infrafexbndlgrp.rn
                                    fexp = '/'.join(fexbndlgrppath.split('/')[:-1])
                                    fexbndlgp = fexbndlgrppath.split('/')[-1:][0]
                                    foundp = searchfexes(fexp,fexbndlgp,fexes)
                                    tempinfraaHPortS.infraFexPlist.append(foundp)
                            elif blocks.get('infraPortBlk'):
                                module = list(xrange(int(blocks['infraPortBlk']['attributes']['fromCard']), int(blocks['infraPortBlk']['attributes']['toCard'])+1))
                                portrange = list(xrange(int(blocks['infraPortBlk']['attributes']['fromPort']), int(blocks['infraPortBlk']['attributes']['toPort'])+1))
                                #print(portrange)
                                for linecard in module:
                                    tempAccp.allports[linecard].extend(portrange)
#                                for linecard in module:
                                    tempAccp.allports[linecard].sort()
                                tempinfraaHPortS.infraPortsBlklist.append(infraPortBlk(**blocks['infraPortBlk']['attributes']))
                    tempAccp.infraHPortSlist.append(tempinfraaHPortS)
        infraAccPortPlist.append(tempAccp)
    return infraAccPortPlist

class infraLeafS():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.infraNodeBlklist = []
class infraRsAccPortP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
class infraNodeBlk():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class infraHPortS():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.infraPortsBlklist = []
        self.infraRsAccBaseGrp = None
        self.infraFexPlist = []

class infraRsAccBaseGrp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
class infraPortBlk():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
class infraRtAccPortP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class leafprofile():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class infraFexBndlGrp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.infraRtAccBaseGrplist = []

class infraRtAccBaseGrp():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def gather_infraFexP(apic,cookie):
    url = """https://{apic}/api/node/class/infraFexP.json?rsp-subtree=full""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    infraFexPlist = []
    for outerobject in result:
        tempFex = infraFexP(**outerobject['infraFexP']['attributes'])
        if outerobject['infraFexP'].get('children'):
            for child in outerobject['infraFexP']['children']:
                if child.get('infraRtAccPortP'):
                    tempFex.infraRtAccPortPlist.append(infraRtAccPortP(**child['infraRtAccPortP']['attributes']))
                elif child.get('infraHPortS'):
                    tempinfraaHPortS = infraHPortS(**child['infraHPortS']['attributes'])
                    if child['infraHPortS'].get('children'):
                        for blocks in child['infraHPortS']['children']:
                            if blocks.get('infraRsAccBaseGrp'):
                                tempinfraaHPortS.infraRsAccBaseGrp = infraRsAccBaseGrp(**blocks['infraRsAccBaseGrp']['attributes'])
                            elif blocks.get('infraPortBlk'):
                                module = list(xrange(int(blocks['infraPortBlk']['attributes']['fromCard']), int(blocks['infraPortBlk']['attributes']['toCard'])+1))
                                portrange = list(xrange(int(blocks['infraPortBlk']['attributes']['fromPort']), int(blocks['infraPortBlk']['attributes']['toPort'])+1))
                                for linecard in module:
                                    tempFex.allports[linecard].extend(portrange)
                                    tempFex.allports[linecard].sort()
                                tempinfraaHPortS.infraPortsBlklist.append(infraPortBlk(**blocks['infraPortBlk']['attributes']))
                    tempFex.infraHPortSlist.append(tempinfraaHPortS)
                elif child.get('infraFexBndlGrp'):
                    tempinfraFexBndlGrp = infraFexBndlGrp(**child['infraFexBndlGrp']['attributes'])
                    if child['infraFexBndlGrp'].get('children'):
                        for subchild in child['infraFexBndlGrp'].get('children'):
                            if subchild.get('infraRtAccBaseGrp'):
                                tempinfraFexBndlGrp.infraRtAccBaseGrplist.append(infraRtAccBaseGrp(**subchild['infraRtAccBaseGrp']['attributes']))
                    tempFex.infraFexBndlGrplist.append(tempinfraFexBndlGrp)

        infraFexPlist.append(tempFex)
    return infraFexPlist

class infraFexP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.infraFexPlist = []
        self.infraHPortSlist = []
        self.infraFexBndlGrplist = []
        self.allports = {1:[]}
    def __repr__(self):
        return self.dn

def searchfexes(fexp,fexbndlgp,fexes):
    for f in fexes:
        #import pdb; pdb.set_trace()
        if f.dn == fexp:
            if f.infraFexBndlGrplist:
                for child in f.infraFexBndlGrplist:
                    if child.rn == fexbndlgp:
                        return f


class pc_policy_row(policy_row):
    def __repr__(self):
        return self.name

def gather_portchannel_policygroups(apic,cookie):
    url = """https://{apic}/api/node/class/infraAccBndlGrp.json?rsp-subtree=full&rsp-subtree-class=infraRsAttEntP,""".format(apic=apic) \
            + """infraRsCdpIfPol,infraRsHIfPol,infraRsLldpIfPol,infraRsMonIfInfraPol"""
    result = GetResponseData(url, cookie)
    policygrouplist = []
    finallist = []
    for num,policy in enumerate(result,1):
        currentpolicygroup = policy_group(policy['infraAccBndlGrp']['attributes'])
        currentpolicygroup.num = '{}.)'.format(num)
        if policy['infraAccBndlGrp'].get('children'):
            for children in policy['infraAccBndlGrp']['children']:
                for child in children:
                    currentpolicygroup.policies[child] = children[child]['attributes']['tDn']
        policygrouplist.append(currentpolicygroup)
        #import pdb; pdb.set_trace()
    for group in policygrouplist:
        finallist.append(pc_policy_row(group))
    return finallist

def gather_physical_policygroups(apic, cookie):
    url = """https://{apic}/api/node/class/infraAccPortGrp.json?rsp-subtree=full""".format(apic=apic)
    result = GetResponseData(url, cookie)
    policygrouplist = []
    finallist = []
    for num,policy in enumerate(result,1):
        currentpolicygroup = policy_group(policy['infraAccPortGrp']['attributes'])
        currentpolicygroup.num = '{}.)'.format(num)
        if policy['infraAccPortGrp'].get('children'):
            for children in policy['infraAccPortGrp']['children']:
                for child in children:
                    currentpolicygroup.policies[child] = children[child]['attributes']['tDn']
        policygrouplist.append(currentpolicygroup)
    for group in policygrouplist:
        finallist.append(policy_row(group))
    return finallist


def displaypolicycolumns(grouplist,display_clone=True):
    columnwidthfind = ('num,','name','column1','column2','column3','column4','column5','column6')
    headers = ('#','Policy Group','AAEP','CDP','Fiber-Channel','Link Level','LLDP','Monitor')
    sizes = get_column_sizes(grouplist, columnwidthfind, minimum=5, baseminimum=headers)
    print('        ' + '-'* (sum(sizes)-5))
    topstring = '   {:{num}} {:{policygroup}} | {:{aaep}} | {:{cdp}} | {:{ll}} | {:{lldp}} | {:{mon}} |'
    topstring = topstring.format('#','Policy Group', 'AAEP','CDP','Link Level','LLDP','Monitor',
                num=sizes[0],policygroup=sizes[1],aaep=sizes[2],cdp=sizes[3],ll=sizes[5],lldp=sizes[6],mon=sizes[7])
    print(topstring)
    print('   {:{num}} {:-<{policygroup}} | {:-<{aaep}} | {:-<{cdp}} | {:-<{ll}} | {:-<{lldp}} | {:-<{mon}} |'.format(
        '','','','','','','',num=sizes[0],policygroup=sizes[1],aaep=sizes[2],cdp=sizes[3],ll=sizes[5],lldp=sizes[6],mon=sizes[7]))
    rowstring =''
    for num,row in enumerate(grouplist,1):
        if rowstring == '':
            #import pdb; pdb.set_trace()
            rowstring += '   {:{numsize}} {:{policygroup}} |'.format(row.num,row.name,numsize=sizes[0],policygroup=sizes[1])
        rowstring += ' {:{aaep}} |'.format(str(row.column1),aaep=sizes[2])
        rowstring += ' {:{cdp}} |'.format(str(row.column2),cdp=sizes[3])
       # rowstring += ' {:{fc}} |'.format(str(row.column3),fc=sizes[3])
        rowstring += ' {:{ll}} |'.format(str(row.column4),ll=sizes[5])
        rowstring += ' {:{lldp}} |'.format(str(row.column5),lldp=sizes[6])
        rowstring += ' {:{mon}} |'.format(str(row.column6),mon=sizes[7])
        print(rowstring)
        rowstring =''
    if display_clone:
        print('\n   {:{num}} {:{policygroup}}   {:{aaep}}   {:{cdp}}   {:{ll}}   {:{lldp}}   {:{mon}}'.format(
            str(len(grouplist) + 1)+ '.)','[CLONE POLICY]','','','','','',num=sizes[0],policygroup=sizes[1],aaep=sizes[2],cdp=sizes[3],ll=sizes[5],lldp=sizes[6],mon=sizes[7]))

def retrieve_leafprofiles(apic, cookie):
    url = """https://{apic}/api/node/class/infraAccPortP.json""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    return result

def retrieve_fexprofiles(apic, cookie):
    url = """https://{apic}/api/node/class/infraFexP.json""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    return result

def display_APS_for_leafProfile(leafp, include_create=True):
        apslist = []
        if leafp[5].infraHPortSlist != []:
            for aps in sorted(leafp[5].infraHPortSlist, key=lambda x: x.name.lower()):
                tempfromtocard_fromtoport_set = set()
                #import pdb; pdb.set_trace()
                for portblklist in aps.infraPortsBlklist:
                    if portblklist.fromCard == portblklist.toCard and portblklist.fromPort == portblklist.toPort:
                        tempfromtocard_fromtoport_set.add('{}/{}'.format(portblklist.fromCard,portblklist.fromPort))
                    elif portblklist.fromCard == portblklist.toCard:
                        tempfromtocard_fromtoport_set.add('{}/{}-{}'.format(portblklist.fromCard,portblklist.fromPort,portblklist.toPort))
                    elif portblklist.fromCard != portblklist.toCard:
                        tempfromtocard_fromtoport_set.add('{}/{}-{}/{}'.format(portblklist.fromCard,portblklist.toCard,portblklist.toCard,portblklist.toPort))
                if 'accportgrp-' in aps.infraRsAccBaseGrp.tDn:
                    apslist.append((aps.name, ','.join(sorted(list(tempfromtocard_fromtoport_set))), aps.infraRsAccBaseGrp.tDn[aps.infraRsAccBaseGrp.tDn.find('accportgrp-')+11:], aps.descr, aps))
                else:      
                    apslist.append((aps.name, ','.join(sorted(list(tempfromtocard_fromtoport_set))), aps.infraRsAccBaseGrp.tDn[aps.infraRsAccBaseGrp.tDn.find('accbundle-')+10:], aps.descr, aps))
            print('     [Displaying "{leafp}" APS list]'.format(leafp=leafp[0]))
            headers = ('Access Port Selector','Interfaces','Policy','Description')
            sizes = get_column_sizes(apslist, minimum=5, baseminimum=headers)
            print('     ' + '-' * (sum(sizes) + 14))
            print('     {:{num}} {:{apsname}} | {:{inter}} | {:{policy}} | {:{descr}}'.format('#',*headers,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('     {:-<{num}} {:-<{apsname}} | {:-<{inter}} | {:-<{policy}} | {:-<{descr}}'.format('','','','','',num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            for number,aps in enumerate(apslist,1):
                print('     {:{num}} {:{apsname}} | {:{inter}} | {:{policy}} | {:{descr}}'.format('{}.)'.format(number),*aps,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('')
            if include_create:
                print('     {:{num}} [CREATE NEW APS]'.format('{}.)'.format(int(number) + 1),num=len('{}.)'.format(len(apslist)))))
        else:
            print('[Displaying "{leafp}" APS list]'.format(leafp=leafp[0]))
            headers = ('Access Port Selector','Interfaces','Description')
            sizes = get_column_sizes(apslist, minimum=5, baseminimum=headers)
            print('     {:{num}} {:{apsname}} | {:{inter}} | {:{policy}} | {:{descr}}'.format('#',*headers,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('     {:-<{num}} {:-<{apsname}} | {:-<{inter}} | {:-<{descr}}'.format('','','','','',num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('      no APS found')
        return apslist

def display_leafprofiles(accportp,fexes,nodedict):
        for x in accportp:
            for y in x.infraRtAccPortPlist:
                nodedict[y.tDn].leafprofiles.append(x)
        for switchp in sorted(nodedict.values(), key=lambda x: x.name):
            for leafp in switchp.leafprofiles:
                for fex in fexes:
                    for portlist in leafp.infraHPortSlist:
                        if fex.dn in portlist.infraRsAccBaseGrp.tDn:
                            leafp.foundfex.append((fex,portlist.infraRsAccBaseGrp.fexId))
                            for y in fex.infraHPortSlist:
                                pass
        leaftable = []
        for switchp in sorted(nodedict.values(), key=lambda x: x.name):
            if len(switchp.leafprofiles) > 1:
                for lp in switchp.leafprofiles:
                    leaftable.append((lp.name,'', switchp.name, switchp.allleafs,('',switchp),lp))
                    if lp.foundfex:
                        for fex in lp.foundfex:
                            leaftable.append((fex[0].name, switchp.name, switchp.allleafs,fex[1],(fex,switchp)))
            else:
                removedempty_leafprofiles = filter(lambda x: x != '', ','.join(map(lambda x: x.name, switchp.leafprofiles)))
                if removedempty_leafprofiles:
                    leaftable.append((switchp.leafprofiles[0].name,switchp.name, switchp.allleafs,'',('',switchp),switchp.leafprofiles[0]))
                    if switchp.leafprofiles:
                       if switchp.leafprofiles[0].foundfex:
                            for fex in switchp.leafprofiles[0].foundfex:
                                leaftable.append((fex[0].name, switchp.name, switchp.allleafs, fex[1],(fex,switchp),switchp.leafprofiles[0]))        #for fex in fexes:

        baseminimum = ('Leaf Profile', 'Switch Profile', 'Leafs Associated', 'Fex ID')
        leaftable = filter(None, leaftable)
        sizes = get_column_sizes(leaftable, minimum=5, baseminimum=baseminimum)
        leaftable = map(lambda x:x[1] + (x[0],), enumerate(leaftable,1))
        print('\n     ' + '-' * (sum(sizes) + 13))
        print('   {:>{num}}   {:{leafp}} | {:{switchp}} | {:{leafaff}} | {:{fexid}}'.format('#', *baseminimum, num=3,leafp=sizes[0],switchp=sizes[1],leafaff=sizes[2],fexid=sizes[3]))
        print('     {:->{num}} {:-<{leafp}} | {:-<{switchp}} | {:-<{leafaff}} | {:-<{fexid}}'.format('','','','','', num=3,leafp=sizes[0],switchp=sizes[1],leafaff=sizes[2],fexid=sizes[3]))
        for row in leaftable:
            print('  {:{num}}.) {:{leafp}} | {:{switchp}} | {:{leafaff}} | {:{fexid}}'.format(row[-1],row[0],row[1],row[2],row[3],num=4, leafp=sizes[0],switchp=sizes[1],leafaff=sizes[2],fexid=sizes[3]))
        return leaftable


def interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic, type="Physical"):
    while True:
        print('What is the inteface epg mode?:\n\n'
              + '**Use either 1 for trunks ports and 2 for normal access ports\n\n' 
              + '1.) Trunk\n'
              + '2.) Access\n'
              + '3.) Untagged\n')
        askepgtype = custom_raw_input("Which mode? [default=1]: ") or '1'
        if askepgtype == '1':
            epg_type = 'trunk_port'
            break
        elif askepgtype == '2':
            epg_type = 'access_port'
            break
        elif askepgtype == '3':
            epg_type = 'untagged_port'
            break
        else:
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue
        
    urllist, confirmationlist =  vlan_and_url_generating(chosenepgs,choseninterfaceobjectlist, apic, epg_type)
    print('')
    print('Please Confirm deployment:\n')
    for confirm in confirmationlist:
        print('{epg} with vlan {vlan}'.format(epg=confirm[1],vlan=confirm[2]))
        for interface in confirm[0]:
            print('{}'.format(interface))
        print('')
    while True:
        verify = custom_raw_input('Continue? [y|n]: ')
        if verify == '':
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue
        elif verify[0].lower() == 'y':
            break
        elif verify[0].lower() == 'n':
            raise KeyboardInterrupt
        else:
            print("\n\x1b[1;37;41mInvalid option...Try again\x1b[0m\n")
            continue    
    add_egps_to_interfaces(urllist, type, cookie)

def vlan_and_url_generating(chosenepgs,choseninterfaceobjectlist, apic, epg_type):
    urllist = []
    confirmationlist = []
    for epg in sorted(chosenepgs):
        url = """https://{apic}/api/node/mo/{}.json""".format(epg,apic=apic)
        logger.info(url)
        print("\nProvide a vlan number for epg: {}".format(epgformater(epg)))
        while True:
            try:
                vlan = custom_raw_input('vlan number [1-3899]: ')
                print('\r')
                if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
                   break
                else:
                    print('Invalid vlan number')
            except ValueError:
                continue
        for interface in sorted(choseninterfaceobjectlist):
            if epg_type == 'trunk_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","instrImedcy":"immediate",\
                     "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface,vlan=vlan)
            elif epg_type == 'access_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","mode":"native","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface,vlan=vlan)
            elif epg_type == 'untagged_port':
                data = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","mode":"untagged","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface,vlan=vlan)
            urlmodify = namedtuple('urlmodify', ('url', 'interface', 'data'))
            urllist.append(urlmodify(url, interface, data))
        confirmationlist.append((choseninterfaceobjectlist,epg, vlan))
    return urllist, confirmationlist

def add_egps_to_interfaces(urllist, interfacetype, cookie):
    queue = Queue.Queue()
    threadlist = []
    queuelist = []
    for url in urllist:
        t = threading.Thread(target=submit_add_post_request, args=(url,interfacetype,queue, cookie))
        t.daemon = True
        t.start()
        threadlist.append(t)
    for t in threadlist:
        t.join()
        queuelist.append(queue.get())
    for q in sorted(queuelist):
        print(q)

def submit_add_post_request(url,interfacetype,queue, cookie):
    result, error = PostandGetResponseData(url.url, url.data, cookie)
    logger.info(result)
    logger.info(error)
    shorturl = url.url[30:-5]
    if error == None and result == []:
        finalresult = 'Success! -- Added ' + shorturl + ' > ' + str(url.interface)
        queue.put(finalresult)
        logger.debug('{} modify: {}'.format(interfacetype, finalresult))
    elif result == 'invalid':
        logger.error('{} modify: {}'.format(interfacetype, error))
        interfacepath = re.search(r'\[.*\]', error)
        if 'already exists' in error:
            queue.put('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + ' > ' + url.interface.dn + '\t -- EPG already on Interface ')# + interfacepath.group())    
        else:
            queue.put('\x1b[1;37;41mFailure\x1b[0m ' + shorturl + '\t -- ' + error)
    else:
        logger.error('{} modify: {}'.format(interfacetype, error))
        print(error)





def create_deploy_new_aps(parentleafprofile,apsname):
        url = """https://{apic}/api/node/mo/uni/infra/accportprof-{plp}/hports-{apsname}-typ-range.json""".format(apic=apic,plp=parentleafprofile,apsname=apsname)
        data = """{{"infraHPortS":{{"attributes":{{"name":"{apsname}","status":"created,modified"}}}}}}""".format(apsname=apsname)
        results, error = PostandGetResponseData(url,data,cookie)
        return results, error

def associate_policygroup_to_aps(parentleafprofile,apsname,policygroup):
        url = """https://{apic}/api/node/mo/uni/infra/accportprof-{plp}/hports-{apsname}-typ-range/rsaccBaseGrp.json""".format(apic=apic,plp=parentleafprofile,apsname=apsname)
        data = """{{"infraRsAccBaseGrp":{{"attributes":{{"tDn":"uni/infra/funcprof/accportgrp-{policygroup}","status":"created,modified"}}}}}}""".format(policygroup=policygroup)
        results, error = PostandGetResponseData(url,data,cookie)
        return results, error
        #,"children":"""
        #"""[{"infraPortBlk":{"attributes":{"fromPort":"17","toPort":"17","name":"block2","rn":"portblk-block2","status":"created,modified"},"children":[]}},{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-ACCESS_PORT","status":"created,modified"},"children":[]}}]}}"""
#


def portblock_factory_creator(leafp,aps,selectedinterfacelist):
    url = """https://{apic}/api/node/mo/uni/infra/accportprof-{leafp}/hports-{aps}-typ-range.json""".format(apic=apic,leafp=leafp,aps=aps)
    dataframe = {"infraHPortS":{"attributes":{"name":"{}".format(aps),"status":"modified"},"children":[]}}
    for interface in selectedinterfacelist:
        port = interface[interface.rfind('/')+1:]
        card = interface[interface.rfind('/')-1:interface.rfind('/')]
        rn = random.randrange(100)
        portblockframe = """{{"infraPortBlk":{{"attributes":{{"fromCard":"{card}","fromPort":"{port}","toCard":"{card}","toPort":"{port}","name":"block{rn}","status":"created,modified"}}}}}}""".format(card=card,port=port,rn=rn)
        dataframe['infraHPortS']['children'].append(json.loads(portblockframe))
    data = json.dumps(dataframe)
    addinterfaces_to_APS_POST = (url,data,cookie)
    return addinterfaces_to_APS_POST


def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        #import pdb; pdb.set_trace()
        while True:
            clear_screen()
            location_banner('Config Interface and Deploy')
            allepglist = get_All_EGPs(apic,cookie)
            nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
            fexes = gather_infraFexP(apic,cookie)
            accportp = gather_infraAccPortP(apic,cookie, fexes)
            profilelist = []
            leafp = retrieve_leafprofiles(apic, cookie)
    
            leaftable = display_leafprofiles(accportp,fexes,nodedict)
            while True:
                reqleafprofile = custom_raw_input("\nWhich Leaf Profile for new interface(s)? [single number]: ")
                if reqleafprofile.isdigit() and int(reqleafprofile) < len(leaftable)+1 and int(reqleafprofile) > 0:
                    break
                else:
                    print('Invalid option...')
                    continue
            selectedleafprofile = leaftable[int(reqleafprofile)-1]
            print('\r')
            displayleaflist = selectedleafprofile[2]
            allconfiguredinterfaces = multithreading_request(return_configured_ports_for_display_per_leaf, displayleaflist, parameters={'apic':apic,'cookie':cookie})
            print('='*80)
            print('Green:Used, Black:Available')
            chosenleafs = []
            unusedinterfaces = None
            for configured_intefaces in allconfiguredinterfaces:
                currentinterfacelist = physical_interface_selection(apic, cookie, [configured_intefaces[0]], returnlistonly=True)
                interfaces.switchpreviewutil.main(apic,cookie,[configured_intefaces[0]], interfacelist=configured_intefaces[1], purpose='custom')
                if not any(map(attrgetter('fexethname'),currentinterfacelist)):
                    chosenleafs.append(configured_intefaces[0])
                    if unusedinterfaces:
                        unusedinterfaces += filter(lambda x: x.name not in configured_intefaces[1], currentinterfacelist)
                    else:
                        unusedinterfaces = filter(lambda x: x.name not in configured_intefaces[1], currentinterfacelist)
                else:
                    def match_fex_or_nonfex(x):
                        if x.fexethname != None:
                            if x.fexethname in configured_intefaces[1]:
                                return False
                            else:
                                return True
                        else:
                            if x.name in configured_intefaces[1]:
                                return False
                            else:
                                return True
                    if unusedinterfaces:
                        unusedinterfaces += filter(match_fex_or_nonfex, currentinterfacelist)
                    else:
                        unusedinterfaces = filter(match_fex_or_nonfex, currentinterfacelist)
            del currentinterfacelist
            print('='*80)
            print('\r')
            def create_attr(listx):
                for x in listx:
                    if x.fexethname != None:
                        x.fullethname = x.fexethname
                    else:
                        x.fullethname = x.name
            create_attr(unusedinterfaces)
            if len(allconfiguredinterfaces) > 1:
                c = Counter(getattr(x, 'fullethname') for x in unusedinterfaces)
                unusedinterfaces = filter(lambda x: c[x.fullethname] > 1, unusedinterfaces)
                finalfullethnamelist = list(set(map(attrgetter('fullethname'), unusedinterfaces)))
                finalfullethnamelist.sort()
                print('Available common interfaces for Leaf Profile spanning \x1b[1;33;40mmultiple\x1b[0m leafs.\nSelected interfaces will be applied to all leafs in profile:\n')
                for num,eth in enumerate(finalfullethnamelist,1):
                    print('     {}.) {}'.format(num,eth))
                while True:
                    selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
                    print('\r')
                    if selectedinterfaces.strip().lstrip() == '':
                        continue
                    intsinglelist = parseandreturnsingelist(selectedinterfaces,finalfullethnamelist)
                    if intsinglelist == 'invalid':
                        continue
                    else:
                        break
                selectedinterfacelist = [finalfullethnamelist[x-1] for x in intsinglelist]
            else:
                interfaces_selection_result = physical_interface_selection(apic, cookie, chosenleafs, returnlistonly=True,provided_interfacelist=unusedinterfaces)
                selectedinterfacelist = [x.fullethname for x in interfaces_selection_result]
            apslist = display_APS_for_leafProfile(leafp=selectedleafprofile)
    
            while True:
                askaps = custom_raw_input('\nWhich Exisiting or New APS will interface(s) be deployed?: ')
                if askaps != '' and askaps.isdigit() and int(askaps) <= len(apslist) +1 and int(askaps) > 0:
                    break
                else:
                    print('\r')
                    print('Invalid option...')
            if askaps != str(len(apslist) + 1):
                apschoosen = apslist[int(askaps)-1]
                url = """https://{apic}/api/node/mo/uni/infra/accportprof-{leafp}/{aps}.json""".format(apic=apic,leafp=selectedleafprofile[0],aps=apschoosen[-1].rn)
                dataframe = {"infraHPortS":{"attributes":{"name":"{}".format(apschoosen[0]),"status":"modified"},"children":[]}}
                for interface in selectedinterfacelist:
                    port = interface[interface.rfind('/')+1:]
                    card = interface[interface.rfind('/')-1:interface.rfind('/')]
                    rn = random.randrange(100)
                    portblockframe = """{{"infraPortBlk":{{"attributes":{{"fromCard":"{card}","fromPort":"{port}","toCard":"{card}","toPort":"{port}","name":"block{rn}","status":"created,modified"}}}}}}""".format(card=card,port=port,rn=rn)
                    dataframe['infraHPortS']['children'].append(json.loads(portblockframe))
                data = json.dumps(dataframe)
                addinterfaces_to_APS_POST = (url,data,cookie)
                del dataframe
                created_APS = False
                interface_check_url = addinterfaces_to_APS_POST[0]
                interface_check_url = interface_check_url.replace('.json','/rsaccBaseGrp.json')
                results = GetResponseData(interface_check_url,cookie)
            else:
                created_APS = True
                print('\nCreating New APS (Wizard)\n')
                while True:
                    new_aps_name = custom_raw_input("   Provide a name for the New APS: ")
                    if new_aps_name == "":
                        continue
                    text = '   Confirm APS name \x1b[1;33;40m{}\x1b[0m'.format(new_aps_name)
                    confirm = askconfirmation(text)
                    if confirm == True:
                        break

                while True:
                    print("\n What will this new interface(s) be:\n\n" 
                        + "    1.)VPC\n"
                        + "    2.)PC\n"
                        + "    3.)Normal (access,trunk)")
                    print('')
                    asktype = custom_raw_input(" Please Select a type: ")
                    if asktype != '' and asktype.isdigit() and int(asktype) <= 3 and int(asktype) > 0:
                        break
                    else:
                        print('\r')
                        print('Invalid option...')
                if asktype == '3':
                    policygroups = gather_physical_policygroups(apic, cookie)
                    interfacetype = 'access|trunk'
                else:
                    policygroups = gather_portchannel_policygroups(apic,cookie)
                    interfacetype = 'port-channel'
                
        
                #leafs = leaf_selection(get_All_leafs(apic, cookie))
                #leafallinterfacesdict = pull_leaf_interfaces(leafs)
                #print_attribute_layout(leafallinterfacesdict,leafs)
                
                while True:
                    if created_APS and asktype != '3':
                        displaypolicycolumns(policygroups, display_clone=False)
                        clonerequest = custom_raw_input("\nWhich policy group would you like to Clone: ")
                        if clonerequest != "" and clonerequest.isdigit() and int(clonerequest) <= len(policygroups) and int(clonerequest) > 0:
                            selectedpolicygroup = policygroups[int(clonerequest)-1].name
                            clone = True
                            break
                        else:
                            print('Invalid option...')
                    else:
                        displaypolicycolumns(policygroups)

                        requestedpolicynum = custom_raw_input("\nWhat Policy Group for new interface. [single number]: ")
                        if requestedpolicynum.isdigit() and int(requestedpolicynum) <= len(policygroups) and int(requestedpolicynum) > 0:
    
                            selectedpolicygroup = policygroups[int(requestedpolicynum)-1].name
                            clone = False
                            break
                        elif requestedpolicynum.isdigit() and int(requestedpolicynum) == len(policygroups) + 1 and int(requestedpolicynum) > 0:
                            clonerequest = custom_raw_input("\nWhich policy group would you like to Clone: ")
                            if clonerequest != "" and clonerequest.isdigit() and int(clonerequest) <= len(policygroups) and int(clonerequest) > 0:
                                selectedpolicygroup = policygroups[int(clonerequest)-1].name
                                clone = True
                                break
                            else:
                                print('Invalid option...')
                        else:
                            print('Invalid option...')
                            continue
                pgdata = False
                if asktype != '3' and clone == True:
                    
                    url = """https://{apic}/api/node/mo/uni/infra/funcprof/accbundle-{policy}.json?rsp-subtree=full&rsp-prop-include=config-only""".format(apic=apic,policy=selectedpolicygroup)
                    pgresults = GetResponseData(url,cookie)
                    print('\nCloning \x1b[1;33;40m{}\x1b[0m...'.format(selectedpolicygroup))
                    while True:
                        new_pg_name = custom_raw_input("\n   Provide a name for the Policy Group: ")
                        if new_pg_name == "":
                            continue
                        text = '   Confirm Policy Group name \x1b[1;33;40m{}\x1b[0m'.format(new_pg_name)
                        confirm = askconfirmation(text)
                        if confirm == False:
                            continue
                        pgurl = """https://{apic}/api/node/mo/uni/infra/funcprof/accbundle-{policy}.json""".format(apic=apic,policy=new_pg_name)
                        pgdata = json.dumps(pgresults).replace(selectedpolicygroup,new_pg_name)
                        policygroupdict = {'url':pgurl,'data':pgdata}
                        break

                if asktype == '3' and clone == True:
                    
                    #pgdata = False
                    url = """https://{apic}/api/node/mo/uni/infra/funcprof/accportgrp-{policy}.json?rsp-subtree=full&rsp-prop-include=config-only""".format(apic=apic,policy=selectedpolicygroup)
                    pgresults = GetResponseData(url,cookie)
                    print('\nCloning \x1b[1;33;40m{}\x1b[0m...'.format(selectedpolicygroup))
                    while True:
                        new_pg_name = custom_raw_input("\n   Provide a name for the Policy Group: ")
                        if new_pg_name == "":
                            continue
                        text = '   Confirm Policy Group name \x1b[1;33;40m{}\x1b[0m'.format(new_pg_name)
                        confirm = askconfirmation(text)
                        if confirm == False:
                            continue
                        pgurl = """https://{apic}/api/node/mo/uni/infra/funcprof/accportgrp-{policy}.json""".format(apic=apic,policy=new_pg_name)
                        pgdata = json.dumps(pgresults).replace(selectedpolicygroup,new_pg_name)
                        policygroupdict = {'url':pgurl,'data':pgdata}
                        break
                print('\n')
             
            while True:
                deploymenttext = 'Using Leaf Profile \x1b[1;33;40m{}\x1b[0m\n'.format(selectedleafprofile[0])
                if created_APS:
                    if pgdata:
                        newapsdict = {'apsname':new_aps_name,'policygroup':policygroupdict}
                    elif not pgdata:
                        newapsdict = {'apsname':new_aps_name,'policygroup':selectedpolicygroup}
                    deploymenttext += "   Deploying \x1b[1;33;40m{}\x1b[0m to New APS: ".format(map(str,selectedinterfacelist))
                    deploymenttext +="\x1b[1;33;40m{}\x1b[0m\n".format(new_aps_name)
                    deploymenttext +="   Interface Type: \x1b[1;33;40m{}\x1b[0m\n".format(interfacetype)
                    if isinstance(newapsdict['policygroup'], dict):
                        deploymenttext +="   Using New Cloned Policy_Group \x1b[1;33;40m{}\x1b[0m from ".format(new_pg_name)
                        deploymenttext +="Policy_Group: \x1b[1;33;40m{}\x1b[0m".format(selectedpolicygroup)
                    else:
                        deploymenttext +="\n   Policy_Group: \x1b[1;33;40m{}\x1b[0m".format(selectedpolicygroup)
                    print(deploymenttext)
                    print('')

                    while True:
                        confirmation = custom_raw_input("Confirm Deployment? [y]: ") or 'y'
                        if confirmation != '' and confirmation[0].lower() == 'y':
                            deploy = True
                            break
                        elif confirmation != '' and confirmation[0].lower() == 'n':
                            custom_raw_input("Canceling...")
                            deploy = False
                            break
                            
                    if deploy == True:
                        print('')
                        createapsresults, error = create_deploy_new_aps(parentleafprofile=selectedleafprofile[0],apsname=newapsdict['apsname'])
                        if createapsresults != []:
                            print('ERROR: Failed creating new APS > {}'.format(error))
                            break
                        else:
                            print('Success > Created APS {}'.format(newapsdict['apsname']))
                        if pgdata:
                            pgcreationresults, error = PostandGetResponseData(cookie=cookie,**newapsdict['policygroup'])
                            if pgcreationresults != []:
                                print('Failure Creating Policy Group > {}'.format(error))
                                break
                            else:
                                print('Success > Created Policy Group {}'.format(new_pg_name))
                            associateresults, error = associate_policygroup_to_aps(policygroup=new_pg_name,parentleafprofile=selectedleafprofile[0],apsname=newapsdict['apsname'])
                            if associateresults != []:
                                print('ERROR: Failed associating Policy Group to APS > {}'.format(error))
                                break
                            else:
                                print('Success > Associated Poicy Group {} to APS {}'.format(new_pg_name,newapsdict['apsname']))
                        else:
                            associateresults, error = associate_policygroup_to_aps(policygroup=selectedpolicygroup,parentleafprofile=selectedleafprofile[0],apsname=newapsdict['apsname'])
                            if associateresults != []:
                                print('ERROR: Failed associating Policy Group to APS > {}'.format(error))
                                break
                            else:
                                print('Success > Associated Poicy Group {} to APS {}'.format(selectedpolicygroup,newapsdict['apsname']))
                        addinterfaces_to_APS_POST = portblock_factory_creator(leafp=selectedleafprofile[0],aps=newapsdict['apsname'],selectedinterfacelist=selectedinterfacelist)
                        results, error = PostandGetResponseData(*addinterfaces_to_APS_POST)
                        if error:
                            print('ERROR: {}'.format(error))
                            custom_raw_input("Continue...")
                            break
                        else:
                            print('Success > Added Ports to APS!\n')
                            break

                            #elif not pgdata:
                            #    results, error = PostandGetResponseData(**newapsdict['policygroup'])
                        #while True:
                        #    confirmation = custom_raw_input("Confirm deploy \x1b[1;33;40m{}\x1b[0m to \x1b[1;33;40m{}\x1b[0m [y]? ".format(map(str,selectedinterfacelist),newapsdict['apsname'])) or 'y'
#
                        #    #confirmation = custom_raw_input("Confirm deploy \x1b[1;33;40m{}\x1b[0m to \x1b[1;33;40m{}\x1b[0m [y]? ".format(map(str,selectedinterfacelist),apschoosen[-1].name)) or 'y'
                        #    if confirmation != '' and confirmation[0].lower() == 'y':
                        #        cancel = False
                        #        break
                        #    elif confirmation != '' and confirmation[0].lower() == 'n':
                        #        custom_raw_input("\nCanceling...")
                        #        cancel = True
                        #        break
                        #    else:
                        #        print('Invalid option...')
                        #else:
                        #    print('ERROR: {}'.format(error))
                        #    break
                        #break
                    else:
                        custom_raw_input("Cancelled!")
                        break
                else:
                    confirmation = custom_raw_input("Confirm deploy \x1b[1;33;40m{}\x1b[0m to \x1b[1;33;40m{}\x1b[0m [y]? ".format(map(str,selectedinterfacelist),apschoosen[-1].name)) or 'y'
                    if confirmation != '' and confirmation[0].lower() == 'y':
                        results, error = PostandGetResponseData(*addinterfaces_to_APS_POST)
                        if error is None:
                            print('\nSuccessfully Added Ports to APS!\n')
                        else:
                            print('ERROR: {}'.format(error))
                            custom_raw_input("Continue...")
                        cancel = False
                        break
                    elif confirmation != '' and confirmation[0].lower() == 'n':
                        custom_raw_input("\nCanceling...")
                        cancel = True
                        break
                    else:
                        print('Invalid option...')
                if cancel:
                    break
            
            if not created_APS:
                interface_check_url = addinterfaces_to_APS_POST[0]
                interface_check_url = interface_check_url.replace('.json','/rsaccBaseGrp.json')
                results = GetResponseData(interface_check_url,cookie)
                #import pdb; pdb.set_trace() 
                
                if results[0].get('infraRsAccBaseGrp'):
                    if 'accportgrp' in results[0]['infraRsAccBaseGrp']['attributes']['tDn']:
                        while True:
                            deployepgs = custom_raw_input("Would you like to deploy STATIC EPGs to new interface(s)? [n]: ") or 'n'
                            if deployepgs != "" and deployepgs[0].lower() == 'y':
                                chosenepgs, choseninterfaceobjectlist = display_and_select_epgs(interfaces_selection_result, allepglist)
                                interface_type_and_deployement(chosenepgs, choseninterfaceobjectlist, apic)
                            elif deployepgs != "" and deployepgs[0].lower() == 'n':
                                pass
                            #custom_raw_input("")
                            break
                        else:
                            pass
    
                else:
                    print('\nERROR: Unable to locate Policy Group for APS\n')  
                    import pdb; pdb.set_trace() 
    
            nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
            fexes = gather_infraFexP(apic,cookie)
            accportp = gather_infraAccPortP(apic,cookie, fexes)
            profilelist = []
            leafp = retrieve_leafprofiles(apic, cookie)
            print('\nDisplaying results:\n')
            leaftable = display_leafprofiles(accportp,fexes,nodedict)
            print('')
            selectedleafprofile = leaftable[int(reqleafprofile)-1]
            display_APS_for_leafProfile(selectedleafprofile, include_create=False)
            #    print('hit')
            #    print('{}  {}  | {}'.format(fex.dn, switchp.name, switchp.allleafs))
    
    
            #for physpolicy in physpolicygroupslist:
            #    print(physpolicy.name, physpolicy.column1,physpolicy.column2,physpolicy.column3,physpolicy.column4,physpolicy.column5,physpolicy.column6,physpolicy.column7)
            custom_raw_input('\n#Press enter to continue...')
    