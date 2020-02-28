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
#import trace
#import pdb
import threading
import Queue
from collections import namedtuple
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging
import csv
from multiprocessing.dummy import Pool as ThreadPool

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)
logger.setLevel(logging.INFO)

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


class interface_elements():
    def __init__(self, leaf, interface, epgs, encap, deployment, desc=None):
        self.leaf = leaf
        self.interface = interface
        self.encap = encap
        self.deployment = deployment
        self.epgs = epgs
        self.userepgs = [tuple(x) for x in self.epgs]
        self.desc = desc



def main(import_apic,import_cookie):
    while True:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        allepglist = get_All_EGPs(apic,cookie)
        allpclist = get_All_PCs(apic,cookie)
        allvpclist = get_All_vPCs(apic,cookie)
        all_leaflist = get_All_leafs(apic,cookie)
        clear_screen()
        location_banner('CSV Auto Deploy Interfaces')
        completelist = []
        with open('deployment5.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for x in csv_reader:
                 completelist.append(filter(None, x))
        interface_elements_list = []
        for x in completelist:
           interface_elements_list.append(interface_elements(leaf=x[0], interface=x[1], epgs=[list(a) for a in zip(x[5].split(','), x[6:])], encap=x[3], deployment=x[4], desc=x[2]))
        url = """https://{apic}/api/class/fvAEPg.json""".format(apic=apic)
        result = GetResponseData(url, cookie)
        for x in result: 
            for y in interface_elements_list:
                for z in y.epgs:
                    if z[1] == x['fvAEPg']['attributes']['name']:
                        z[1] = x['fvAEPg']['attributes']['dn']
        descriptiondeployment_list = []
        vlanepgdeployment_list = []
        counter = 0
        print('\n T = Trunk\n A = Access(802.1p)\n')
        print("\x1b[1;33;40m {}".format('-'*64))
        print(" {:5}| {:10} | {:8}     | {}".format('Leaf','Interface','vlan #', 'Tenant-App-EPG'))
        print(" {}|{}|{}|{}".format('-'*5,'-'*12,'-'*14,'-'*30))
        #print(" {}|{}|{}|{}".format(' '*5,' '*12,' '*12,' '*30))
        for x in interface_elements_list:
            url = """https://{apic}/api/node/mo/uni/infra/hpaths-{leaf}_{interface}.json""".format(apic=apic, leaf=x.leaf, interface=x.interface.replace('/', '_'))
            #print(url)
            data = """{{"infraHPathS":{{"attributes":{{"descr":"{desc}"}},\"children\":[{{"infraRsHPathAtt":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/pathep-[{interface}]"}}}}}}]}}}}""".format(desc=x.desc, leaf=x.leaf, interface=x.interface)
            descriptiondeployment_list.append((url,data))
     #       try:
     #          # import pdb; pdb.set_trace()
     #           result, error = PostandGetResponseData(url, data, cookie)
     #          # print(result)
     #       except:
     #           import pdb; pdb.set_trace()
            for z in x.epgs:
                url = """https://{apic}/api/node/mo/{epg}.json""".format(apic=apic,epg=z[1])
                #import pdb; pdb.set_trace()
                if x.encap.lower() == 'trunk' and x.deployment.lower() == 'immediate':
                    data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlannum}","instrImedcy":"immediate","tDn":"topology/pod-1/paths-{leaf}/pathep-[{interface}]","status":"modified,created"}}}}}}""".format(vlannum=z[0],leaf=x.leaf,interface=x.interface)
                elif x.encap.lower() == 'access' and x.deployment.lower() == 'immediate':
                    data = """{{"fvRsPathAtt":{{"attributes":{{"mode":"native","encap":"vlan-{vlannum}","instrImedcy":"immediate","tDn":"topology/pod-1/paths-{leaf}/pathep-[{interface}]","status":"modified,created"}}}}}}""".format(vlannum=z[0],leaf=x.leaf,interface=x.interface)
                elif x.encap.lower() == 'trunk' and x.deployment.lower() == 'on-demand':
                    data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlannum}","instrImedcy":"lazy","tDn":"topology/pod-1/paths-{leaf}/pathep-[{interface}]","status":"modified,created"}}}}}}""".format(vlannum=z[0],leaf=x.leaf,interface=x.interface)
                elif x.encap.lower() == 'access' and x.deployment.lower() == 'on-demand':
                    data = """{{"fvRsPathAtt":{{"attributes":{{"mode":"native","encap":"vlan-{vlannum}","instrImedcy":"lazy","tDn":"topology/pod-1/paths-{leaf}/pathep-[{interface}]","status":"modified,created"}}}}}}""".format(vlannum=z[0],leaf=x.leaf,interface=x.interface)
                vlanepgdeployment_list.append((url,data))
                if counter == 0:
                    if x.encap.lower() == 'trunk':
                        print(""" {}  | {:10} | vlan-{:5} {} | {}""".format(x.leaf,x.interface,z[0],'T',z[1][4:].replace('tn-','').replace('ap-','').replace('epg-','')))
                    else:
                        print(""" {}  | {:10} | vlan-{:5} {} | {}""".format(x.leaf,x.interface,z[0],'A',z[1][4:].replace('tn-','').replace('ap-','').replace('epg-','')))
                    counter += 1
                else:
                    if x.encap.lower() == 'trunk':
                        print(""" {:4}   {:10} | vlan-{:5} {} | {}""".format('', '',z[0], 'T',z[1][4:].replace('tn-','').replace('ap-','').replace('epg-','')))
                    else:
                        print(""" {:4}   {:10} | vlan-{:5} {} | {}""".format('', '',z[0], 'A',z[1][4:].replace('tn-','').replace('ap-','').replace('epg-','')))
                    #counter -= 1
            if counter == 1:
                counter -= 1
            #if counter == 0:
            #    counter += 1
            #else:
            #    counter -= 1
        print('\x1b[0m')
        while True:
            ask = custom_raw_input('Confirm deployment?: [y|n]:')
            if ask != '' and ask[0].lower() == 'y':
                cancel = False
                break
            else:
                cancel = True
                break
        if cancel:
            print("\nCancelled!")
            custom_raw_input('\n#Press Enter to continue...')
            break
        pool = ThreadPool(10)
        #for x in sorted(vlanepgdeployment_list, key=lambda x:x[0]):
        #    import pdb; pdb.set_trace()
        #divideandconcurvlans_list = []
        #for x in vlanepgdeployment_list:
        #    for z in x[1]:
        #        divideandconcurvlans_list.append((x[0],z))
        results = pool.map(lambda x : PostandGetResponseData(x[0], x[1], cookie), vlanepgdeployment_list)
        #import pdb; pdb.set_trace()

        #import pdb; pdb.set_trace()
        #results = pool.map(PostandGetResponseData, vlanepgdeployment_list[0], vlanepgdeployment_list[1], cookie)
        pool.close()
        pool.join()
        for x in results:
            if x[1] is not None:
                print("Error", x[0], x[1])
        del(pool)
        pool = ThreadPool(10)
        results = pool.map(lambda x : PostandGetResponseData(x[0], x[1], cookie), descriptiondeployment_list)
        pool.close()
        pool.join()
        for x in results:
            if x[1] is not None:
                print("Error", x[0], x[1])
        custom_raw_input('\n#Press Enter to continue...')