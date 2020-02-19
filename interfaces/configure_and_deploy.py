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
from multiprocessing.dummy import Pool as ThreadPool

#import fabric_access

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
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the parent custom logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

class policy_group():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.policies = {}
       # localobj = globals()[child]
       # physinterface.profiles[child] = localobj(children[child]['attributes'])
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
            #import pdb; pdb.set_trace()
          #  if len(obj.policies) == 18:
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
#    def gatherallleafs(self):
#        infraranges = []
#        for local_infraPortBlk in self.infraHPortSlist:
#            for x in local_infraPortBlk.infraPortsBlklist:
#                infraranges.extend(range(x.from_, x.to_ + 1))
#        allranges = list(set(infraranges))
#        self.allleafs = allranges
    def __repr__(self):
        return self.dn

def gather_infraNodeP(apic,cookie):
    url = """https://{apic}/api/node/class/infraNodeP.json?rsp-subtree=full""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    infraNodePlist = []
    infraNodePdict = {}
    for infrnodep in result:
       # import pdb; pdb.set_trace()
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
                                    
                                    #import pdb; pdb.set_trace()
                                    fexbndlgrppath = blocks['infraRsAccBaseGrp']['attributes']['tDn']# (ending) -> -> Fexp/infrafexbndlgrp.rn
                                    fexp = '/'.join(fexbndlgrppath.split('/')[:-1])
                                    fexbndlgp = fexbndlgrppath.split('/')[-1:][0]
                                    #match fexp then find fexbndlgrp with rn
                                   # fexid = blocks['infraRsAccBaseGrp']['attributes']['tCl'] 
                                   # -> Fexp/infrafexbndlgrp.rn
                                    #fexresult = searchfexP(fexid)
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



#class infraFexP():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
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

#def return_physical_programmed_ports_perleaf(leaf, apic, cookie):
#    nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
#    fexes = gather_infraFexP(apic,cookie)
#    accportp = gather_infraAccPortP(apic,cookie, fexes)
#    for x in accportp:
#        for y in x.infraRtAccPortPlist:
#            nodedict[y.tDn].leafprofiles.append(x)
#    leafspfound = []
#    for switchp in sorted(nodedict.values(), key=lambda x: x.name):
#        if int(leaf) in switchp.allleafs:
#            leafspfound.append(switchp)
#    return leafspfound, fexes
    #import pdb; pdb.set_trace()
       # print('{}  {}'.format(switchp.name, switchp.allleafs))
       ## import pdb; pdb.set_trace()
    #for leafp in leafspfound:

       # for leafp in switchp.leafprofiles:
       #     print('\t' + leafp.name)
       #     #import pdb; pdb.set_trace()
       #     for portlist in leafp.infraHPortSlist:
       #         print('\t\t' + portlist.name)
       #         #print(portlist.__dict__)
       #         print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
       #         if portlist.infraRsAccBaseGrp.tCl == 'infraAccPortGrp':
       #             print('\t\t\t' + 'individual')
       #         elif portlist.infraRsAccBaseGrp.tCl == 'infraAccBndlGrp':
       #             print('\t\t\t' + 'Port-channel')                    
       #         elif portlist.infraRsAccBaseGrp.tCl == 'infraFexBndlGrp':
       #             print('\t\t\t' + 'Fex-uplinks')
       #         if portlist.infraFexPlist:
       #             print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
       #         
       #         #print('\t\t\t' + portlist.infraRsAccBaseGrp.tCl)
       #         for z in portlist.infraPortsBlklist:
       #             print('\t\t\t ' + z.fromPort + ' - ' + z.toPort)

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
        #import pdb; pdb.set_trace()
    for group in policygrouplist:
        finallist.append(policy_row(group))
    return finallist

        #if interface['l1PhysIf'].get('children'):
        #    for children in interface['l1PhysIf']['children']:
        #        for child in children:
        #            localobj = globals()[child]
        #            physinterface.profiles[child] = localobj(children[child]['attributes'])
   # for policygroup in policygrouplist:
   #     policy_row

def displaypolicycolumns(grouplist):
    columnwidthfind = ('num,','name','column1','column2','column3','column4','column5','column6')
    headers = ('#','Policy Group','AAEP','CDP','Fiber-Channel','Link Level','LLDP','Monitor')
    sizes = get_column_sizes(grouplist, columnwidthfind, minimum=5, baseminimum=headers)
    print('        ' + '-'* (sum(sizes)-5))
    #import pdb; pdb.set_trace()
    topstring = '   {:{num}} {:{policygroup}} | {:{aaep}} | {:{cdp}} | {:{ll}} | {:{lldp}} | {:{mon}} |'
    #topstring =' {:13} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} |'
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

#def ask_and_display_leafprofiles(apic,cookie)




def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Config Interface and Deploy')
        import pdb; pdb.set_trace()
        nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
        fexes = gather_infraFexP(apic,cookie)
        accportp = gather_infraAccPortP(apic,cookie, fexes)
        profilelist = []
        leafp = retrieve_leafprofiles(apic, cookie)
        #for lp in leafp:
        #    profilelist.append(lp['infraAccPortP']['attributes']['dn'].split('/')[2])
        #fexp = retrieve_fexprofiles(apic, cookie)
        #for fp in fexp:
        #    profilelist.append(fp['infraFexP']['attributes']['dn'].split('/')[2])
        #print('\n')
        #print('\t # | Leaf Profile or Fex Profile')
        #print('\t------------------------------------')
        #for num,profile in enumerate(profilelist,1):
        #    print("\t{:2}.) {}".format(num,profile.replace("accportprof-","").replace("fexprof-", "")))
        #while True:
        #    selected = custom_raw_input("\nSelect interface 'desired' location: ")
        #    selected = selected.strip().lstrip()
        #    if selected.isdigit() and int(selected) > 0 and int(selected) <= len(profilelist):
        #        import pdb; pdb.set_trace()
        #        print(profilelist[int(selected)-1])
        #        break
        #    else:
        #        print("\nInvalid selection, Please try again...")
        #        continue
#
            ######################################################################################################

        for x in accportp:
            for y in x.infraRtAccPortPlist:
                nodedict[y.tDn].leafprofiles.append(x)



        for switchp in sorted(nodedict.values(), key=lambda x: x.name):
           # print('{}  {}'.format(switchp.name, switchp.allleafs))
           # import pdb; pdb.set_trace()
            for leafp in switchp.leafprofiles:
               # print('\t' + leafp.name)
                for fex in fexes:
                    for portlist in leafp.infraHPortSlist:
                        #print(fex.dn, portlist.infraRsAccBaseGrp.tDn)
                        if fex.dn in portlist.infraRsAccBaseGrp.tDn:
                            leafp.foundfex.append((fex,portlist.infraRsAccBaseGrp.fexId))
                        #    print('\t\t{} [fex ID: {}]'.format(fex, portlist.infraRsAccBaseGrp.fexId))
                          #  print(portlist.infraRsAccBaseGrp.fexId)
                        #for x in fexes:
                            for y in fex.infraHPortSlist:
                                pass
                                #import pdb; pdb.set_trace()
                  #              print('\t\t\t' + y.infraRsAccBaseGrp.tDn)
                  #              #print(y.__dict__)
                  #              for z in y.infraPortsBlklist:
                  #                  if z.fromPort == z.toPort:
                  #                      print('\t\t\t\t ' + z.fromPort)
                  #                  else:   
                  #                      print('\t\t\t\t ' + z.fromPort + ' - ' + z.toPort)

            #    #import pdb; pdb.set_trace()
            #    for portlist in leafp.infraHPortSlist:
            #        print('\t\t' + portlist.name)
            #        #print(portlist.__dict__)
            #        print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
            #        if portlist.infraRsAccBaseGrp.tCl == 'infraAccPortGrp':
            #            print('\t\t\t' + 'individual')
            #        elif portlist.infraRsAccBaseGrp.tCl == 'infraAccBndlGrp':
            #            print('\t\t\t' + 'Port-channel')                    
            #        elif portlist.infraRsAccBaseGrp.tCl == 'infraFexBndlGrp':
            #            print('\t\t\t' + 'Fex-uplinks')
            #        if portlist.infraFexPlist:
            #            print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
            #        
#
            #        #print('\t\t\t' + portlist.infraRsAccBaseGrp.tCl)
            #        for z in portlist.infraPortsBlklist:
            #            if z.fromPort == z.toPort:
            #                print('\t\t\t\t ' + z.fromPort)
            #            else:   
            #                print('\t\t\t\t ' + z.fromPort + ' - ' + z.toPort)
        leaftable = []
        for switchp in sorted(nodedict.values(), key=lambda x: x.name):
            if len(switchp.leafprofiles) > 1:
                for lp in switchp.leafprofiles:
                    leaftable.append((lp.name,'', switchp.name, switchp.allleafs,('',switchp),lp))
                   #print('{}  {}  | {}'.format(lp.name, switchp.name, switchp.allleafs))
                    if lp.foundfex:
                        for fex in lp.foundfex:
                            leaftable.append((fex[0].name, switchp.name, switchp.allleafs,fex[1],(fex,switchp)))
                    
            else:
                removedempty_leafprofiles = filter(lambda x: x != '', ','.join(map(lambda x: x.name, switchp.leafprofiles)))
                #import pdb; pdb.set_trace()
                if removedempty_leafprofiles:
                    leaftable.append((switchp.leafprofiles[0].name,switchp.name, switchp.allleafs,'',('',switchp),switchp.leafprofiles[0]))

                    #print('{}  {}  | {}'.format(','.join(map(lambda x: x.name, switchp.leafprofiles)), switchp.name, switchp.allleafs ))
                    if switchp.leafprofiles:
                       if switchp.leafprofiles[0].foundfex:
                        #if .foundfex:
                            for fex in switchp.leafprofiles[0].foundfex:
                                leaftable.append((fex[0].name, switchp.name, switchp.allleafs, fex[1],(fex,switchp),switchp.leafprofiles[0]))        #for fex in fexes:

        baseminimum = ('Leaf Profile', 'Switch Profile', 'Leafs Affected', 'Fex ID')
        leaftable = filter(None, leaftable)
        sizes = get_column_sizes(leaftable, minimum=5, baseminimum=baseminimum)
        leaftable = map(lambda x:x[1] + (x[0],), enumerate(leaftable,1))
        #pdb
        print('\n     ' + '-' * (sum(sizes) + 13))
        print('   {:>{num}}   {:{leafp}} | {:{switchp}} | {:{leafaff}} | {:{fexid}}'.format('#', *baseminimum, num=3,leafp=sizes[0],switchp=sizes[1],leafaff=sizes[2],fexid=sizes[3]))
        print('     {:->{num}} {:-<{leafp}} | {:-<{switchp}} | {:-<{leafaff}} | {:-<{fexid}}'.format('','','','','', num=3,leafp=sizes[0],switchp=sizes[1],leafaff=sizes[2],fexid=sizes[3]))
        for row in leaftable:
            print('  {:{num}}.) {:{leafp}} | {:{switchp}} | {:{leafaff}} | {:{fexid}}'.format(row[-1],row[0],row[1],row[2],row[3],num=4, leafp=sizes[0],switchp=sizes[1],leafaff=sizes[2],fexid=sizes[3]))
        while True:
            reqleafprofile = custom_raw_input("\nWhat Leaf Profile for new interface(s). [single number]: ")
            if reqleafprofile.isdigit() and int(reqleafprofile) < len(leaftable)+1 and int(reqleafprofile) > 0:
                break
            else:
                print('Invalid option...')
                continue
        requestpolicy = leaftable[int(reqleafprofile)-1]
        print('\r')
        displayleaflist = requestpolicy[2]

        results = multithreading_request(return_configured_ports_for_display_per_leaf, displayleaflist, parameters={'apic':apic,'cookie':cookie})
        #import pdb; pdb.set_trace()
        #leafmap = zip(results[])
        #import pdb; pdb.set_trace()
        #interfaces.switchpreviewutil.main(apic,cookie,[result[0]], interfacelist=result[1], purpose='custom')
        print('='*80)
        print('Green:Used, Black:Available')
        for result in results:
            interfaces.switchpreviewutil.main(apic,cookie,[result[0]], interfacelist=result[1], purpose='custom')
        print('='*80)
        print('\r')
        ##import pdb; pdb.set_trace()
        ##
        ##for leaf in requestpolicy[2]:
        ##    #import pdb; pdb.set_trace()
##
        ##    display_configured_ports(leaf,apic,cookie)
     #       switchpfound, fexes = fabric_access.display_switch_to_leaf_structure.return_physical_programmed_ports_perleaf(leaf, apic, cookie)
     #       interfaces_with_APS_defined = []
     #       fexfound = []
     #       for switchp in switchpfound:
     #          # for leafp in switchp.leafprofiles:
     #          # print(switchp.name)
     #         #  import pdb; pdb.set_trace()
     #           for leafp in switchp.leafprofiles:
     #          #     print('\t' + leafp.name)
     #               interfaces_with_APS_defined.append((switchp.allleafs,leafp.allports))
     #               #import pdb; pdb.set_trace()
     #               for portlist in leafp.infraHPortSlist:
     #          #         print('\t\t' + portlist.name)
     #                   #print(portlist.__dict__)
     #                   #print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
     #                   #print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
     #                   #if portlist.infraRsAccBaseGrp.tDn in fexes:
     #                   for x in fexes:
     #                       if portlist.infraRsAccBaseGrp.tDn != '' and  x.dn in portlist.infraRsAccBaseGrp.tDn:
     #                         #  import pdb; pdb.set_trace()
     #                           if portlist.infraFexPlist:
     #                  #     print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
     #                               fexfound.append((x,portlist.infraRsAccBaseGrp.fexId))
     #                  # if portlist.infraRsAccBaseGrp.tCl == 'infraAccPortGrp':
     #                  #     print('\t\t\t' + 'individual')
     #                  # elif portlist.infraRsAccBaseGrp.tCl == 'infraAccBndlGrp':
     #                  #     print('\t\t\t' + 'Port-channel')                    
     #                  # elif portlist.infraRsAccBaseGrp.tCl == 'infraFexBndlGrp':
     #                  #     print('\t\t\t' + 'Fex-uplinks')
     #                  # if portlist.infraFexPlist:
     #                  #     print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
     #                       
     #                       
     #                   
     #                      # for z in portlist.infraPortsBlklist:
     #                      #     print('\t\t\t ' + z.fromPort + ' - ' + z.toPort)
     #                      #     for x in range(int(z.fromPort),int(z.toPort)+1):
     #                      #         interfaces_with_APS_defined.append((fexes,x))
     #                                               #print('\t\t\t' + portlist.infraRsAccBaseGrp.tCl)
     #               #    for z in portlist.infraPortsBlklist:
     #               #        print('\t\t\t ' + z.fromPort + ' - ' + z.toPort)
     #               #   # if len(list(range(int(z.fromPort),int(z.toPort)+1))) > 1:
     #               #   #     for x in range(range(int(z.fromPort),int(z.toPort)+1)):
     #               #    
     #               #            
     #               #        for x in range(int(z.fromPort),int(z.toPort)+1):
     #               #            interfaces_with_APS_defined.append((switchp.allleafs,x))
#
     #       for fex in fexfound:
     #           interfaces_with_APS_defined.append((fex[1],fex[0].allports))
     #       compiledports = []
     #       for interface in interfaces_with_APS_defined:
     #           if type(interface[0]) != unicode:
     #              # import pdb; pdb.set_trace()
     #               for templeaf in interface[0]:
     #                   for modulenum, ports in interface[1].items():
     #                       for port in ports:  
     #                           compiledports.append(('eth' + str(modulenum) + '/' + str(port)))
     #                   #import pdb; pdb.set_trace()
     #           else:
     #               for modulenum, ports in interface[1].items():
     #                   for port in ports:
     #                       compiledports.append(('eth' + str(interface[0]) + '/' + str(modulenum) + '/' + str(port)))
     #       compiledports = list(set(compiledports))
     #       #import custom_utils
     #       newlist = []
     #       for x in compiledports:
     #           newlist.append(l1PhysIf(id = x, shortnum = x.split('/')[-1][0]))
     #       switchpreviewutil.main(apic,cookie,[leaf], interfacelist=compiledports, purpose='custom')
        if requestpolicy[5].infraHPortSlist != []:
            apslist = []
            for aps in sorted(requestpolicy[5].infraHPortSlist, key=lambda x: x.name.lower()):
                tempfromtocard_fromtoport_set = set()
                #import pdb; pdb.set_trace()
                for portblklist in aps.infraPortsBlklist:
                    if portblklist.fromCard == portblklist.toCard and portblklist.fromPort == portblklist.toPort:
                        tempfromtocard_fromtoport_set.add('{}/{}'.format(portblklist.fromCard,portblklist.fromPort))
                    elif portblklist.fromCard == portblklist.toCard:
                        tempfromtocard_fromtoport_set.add('{}/{}-{}'.format(portblklist.fromCard,portblklist.fromPort,portblklist.toPort))
                    elif portblklist.fromCard != portblklist.toCard:
                        tempfromtocard_fromtoport_set.add('{}/{}-{}/{}'.format(portblklist.fromCard,portblklist.toCard,portblklist.toCard,portblklist.toPort))
                    #tempfromtocard_fromtoport_set.add('{}/{}'.format(portblklist.fromCard,portblklist.fromPort))
                    #tempfromtocard_fromtoport_set.add('{}/{}'.format(portblklist.toCard, portblklist.toPort)
                if 'accportgrp-' in aps.infraRsAccBaseGrp.tDn:
                    apslist.append((aps.name, ','.join(sorted(list(tempfromtocard_fromtoport_set))), aps.infraRsAccBaseGrp.tDn[aps.infraRsAccBaseGrp.tDn.find('accportgrp-')+11:], aps.descr))
                else:      
                    apslist.append((aps.name, ','.join(sorted(list(tempfromtocard_fromtoport_set))), aps.infraRsAccBaseGrp.tDn[aps.infraRsAccBaseGrp.tDn.find('accbundle-')+10:], aps.descr))
            headers = ('Access Port Selector','Interfaces','Policy','Description')
            sizes = get_column_sizes(apslist, minimum=5, baseminimum=headers)
            print('     ' + '-' * (len(''.join(list(headers))) + 11))
            print('     {:{num}} {:{apsname}} | {:{inter}} | {:{policy}} | {:{descr}}'.format('#',*headers,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('     {:-<{num}} {:-<{apsname}} | {:-<{inter}} | {:-<{policy}} | {:-<{descr}}'.format('','','','','',num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            for number,aps in enumerate(apslist,1):
                print('     {:{num}} {:{apsname}} | {:{inter}} | {:{policy}} | {:{descr}}'.format('{}.)'.format(number),*aps,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('')
            print('     {:{num}} [CREATE NEW APS]'.format('{}.)'.format(int(number) + 1),num=len('{}.)'.format(len(apslist)))))
        else:
            headers = ('Access Port Selector','Interfaces','Description')
            sizes = get_column_sizes(apslist, minimum=5, baseminimum=headers)
            print('     {:{num}} {:{apsname}} | {:{inter}} | {:{policy}} | {:{descr}}'.format('#',*headers,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('     {:-<{num}} {:-<{apsname}} | {:-<{inter}} | {:-<{descr}}'.format('','','','','',num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
            print('      no APS found')
        

        while True:
            askaps = custom_raw_input('\nWhich APS will interfaces be deployed?: ')
            if askaps != '' and askaps.isdigit() and int(askaps) <= len(apslist) +1 and int(askaps) > 0:
                break
            else:
                print('\r')
                print('Invalid option...')
        if askaps == str(len(apslist) + 1):
            print('create APS')
        else:
            apschoosen = apslist[int(askaps)-1]
            print(apschoosen)
        #headers = ('Access Port Selector','Interfaces','Description')
        #sizes = get_column_sizes(apslist, minimum=5, baseminimum=headers)
        #print('     {:{num}} {:{apsname}} | {:{inter}} | {:{descr}}'.format('#',*headers,num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
        #print('     {:-<{num}} {:-<{apsname}} | {:-<{inter}} | {:-<{descr}}'.format('','','','',num=len('{}.)'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
        #for number,aps in enumerate(apslist,1):
        #    print('     {:{num}} {:{apsname}} | {:{inter}} | {:{descr}}'.format('{}.)'.format(number),*aps,num=len('{}'.format(len(apslist))),apsname=sizes[0],inter=sizes[1],policy=sizes[2],descr=sizes[3]))
        import pdb; pdb.set_trace()
        print(requestpolicy)

        while True:
            print("\n What will this interface(s) be:\n" \
                + "\r" \
                + "    1.)VPC\n"\
                + "    2.)PC\n"\
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
        else:
            policygroups = gather_portchannel_policygroups(apic,cookie)
        

        #leafs = leaf_selection(get_All_leafs(apic, cookie))
        #leafallinterfacesdict = pull_leaf_interfaces(leafs)
        #print_attribute_layout(leafallinterfacesdict,leafs)
        displaypolicycolumns(policygroups)
        while True:
            requestedpolicynum = custom_raw_input("\nWhat Policy Group for new interface. [single number]: ")
            if requestedpolicynum.isdigit() and int(requestedpolicynum) <= len(policygroups) and int(requestedpolicynum) > 0:
                break
            else:
                print('Invalid option...')
                continue
        requestpolicy = policygroups[int(requestedpolicynum)-1]
        print(requestpolicy.name)



        import pdb; pdb.set_trace()

        #    print('hit')
        #    print('{}  {}  | {}'.format(fex.dn, switchp.name, switchp.allleafs))


        #for physpolicy in physpolicygroupslist:
        #    print(physpolicy.name, physpolicy.column1,physpolicy.column2,physpolicy.column3,physpolicy.column4,physpolicy.column5,physpolicy.column6,physpolicy.column7)
        custom_raw_input('\n#Press enter to continue...')
