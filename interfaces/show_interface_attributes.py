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


#['l1PrioFlowCtrlP']
#['l1RsQosEgressDppIfPolCons']
#['l1RsLldpIfPolCons']
#['l1RsMonPolIfPolCons']
#['l1RsStpIfPolCons']
#['l1RsQosIngressDppIfPolCons']
#['l1RsL2PortSecurityCons']
#['l1RsStormctrlIfPolCons']
#['l1RsL3IfPolCons']
#['l1RsMacsecPolCons']
#['l1RsDwdmIfPolCons']
#['l1RsMcpIfPolCons']
#['l1RsL2IfPolCons']
#['l1RsFcIfPolCons']
#['l1RsQosSdIfPolCons']
#['l1RsCoppIfPolCons']
#['l1RsHIfPolCons']
#['l1RsQosPfcIfPolCons']
#['l1RsCdpIfPolCons']

class l1PhysIf():
    def __init__(self, **kwargs):
        self.profiles = {}
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.id
    def __setitem__(self, a,b):
        setattr(self, a, b)

def gather_l1PhysIf_info(result):
    listofinterfaces = []
    for interface in result:
        physinterface = l1PhysIf(**interface['l1PhysIf']['attributes'])
        if interface['l1PhysIf'].get('children'):
            for children in interface['l1PhysIf']['children']:
                for child in children:
                    localobj = globals()[child]
                    physinterface.profiles[child] = localobj(children[child]['attributes'])
                #if children.get('pcAggrMbrIf'):
                #    physinterface.add_child(pcAggrMbrIf(**children['pcAggrMbrIf']['attributes']))
                #elif children.get('rmonIfIn'):
                #    physinterface.add_child(rmonIfIn(**children['rmonIfIn']['attributes']))
                #elif children.get('rmonIfOut'):
                #    physinterface.add_child(rmonIfIn(**children['rmonIfOut']['attributes']))
                #elif children.get('ethpmPhysIf'):
                #    ethpmFcotchildobject = ethpmPhysIf(**children['ethpmPhysIf']['attributes'])
                #    if children['ethpmPhysIf'].get('children'):
                #        for ethpmchild in children['ethpmPhysIf']['children']:
                #            if ethpmchild.get('ethpmFcot'):
                #                ethpmFcotchildobject.add_child(ethpmFcot(**ethpmchild['ethpmFcot']['attributes']))
                #    physinterface.add_child(ethpmFcotchildobject)
                #elif children.get('rmonEtherStats'):
                #    physinterface.add_child(rmonEtherStats(**children['rmonEtherStats']['attributes']))
        listofinterfaces.append(physinterface)
    import pdb; pdb.set_trace()
    return listofinterfaces

#def gather_l1PhysIf_info(result):
#    listofinterfaces = []
#    for interface in result:
#        physinterface = l1PhysIf(**interface['l1PhysIf']['attributes'])
#        if interface['l1PhysIf'].get('children'):
#            for children in interface['l1PhysIf']['children']:
#                if children.get('pcAggrMbrIf'):
#                    physinterface.add_child(pcAggrMbrIf(**children['pcAggrMbrIf']['attributes']))
#                elif children.get('rmonIfIn'):
#                    physinterface.add_child(rmonIfIn(**children['rmonIfIn']['attributes']))
#                elif children.get('rmonIfOut'):
#                    physinterface.add_child(rmonIfIn(**children['rmonIfOut']['attributes']))
#                elif children.get('ethpmPhysIf'):
#                    ethpmFcotchildobject = ethpmPhysIf(**children['ethpmPhysIf']['attributes'])
#                    if children['ethpmPhysIf'].get('children'):
#                        for ethpmchild in children['ethpmPhysIf']['children']:
#                            if ethpmchild.get('ethpmFcot'):
#                                ethpmFcotchildobject.add_child(ethpmFcot(**ethpmchild['ethpmFcot']['attributes']))
#                    physinterface.add_child(ethpmFcotchildobject)
#                elif children.get('rmonEtherStats'):
#                    physinterface.add_child(rmonEtherStats(**children['rmonEtherStats']['attributes']))
#        listofinterfaces.append(physinterface)
#    return listofinterfaces

def pull_leaf_interfaces(leafs):
    leafdictwithresults = {}
    leaf_interface_collection = []
    for leaf in leafs:
        #url = """https://{apic}/api/node-{}/class/l1PhysIf.json?rsp-subtree-class=rmonIfIn,rmonIfOut,pcAggrMbrIf,ethpmPhysIf,l1PhysIf,rmonEtherStats&rsp-subtree=full""".format(leaf,apic=apic)
        url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=l1RsQosEgressDppIfPolCons,l1RsLldpIfPolCons,l1RsMonPolIfPolCons,l1RsStpIfPolCons,l1RsQosIngressDppIfPolCons,l1RsL2PortSecurityCons,l1RsStormctrlIfPolCons,l1RsL3IfPolCons,l1RsMacsecPolCons,l1RsDwdmIfPolCons,l1RsMcpIfPolCons,l1RsL2IfPolCons,l1RsFcIfPolCons,l1RsQosSdIfPolCons,l1RsCoppIfPolCons,l1RsHIfPolCons,l1RsQosPfcIfPolCons,l1RsCdpIfPolCons&order-by=l1PhysIf.id|asc""".format(apic=apic,leaf=leaf)
        logger.info(url)
        result = GetResponseData(url, cookie)
        logger.debug(result)
        leafdictwithresults[leaf] = result
    return leafdictwithresults


def leaf_selection(all_leaflist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    nodelist.sort()
    print('\nAvailable leafs to choose from:\n')
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
        asknode = custom_raw_input('\nWhat leaf(s): ')
        print('\r')
        returnedlist = parseandreturnsingelist(asknode, nodelist)
        if returnedlist == 'invalid':
            continue
        leaflist =  [nodelist[int(node)-1] for node in returnedlist]
        return leaflist

def match_port_channels_to_interfaces(interfaces, leaf):
   # for leaf in leafs:
    listofpcinterfaces = []
    url = """https://{apic}/api/node/class/topology/pod-1/node-{}/pcAggrIf.json?rsp-subtree-include=relations&target-subtree-class=pcAggrIf,"""\
           """ethpmAggrIf&rsp-subtree=children&rsp-subtree-class=pcRsMbrIfs,ethpmAggrIf""".format(leaf,apic=apic)
    logger.info(url)
    result = GetResponseData(url, cookie)
    logger.debug(result)
    for pc in result:
        pcinterface = pcAggrIf(**pc['pcAggrIf']['attributes'])
        if pc['pcAggrIf'].get('children'):
            for children in pc['pcAggrIf']['children']:
                if children.get('pcRsMbrIfs'):
                    pcinterface.add_portmember(pcRsMbrIfs(**children['pcRsMbrIfs']['attributes']))
                elif children.get('ethpmAggrIf'):
                    pcinterface.add_child(ethpmAggrIf(**children['ethpmAggrIf']['attributes']))
        listofpcinterfaces.append(pcinterface)
    for interface in interfaces:
        for pc in listofpcinterfaces:
            if len(pc.portmembers) > 1:
                for pcinter in pc.portmembers:
                    if pcinter.tSKey ==  interface.id:
                        interface.add_portchannel(pc)
            else:
                if pc.portmembers[0].tSKey == interface.id:
                    interface.add_portchannel(pc)

def print_interfaces_layout(leafallinterfacesdict,leafs):
    interface_output = ''
    print('-'*160)
    print('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}'.format('Port','Status', 'EPGs', 'SFP',  'In/Out Err', 'In/Out Packets', 'PcMode', 'PC #', 'PC/vPC Name','Description' ))
    print('-'*160)
    for leaf,leafinterlist in sorted(leafallinterfacesdict.items()):
        interfaces = gather_l1PhysIf_info(leafinterlist)
        for profile in interfaces:
            print(profile)
            filteredlist = (filter(lambda x : hasattr(x, 'tDn'), profile.__dict__.values()))
            import pdb; pdb.set_trace()
            #print(profile.__dict__)
            print('\n\n')
        match_port_channels_to_interfaces(interfaces, leaf)
        interfacelist = []
        interfacelist2 = []
        for inter in interfaces:
            if inter.id.count('/') > 1:
                removed_eth = inter.id[3:]
                ethlist = removed_eth.split('/')
                inter['fex']=int(ethlist[0])
                inter['shortnum']=int(ethlist[2])
                interfacelist2.append(inter)
            else:
                inter['shortnum'] = int(inter.id[5:])
                interfacelist.append(inter)
                
        interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortnum)))
        interfacelist = sorted(interfacelist, key=lambda x: x.shortnum)
        interfacenewlist = interfacelist + interfacelist2
        interfacelist = []
        interfacelist2 = []
        currentleaf = '\x1b[2;30;47m{}\x1b[0m'.format(leaf)
        interface_output += currentleaf + '\n'
        for column in interfacenewlist:
            if column.adminSt == 'up' and (column.children[4].operStQual == 'sfp-missing' or column.children[4].operStQual == 'link-failure'):
                status = 'down/down'
            elif column.adminSt == 'down':
                status = 'admin-down'
            elif column.children[4].operStQual == 'suspended-due-to-no-lacp-pdus':
                status = 'down/down'
            else:
                status = 'up/up'
            if column.children[1].pcMode == 'on':
                pcmode = ''
            elif column.children[1].pcMode == 'static':
                pcmode = 'static'
            elif column.children[1].pcMode == 'active':
                pcmode = 'lacp'
            else:
                pcmode = column.children[1]
            errors = column.children[3].errors + '/' + column.children[2].errors
            if column.children[4].operStQual == 'admin-down' or column.children[4].operStQual == 'sfp-missing' or column.children[4].operStQual == 'link-failure':
                pcstatus = '(D)'
            elif column.children[4].operStQual.startswith('suspended'):
                pcstatus = '(s)'
            else:
                pcstatus = '(P)'
            if column.children[4].children[0].typeName == '' and not column.id.count('/') == 2:
                sfp = 'sfp-missing'
            else:
                sfp = column.children[4].children[0]
            if column.switchingSt == 'enabled':
                epgs_status = 'Yes'
            elif column.switchingSt == 'disabled':
                epgs_status = 'No'
            packets = column.children[0].rXNoErrors + '/' + column.children[0].tXNoErrors
            if column.pc_mbmr:
                interface_output += ('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}\n'.format(column.id, status, epgs_status,
                                           str(sfp) , errors, packets, pcstatus + ' ' + pcmode, column.pc_mbmr[0].id, column.pc_mbmr[0],column.descr))#column.pc_mbmr[0].children[0].operVlans))
            else: 
                interface_output += ('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}\n'.format(column.id, status, epgs_status,
                                           str(sfp),errors, packets , '','','',column.descr))
    print(interface_output)

def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Show interface status')
        leafs = leaf_selection(get_All_leafs(apic, cookie))
        leafallinterfacesdict = pull_leaf_interfaces(leafs)
        print_interfaces_layout(leafallinterfacesdict,leafs)
        custom_raw_input('#Press enter to continue...')
