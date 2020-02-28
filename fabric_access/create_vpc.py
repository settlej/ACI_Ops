#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import json
import ssl
import os
import datetime
import itertools
import threading
import Queue
from collections import namedtuple
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)
logger.setLevel(logging.DEBUG)

# Define logging handler for file and console logging.  Console logging can be desplayed during
# program run time, similar to print.  Program can display or write to log file if more debug 
# info needed.  DEBUG is lowest and will display all logging messages in program.  
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('aciops.log')
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

def create_infraNodeP(aps_name, apic, cookie, interfaces):
    
    url = """url: https://{apic}/api/node/mo/uni/infra/accportprof-Switch101-102_Profile_ifselector/hports-{aps_name}-typ-range.json""".format(apic=apic,aps_name=aps_name)
    data= """{"infraHPortS":{"attributes":
                                {"name":"{aps_name}","status":"created,modified"},
                                    "children":[
                                        {"infraPortBlk":{"attributes":
                                                            {"fromPort":"{first_interfacenum}","toPort":"{last_interfacenum}","name":"block2","status":"created,modified"},"children":[]}},
                                        {"infraRsAccBaseGrp":{"attributes":
                                                            {"status":"created,modified"},"children":[]}}]}}""".format(aps_name=aps_name,first_interfacenum=first_interfacenum,last_interfacenum=last_interfacenum)

class infraNodeP():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.infraRsAccPortPlist = []
        self.infraLeafSlist = []
        self.allleafs = None
        self.leafprofiles = []
    def gatherallleafs(self):
        infraranges = []
        for local_infraNodeBlk in self.infraLeafSlist:
            #print(local_infraNodeBlk)
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
        self.infraRtAccPortPlist = []
        self.infraHPortSlist = []
        self.allports = []
    def gatherallleafs(self):
        infraranges = []
        for local_infraPortBlk in self.infraHPortSlist:
            for x in local_infraPortBlk.infraPortslist:
                infraranges.extend(range(x.from_, x.to_ + 1))
        allranges = list(set(infraranges))
        self.allleafs = allranges
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
    #for nodep in infraNodePlist:
    #    nodep.gatherallleafs()
    return infraNodePlist, infraNodePdict
    #import pdb; pdb.set_trace()



def gather_infraAccPortP(apic,cookie):
    url = """https://{apic}/api/node/class/infraAccPortP.json?rsp-subtree=full""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    infraAccPortPlist = []
    #print(result)
    for outerobject in result:
       # import pdb; pdb.set_trace()
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
                                tempinfraaHPortS.infraRsAccBaseGrp.append(infraRsAccBaseGrp(**blocks['infraRsAccBaseGrp']['attributes']))
                            elif blocks.get('infraPortBlk'):
                                module = list(xrange(int(blocks['infraPortBlk']['attributes']['fromCard']), int(blocks['infraPortBlk']['attributes']['toCard'])+1))
                                portrange = list(xrange(int(blocks['infraPortBlk']['attributes']['fromPort']), int(blocks['infraPortBlk']['attributes']['toPort'])+1))
                                print(portrange)
                                for linecard in module:
                                    tempAccp.allports.append({linecard:portrange})
#                                tempAccp.allports.append({module:portrange})
                                tempinfraaHPortS.infraPortslist.append(infraPortBlk(**blocks['infraPortBlk']['attributes']))
                    tempAccp.infraHPortSlist.append(tempinfraaHPortS)
                    #tempAccp.infraHPortslist.append(infraHPortS(**blocks['infraHPortS']['attributes']))
        infraAccPortPlist.append(tempAccp)
    #import pdb; pdb.set_trace()
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
        self.infraPortslist = []
        self.infraRsAccBaseGrp = []
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
#def interface_range():
#    raw_interfaces = custom_raw_input('Interface range for VPC [example: 1/1-8 or 1/1,1/3]: ')
#    parseandreturnsingelist(raw_input,interfacelist)
def gather_infraFexP(apic,cookie):
    url = """https://{apic}/api/node/class/infraFexP.json?rsp-subtree=full""".format(apic=apic)
    result = GetResponseData(url,cookie)
#def gather_infraNodeP(apic,cookie):
#    url = """https://{apic}/api/node/class/infraNodeP.json?rsp-subtree=full""".format(apic=apic)
#    result = GetResponseData(url,cookie)


def display_and_select_leafselector(apic,cookie):
    url = """https://{apic}/api/node/mo/uni/infra.json?target-subtree-class=infraFexP,infraAccPortP&query-target=subtree""".format(apic=apic)
    result = GetResponseData(url,cookie)
    logger.debug(result)
    leafprofilelist = []
    fexprofilelist = []
    for profile in result:
        #import pdb; pdb.set_trace()
        if profile.get('infraAccPortP'):
            #print('{}.) {}'.format(num,profile['infraAccPortP']['attributes']['name']))
            leafprofilelist.append(leafprofile(**profile['infraAccPortP']['attributes']))
        elif profile.get('infraFexP'):
            #print('{}.) {}'.format(num,profile['infraFexP']['attributes']['name']))
            fexprofilelist.append(leafprofile(**profile['infraFexP']['attributes']))
    #print(leafprofilelist)
    profiledict = {}
    print('\nLEAF___')
    for num1, ltype in enumerate(sorted(leafprofilelist),1):
        print('{}.) {}'.format(num1,ltype.name))
        profiledict[num1] = ltype
    print('\nFEX____')
    for num2, ltype in enumerate(sorted(fexprofilelist),num1+1):
        print('{}.) {}'.format(num2,ltype.name))
        profiledict[num2] = ltype
    import pdb; pdb.set_trace()

    

def ask_vPC_location(all_leaflist, apic, cookie):
    return physical_leaf_selection(all_leaflist, apic, cookie)

def ask_vPC_name():
    while True:
        vpcname = custom_raw_input('Name for new vPC [example: 101-102_ENC01_VPC5]: ')
        askconfirm = custom_raw_input('"{}" Coninue? [Y]: ') or 'Y'
        if askconfirm.upper().strip().lstrip() == 'Y':
            return vpcname
        else:
            continue

def main(import_apic,import_cookie):
#    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Creating VPC')
        #gather_infraAccPortP(apic,cookie)
        nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
        print(nodedict)
        apps = gather_infraAccPortP(apic,cookie)
        print('before')
        for x in apps:
            print(x.name)
            for y in x.infraHPortSlist:
                print('\t' + y.name)
                for z in y.infraPortslist:
                    print('\t\t ' + z.fromPort + ' - ' + z.toPort)
            for y in x.infraRtAccPortPlist:
                print('\tSwitchprof: ' + y.tDn)

            for y in x.infraRtAccPortPlist:
                nodedict[y.tDn].leafprofiles.append(x)
    #    import pdb; pdb.set_trace()
        for z in nodedict.values():
            print(z)
            for zz in z.leafprofiles:
                print(zz.allports)
        print('after')
        #import pdb; pdb.set_trace()
        #gather_infraFexP(apic,cookie)
        #nodeprofilelist = gather_infraNodeP(apic,cookie)
        #for x in sorted(nodeprofilelist, key=lambda x:x.dn):
        #    #x.gatherallleafs()
        #    print(x.allleafs)
        #    
        #    print(x.dn)
        
        
        
        
        
        
        
        ##all_leaflist = get_All_leafs(apic,cookie)
        ##chosenleafs = ask_vPC_location(all_leaflist, apic, cookie)
        ##switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_status')
        #returnedlist = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
        #vpcname = ask_vPC_name()
        display_and_select_leafselector(apic,cookie)
        raw_input()