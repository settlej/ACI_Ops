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
import logging
import os
import time
import itertools
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


#def goodspacing(column):
#    if column.fex:
#        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
#    elif column.fex == '':
#        return column.leaf + ' ' + str(column.name)
#
#def grouper(iterable, n, fillvalue=''):
#    "Collect data into fixed-length chunks or blocks"
#    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
#    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
#    return itertools.izip_longest(*args, fillvalue=fillvalue)
#
#def parseandreturnsingelist(liststring, collectionlist):
#    try:
#        rangelist = []
#        singlelist = []
#        seperated_list = liststring.split(',')
#        for x in seperated_list:
#            if '-' in x:
#                rangelist.append(x)
#            else:
#                singlelist.append(int(x))
#        if len(rangelist) >= 1:
#            for foundrange in rangelist:
#                tempsplit = foundrange.split('-')
#                for i in xrange(int(tempsplit[0]), int(tempsplit[1])+1):
#                    singlelist.append(int(i))
#   #     print(sorted(singlelist))
#        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
#            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
#            return 'invalid'
#        return list(set(singlelist)) 
#    except ValueError as v:
#        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
#        return 'invalid'
#
#class fabricPathEp(object):
#    def __init__(self, descr=None, dn=None,name=None, number=None):
#        self.name = name
#        self.descr = descr
#        self.dn = dn
#        self.number = number
#        self.leaf =  dn.split('/')[2].replace('paths','leaf')
#        self.shortname = name.replace('eth1/','')
#        self.removedint = '/'.join(dn.split('/')[:-2])
#        if 'extpaths' in self.dn:
#            self.fex = self.dn.split('/')[3].replace('extpaths','fex')
#        else:
#            self.fex = ''
#    def __repr__(self):
#        return self.dn
#    def __getitem__(self, number):
#        if number in self.dn:
#            return self.dn
#        else:
#            return None

class l1PhysIf():
    def __init__(self, interface):
        self.interface = interface
        self.rmonIfIn = None
        self.rmonEtherStats = None
        self.l1RsAttEntityPCons = None
        self.l1RsCdpIfPolCons = None
        self.ethpmPhysIf = None
        self.eqptIngrTotal5min = None
        self.eqptEgrTotal5min = None
        self.fvDomDef = []
        self.l1RtMbrIfs = []
        self.pcAggrMbrIf = []
    def add_phys_attr(self, kwargs):
        self.__dict__.update(**kwargs)
    def __str__(self):
        return self.interface
    def __repr__(self):
        return self.interface

#def physical_selection(all_leaflist,leaf=None):
#    import pdb; pdb.set_trace()
#    if leaf == None:
#        nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
#        nodelist.sort()
#        for num,node in enumerate(nodelist,1):
#            print("{}.) {}".format(num,node))
#        while True:
#            #try:
#                asknode = custom_raw_input('\nWhat leaf: ')
#                print('\r')
#                if asknode.strip().lstrip() == '' or '-' in asknode or ',' in asknode or not asknode.isdigit():
#                    print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
#                    continue
#                returnedlist = parseandreturnsingelist(asknode, nodelist)
#                if returnedlist == 'invalid':
#                    continue
#                chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
#                break
#            #except KeyboardInterrupt as k:
#            #    print('\n\nEnding Script....\n')
#            #    return
#    else:
#        chosenleafs = [leaf]
#    compoundedleafresult = []
#    for leaf in chosenleafs:
#        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
#              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
#              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
#        result = GetResponseData(url, cookie)
#        compoundedleafresult.append(result)
#    result = compoundedleafresult
#    interfacelist = []
#    interfacelist2 = []
#    for x in result:
#        for pathep in x:
#            dn = pathep['fabricPathEp']['attributes']['dn']
#            name = pathep['fabricPathEp']['attributes']['name']
#            descr = pathep['fabricPathEp']['attributes']['descr']
#            if 'extpaths' in dn:
#                interfacelist2.append(fabricPathEp(descr=descr, dn=dn ,name=name))
#            else:
#                interfacelist.append(fabricPathEp(descr=descr, dn=dn ,name=name))
#            
#    interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortname)))
#    interfacelist = sorted(interfacelist, key=lambda x: int(x.shortname))
#    interfacenewlist = interfacelist2 + interfacelist
#    interfacelist = []
#    interfacelist2 = []
#    finalsortedinterfacelist = sorted(interfacenewlist, key=lambda x: x.removedint)
#    interfacedict = {}
#    for num,interf in enumerate(finalsortedinterfacelist,1):
#        if interf != '':
#           interfacedict[interf] = str(num) + '.) '
#           interf.number = num
#    listlen = len(finalsortedinterfacelist) / 3
#    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
#    finalgrouped = zip(*firstgrouped)
#    for column in finalgrouped:
#        a = column[0].number
#        b = goodspacing(column[0]) + '  ' + column[0].descr
#        c = column[1].number
#        d = goodspacing(column[1]) + '  ' + column[1].descr
#        if column[2] == '' or column[2] == None:
#            e = ''
#            f = ''
#        else:
#            #e = interfacedict[column[2]]
#            e = column[2].number
#            f = goodspacing(column[2]) + '  ' + column[2].descr
#            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
#        print('{:6}.) {:42}{}.) {:42}{}.) {}'.format(a,b,c,d,e,f))
#    while True:
#        #try:
#            selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
#            print('\r')
#            if selectedinterfaces.strip().lstrip() == '' or '-' in selectedinterfaces or ',' in selectedinterfaces: # or not selectedinterfaces.isdigit():
#                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
#                continue
#            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
#            if intsinglelist == 'invalid':
#                continue
#            return filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist), leaf

def displayepgs(result):
    #print(result)
    if result[0]['l1PhysIf']['attributes']['layer'] == 'Layer3':
        print(' Layer 3 interface, no layer 2 EPGs\n')
        return
    if result[0]['l1PhysIf'].get('children'):
        for int in result[0]['l1PhysIf']['children']:
            for epgs in int['pconsCtrlrDeployCtx']['children']:
                epgpath = epgs['pconsResourceCtx']['attributes']['ctxDn'].split('/')
                #print(epgpath)
                tenant = epgpath[1][3:]
                app = epgpath[2][3:]
                epg = epgpath[3][4:]
                print(' {:10}{:15}{}'.format(tenant,app,epg))
    else:
        print(' No Epgs found!\n')


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    clear_screen()
    location_banner('Show interface counters and EPGs')
    while True:

        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print('\nSelect leaf(s): ')
        print('\r')
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")

        chosendestinterfaceobject, leaf = physical_selection(all_leaflist, apic, cookie, provideleaf=True)
        #import pdb; pdb.set_trace()
        interface =  chosendestinterfaceobject[0].name
        #str(chosendestinterfaceobject[0]).replace('paths','nodes')
        epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf[0]),apic=apic)
        #url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
        #print(url)
        epgresult = GetResponseData(epgurl, cookie)
            
        url = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?""".format(interface=str(interface),leaf=str(leaf[0]),apic=apic) \
                  + """query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,""" \
                  + """rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,"""\
                  + """l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min"""
        logger.info(url)
#rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg
           # query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min
        result = GetResponseData(url, cookie)
        
            #print(result)
            #https://192.168.255.2/api/node-101/mo/sys/phys-[eth1/12].json?query-target=subtree&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef
            #for x in kk['imdata'][0]['l1PhysIf']['children']:    
            #     for y in x:
        clear_screen() 
        while True:   
            interfaceObject = l1PhysIf(interface)
            for x in result:
                if x.get('rmonIfIn'):
                    interfaceObject.rmonIfIn = x['rmonIfIn']['attributes']
                elif x.get('rmonIfOut'):
                    interfaceObject.rmonIfOut = x['rmonIfOut']['attributes']
                elif x.get('rmonEtherStats'):
                    interfaceObject.rmonEtherStats =  x['rmonEtherStats']['attributes']
                elif x.get('ethpmPhysIf'):
                    interfaceObject.ethpmPhysIf = x['ethpmPhysIf']['attributes']
                elif x.get('l1PhysIf'):
                    interfaceObject.add_phys_attr(x['l1PhysIf']['attributes'])
                    for y in x['l1PhysIf']['children']:
                        if y.get('eqptIngrTotal5min'):
                            interfaceObject.eqptIngrTotal5min = y['eqptIngrTotal5min']['attributes']
                        elif y.get('eqptEgrTotal5min'):
                            interfaceObject.eqptEgrTotal5min = y['eqptEgrTotal5min']['attributes']
                elif x.get('fvDomDef'):
                    interfaceObject.fvDomDef.append(x['fvDomDef']['attributes'])
                elif x.get('l1RsAttEntityPCons'):
                    interfaceObject.l1RsAttEntityPCons = x['l1RsAttEntityPCons']['attributes']
                elif x.get('l1RsCdpIfPolCons'):
                    interfaceObject.l1RsCdpIfPolCons = x['l1RsCdpIfPolCons']['attributes']
                elif x.get('l1RtMbrIfs'):
                    interfaceObject.l1RtMbrIfs.append(x['l1RtMbrIfs']['attributes'])
                elif x.get('pcAggrMbrIf'):
                    interfaceObject.pcAggrMbrIf.append(x['pcAggrMbrIf']['attributes'])
            print('\n {} is {}, line protocol is {}'.format(interface.capitalize(),interfaceObject.adminSt,interfaceObject.ethpmPhysIf['operSt']))
            print(' Description: {}'.format(interfaceObject.descr))
            print(' MAC: {}'.format(interfaceObject.ethpmPhysIf['backplaneMac']))
            print(' Speed: {}, Duplex: {}, MTU: {}'.format(interfaceObject.ethpmPhysIf['operSpeed'],interfaceObject.ethpmPhysIf['operDuplex'].upper(),interfaceObject.mtu)) 
            print(' Auto negotiation: {}'.format(interfaceObject.autoNeg))
            print(' Operational layer: {}'.format(interfaceObject.layer))
            print(' Spanning destination interface: {}'.format(interfaceObject.spanMode))
            if interfaceObject.ethpmPhysIf['bundleIndex'] != 'unspecified':
                print(' Portchannal #: {}, Po name: (incomplete)'.format(interfaceObject.ethpmPhysIf['bundleIndex']))
                #if interfaceObject.l1RtMbrIfs:
                 #   for interf in interfaceObject.l1RtMbrIfs:
                        #print(interf['tDn'])
                        #print(interf['tSKey'])
                if interfaceObject.pcAggrMbrIf:
                    for interf in interfaceObject.pcAggrMbrIf:
                        print('   Port-Channel Type: {}'.format(interf['pcMode']))
            if interfaceObject.ethpmPhysIf['allowedVlans'] == '':
                interfaceObject.ethpmPhysIf['allowedVlans'] = 'None,'
            if interfaceObject.ethpmPhysIf['operVlans'] == '':
                interfaceObject.ethpmPhysIf['operVlans'] = 'None'
            print(' Configured internal vlans: {} Working internal vlans: {}'.format(interfaceObject.ethpmPhysIf['allowedVlans'],interfaceObject.ethpmPhysIf['operVlans']))
            print('')
            if interfaceObject.eqptEgrTotal5min == None:
                print(' [5 min] Input packet rate 0, Input Byte rate: 0')
                print(' [5 min] Output packet rate 0, Output Byte rate: 0')
            else:
                print(' [5 min] Input packet rate {}, Input Byte rate: {}'.format(round(float(interfaceObject.eqptIngrTotal5min['pktsRate']),2),round(float(interfaceObject.eqptIngrTotal5min['bytesRate']),2)))
                print(' [5 min] Output packet rate {}, Output Byte rate: {}'.format(round(float(interfaceObject.eqptEgrTotal5min['pktsRate']),2),round(float(interfaceObject.eqptEgrTotal5min['bytesRate']),2)))
            print(' RX')
            print('     input packets {}, bytes {}, broadcasts {}, mutlicasts {}'.format(interfaceObject.rmonEtherStats['tXNoErrors'],interfaceObject.rmonIfIn['octets'],interfaceObject.rmonIfIn['broadcastPkts'],interfaceObject.rmonIfIn['multicastPkts']))
            print('     input errors {}, giants {}, crc {}, fragments {}, oversize {}'.format(interfaceObject.rmonIfIn['errors'],interfaceObject.rmonEtherStats['rxGiantPkts'],interfaceObject.rmonEtherStats['cRCAlignErrors'],interfaceObject.rmonEtherStats['fragments'],interfaceObject.rmonEtherStats['rxOversizePkts']))
            print(' TX')
            print('     output packets {}, bytes {}, broadcasts {}, mutlicasts {}'.format(interfaceObject.rmonEtherStats['rXNoErrors'],interfaceObject.rmonIfOut['octets'],interfaceObject.rmonIfOut['broadcastPkts'],interfaceObject.rmonIfOut['multicastPkts']))
            print('     output errors {}, collisions {}, jabbers {}, drops {}'.format(interfaceObject.rmonIfOut['errors'],interfaceObject.rmonEtherStats['collisions'],interfaceObject.rmonEtherStats['jabbers'],interfaceObject.rmonEtherStats['dropEvents']))
            print('')
            print(' EPGs configured: {}'.format(interfaceObject.switchingSt))
            #if interfaceObject.switchingSt == 'enabled':
            print('')
            print(' {:10}{:15}{}'.format('Tenant','APP','EPG'))
            print(' ' + '-'*40)
            displayepgs(epgresult)
            #    print(' EPGs: ')
            print(' Configured usage type: {}'.format(interfaceObject.usage))            
            print('\n Availabe Domains: ')
            if interfaceObject.fvDomDef:
                for interf in interfaceObject.fvDomDef:
                    print(' {}'.format(interf['domPKey']))
            print('\n Profiles:')
            if interfaceObject.l1RsAttEntityPCons:
                print(' {}'.format(interfaceObject.l1RsAttEntityPCons['tDn']))
            if interfaceObject.l1RsCdpIfPolCons:
                print(' {}'.format(interfaceObject.l1RsCdpIfPolCons['tDn']))
            #if interfaceObject.l1RtMbrIfs:
            #    for interf in interfaceObject.l1RtMbrIfs:
            #        print(interf['tDn'])
            #        print(interf['tSKey'])
         #   if interfaceObject.pcAggrMbrIf:
         #       for interf in interfaceObject.pcAggrMbrIf:
         #           print(interf['pcMode'])
         #           print(interf['operSt'])
            epgresult = GetResponseData(epgurl, cookie)
            result = GetResponseData(url, cookie)
            time.sleep(6)
            clear_screen()


def single_interface_pull(import_apic,import_cookie, selectedleaf, interfacepull):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    authcounter = 0
    while True:
        #interface =  chosendestinterfaceobject[0].name
        leaf = selectedleaf
        interface = interfacepull
        #str(chosendestinterfaceobject[0]).replace('paths','nodes')
        epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf[0]),apic=apic)
        #url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
        #print(url)
        epgresult = GetResponseData(epgurl, cookie)
            
        url = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?""".format(interface=str(interface),leaf=str(leaf[0]),apic=apic) \
                  + """query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,""" \
                  + """rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,"""\
                  + """l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min"""

#rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg
           # query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min
        result = GetResponseData(url, cookie)
            #print(result)
            #https://192.168.255.2/api/node-101/mo/sys/phys-[eth1/12].json?query-target=subtree&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef
            #for x in kk['imdata'][0]['l1PhysIf']['children']:    
            #     for y in x:
       # clear_screen() 
        while True:   
            interfaceObject = l1PhysIf(interface)
            for x in result:
                if x.get('rmonIfIn'):
                    interfaceObject.rmonIfIn = x['rmonIfIn']['attributes']
                elif x.get('rmonIfOut'):
                    interfaceObject.rmonIfOut = x['rmonIfOut']['attributes']
                elif x.get('rmonEtherStats'):
                    interfaceObject.rmonEtherStats =  x['rmonEtherStats']['attributes']
                elif x.get('ethpmPhysIf'):
                    interfaceObject.ethpmPhysIf = x['ethpmPhysIf']['attributes']
                elif x.get('l1PhysIf'):
                    interfaceObject.add_phys_attr(x['l1PhysIf']['attributes'])
                    for y in x['l1PhysIf']['children']:
                        if y.get('eqptIngrTotal5min'):
                            interfaceObject.eqptIngrTotal5min = y['eqptIngrTotal5min']['attributes']
                        elif y.get('eqptEgrTotal5min'):
                            interfaceObject.eqptEgrTotal5min = y['eqptEgrTotal5min']['attributes']
                elif x.get('fvDomDef'):
                    interfaceObject.fvDomDef.append(x['fvDomDef']['attributes'])
                elif x.get('l1RsAttEntityPCons'):
                    interfaceObject.l1RsAttEntityPCons = x['l1RsAttEntityPCons']['attributes']
                elif x.get('l1RsCdpIfPolCons'):
                    interfaceObject.l1RsCdpIfPolCons = x['l1RsCdpIfPolCons']['attributes']
                elif x.get('l1RtMbrIfs'):
                    interfaceObject.l1RtMbrIfs.append(x['l1RtMbrIfs']['attributes'])
                elif x.get('pcAggrMbrIf'):
                    interfaceObject.pcAggrMbrIf.append(x['pcAggrMbrIf']['attributes'])
            print('\x1b[1;33;40m')
            if 'blacklist' in interfaceObject.usage:
                print('\n {} is Administratively Down'.format(interface.capitalize()))
            else:
                print('\n {} is {}, line protocol is {}'.format(interface.capitalize(),interfaceObject.adminSt,interfaceObject.ethpmPhysIf['operSt']))
            print(' Description: {}'.format(interfaceObject.descr))
            print(' MAC: {}'.format(interfaceObject.ethpmPhysIf['backplaneMac']))
            print(' Speed: {}, Duplex: {}, MTU: {}'.format(interfaceObject.ethpmPhysIf['operSpeed'],interfaceObject.ethpmPhysIf['operDuplex'].upper(),interfaceObject.mtu)) 
            print(' Auto negotiation: {}'.format(interfaceObject.autoNeg))
            print(' Operational layer: {}'.format(interfaceObject.layer))
            print(' Spanning destination interface: {}'.format(interfaceObject.spanMode))
            if interfaceObject.ethpmPhysIf['bundleIndex'] != 'unspecified':
                print(' Portchannal #: {}, Po name: (incomplete)'.format(interfaceObject.ethpmPhysIf['bundleIndex']))
                #if interfaceObject.l1RtMbrIfs:
                 #   for interf in interfaceObject.l1RtMbrIfs:
                        #print(interf['tDn'])
                        #print(interf['tSKey'])
                if interfaceObject.pcAggrMbrIf:
                    for interf in interfaceObject.pcAggrMbrIf:
                        print('   Port-Channel Type: {}'.format(interf['pcMode']))
            if interfaceObject.ethpmPhysIf['allowedVlans'] == '':
                interfaceObject.ethpmPhysIf['allowedVlans'] = 'None,'
            if interfaceObject.ethpmPhysIf['operVlans'] == '':
                interfaceObject.ethpmPhysIf['operVlans'] = 'None'
            print(' Configured internal vlans: {} Working internal vlans: {}'.format(interfaceObject.ethpmPhysIf['allowedVlans'],interfaceObject.ethpmPhysIf['operVlans']))
            print('')
            if interfaceObject.eqptEgrTotal5min == None:
                print(' [5 min] Input packet rate 0, Input Byte rate: 0')
                print(' [5 min] Output packet rate 0, Output Byte rate: 0')
            else:
                print(' [5 min] Input packet rate {}, Input Byte rate: {}'.format(round(float(interfaceObject.eqptIngrTotal5min['pktsRate']),2),round(float(interfaceObject.eqptIngrTotal5min['bytesRate']),2)))
                print(' [5 min] Output packet rate {}, Output Byte rate: {}'.format(round(float(interfaceObject.eqptEgrTotal5min['pktsRate']),2),round(float(interfaceObject.eqptEgrTotal5min['bytesRate']),2)))
            print(' RX')
            print('     input packets {}, bytes {}, broadcasts {}, mutlicasts {}'.format(interfaceObject.rmonEtherStats['tXNoErrors'],interfaceObject.rmonIfIn['octets'],interfaceObject.rmonIfIn['broadcastPkts'],interfaceObject.rmonIfIn['multicastPkts']))
            print('     input errors {}, giants {}, crc {}, fragments {}, oversize {}'.format(interfaceObject.rmonIfIn['errors'],interfaceObject.rmonEtherStats['rxGiantPkts'],interfaceObject.rmonEtherStats['cRCAlignErrors'],interfaceObject.rmonEtherStats['fragments'],interfaceObject.rmonEtherStats['rxOversizePkts']))
            print(' TX')
            print('     output packets {}, bytes {}, broadcasts {}, mutlicasts {}'.format(interfaceObject.rmonEtherStats['rXNoErrors'],interfaceObject.rmonIfOut['octets'],interfaceObject.rmonIfOut['broadcastPkts'],interfaceObject.rmonIfOut['multicastPkts']))
            print('     output errors {}, collisions {}, jabbers {}, drops {}'.format(interfaceObject.rmonIfOut['errors'],interfaceObject.rmonEtherStats['collisions'],interfaceObject.rmonEtherStats['jabbers'],interfaceObject.rmonEtherStats['dropEvents']))
            print('')
            print(' EPGs configured: {}'.format(interfaceObject.switchingSt))
            #if interfaceObject.switchingSt == 'enabled':
            print('')
            print(' {:10}{:15}{}'.format('Tenant','APP','EPG'))
            print(' ' + '-'*40)
            displayepgs(epgresult)
            #    print(' EPGs: ')
            print(' Configured usage type: {}'.format(interfaceObject.usage))            
            print('\n Availabe Domains: ')
            if interfaceObject.fvDomDef:
                for interf in interfaceObject.fvDomDef:
                    print(' {}'.format(interf['domPKey']))
            print('\n Profiles:')
            if interfaceObject.l1RsAttEntityPCons:
                print(' {}'.format(interfaceObject.l1RsAttEntityPCons['tDn']))
            print(' {}'.format(interfaceObject.l1RsCdpIfPolCons['tDn']))
            #if interfaceObject.l1RtMbrIfs:
            #    for interf in interfaceObject.l1RtMbrIfs:
            #        print(interf['tDn'])
            #        print(interf['tSKey'])
         #   if interfaceObject.pcAggrMbrIf:
         #       for interf in interfaceObject.pcAggrMbrIf:
         #           print(interf['pcMode'])
         #           print(interf['operSt'])
            epgresult = GetResponseData(epgurl, cookie)
            result = GetResponseData(url, cookie)
            print('\x1b[0m')
            #cookie = refreshToken(apic, cookie)
            refresh = custom_raw_input('Refresh [Y]: ') or 'Y'
            #import pdb; pdb.set_trace()
            if authcounter == 5:
                cookie = refreshToken(apic, cookie)
                authcounter = 0
            if refresh == 'Y':
                authcounter += 1
                continue
            else:
                break
        break


#['rmonifIn']['attributes'][errors'] == rx inpur errors
#elif x.get('rmonIfIn'):
#    print(x['rmonIfIn']['attributes']['bytes']) == rx bytes
#    print(x['rmonIfIn']['attributes']['multicastPkts'] == rx mulitcast packets
#if x.get('rmonIfOut'):
#    print(x['rmonIfOut']['attributes']['multicastPkts'] == tx mulitcast packets
#    print(x['rmonifOut']['attributes']['errors'] == tx out errorrs
#    print(x['rmonifOut']['attributes']['octets'] == tx bytes
#    print(x['rmonifOut']['attributes']['broadcastPkts'] == tx broadcast packets
#if x.get('rmonEtherStats'):
#    print(x['rmonEtherStats']['attributes']['cRCAlignErrors'] == CRC rx
#    print(x['rmonEtherStats']['attributes']['multicastPkts'] == tx mulitcast packets
#    print(x['rmonEtherStats']['attributes']['rxGiantPkts'] == rx rxGiantPkts
#    print(x['rmonEtherstats']['attributes']['rxOversizePkts'] == rx jumo packets
#    print(x['rmonEtherStats']['attributes']['txNoErrors'] == tx output packets
#if x.get('ethpmPhysIf'):
#    print(x['ethpmPhysIf']['attributes']['backplaneMac'] == interface mac
#    print(x['ethpmPhysIf']['attributes']['bundleIndex'] == port-channel number
#    print(x['ethpmPhysIf']['attributes']['operVlans'] == up vlans
#    print(x['ethpmPhysIf']['attributes']['allowedVlans'] == configed vlans
#    print(x['ethpmPhysIf']['attributes']['operDuplex'] == operDuplex
#    print(x['ethpmPhysIf']['attributes']['operSpeed'] == link operSpeed
#    print(x['ethpmPhysIf']['attributes']['operSt'] == link status
#if x.get('l1PhysIf'):
#    print(x['l1PhysIf']['attributes']['adminSt'] = up
#    print(x['l1PhysIf']['attributes']['autoNeg'] = on 
#    print(x['l1PhysIf']['attributes']['layer'] = layer2 or layer3
#    print(x['l1PhysIf']['attributes']['mtu'] 
#    print(x['l1PhysIf']['attributes']['descr']
#    print(x['l1PhysIf']['attributes']['spanMode'] = is span dest
#    print(x['l1PhysIf']['attributes']['switchingSt'] = epgs on interface
#    print(x['l1PhysIf']['attributes']['usage'] = epg,interface
#    print(x['l1PhysIf']['attributes']['speed'] = inherit
#if x.get('fvDomDef'):
#    print(x['fvDomDef']['attributes']['domPKey'] = domain allowed on interface
#if x.get('fvDomDef'):
#    print(x['l1RsAttEntityPCons']['attributes']['tDn'] = AAEP on interface
#if x.get('fvDomDef'):
#    print(x['l1RsCdpIfPolCons']['attributes']['tDn'] = current cdp policy
#if x.get('fvDomDef'):
#
#    print(x['l1RtMbrIfs']['attributes']['tDn'] == po tDn
#    print(x['l1RtMbrIfs']['attributes']['tSKey'] == po num
#if x.get('pcAggrMbrIf'):
#    print(x['pcAggrMbrIf']['attributes']['pcMode']
#    print(x['pcAggrMbrIf']['attributes']['operSt']
#
#
#
