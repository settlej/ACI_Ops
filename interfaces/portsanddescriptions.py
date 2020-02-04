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

class l1PhysIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.pc_mbmr = []
        self.children = []
    def __repr__(self):
        return self.id
    def __setitem__(self, a,b):
        setattr(self, a, b)
    def add_child(self, obj):
        self.children.append(obj)
    def __getitem__(self, x):
        if x == self.id:
            return True
    def add_portchannel(self, p):
        self.pc_mbmr.append(p) 

class pcAggrMbrIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.pcMode

class rmonIfIn():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.errors
class rmonIfOut():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.errors

class ethpmPhysIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.children = []
    def __repr__(self):
        return self.operSt
    def add_child(self, obj):
        self.children.append(obj)

class ethpmFcot():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.typeName

class rmonEtherStats():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.rn

class pcAggrIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.children = []
        self.portmembers = []
    def __repr__(self):
        return self.name
    def add_child(self, child):
        self.children.append(child)
    def add_portmember(self, x):
        self.portmembers.append(x)

class pcRsMbrIfs():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.tSKey

class ethpmAggrIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return self.allowedvlans


def gather_l1PhysIf_info(result):
    listofinterfaces = []
    for interface in result:
        physinterface = l1PhysIf(**interface['l1PhysIf']['attributes'])
        if interface['l1PhysIf'].get('children'):
            for children in interface['l1PhysIf']['children']:
                if children.get('pcAggrMbrIf'):
                    physinterface.add_child(pcAggrMbrIf(**children['pcAggrMbrIf']['attributes']))
                elif children.get('rmonIfIn'):
                    physinterface.add_child(rmonIfIn(**children['rmonIfIn']['attributes']))
                elif children.get('rmonIfOut'):
                    physinterface.add_child(rmonIfIn(**children['rmonIfOut']['attributes']))
                elif children.get('ethpmPhysIf'):
                    ethpmFcotchildobject = ethpmPhysIf(**children['ethpmPhysIf']['attributes'])
                    if children['ethpmPhysIf'].get('children'):
                        for ethpmchild in children['ethpmPhysIf']['children']:
                            if ethpmchild.get('ethpmFcot'):
                                ethpmFcotchildobject.add_child(ethpmFcot(**ethpmchild['ethpmFcot']['attributes']))
                    physinterface.add_child(ethpmFcotchildobject)
                elif children.get('rmonEtherStats'):
                    physinterface.add_child(rmonEtherStats(**children['rmonEtherStats']['attributes']))
        listofinterfaces.append(physinterface)
    return listofinterfaces

def pull_leaf_interfaces(leafs):
    leafdictwithresults = {}
    leaf_interface_collection = []
    for leaf in leafs:
        url = """https://{apic}/api/node-{}/class/l1PhysIf.json?rsp-subtree-class=rmonIfIn,rmonIfOut,pcAggrMbrIf,ethpmPhysIf,l1PhysIf,rmonEtherStats&rsp-subtree=full""".format(leaf,apic=apic)
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

class rowobj():
    def __init__(self, args,headers):
        for k,v in zip(headers,args):
            #import pdb; pdb.set_trace()
            self[k] = v
    def __setitem__(self, k,v):
        setattr(self, k, v)
    def __getitem__(self,k):
        return getattr(self,k)

def print_interfaces_layout(leafallinterfacesdict,leafs):
    interface_output = ''
    topstringheaders = ('Port','Status', 'EPGs', 'SFP',  'In/Out_Err', 'In/Out_Packets', 'PcMode', 'PC #', 'PC/vPC_Name','Description')
    leaflist = []
    for currentleaf,leafinterlist in sorted(leafallinterfacesdict.items()):
        interfaces = gather_l1PhysIf_info(leafinterlist)
        match_port_channels_to_interfaces(interfaces, currentleaf)
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
        
        rowobj_headers = ('id','status','epgs_status','sfp','errors','packets','pcstatus','pcid','pc_name','descr')
        rowlist = []
        
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
                #interface_output += ('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}\n'.format(column.id, status, epgs_status,
                                           #str(sfp) , errors, packets, '{} {}'.format(pcstatus,pcmode), column.pc_mbmr[0].id, column.pc_mbmr[0],column.descr))#column.pc_mbmr[0].children[0].operVlans))
                rowlist.append((column.id, status, epgs_status, str(sfp) , errors, packets, '{} {}'.format(pcstatus,pcmode),
                             column.pc_mbmr[0].id, column.pc_mbmr[0],column.descr))
            else: 
                rowlist.append((column.id, status, epgs_status,str(sfp),errors, packets , '','','',column.descr))
                #interface_output += ('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}\n'.format(column.id, status, epgs_status,
                                          # str(sfp),errors, packets , '','','',column.descr))
        leaflist.append((currentleaf, rowlist))

    allsizes = []
    for leaf in leaflist:
        allsizes.append(get_column_sizes(leaf[1], minimum=5,baseminimum=topstringheaders))
    allsizes = zip(*allsizes)
    sizes = map(max, allsizes)
    topstring = ' {:{column0}}    {:{column1}}  {:{column2}}  {:{column3}}  {:{column4}}  {:{column5}}  {:{column6}}  {:{column7}}  {:{column8}}  {:{column9}}'.format(
        *topstringheaders,column0=sizes[0],column1=sizes[1],column2=sizes[2],column3=sizes[3],
            column4=sizes[4],column5=sizes[5],column6=sizes[6],column7=sizes[7],column8=sizes[8],column9=sizes[9])

    rowstring = ''
    for leaf in leaflist:
        print(' ' + '-' * (sum(sizes) + 21))
        print(topstring)
        print(' ' + '-' * (sum(sizes) + 21))
        print(' \x1b[2;30;47mleaf '+ leaf[0] + '\x1b[0m')
        for row in leaf[1]:
            rowstring += (' {:{column0}}    {:{column1}}  {:{column2}}  {:{column3}}  {:{column4}}  {:{column5}}  {:{column6}}  {:{column7}}  {:{column8}}  {:{column9}}\n').format(
                row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],column0=sizes[0],column1=sizes[1],column2=sizes[2],column3=sizes[3],
                column4=sizes[4],column5=sizes[5],column6=sizes[6],column7=sizes[7],column8=sizes[8],column9=sizes[9])
        print(rowstring)
        rowstring = ''
        #import pdb; pdb.set_trace()
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
