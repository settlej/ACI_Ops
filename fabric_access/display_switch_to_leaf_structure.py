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

def return_physical_programmed_ports_perleaf(leaf, apic, cookie):
    #import pdb; pdb.set_trace()
    nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
    fexes = gather_infraFexP(apic,cookie)
    apps = gather_infraAccPortP(apic,cookie, fexes)
    for x in apps:
        for y in x.infraRtAccPortPlist:
            nodedict[y.tDn].leafprofiles.append(x)
    leafspfound = []
    for switchp in sorted(nodedict.values(), key=lambda x: x.name):
        if int(leaf) in switchp.allleafs:
            leafspfound.append(switchp)
    return leafspfound, fexes
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


def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Display Physical Setup')
        nodeprofilelist, nodedict = gather_infraNodeP(apic,cookie)
        fexes = gather_infraFexP(apic,cookie)
        apps = gather_infraAccPortP(apic,cookie, fexes)
        for x in apps:
            for y in x.infraRtAccPortPlist:
                nodedict[y.tDn].leafprofiles.append(x)
        for switchp in sorted(nodedict.values(), key=lambda x: x.name):
            print('{}  {}'.format(switchp.name, switchp.allleafs))
           # import pdb; pdb.set_trace()
            for leafp in switchp.leafprofiles:
                print('\t' + leafp.name)
                for fex in fexes:
                    for portlist in leafp.infraHPortSlist:
                        #print(fex.dn, portlist.infraRsAccBaseGrp.tDn)
                        if fex.dn in portlist.infraRsAccBaseGrp.tDn:
                            print('\t\t{} [fex ID: {}]'.format(fex, portlist.infraRsAccBaseGrp.fexId))
                          #  print(portlist.infraRsAccBaseGrp.fexId)
                        #for x in fexes:
                            for y in fex.infraHPortSlist:
                                #import pdb; pdb.set_trace()
                                print('\t\t\t' + y.infraRsAccBaseGrp.tDn)
                                #print(y.__dict__)
                                for z in y.infraPortsBlklist:
                                    if z.fromPort == z.toPort:
                                        print('\t\t\t\t ' + z.fromPort)
                                    else:   
                                        print('\t\t\t\t ' + z.fromPort + ' - ' + z.toPort)

                #import pdb; pdb.set_trace()
                for portlist in leafp.infraHPortSlist:
                    print('\t\t' + portlist.name)
                    #print(portlist.__dict__)
                    print('\t\t\t' + portlist.infraRsAccBaseGrp.tDn)
                    if portlist.infraRsAccBaseGrp.tCl == 'infraAccPortGrp':
                        print('\t\t\t' + 'individual')
                    elif portlist.infraRsAccBaseGrp.tCl == 'infraAccBndlGrp':
                        print('\t\t\t' + 'Port-channel')                    
                    elif portlist.infraRsAccBaseGrp.tCl == 'infraFexBndlGrp':
                        print('\t\t\t' + 'Fex-uplinks')
                    if portlist.infraFexPlist:
                        print('\t\t\t' + portlist.infraRsAccBaseGrp.fexId)
                    

                    #print('\t\t\t' + portlist.infraRsAccBaseGrp.tCl)
                    for z in portlist.infraPortsBlklist:
                        if z.fromPort == z.toPort:
                            print('\t\t\t\t ' + z.fromPort)
                        else:   
                            print('\t\t\t\t ' + z.fromPort + ' - ' + z.toPort)
            print('\n')
               # for fex in y.infraFexPlist:
               #     print('\t\t {}'.format(fex))
               #     print('\t\t  {}'.format(fex.allports))
                
                #nodedict[y.tDn].leafprofiles.append(x)
            #import pdb; pdb.set_trace()
        ask = custom_raw_input("\nRefresh [n]: ") or 'n'
        if ask != '' and ask[0].lower() == 'y':
            continue
        else:
            break

 #       for x in apps:
 #           print(x.name)
 #           for y in x.infraHPortSlist:
 #               print('\t' + y.name)
 #               for z in y.infraPortsBlklist:
 #                   print('\t\t ' + z.fromPort + ' - ' + z.toPort)
 #               for fex in y.infraFexPlist:
 #                   print('\t\t {}'.format(fex))
 #                   print('\t\t  {}'.format(fex.allports))
 #           #for y in x.infraRtAccPortPlist:
 #           #    print('\tSwitchprof: ' + y.tDn)
 #           for y in x.infraRtAccPortPlist:
 #               nodedict[y.tDn].leafprofiles.append(x)
        #import pdb; pdb.set_trace()
        #print('\n\n\n')
        #for z in nodedict.values():
        #    print('{}'.format(str(z)[str(z).find('nprof-')+6:]))
        #    print('\t{}'.format(z.allleafs))
        #    for zz in z.leafprofiles:
        #        print('\t{}'.format(str(zz)[str(zz).find('prof-')+5:]))
        #        print('\t\t{}'.format(zz.allports))
#
        #        #print(sorted(zz.allports.items(), key=lambda x: x[1][1]))
        #print('\n\n\n')
        #for f in fexes:
        #    print('{}'.format(f.dn))
        #    print('{}'.format(f.allports))
        #    for fn in f.infraHPortSlist:
        #        #print(fn.infraRsAccBaseGrp[0].fexId)
        #        #for fnx in fn.infraRsAccBaseGrp:
        #        print(fn.infraRsAccBaseGrp.tDn)
        #            #print('\t{}'.format(fnx.tDn))
        #    for x in f.infraFexBndlGrplist:
        #        for xx in x.infraRtAccBaseGrplist:
        #            print('\t\t\t{}'.format(xx.rn))
        #print('\n\n')
        #    #print('{}'.format())
        #import pdb; pdb.set_trace()
        raw_input()