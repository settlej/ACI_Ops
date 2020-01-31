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


class l1PhysIf():
    def __init__(self, interface):
        self.interface = interface
        self.rmonIfIn = None
        self.rmonEtherStats = None
        self.ethpmPhysIf = None
        self.eqptIngrTotal5min = None
        self.eqptEgrTotal5min = None
        self.fvDomDef = []
        self.l1RtMbrIfs = []
        self.pcAggrMbrIf = []
        self.l1RsAttEntityPCons = None
        self.l1RsCdpIfPolCons = None
        self.l1RsCoppIfPolCons = None
        self.l1RsDwdmIfPolCons = None
        self.l1RsFcIfPolCons = None
        self.l1RsHIfPolCons = None
        self.l1RsL2IfPolCons = None
        self.l1RsL2PortSecurityCons = None
        self.l1RsL3IfPolCons = None
        self.l1RsLldpIfPolCons = None
        self.l1RsMacsecPolCons = None
        self.l1RsMcpIfPolCons = None
        self.l1RsMonPolIfPolCons = None
        self.l1RsQosEgressDppIfPolCons = None
        self.l1RsQosIngressDppIfPolCons = None
        self.l1RsQosPfcIfPolCons = None
        self.l1RsQosSdIfPolCons = None
        self.l1RsStormctrlIfPolCons = None
        self.l1RsStpIfPolCons = None
    def add_phys_attr(self, kwargs):
        self.__dict__.update(**kwargs)
    def __str__(self):
        return self.interface
    def __repr__(self):
        return self.interface


def displayepgs(result):
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
                print('   {:10}{:15}{}'.format(tenant,app,epg))
    else:
        print('   \x1b[1;31;40mNo Epgs found!\x1b[0m\n')


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:
        clear_screen()
        location_banner('Show interface counters and EPGs')
        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print('\nSelect leaf(s): ')
        print('\r')
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        switchpreviewutil.main(apic,cookie,chosenleafs, purpose='port_switching')
        chosendestinterfaceobject = physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False)
        leaf = chosenleafs
        #chosendestinterfaceobject, leaf = physical_selection(all_leaflist, apic, cookie, provideleaf=True)
        #import pdb; pdb.set_trace()
        interface =  chosendestinterfaceobject[0].name
        epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf[0]),apic=apic)
        #url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
        logger.info(epgurl)
        epgresult = GetResponseData(epgurl, cookie)
        logger.debug(epgresult)
        url = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?""".format(interface=str(interface),leaf=str(leaf[0]),apic=apic) \
                  + """query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,""" \
                  + """rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,"""\
                  + """l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min,""" \
                  + """l1RsQosEgressDppIfPolCons,l1RsLldpIfPolCons,l1RsMonPolIfPolCons,l1RsStpIfPolCons,l1RsQosIngressDppIfPolCons,""" \
                  + """l1RsL2PortSecurityCons,l1RsStormctrlIfPolCons,l1RsL3IfPolCons,l1RsMacsecPolCons,l1RsDwdmIfPolCons,l1RsMcpIfPolCons,"""\
                  + """l1RsL2IfPolCons,l1RsFcIfPolCons,l1RsQosSdIfPolCons,l1RsCoppIfPolCons,l1RsHIfPolCons,l1RsQosPfcIfPolCons,l1RsStpIfPolCons"""

        logger.info(url)
        result = GetResponseData(url, cookie)
        clear_screen() 
        while True:   
            display_interface_stats(epgresult,interface, result)
            refresh = custom_raw_input('\nRefresh [Y]: ') or 'Y'
            if refresh.strip().lstrip().upper() == 'Y':
                clear_screen()
                continue
            elif refresh.strip().lstrip().upper() == 'N':
                break
            else:
                print('\nInvalid Option, Try again..\n')
            #break
                
def display_interface_stats(epgresult, interface, result):
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
      #  elif x.get('l1RsAttEntityPCons'):
      #      interfaceObject.l1RsAttEntityPCons = x['l1RsAttEntityPCons']['attributes']
      #  elif x.get('l1RsCdpIfPolCons'):
      #      interfaceObject.l1RsCdpIfPolCons = x['l1RsCdpIfPolCons']['attributes']
        elif x.get('l1RtMbrIfs'):
            interfaceObject.l1RtMbrIfs.append(x['l1RtMbrIfs']['attributes'])
        elif x.get('pcAggrMbrIf'):
            interfaceObject.pcAggrMbrIf.append(x['pcAggrMbrIf']['attributes'])
        elif x.get('l1RsAttEntityPCons'):
            interfaceObject.l1RsAttEntityPCons = x['l1RsAttEntityPCons']['attributes']
        elif x.get('l1RsCdpIfPolCons'):
            interfaceObject.l1RsCdpIfPolCons = x['l1RsCdpIfPolCons']['attributes']
        elif x.get('l1RsCoppIfPolCons'):
            interfaceObject.l1RsCoppIfPolCons = x['l1RsCoppIfPolCons']['attributes']
        elif x.get('l1RsDwdmIfPolCons'):
            interfaceObject.l1RsDwdmIfPolCons = x['l1RsDwdmIfPolCons']['attributes']
        elif x.get('l1RsFcIfPolCons'):
            interfaceObject.l1RsFcIfPolCons = x['l1RsFcIfPolCons']['attributes']
        elif x.get('l1RsHIfPolCons'):
            interfaceObject.l1RsHIfPolCons = x['l1RsHIfPolCons']['attributes']
        elif x.get('l1RsL2IfPolCons'):
            interfaceObject.l1RsL2IfPolCons = x['l1RsL2IfPolCons']['attributes']
        elif x.get('l1RsL2PortSecurityCons'):
            interfaceObject.l1RsL2PortSecurityCons = x['l1RsL2PortSecurityCons']['attributes']
        elif x.get('l1RsL3IfPolCons'):
            interfaceObject.l1RsL3IfPolCons = x['l1RsL3IfPolCons']['attributes']
        elif x.get('l1RsLldpIfPolCons'):
            interfaceObject.l1RsLldpIfPolCons = x['l1RsLldpIfPolCons']['attributes']
        elif x.get('l1RsMacsecPolCons'):
            interfaceObject.l1RsMacsecPolCons = x['l1RsMacsecPolCons']['attributes']
        elif x.get('l1RsMcpIfPolCons'):
            interfaceObject.l1RsMcpIfPolCons = x['l1RsMcpIfPolCons']['attributes']
        elif x.get('l1RsMonPolIfPolCons'):
            interfaceObject.l1RsMonPolIfPolCons = x['l1RsMonPolIfPolCons']['attributes']
        elif x.get('l1RsQosEgressDppIfPolCons'):
            interfaceObject.l1RsQosEgressDppIfPolCons = x['l1RsQosEgressDppIfPolCons']['attributes']
        elif x.get('l1RsQosIngressDppIfPolCons'):
            interfaceObject.l1RsQosIngressDppIfPolCons = x['l1RsQosIngressDppIfPolCons']['attributes']
        elif x.get('l1RsQosPfcIfPolCons'):
            interfaceObject.l1RsQosPfcIfPolCons = x['l1RsQosPfcIfPolCons']['attributes']
        elif x.get('l1RsQosSdIfPolCons'):
            interfaceObject.l1RsQosSdIfPolCons = x['l1RsQosSdIfPolCons']['attributes']
        elif x.get('l1RsStormctrlIfPolCons'):
            interfaceObject.l1RsStormctrlIfPolCons = x['l1RsStormctrlIfPolCons']['attributes']
        elif x.get('l1RsStpIfPolCons'):
            interfaceObject.l1RsStpIfPolCons = x['l1RsStpIfPolCons']['attributes']
    if interfaceObject.switchingSt == 'enabled' and interfaceObject.ethpmPhysIf['operSt'] == 'up' and not 'blacklist' in interfaceObject.usage:
        link_status = 'up/up'
    elif interfaceObject.switchingSt == 'disabled' and interfaceObject.ethpmPhysIf['operSt'] == 'up' and not 'blacklist' in interfaceObject.usage:
        link_status = 'up/down'
    else:
        link_status = 'down/down'
    if 'blacklist' in interfaceObject.usage:
        print('\n {}   is Administratively Down'.format(interface.capitalize()))
    else:
        if 'down' in link_status:
            print('\n {}\n   is admin {}, link-status is \x1b[1;31;40m{}\x1b[0m'.format(interface.capitalize(),interfaceObject.adminSt,link_status))
        
        else:
            print('\n {}\n   is admin {}, link-status is \x1b[1;33;40m{}\x1b[0m'.format(interface.capitalize(),interfaceObject.adminSt,link_status))
            
    print('   Description: {}'.format(interfaceObject.descr))
    print('   MAC: {}'.format(interfaceObject.ethpmPhysIf['backplaneMac']))
    print('   Speed: {}, Duplex: {}, MTU: {}'.format(interfaceObject.ethpmPhysIf['operSpeed'],interfaceObject.ethpmPhysIf['operDuplex'].upper(),interfaceObject.mtu)) 
    print('   Auto negotiation: {}'.format(interfaceObject.autoNeg))
    print('   Operational layer: {}'.format(interfaceObject.layer))
    print('   Spanning destination interface: {}'.format(interfaceObject.spanMode))
    if interfaceObject.ethpmPhysIf['bundleIndex'] != 'unspecified':
        print('   Portchannal #: {}, Po name: (incomplete)'.format(interfaceObject.ethpmPhysIf['bundleIndex']))
        #if interfaceObject.l1RtMbrIfs:
         #   for interf in interfaceObject.l1RtMbrIfs:
                #print(interf['tDn'])
                #print(interf['tSKey'])
        if interfaceObject.pcAggrMbrIf:
            for interf in interfaceObject.pcAggrMbrIf:
                print('     Port-Channel Type: {}'.format(interf['pcMode']))
    if interfaceObject.ethpmPhysIf['allowedVlans'] == '':
        interfaceObject.ethpmPhysIf['allowedVlans'] = 'None,'
    if interfaceObject.ethpmPhysIf['operVlans'] == '':
        interfaceObject.ethpmPhysIf['operVlans'] = 'None'
    print('   Configured internal vlans: {} Working internal vlans: {}'.format(interfaceObject.ethpmPhysIf['allowedVlans'],interfaceObject.ethpmPhysIf['operVlans']))
    print('')
    if interfaceObject.eqptEgrTotal5min == None:
        print('   [5 min] Input Byte rate: \x1b[1;33;40m0\x1b[0m, Input packet rate \x1b[1;33;40m0\x1b[0m')
        print('   [5 min] Output Byte rate: \x1b[1;33;40m0\x1b[0m, Output packet rate \x1b[1;33;40m0\x1b[0m')
    else:
        print('   [5 min] Input Byte rate: \x1b[1;33;40m{}\x1b[0m, Input packet rate \x1b[1;33;40m{}\x1b[0m'.format(round(float(interfaceObject.eqptIngrTotal5min['bytesRate']),2),round(float(interfaceObject.eqptIngrTotal5min['pktsRate']),2)))
        print('   [5 min] Output Byte rate: \x1b[1;33;40m{}\x1b[0m, Output packet rate \x1b[1;33;40m{}\x1b[0m'.format(round(float(interfaceObject.eqptEgrTotal5min['bytesRate']),2),round(float(interfaceObject.eqptEgrTotal5min['pktsRate']),2)))
    print('   RX')
    print('       input packets \x1b[1;33;40m{}\x1b[0m, bytes {}, broadcasts {}, mutlicasts {}'.format(interfaceObject.rmonEtherStats['rXNoErrors'],interfaceObject.rmonIfIn['octets'],interfaceObject.rmonIfIn['broadcastPkts'],interfaceObject.rmonIfIn['multicastPkts']))
    print('       input errors {}, giants {}, crc {}, fragments {}, oversize {}'.format(interfaceObject.rmonIfIn['errors'],interfaceObject.rmonEtherStats['rxGiantPkts'],interfaceObject.rmonEtherStats['cRCAlignErrors'],interfaceObject.rmonEtherStats['fragments'],interfaceObject.rmonEtherStats['rxOversizePkts']))
    print('   TX')
    print('       output packets \x1b[1;33;40m{}\x1b[0m, bytes {}, broadcasts {}, mutlicasts {}'.format(interfaceObject.rmonEtherStats['tXNoErrors'],interfaceObject.rmonIfOut['octets'],interfaceObject.rmonIfOut['broadcastPkts'],interfaceObject.rmonIfOut['multicastPkts']))
    print('       output errors {}, collisions {}, jabbers {}, drops {}'.format(interfaceObject.rmonIfOut['errors'],interfaceObject.rmonEtherStats['collisions'],interfaceObject.rmonEtherStats['jabbers'],interfaceObject.rmonEtherStats['dropEvents']))
    print('')
    print('   EPGs configured: {}'.format(interfaceObject.switchingSt))
    #if interfaceObject.switchingSt == 'enabled':
    print('')
    print('   {:10}{:15}{}'.format('Tenant','APP','EPG'))
    print('   ' + '-'*40 + '\x1b[1;33;40m')
    displayepgs(epgresult)
    print('\x1b[0m')
    #    print(' EPGs: ')
    print('    Configured usage type: {}'.format(interfaceObject.usage))            
    print('\n   Availabe Domains: ')
    if interfaceObject.fvDomDef:
        if len(interfaceObject.fvDomDef) >= 1:
            for interf in interfaceObject.fvDomDef:
                print('   {}'.format(interf['domPKey']))
        else:
            print('   \x1b[1;31;40m{}\x1b[0m'.format('No Domains found'))
    print('\n   Profiles:')
    if interfaceObject.l1RsAttEntityPCons:
        print('     \x1b[1;33;40m{}\x1b[0m'.format(interfaceObject.l1RsAttEntityPCons['tDn']))
    else:
        print('     \x1b[1;31;40m{}\x1b[0m'.format('AAEP Missing'))
    if interfaceObject.l1RsCdpIfPolCons:
        print('     {}'.format(interfaceObject.l1RsCdpIfPolCons['tDn']))
            #if interfaceObject.l1RtMbrIfs:
            #    for interf in interfaceObject.l1RtMbrIfs:
            #        print(interf['tDn'])
            #        print(interf['tSKey'])
         #   if interfaceObject.pcAggrMbrIf:
         #       for interf in interfaceObject.pcAggrMbrIf:
         #           print(interf['pcMode'])
         #           print(interf['operSt'])
    if interfaceObject.l1RsCoppIfPolCons:
        print('     {}'.format(interfaceObject.l1RsCoppIfPolCons['tDn']))                 
    if interfaceObject.l1RsDwdmIfPolCons:
        print('     {}'.format(interfaceObject.l1RsDwdmIfPolCons['tDn']))                 
    if interfaceObject.l1RsFcIfPolCons:
        print('     {}'.format(interfaceObject.l1RsFcIfPolCons['tDn']))                
    if interfaceObject.l1RsHIfPolCons:
        print('     {}'.format(interfaceObject.l1RsHIfPolCons['tDn']))                 
    if interfaceObject.l1RsL2IfPolCons:
        print('     {}'.format(interfaceObject.l1RsL2IfPolCons['tDn']))                 
    if interfaceObject.l1RsL2PortSecurityCons:
        print('     {}'.format(interfaceObject.l1RsL2PortSecurityCons['tDn']))                 
    if interfaceObject.l1RsL3IfPolCons:
        print('     {}'.format(interfaceObject.l1RsL3IfPolCons['tDn']))                 
    if interfaceObject.l1RsLldpIfPolCons:
        print('     {}'.format(interfaceObject.l1RsLldpIfPolCons['tDn']))                 
    if interfaceObject.l1RsMacsecPolCons:
        print('     {}'.format(interfaceObject.l1RsMacsecPolCons['tDn']))                 
    if interfaceObject.l1RsMcpIfPolCons:
        print('     {}'.format(interfaceObject.l1RsMcpIfPolCons['tDn']))                 
    if interfaceObject.l1RsMonPolIfPolCons:
        print('     {}'.format(interfaceObject.l1RsMonPolIfPolCons['tDn']))                 
    if interfaceObject.l1RsQosEgressDppIfPolCons:
        print('     {}'.format(interfaceObject.l1RsQosEgressDppIfPolCons['tDn']))                 
    if interfaceObject.l1RsQosIngressDppIfPolCons:
        print('     {}'.format(interfaceObject.l1RsQosIngressDppIfPolCons['tDn']))                 
    if interfaceObject.l1RsQosPfcIfPolCons:
        print('     {}'.format(interfaceObject.l1RsQosPfcIfPolCons['tDn']))                 
    if interfaceObject.l1RsQosSdIfPolCons:
        print('     {}'.format(interfaceObject.l1RsQosSdIfPolCons['tDn']))                 
    if interfaceObject.l1RsStormctrlIfPolCons:
        print('     {}'.format(interfaceObject.l1RsStormctrlIfPolCons['tDn']))                 
    if interfaceObject.l1RsStpIfPolCons:
        print('     {}'.format(interfaceObject.l1RsStpIfPolCons['tDn']))
    #epgresult = GetResponseData(epgurl, cookie)
    #result = GetResponseData(url, cookie)


def single_interface_pull(import_apic,import_cookie, selectedleaf, interfacepull):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    authcounter = 0
    while True:
        leaf = selectedleaf
        interface = interfacepull
        #str(chosendestinterfaceobject[0]).replace('paths','nodes')
        epgurl = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(interface=str(interface),leaf=str(leaf),apic=apic)
        #url = """https://{apic}/api/node/mo/{path}.json?rsp-subtree-include=full-deployment&target-node=all&target-path=l1EthIfToEPg""".format(apic=apic,path=str(chosendestinterfaceobject[0]))
        logger.info(epgurl)
        epgresult = GetResponseData(epgurl, cookie)
            
        url = """https://{apic}/api/node-{leaf}/mo/sys/phys-[{interface}].json?""".format(interface=str(interface),leaf=str(leaf),apic=apic) \
                  + """query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,""" \
                  + """rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,"""\
                  + """l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min"""
        logger.info(url)
           # query-target=subtree&rsp-subtree-include=stats&target-subtree-class=rmonIfOut,l1PhysIf,rmonIfIn,rmonEtherStats,ethpmPhysIf,l1RsAttEntityPCons,l1RsCdpIfPolCons,l1RtMbrIfs,pcAggrMbrIf,fvDomDef,eqptIngrTotal5min,eqptEgrTotal5min
        result = GetResponseData(url, cookie)
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
            if interfaceObject.switchingSt == 'enabled' and interfaceObject.ethpmPhysIf['operSt'] == 'up' and not 'blacklist' in interfaceObject.usage:
                link_status = 'up/up'
            elif interfaceObject.switchingSt == 'disabled' and interfaceObject.ethpmPhysIf['operSt'] == 'up' and not 'blacklist' in interfaceObject.usage:
                link_status = 'up/down'
            else:
                link_status = 'down/down'
            if 'blacklist' in interfaceObject.usage:
                print('\n {} is Administratively Down'.format(interface.capitalize()))
            else:
                print('\n {} is admin {}, link-status is {}'.format(interface.capitalize(),interfaceObject.adminSt,link_status))
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
                print(' [5 min] Input Byte rate: 0, Input packet rate 0')
                print(' [5 min] Output Byte rate: 0, Output packet rate 0')
            else:
                print(' [5 min] Input Byte rate: {}, Input packet rate {}'.format(round(float(interfaceObject.eqptIngrTotal5min['bytesRate']),2),round(float(interfaceObject.eqptIngrTotal5min['pktsRate']),2)))
                print(' [5 min] Output Byte rate: {}, Output packet rate {}'.format(round(float(interfaceObject.eqptEgrTotal5min['bytesRate']),2),round(float(interfaceObject.eqptEgrTotal5min['pktsRate']),2)))
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
