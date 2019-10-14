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
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
        self.allports = {1:[]}
#    def gatherallleafs(self):
#        infraranges = []
#        for local_infraPortBlk in self.infraHPortSlist:
#            for x in local_infraPortBlk.infraPortslist:
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



def gather_infraAccPortP(apic,cookie):
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
                                tempinfraaHPortS.infraRsAccBaseGrplist.append(infraRsAccBaseGrp(**blocks['infraRsAccBaseGrp']['attributes']))
                                if blocks['infraRsAccBaseGrp']['attributes']['tCl'] == "infraFexBndlGrp":
                                    fexid = blocks['infraRsAccBaseGrp']['attributes']['tCl'] 
                                    fexresult = searchfexP(fexid)
                                    tempinfraaHPortS.infraFexPlist.append(fexresult)
                            elif blocks.get('infraPortBlk'):
                                module = list(xrange(int(blocks['infraPortBlk']['attributes']['fromCard']), int(blocks['infraPortBlk']['attributes']['toCard'])+1))
                                portrange = list(xrange(int(blocks['infraPortBlk']['attributes']['fromPort']), int(blocks['infraPortBlk']['attributes']['toPort'])+1))
                                #print(portrange)
                                for linecard in module:
                                    tempAccp.allports[linecard].extend(portrange)
#                                for linecard in module:
                                    tempAccp.allports[linecard].sort()
                                tempinfraaHPortS.infraPortslist.append(infraPortBlk(**blocks['infraPortBlk']['attributes']))
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
        self.infraPortslist = []
        self.infraRsAccBaseGrplist = []
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



class infraFexP():
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
                                tempinfraaHPortS.infraRsAccBaseGrplist.append(infraRsAccBaseGrp(**blocks['infraRsAccBaseGrp']['attributes']))
                            elif blocks.get('infraPortBlk'):
                                module = list(xrange(int(blocks['infraPortBlk']['attributes']['fromCard']), int(blocks['infraPortBlk']['attributes']['toCard'])+1))
                                portrange = list(xrange(int(blocks['infraPortBlk']['attributes']['fromPort']), int(blocks['infraPortBlk']['attributes']['toPort'])+1))
                                for linecard in module:
                                    tempFex.allports[linecard].extend(portrange)
                                    tempFex.allports[linecard].sort()
                                tempinfraaHPortS.infraPortslist.append(infraPortBlk(**blocks['infraPortBlk']['attributes']))
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

def main(import_apic,import_cookie):
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Creating VPC')
        nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
        apps = gather_infraAccPortP(apic,cookie)
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
        print('\n\n\n')
        for z in nodedict.values():
            print('{}'.format(str(z)[str(z).find('nprof-')+6:]))
            print('\t{}'.format(z.allleafs))
            for zz in z.leafprofiles:
                print('\t{}'.format(str(zz)[str(zz).find('prof-')+5:]))
                print('\t\t{}'.format(zz.allports))
                #print(sorted(zz.allports.items(), key=lambda x: x[1][1]))
        print('\n\n\n')
        fexes = gather_infraFexP(apic,cookie)
        for f in fexes:
            print('{}'.format(f.dn))
            print('{}'.format(f.allports))
            for fn in f.infraHPortSlist:
                print(fn.infraRsAccBaseGrplist[0].fexId)
                for fnx in fn.infraRsAccBaseGrplist:
                    print('\t{}'.format(fnx.tDn))
            for x in f.infraFexBndlGrplist:
                for xx in x.infraRtAccBaseGrplist:
                    print('{}'.format(xx.rn))
        print('\n\n')
            #print('{}'.format())
        import pdb; pdb.set_trace()
        raw_input()