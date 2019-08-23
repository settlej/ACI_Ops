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
import pdb
import os
from localutils.custom_utils import *

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

def get_All_leafs():
    url = """https://localhost/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))"""
    result, totalCount = GetResponseData(url)
    return result

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


def parseandreturnsingelist(liststring, collectionlist):
    try:
        rangelist = []
        singlelist = []
        seperated_list = liststring.split(',')
        for x in seperated_list:
            if '-' in x:
                rangelist.append(x)
            else:
                singlelist.append(int(x))
        if len(rangelist) >= 1:
            for foundrange in rangelist:
                tempsplit = foundrange.split('-')
                for i in xrange(int(tempsplit[0]), int(tempsplit[1])+1):
                    singlelist.append(int(i))
        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
            return 'invalid'
        return list(set(singlelist)) 
    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'

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
        url = """https://localhost/api/node-{}/class/l1PhysIf.json?rsp-subtree-class=rmonIfIn,rmonIfOut,pcAggrMbrIf,ethpmPhysIf,l1PhysIf,rmonEtherStats&rsp-subtree=full""".format(leaf)
      #  url = """https://localhost/api/class/l1PhysIf.json?rsp-subtree-class=rmonIfIn,pcAggrMbrIf,ethpmPhysIf,l1PhysIf&rsp-subtree=full""".format(leaf)
        #print(url)
        result, totalcount = GetResponseData(url)
        leafdictwithresults[leaf] = result
        #leaf_interface_collection.append(leafdictwithresults)
    #for l in sorted(leafdictwithresults):
     #   print(leafdictwithresults[l])
    #print(len(leaf_interface_collection))
    return leafdictwithresults


def leaf_selection(all_leaflist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    #print(nodelist)
    nodelist.sort()
    print('\nAvailable leafs to choose from:\n')
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
       # try:
            asknode = custom_raw_input('\nWhat leaf(s): ')
            print('\r')
            returnedlist = parseandreturnsingelist(asknode, nodelist)
            if returnedlist == 'invalid':
                continue
            leaflist =  [nodelist[int(node)-1] for node in returnedlist]
            #print(leaflist)
            return leaflist
        #except KeyboardInterrupt as k:
        #    print('\n\nEnding Script....\n')
        #    exit()
def match_port_channels_to_interfaces(interfaces, leaf):
   # for leaf in leafs:
    listofpcinterfaces = []
    url = """https://localhost/api/node/class/topology/pod-1/node-{}/pcAggrIf.json?rsp-subtree-include=relations&target-subtree-class=pcAggrIf,"""\
           """ethpmAggrIf&rsp-subtree=children&rsp-subtree-class=pcRsMbrIfs,ethpmAggrIf""".format(leaf)
  #  https://192.168.255.2/api/node/class/topology/pod-1/node-101/pcAggrIf.json?&target-subtree-class=pcAggrIf,ethpmAggrIf&rsp-subtree=children&rsp-subtree-class=pcRsMbrIfs,ethpmAggrIf
    result, totalcount = GetResponseData(url)
    #print(result)
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
            if pc.portmembers > 1:
                for pcinter in pc.portmembers:
                    if pcinter.tSKey ==  interface.id:
                        interface.add_portchannel(pc)
            else:
                print(pc.portmembers[0].tSkey, interface.id)
                if pcinter.tSKey == interface.id:
                
                    interface.add_portchannel(pc)
    
        

def print_interfaces_layout(leafallinterfacesdict,leafs):
    interface_output = ''
    print('-'*160)
    print('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}'.format('Port','Status', 'EPGs', 'SFP',  'In/Out Err', 'In/Out Packets', 'PcMode', 'PC #', 'PC/vPC Name','Description' ))
    print('-'*160)
    for leaf,leafinterlist in sorted(leafallinterfacesdict.items()):
        interfaces = gather_l1PhysIf_info(leafinterlist)
        #print(interfaces)
        match_port_channels_to_interfaces(interfaces, leaf)
    
    
        interfacelist = []
        interfacelist2 = []
        for inter in interfaces:
            if inter.id.count('/') > 1:
                removed_eth = inter.id[5:]
                ethlist = removed_eth.split('/')
                inter['fex']=int(ethlist[0])
                inter['shortnum']=int(ethlist[2])
                interfacelist2.append(inter)
            else:
                inter['shortnum'] = int(inter.id[5:])
                #print(inter.shortnum)
                interfacelist.append(inter)
                
        interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortnum)))
        interfacelist = sorted(interfacelist, key=lambda x: x.shortnum)
        interfacenewlist = interfacelist + interfacelist2
        interfacelist = []
        interfacelist2 = []
        currentleaf = '\x1b[2;30;47m{}\x1b[0m'.format(leaf)
        interface_output += currentleaf + '\n'
        for column in interfacenewlist:
            #print(column.children)

            #if column.id == 'eth1/8':
            #    pdb.set_trace()
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
           # elif
           #     sfp

            if column.pc_mbmr:
                interface_output += ('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}\n'.format(column.id, status, epgs_status,
                                           sfp , errors, packets, pcstatus + ' ' + pcmode, column.pc_mbmr[0].id, column.pc_mbmr[0],column.descr))#column.pc_mbmr[0].children[0].operVlans))
            else: 
                interface_output += ('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}\n'.format(column.id, status, epgs_status,
                                           sfp,errors, packets , '','','',column.descr))


    print(interface_output)

def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        leafs = leaf_selection(get_All_leafs())
        leafallinterfacesdict = pull_leaf_interfaces(leafs)
        print_interfaces_layout(leafallinterfacesdict,leafs)
    #for leafinterlist in allinterfaceslist:
    #    interfaces = gather_l1PhysIf_info(leafinterlist)
#
    #    interfaces = match_port_channels_to_interfaces(interfaces, leafs)
    #
    #
    #    interfacelist = []
    #    interfacelist2 = []
    #    for inter in interfaces:
    #        if inter.id.count('/') > 1:
    #            removed_eth = inter.id[5:]
    #            ethlist = removed_eth.split('/')
    #            inter['fex']=int(ethlist[0])
    #            inter['shortnum']=int(ethlist[2])
    #            interfacelist2.append(inter)
    #        else:
    #            inter['shortnum'] = int(inter.id[5:])
    #            #print(inter.shortnum)
    #            interfacelist.append(inter)
    #            
    #    interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortnum)))
    #    interfacelist = sorted(interfacelist, key=lambda x: x.shortnum)
    #    interfacenewlist = interfacelist + interfacelist2
    #    interfacelist = []
    #    interfacelist2 = []
#
#
    #for column in interfacenewlist:
    #    if column.adminSt == 'up' and (column.children[2].operStQual == 'sfp-missing' or column.children[2].operStQual == 'link-failure'):
    #        status = 'down/down'
    #    elif column.adminSt == 'down' and column.children[2].operStQual == 'admin-down':
    #        status = 'admin-down'
    #    else:
    #        status = 'up/up'
    #    if column.children[0].pcMode == 'on':
    #        pcmode = ''
    #    elif column.children[0].pcMode == 'static':
    #        pcmode = 'static'
    #    elif column.children[0].pcMode == 'active':
    #        pcmode = 'lacp'
    #    else:
    #        pcmode = column.children[0]
    #    errors = column.children[1]
#
    #    if column.children[2].children[0].typeName == '':
    #        sfp = 'sfp-missing'
    #    else:
    #        sfp = column.children[2].children[0]
    #    print('{:13}{:10}{:10}{:10}{:10}{:17}{}'.format(column.id, status, column.switchingSt,
    #                                  pcmode, errors, sfp ,column.descr))
  
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as k:
                print('\n\nEnding Script....\n')
                exit()
