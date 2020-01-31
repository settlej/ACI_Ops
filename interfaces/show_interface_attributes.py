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
from collections import OrderedDict

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
class l1RsAttEntityPCons():
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
    #import pdb; pdb.set_trace()
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
        url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l1PhysIf.json?rsp-subtree=children&rsp-subtree-class=l1RsAttEntityPCons,l1RsQosEgressDppIfPolCons,l1RsLldpIfPolCons,l1RsMonPolIfPolCons,l1RsStpIfPolCons,l1RsQosIngressDppIfPolCons,l1RsL2PortSecurityCons,l1RsStormctrlIfPolCons,l1RsL3IfPolCons,l1RsMacsecPolCons,l1RsDwdmIfPolCons,l1RsMcpIfPolCons,l1RsL2IfPolCons,l1RsFcIfPolCons,l1RsQosSdIfPolCons,l1RsCoppIfPolCons,l1RsHIfPolCons,l1RsQosPfcIfPolCons,l1RsCdpIfPolCons,l1RsStpIfPolCons&order-by=l1PhysIf.id|asc""".format(apic=apic,leaf=leaf)
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


def print_attribute_layout(leafallinterfacesdict,leafs):
    for leaf,leafinterlist in sorted(leafallinterfacesdict.items()):
        interfaces = gather_l1PhysIf_info(leafinterlist)
        rowlist =[]
        for profile in interfaces:
            rowlist.append(rowobj(profile))
        rowstring = ''
        columnwidthfind = ('column1','column2','column3','column4','column5','column6',
        'column7','column8','column9','column10','column11','column12','column13','column14','column15','column16',
        'column17','column18','column19')
        headers = ('AAEP','CDP','CoPP','Dwdm','Fiber-Channel','Link Level','L2 Policy','Port-Security','L3 Policy',
        'LLDP','MACsec','MCP','Monitor','Egress D-Plane','Ingress D-Plane','Flow-Control','Slow-Drain','Storm-Control','Spanning-Tree')
        sizes = get_column_sizes(rowlist, columnwidthfind, minimum=5, baseminimum=headers)
        #sizes = map(lambda x: str(x)[str(x).find('-')+1:], sizes)
        print(' ' + '-'* (sum(sizes[:9]) + 42))
        
        #import pdb; pdb.set_trace()
        topstring = ' {:13} | {:{aaep}} | {:{cdp}} | {:{copp}} | {:{dwdm}} | {:{fc}} | {:{ll}} | {:{l2}} | {:{ps}} | {:{l3}} |'
        #topstring =' {:13} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} |'
        topstring = topstring.format('Interface', 'AAEP','CDP','CoPP','Dwdm','Fiber-Channel','Link Level','L2 Policy','Port-Security','L3 Policy',
                    aaep=sizes[0],cdp=sizes[1],copp=sizes[2],dwdm=sizes[3],fc=sizes[4],ll=sizes[5],l2=sizes[6],ps=sizes[7],l3=sizes[8])
        print(topstring)
        print(' {:-<13} | {:-<{aaep}} | {:-<{cdp}} | {:-<{copp}} | {:-<{dwdm}} | {:-<{fc}} | {:-<{ll}} | {:-<{l2}} | {:-<{ps}} | {:-<{l3}} |'.format(
            '','','','','','','','','','',aaep=sizes[0],cdp=sizes[1],copp=sizes[2],dwdm=sizes[3],fc=sizes[4],ll=sizes[5],l2=sizes[6],ps=sizes[7],l3=sizes[8]))

        for row in rowlist:
            if rowstring == '':
                rowstring += ' {:13} |'.format(row.id)
            rowstring += ' {:{aaep}} |'.format(str(row.column1),aaep=sizes[0])
            rowstring += ' {:{cdp}} |'.format(str(row.column2),cdp=sizes[1])
            rowstring += ' {:{copp}} |'.format(str(row.column3),copp=sizes[2])
            rowstring += ' {:{dwdm}} |'.format(str(row.column4),dwdm=sizes[3])
            rowstring += ' {:{fc}} |'.format(str(row.column5),fc=sizes[4])
            rowstring += ' {:{ll}} |'.format(str(row.column6),ll=sizes[5])
            rowstring += ' {:{l2}} |'.format(str(row.column7),l2=sizes[6])
            rowstring += ' {:{ps}} |'.format(str(row.column8),ps=sizes[7])
            rowstring += ' {:{l3}} |'.format(str(row.column9),l3=sizes[8])
            print(rowstring)
            rowstring =''
        
        #rowstring = ''
        #for profile in interfaces:
        #    od = OrderedDict(profile.profiles, key=lambda x:x[0])
        #    for column in sorted(od)[:10]:
        #        if rowstring == '':
        #            rowstring += ' {:13} |'.format(profile)
        #        else:
        #            if column == 'l1RsL2PortSecurityCons':
        #                rowstring += ' {:20} |'.format(profile.profiles[column].tDn[profile.profiles[column].tDn.find('-')+1:])
        #            else:
        #                #rowstring += ' {:20} |'.format(column)
        #                rowstring += ' {:20} |'.format(profile.profiles[column].tDn[profile.profiles[column].tDn.find('-')+1:])
        #    print(rowstring)
        #    rowstring = ''
        print('')
        print(' ' + '-'* (sum(sizes[9:]) + 45))
        #aaep=sizes[0],cdp=sizes[1],copp=sizes[2],dwdm=sizes[3],fc=sizes[4],ll=sizes[5],l2=sizes[6],ps=sizes[7],l3=sizes[8],lldp=sizes[9],macsec=sizes[10],mcp=sizes[11],mon=sizes[12],egress=sizes[13],ingress=sizes[14],flowc=sizes[15],slow=sizes[16],storm=sizes[17],stp=sizes[18])
        topstring = ' {:13} | {:{lldp}} | {:{macsec}} | {:{mcp}} | {:{mon}} | {:{egress}} | {:{ingress}} | {:{flowc}} | {:{slow}} | {:{storm}} | {:{stp}} |'
       # topstring = ' {:13} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} | {:20} |'
        topstring = topstring.format('Interface','LLDP','MACsec','MCP','Monitor','Egress D-Plane','Ingress D-Plane','Flow-Control','Slow-Drain','Storm-Control','Spanning-tree',
                    lldp=sizes[9],macsec=sizes[10],mcp=sizes[11],mon=sizes[12],egress=sizes[13],ingress=sizes[14],flowc=sizes[15],slow=sizes[16],storm=sizes[17],stp=sizes[18])
        print(topstring)
        print(' {:-<13} | {:-<{lldp}} | {:-<{macsec}} | {:-<{mcp}} | {:-<{mon}} | {:-<{egress}} | {:-<{ingress}} | {:-<{flowc}} | {:-<{slow}} | {:-<{storm}} | {:-<{stp}} |'.format(
                    '','','','','','','','','','','',lldp=sizes[9],macsec=sizes[10],mcp=sizes[11],mon=sizes[12],egress=sizes[13],ingress=sizes[14],flowc=sizes[15],
                    slow=sizes[16],storm=sizes[17],stp=sizes[18]))
        #print('-'*222)
        rowstring =''
        for row in rowlist:
            if rowstring == '':
                rowstring += ' {:13} |'.format(row.id)
            rowstring += ' {:{lldp}} |'.format(str(row.column10),lldp=sizes[9])
            rowstring += ' {:{macsec}} |'.format(str(row.column11),macsec=sizes[10])
            rowstring += ' {:{mcp}} |'.format(str(row.column12),mcp=sizes[11])
            rowstring += ' {:{mon}} |'.format(str(row.column13),mon=sizes[12])
            rowstring += ' {:{egress}} |'.format(str(row.column14),egress=sizes[13])
            rowstring += ' {:{ingress}} |'.format(str(row.column15),ingress=sizes[14])
            rowstring += ' {:{flowc}} |'.format(str(row.column16),flowc=sizes[15])
            rowstring += ' {:{slow}} |'.format(str(row.column17),slow=sizes[16])
            rowstring += ' {:{storm}} |'.format(str(row.column18),storm=sizes[17])
            rowstring += ' {:{stp}} |'.format(str(row.column19),stp=sizes[18])
            print(rowstring)
            rowstring =''
        #for profile in interfaces:
        #    od = OrderedDict(profile.profiles, key=lambda x:x[0])
        #    for column in sorted(od)[9:]:
#
        #        if rowstring == '':
        #            rowstring += ' {:13} |'.format(profile)
        #        else:
        #            if column == 'l1RsL2PortSecurityCons':
        #                rowstring += ' {:20} |'.format(profile.profiles[column].tDn[profile.profiles[column].tDn.find('-')+1:])
        #            else:
        #                #rowstring += ' {:20} |'.format(column)
        #                rowstring += ' {:20} |'.format(profile.profiles[column].tDn[profile.profiles[column].tDn.find('-')+1:])
        #    print(rowstring)
        #    rowstring = ''
        #rowlist = []
      #  for profile in interfaces:
      #      rowlist.append(row(profile))
      #  import pdb; pdb.set_trace()


class rowobj():
    column_order = {
       'column1'  : 'l1RsAttEntityPCons',
       'column2'  : 'l1RsCdpIfPolCons',
       'column3'  : 'l1RsCoppIfPolCons',
       'column4'  : 'l1RsDwdmIfPolCons',
       'column5'  : 'l1RsFcIfPolCons',
       'column6'  : 'l1RsHIfPolCons',
       'column7'  : 'l1RsL2IfPolCons',
       'column8'  : 'l1RsL2PortSecurityCons',
       'column9'  : 'l1RsL3IfPolCons',
       'column10' : 'l1RsLldpIfPolCons',
       'column11' : 'l1RsMacsecPolCons',
       'column12' : 'l1RsMcpIfPolCons',
       'column13' : 'l1RsMonPolIfPolCons',
       'column14' : 'l1RsQosEgressDppIfPolCons',
       'column15' : 'l1RsQosIngressDppIfPolCons',
       'column16' : 'l1RsQosPfcIfPolCons',
       'column17' : 'l1RsQosSdIfPolCons',
       'column18' : 'l1RsStormctrlIfPolCons',
       'column19' : 'l1RsStpIfPolCons'
       }
    def __init__(self, obj):
        self.id = obj.id
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
        for num, column in enumerate(sorted(obj.profiles.items())):
            #import pdb; pdb.set_trace()
          #  if len(obj.profiles) == 18:
            if obj.profiles.get(rowobj.column_order['column' + str(num+1)]):
                insideobj = obj.profiles[rowobj.column_order['column' + str(num+1)]] 
                if 'uni' in str(insideobj):
                    self['column' + str(num+1)] = str(insideobj)[str(insideobj).find('-')+1:]
                else:
                    self['column' + str(num+1)] = str(insideobj)

    
    def __setitem__(self, k,v):
        setattr(self, k, v)
    def __getitem__(self,k):
        return getattr(self,k)
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
        print_attribute_layout(leafallinterfacesdict,leafs)

        custom_raw_input('\n#Press enter to continue...')
