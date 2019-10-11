#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import time
import json
import ssl
import trace
import pdb
import os
import Queue
import threading
import itertools
from localutils.custom_utils import *
import interfaces.interfacecounters as showinterface
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

#class l1PhysIf():
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#        self.fex = None
#        self.typefex = None 
#        self.uplink = None 
#        self.pctype = None
#       # self.
#        self.pc_mbmr = []
#        self.children = []
#    def __repr__(self):
#        return self.id
#    def __setitem__(self, a,b):
#        setattr(self, a, b)
#    def add_child(self, obj):
#        self.children.append(obj)
#    def __getitem__(self, x):
#        if x == self.id:
#            return True
#    def add_portchannel(self, p):
#        self.pc_mbmr.append(p) 
#    def port_status_color(self):
#        if self.portstatus == 'up/up' and self.switchingSt == 'enabled':
#            color = '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.portstatus == 'up/up' and self.switchingSt == 'disabled':
#            color = '\x1b[0;30;43m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.portstatus == 'admin-down':
#            #2;30;47
#            color = '\x1b[2;30;47m{:2}\x1b[0m'.format(self.shortnum)
#            #color = '\x1b[0;37;45m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        else:
#            color = '\x1b[1;37;41m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#    def port_type_color(self):
#        if 'controller' in self.usage:
#            color = '\x1b[1;37;45m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.layer == "Layer2" and self.pcmode == 'off' and self.epgs_status == 'Yes':
#            #light green
#            color = '\x1b[2;30;42m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.layer == "Layer2" and not self.pcmode == 'off' and self.pctype == 'pc':
#            color = '\x1b[5;30;42m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.layer == "Layer2" and not self.pcmode == 'off' and self.pctype == 'vpc':
#            color = '\x1b[2;37;44m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif 'fabric' in self.usage:
#            color = '\x1b[3;30;47m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.layer == "Layer3":
#            #orange
#            color = '\x1b[2;30;43m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.fex == True:
#            color = '\x1b[5;30;41m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        else:
#            color = '\x1b[5;30;37m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#    def port_error_color(self):
#        #if 100 <= self.allerrors >= 10 :
#        #    color = '\x1b[1;37;42{:2}\x1b[0m'.format(self.shortnum)
#        #    return color
#        if self.allerrors <= 100:
#            color = '\x1b[2;30;47m{:2}\x1b[0m'.format(self.shortnum)
#            return color        
#        elif 1000 <= self.allerrors >= 101:
#            color = '\x1b[3;30;46m{:2}\x1b[0m'.format(self.shortnum)
#            return color
#        elif self.allerrors >= 1001:
#            color = '\x1b[3;37;41m{:2}\x1b[0m'.format(self.shortnum)
#            return color          
#        else:
#            color = '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)
#            return color

        
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
#        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
#            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
#            return 'invalid'
#        return list(set(singlelist)) 
#    except ValueError as v:
#        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
#        return 'invalid'

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

def pull_leaf_interfaces(leaf, q):
    #leafdictwithresults = {}
    #leaf_interface_collection = []
    #for leaf in leafs:
    url = """https://{apic}/api/node-{}/class/l1PhysIf.json?rsp-subtree-class=rmonIfIn,rmonIfOut,pcAggrMbrIf,ethpmPhysIf,l1PhysIf,rmonEtherStats&rsp-subtree=full""".format(leaf,apic=apic)
      #  url = """https://{apic}/api/class/l1PhysIf.json?rsp-subtree-class=rmonIfIn,pcAggrMbrIf,ethpmPhysIf,l1PhysIf&rsp-subtree=full""".format(leaf)
        #print(url)
    logger.info(url)
    result = GetResponseData(url, cookie)
    logger.info('complete')
    q.put((leaf, result))
    #leafdictwithresults[leaf] = result
        #leaf_interface_collection.append(leafdictwithresults)
    #for l in sorted(leafdictwithresults):
     #   print(leafdictwithresults[l])
    #print(len(leaf_interface_collection))
    #return leafdictwithresults


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
    url = """https://{apic}/api/node/class/topology/pod-1/node-{}/pcAggrIf.json?rsp-subtree-include=relations&target-subtree-class=pcAggrIf,"""\
           """ethpmAggrIf&rsp-subtree=children&rsp-subtree-class=pcRsMbrIfs,ethpmAggrIf""".format(leaf,apic=apic)
  #  https://192.168.255.2/api/node/class/topology/pod-1/node-101/pcAggrIf.json?&target-subtree-class=pcAggrIf,ethpmAggrIf&rsp-subtree=children&rsp-subtree-class=pcRsMbrIfs,ethpmAggrIf
    logger.info(url)
    result = GetResponseData(url, cookie)
    logger.info('complete')
    logger.debug(result)
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
            if len(pc.portmembers) > 1:
                for pcinter in pc.portmembers:
                    if pcinter.tSKey ==  interface.id:
                        interface.add_portchannel(pc)
            else:
                #print(pc.portmembers[0].tSkey, interface.id)
                if pc.portmembers[0].tSKey == interface.id:
                    interface.add_portchannel(pc)
    
        

def print_interfaces_layout(leafallinterfacesdict,leafs):
    interface_output = ''
    nodeinterfacegrouping = []
    #print('-'*160)
    #print('{:13}{:14}{:5}{:18}{:12}{:26}{:12}{:7}{:28}{}'.format('Port','Status', 'EPGs', 'SFP',  'In/Out Err', 'In/Out Packets', 'PcMode', 'PC #', 'PC/vPC Name','Description' ))
    #print('-'*160)
    for leaf,leafinterlist in sorted(leafallinterfacesdict.items()):
        interfaces = gather_l1PhysIf_info(leafinterlist)
        match_port_channels_to_interfaces(interfaces, leaf)
        interfacelist = []
        interfacelist2 = []
        #print(leaf)
        #print(interfaces)
        for inter in interfaces:
            if inter.id.count('/') > 1:
                removed_eth = inter.id[3:]
                ethlist = removed_eth.split('/')
                inter['fex']=int(ethlist[0])
                inter['nodeid']='leaf{} fex{}'.format(str(leaf), str(ethlist[0]))
                inter['shortnum']=int(ethlist[2])
                interfacelist2.append(inter)
            else:
                inter['nodeid']='leaf{}'.format(str(leaf))
                inter['shortnum'] = int(inter.id[5:])
                interfacelist.append(inter)
                
        interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortnum)))
        interfacelist = sorted(interfacelist, key=lambda x: x.shortnum)
        interfacenewlist = interfacelist + interfacelist2
        interfacelist = []
        interfacelist2 = []
        currentleaf = '\x1b[2;30;47m{}\x1b[0m'.format(leaf)
        interface_output += currentleaf + '\n'
        url = """https://{apic}/api/node/class/infraAccBndlGrp.json?query-target=subtree&target-subtree-class=infraAccBndlGrp""".format(apic=apic)
        logger.info(url)
        result = GetResponseData(url, cookie)
        logger.info('complete')
        accbndlgrplist = []
        for pc in result:
            accbndlgrp = pc['infraAccBndlGrp']['attributes']["dn"]
            location = accbndlgrp.find('accbundle-') + 10
            bundlename = accbndlgrp[location:]
            bundletype = pc['infraAccBndlGrp']['attributes']['lagT']#:"uni/infra/funcprof/accbundle-Host3"lagT = node (vpc)
            accbndlgrplist.append((bundlename, bundletype))

        for column in interfacenewlist:
            #import pdb; pdb.set_trace()
            if column.adminSt == 'up' and (column.children[4].operStQual == 'sfp-missing' or column.children[4].operStQual == 'link-failure'):
                status = 'down/down'
            elif column.adminSt == 'down':
                status = 'admin-down'
            elif column.children[4].operStQual == 'suspended-due-to-no-lacp-pdus':
                status = 'down/down'
            else:
                status = 'up/up'
            column['portstatus'] = status
            if column.children[1].pcMode == 'on':
                pcmode = 'off'
            elif column.children[1].pcMode == 'static':
                pcmode = 'static'
            elif column.children[1].pcMode == 'active':
                pcmode = 'lacp'
            else:
                pcmode = column.children[1]
            column['pcmode'] = pcmode
            errors = column.children[3].errors + '/' + column.children[2].errors
            if column.children[4].operStQual == 'admin-down' or column.children[4].operStQual == 'sfp-missing' or column.children[4].operStQual == 'link-failure':
                pcstatus = '(D)'
            elif column.children[4].operStQual.startswith('suspended'):
                pcstatus = '(s)'
            else:
                pcstatus = '(P)'
            column['pcstatus'] = pcstatus[1:-1]
            if column.children[4].children[0].typeName == '' and not column.id.count('/') == 2:
                sfp = 'sfp-missing'
            else:
                sfp = column.children[4].children[0]
            column['sfp'] = sfp
            if 'epg' in column.usage:
                epgs_status = 'yes'
            elif not 'epg' in column.usage:
                epgs_status = 'no'
            #if column.switchingSt == 'enabled':
            #    epgs_status = 'Yes'
            #elif column.switchingSt == 'disabled':
            #    epgs_status = 'No'
            column['epgs_status'] = epgs_status
            packets = column.children[0].rXNoErrors + '/' + column.children[0].tXNoErrors
            #import pdb; pdb.set_trace()
            column.allerrors = int(column.children[3].errors) + int(column.children[2].errors)
            if column.mode == 'fex-fabric':
                column['fex'] = True
            if column.pc_mbmr:
                column['pclocalnum'] = column.pc_mbmr[0].id
                column['pcname'] = column.pc_mbmr[0]
                for pc in accbndlgrplist:
                    logger.debug(pc)
                    logger.debug(column.pcname)
                    if str(pc[0]) == str(column.pcname):
                        if str(pc[1]) == 'node':
                            column['pctype'] = 'vpc'
                        elif str(pc[1]) == 'link':
                            column['pctype'] = 'pc'       
            else: 
                column['pclocalnum'] = None
                column['pcname'] = None
                column['pctype'] = None
                column['fex'] == False
        #import pdb; pdb.set_trace()
        nodeinterfacegrouping.append(interfacenewlist)
    #print(nodeinterfacegrouping)
    return nodeinterfacegrouping

def dispaly_port_status(nodeinterfacegrouping):
    print('='*80)
    print('Green:up/up, Yellow:up/down, Red:down/down, White:admin-down\n')
    for node in nodeinterfacegrouping:
        #print(node)
        #print('\n\n\n')
        groups = []
        uniquekeys = []
        data = node
        for k, g in itertools.groupby(data, lambda x:x.nodeid):
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        evenlist = []
        oddlist = []
        for group in groups:
            #if group[0].fex:
            print('{:^80}'.format(group[0].nodeid))
            for num,inters in enumerate(group):
                if num % 2:
                    evenlist.append(inters)
                else:
                    oddlist.append(inters)
            oddstring = ''
            for odd in oddlist:
                oddstring += odd.port_status_color() + ' '
                #print odd.port_status_color(),
            print(oddstring)
            for even in evenlist:
                print even.port_status_color(),
            print('\n')
            oddlist = []
            evenlist = []
        groups = []

def display_port_types(nodeinterfacegrouping):
    print('='*80)
    print('Blue:VPC, Green:L2 + EPGS, Yellow:L3, Purple:APIC, Red:Fex-uplinks, White:Uplinks\nRed-Numbers:Span-dest, Black:Not-Setup\n')

    for node in nodeinterfacegrouping:
        #print(node)
        #print('\n\n\n')
        groups = []
        uniquekeys = []
        data = node
        for k, g in itertools.groupby(data, lambda x:x.nodeid):
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        evenlist = []
        oddlist = []
        for group in groups:
            print('{:^80}'.format(group[0].nodeid + ' (Port Usage)'))
            #print('\x1b[1;33;40m{:^80}\x1b[0m'.format(group[0].nodeid + ' (Port Usage)'))
            #print('\x1b[5;37;47m')
            for num,inters in enumerate(group):
                if num % 2:
                    evenlist.append(inters)
                else:
                    oddlist.append(inters)
            oddstring = ''
            for odd in oddlist:
                oddstring += odd.port_type_color() + ' '
                #print odd.port_status_color(),
            print(oddstring)
            evenstring = ''
            for even in evenlist:
                evenstring += even.port_type_color() + ' '
            print(evenstring + '\n')
            #import pdb; pdb.set_trace()
            oddlist = []
            evenlist = []
        groups = []


def display_port_errors(nodeinterfacegrouping):
    print('='*80)
    print('White: 100 > errors, Yellow: 100 between 1000 errors, Red: > 1000 errors\n')
    for node in nodeinterfacegrouping:
        #print(node)
        #print('\n\n\n')
        groups = []
        uniquekeys = []
        data = node
        for k, g in itertools.groupby(data, lambda x:x.nodeid):
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        evenlist = []
        oddlist = []
        for group in groups:
            print('{:^80}'.format(group[0].nodeid + ' (Errors)'))

            #print('Green: , Green:L2 + EPGS , Yellow:L3 , Black:L2')

            #print('\x1b[5;37;47m')
            for num,inters in enumerate(group):
                if num % 2:
                    evenlist.append(inters)
                else:
                    oddlist.append(inters)
            oddstring = ''
            for odd in oddlist:
                oddstring += odd.port_error_color() + ' '
                #print odd.port_status_color(),
            print(oddstring)
            evenstring = ''
            for even in evenlist:
                evenstring += even.port_error_color() + ' '
            print(evenstring + '\n')
            #import pdb; pdb.set_trace()
            oddlist = []
            evenlist = []
        groups = []
    



def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Switch View')
        q = Queue.Queue()
        leafs = leaf_selection(get_All_leafs(apic, cookie))
        counter = 0
        authcounter = 0
        action = ''
        while True:
            if counter == 0:
                threadlist = []
                leafdictwithresults = {}
                for leaf in leafs:
                    t = threading.Thread(target=pull_leaf_interfaces, args=[leaf,q])
                    t.start()
                    threadlist.append(t)
                resultlist = []
                for thread in threadlist:
                    thread.join()
                    resultlist.append(q.get())
                for result in resultlist:
                    leafdictwithresults[result[0]] = result[1]
            #leafallinterfacesdict = pull_leaf_interfaces(leafs
                nodeinterfacegrouping = print_interfaces_layout(leafdictwithresults,leafs)
                counter += 1  
            clear_screen()
            dispaly_port_status(nodeinterfacegrouping)
            #Pre-pull for refresh
            threadlist = []
            leafdictwithresults = {}
            for leaf in leafs:
                t = threading.Thread(target=pull_leaf_interfaces, args=[leaf,q])
                t.start()
                threadlist.append(t)
            resultlist = []
            for thread in threadlist:
                thread.join()
                resultlist.append(q.get())
            for result in resultlist:
                leafdictwithresults[result[0]] = result[1]
            nodeinterfacegrouping = print_interfaces_layout(leafdictwithresults,leafs)
            authcounter += 1
            if authcounter == 5:
                refreshToken(apic,cookie)
                authcounter = 0 
            if action == 'a':
                time.sleep(3)
                continue
            action = custom_raw_input("Options ('a' = auto refresh 3 sec, 'm' = manual refresh, 's' = int stats) default=[m]:")
            if action == 'm':
                continue
            elif action == 's':
                interfacesearch = custom_raw_input('interface (xxx ethx/x) [example: 101 eth1/1]: ')
                leaf, interfacepull = interfacesearch.split()
                showinterface.single_interface_pull(apic,cookie, leaf, interfacepull)
                cookie = refreshToken(apic, cookie)
            #import pdb; pdb.set_trace()
            
def main_detail(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        clear_screen()
        location_banner('Switch View (Detail)')
        q = Queue.Queue()
        leafs = leaf_selection(get_All_leafs(apic, cookie))
        #import pdb; pdb.set_trace()
        counter = 0
        authcounter = 0
        action = ''
        while True:
            if counter == 0:
                threadlist = []
                leafdictwithresults = {}
                for leaf in leafs:
                    t = threading.Thread(target=pull_leaf_interfaces, args=[leaf,q])
                    t.start()
                    threadlist.append(t)
                resultlist = []
                for thread in threadlist:
                    thread.join()
                    resultlist.append(q.get())
                for result in resultlist:
                    leafdictwithresults[result[0]] = result[1]
            #leafallinterfacesdict = pull_leaf_interfaces(leafs)    
                nodeinterfacegrouping = print_interfaces_layout(leafdictwithresults,leafs)
                counter += 1
            clear_screen()
            dispaly_port_status(nodeinterfacegrouping)
            display_port_types(nodeinterfacegrouping)
            display_port_errors(nodeinterfacegrouping)
            threadlist = []
            leafdictwithresults = {}
            for leaf in leafs:
                t = threading.Thread(target=pull_leaf_interfaces, args=[leaf,q])
                t.start()
                threadlist.append(t)
            resultlist = []
            for thread in threadlist:
                thread.join()
                resultlist.append(q.get())
            for result in resultlist:
                leafdictwithresults[result[0]] = result[1]
            nodeinterfacegrouping = print_interfaces_layout(leafdictwithresults,leafs)
            authcounter += 1
            if authcounter == 5:
                refreshToken(apic,cookie)
                authcounter = 0 
            if action == 'a':
                time.sleep(3)
                continue
            action = custom_raw_input("Options ('a' = auto refresh 3 sec, 'm' = manual refresh) default=[m]:")
            if action == 'm':
                continue
            #import pdb; pdb.set_trace()
