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
import threading
import Queue
import interfaces.switchpreviewutil as switchpreviewutil
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger('aciops.' + __name__)

class rmonIf():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.name = '/'.join(self.dn.split('/')[4:-1])[6:-1]
        self.leaf = self.dn.split('/')[2]
        self.pod = self.dn.split('/')[1]
    def __repr__(self):
        return self.dn

class eqpt():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
        self.name = '/'.join(self.dn.split('/')[4:-1])[6:-1]
        self.leaf = self.dn.split('/')[2]
        self.pod = self.dn.split('/')[1]
    def __repr__(self):
        return self.dn


class perleaf_locall1PhysIf():
    def __init__(self, leaf,  kwargs, interface = None, incounter = None , outcounter = None):
        self.__dict__.update(**kwargs)
        self.name = ''.join(self.dn.split('[')[1][:-1])
        self.leaf = leaf
        self.interface = interface
        self.incounter = incounter
        self.outcounter = outcounter
    def __repr__(self):
        return self.interface

class locall1PhysIf():
    def __init__(self, kwargs, interface = None, incounter = None , outcounter = None):
        self.__dict__.update(**kwargs)
        self.name = ''.join(self.dn.split('[')[1][:-1])
        self.leaf = self.dn.split('/')[2]
        self.pod = self.dn.split('/')[1]
        self.interface = interface
        self.incounter = incounter
        self.outcounter = outcounter
    def __repr__(self):
        return self.interface

def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    while True:
        clear_screen()
        location_banner('Top Interface Counters')
        print('\nWhould you like to see counters for: \n\n  1.) Entire ACI Fabric\n  2.) Per Leaf\n\n')
        while True:
            ask = custom_raw_input('Please Select Number: ')
            if not ask.isdigit():
                continue
            elif ask == '1':
                while True:
                    clear_screen()
                    location_banner('Top Interface Counters')
                    displaycounters_all()
                    ask = custom_raw_input("\nRefresh [y]: ") or 'y'
                    if ask != '' and ask[0].lower() == 'y':
                        continue
                    else:
                        break
                break
            elif ask == '2':
                all_leaflist = get_All_leafs(apic,cookie)
                if all_leaflist == []:
                    print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
                    custom_raw_input('\n#Press enter to continue...')
                    return
                print('\nSelect leaf(s): ')
                print('\r')
                chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
                while True:
                    clear_screen()
                    location_banner('Top Interface Counters')
                    displaycounters_perleaf(chosenleafs[0])
                    ask = custom_raw_input("\nRefresh [y]: ") or 'y'
                    if ask != '' and ask[0].lower() == 'y':
                        continue
                    else:
                        break
                break
            else:
                continue


def displaycounters_all():
        interfaceorder = {}
        counter = 0
        print('\x1b[2;40H*** Warning, (bps) rate is based on 5 min interval that resets every 300 sec to 0 \n' +
              '\x1b[3;40H    if all output rates display 0 then wait between 1-10 sec to refresh ***\n')
        print('\x1b[7;2H' + ('*' * 20))
        print(" Top 50 Input Errors")
        print('*' * 21)

        print('\x1b[7;39H{}'.format('*' * 20))
        print("\x1b[8;39HTop 50 Output Errors")
        print('\x1b[9;39H{}'.format('*' * 20))

        print(' \x1b[7;75H{}'.format('*' * 40))
        print(" \x1b[8;75HTop 50 Input (bps) Rate [Access Ports]")
        print(' \x1b[9;75H{}'.format('*' * 40))

        print('\x1b[7;121H{}'.format('*' * 40))
        print("\x1b[8;121HTop 50 Output (bps) Rate [Access Ports]")
        print('\x1b[9;121H{}'.format('*' * 40))

        print(' loading...')
        url = """https://{apic}/api/class/l1PhysIf.json?rsp-subtree-class=l1PhysIf,eqptIngrTotal5min,eqptEgrTotal5min,rmonIfIn,rmonIfOut&rsp-subtree=full&rsp-subtree-include=stats""".format(apic=apic)
        result = GetResponseData(url, cookie)
        logger.info(url)
        errorlist = []
        for x in result:
            if x['l1PhysIf'].get('children') and len(x['l1PhysIf']['children']) > 2:
                errorlist.append(locall1PhysIf(x['l1PhysIf']['attributes'], interface=x['l1PhysIf']['attributes']['dn'],
                        incounter=x['l1PhysIf']['children'][3]['rmonIfIn']['attributes']['errors'],
                        outcounter=x['l1PhysIf']['children'][2]['rmonIfOut']['attributes']['errors']))
            else:
                errorlist.append(locall1PhysIf(x['l1PhysIf']['attributes'], interface=x['l1PhysIf']['attributes']['dn'],
                        incounter=x['l1PhysIf']['children'][1]['rmonIfIn']['attributes']['errors'],
                        outcounter=x['l1PhysIf']['children'][0]['rmonIfOut']['attributes']['errors']))
        upto50counter = 1
        for num,errorline in enumerate(sorted(errorlist, key=lambda x: float(x.incounter), reverse=True)):
            if interfaceorder.get(num):
                a = " {} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod, errorline.leaf, errorline.name, int(errorline.incounter))
                interfaceorder[num].append(a)
            else:
                a = list()
                a.append(" {} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod, errorline.leaf, errorline.name, int(errorline.incounter)))
                interfaceorder[num] = a
            if upto50counter == 50:
                break
            else:
                upto50counter += 1
                counter += 1
        upto50counter = 1
        counter = 0
        for num,errorline in enumerate(sorted(errorlist, key=lambda x: float(x.outcounter), reverse=True)):
            if interfaceorder.get(num):
                a = " {} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod, errorline.leaf, errorline.name, int(errorline.outcounter))
                interfaceorder[num].append(a)
            else:
                a = list()
                a.append(" {} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod, errorline.leaf, errorline.name, int(errorline.outcounter)))
                interfaceorder[num] = a
            if upto50counter == 50:
                break
            else:
                upto50counter += 1
                counter += 1

        ratelist = []
        for x in result:
            if 'epg' in x['l1PhysIf']['attributes']['usage'] or 'fex-fabric' in x['l1PhysIf']['attributes']['mode']:
                if x['l1PhysIf'].get('children') and len(x['l1PhysIf']['children']) > 2:
                    ratelist.append(locall1PhysIf(x['l1PhysIf']['attributes'], interface=x['l1PhysIf']['attributes']['dn'],
                            incounter=x['l1PhysIf']['children'][0]['eqptIngrTotal5min']['attributes']['bytesRate'],
                            outcounter=x['l1PhysIf']['children'][1]['eqptEgrTotal5min']['attributes']['bytesRate']))
        upto50counter = 1
        counter = 0
        for num,errorline in enumerate(sorted(ratelist, key=lambda x: float(x.incounter), reverse=True)):
            if interfaceorder.get(num):
                a = "{} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod,errorline.leaf,errorline.name, int(round(float(errorline.incounter))) * 8)
                interfaceorder[num].append(a)
            else:
                a = list()
                a.append("{} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(x.pod,x.leaf,x.name, int(round(float(x.incounter))) * 8))
                interfaceorder[num] = a
            if upto50counter == 50:
                break
            else:
                upto50counter += 1
                counter += 1
        counter = 0
        upto50counter = 1
        for num,errorline in enumerate(sorted(ratelist, key=lambda x: float(x.outcounter), reverse=True)):
            if interfaceorder.get(num):
                a = "{} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod,errorline.leaf,errorline.name, int(round(float(errorline.outcounter))) * 8)
                interfaceorder[num].append(a)
            else:
                a = list()
                a.append("{} {} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.pod,errorline.leaf,errorline.name, int(round(float(errorline.outcounter))) * 8))
                interfaceorder[num] = a
            if upto50counter == 50:
                break
            else:
                upto50counter += 1
                counter += 1
        for num,x in enumerate(sorted(interfaceorder, key=lambda x: int(x))):
            if num == 0:
                print("\x1b[10;0H{:50} {:50} {:59} {:60}".format(interfaceorder[x][0],interfaceorder[x][1],interfaceorder[x][2],interfaceorder[x][3]))
            else:
                print("{:50} {:50} {:59} {:60}".format(interfaceorder[x][0],interfaceorder[x][1],interfaceorder[x][2],interfaceorder[x][3]))
        ratelist = []
        interfaceorder = []



def displaycounters_perleaf(leaf):
        interfaceorder = {}
        counter = 0
        print('\x1b[2;40H*** Warning, (bps) rate is based on 5 min interval that resets every 300 sec to 0 \n' +
              '\x1b[3;40H    if all output rate displays 0 then wait between 1-10 sec to refresh ***\n')
        
        print('\x1b[7;2H' + ('*' * 20))
        print(" Top 40 Input Errors")
        print('*' * 21)

        print('\x1b[7;39H{}'.format('*' * 20))
        print("\x1b[8;39HTop 40 Output Errors")
        print('\x1b[9;39H{}'.format('*' * 20))

        print(' \x1b[7;75H{}'.format('*' * 40))
        print(" \x1b[8;75HTop 40 Input (bps) Rate [Access Ports]")
        print(' \x1b[9;75H{}'.format('*' * 40))

        print('\x1b[7;121H{}'.format('*' * 40))
        print("\x1b[8;121HTop 40 Output (bps) Rate [Access Ports]")
        print('\x1b[9;121H{}'.format('*' * 40))

        print(' loading...')
        url = """https://{apic}/api/node-{leaf}/class/l1PhysIf.json?rsp-subtree-class=l1PhysIf,eqptIngrTotal5min,eqptEgrTotal5min,rmonIfIn,rmonIfOut&rsp-subtree=full&rsp-subtree-include=stats""".format(apic=apic,leaf=leaf)
        result = GetResponseData(url, cookie)
        logger.info(url)
        errorlist = []
        for x in result:
            if x['l1PhysIf'].get('children') and len(x['l1PhysIf']['children']) > 2:
                errorlist.append(perleaf_locall1PhysIf(leaf,x['l1PhysIf']['attributes'], interface=x['l1PhysIf']['attributes']['dn'],
                        incounter=x['l1PhysIf']['children'][3]['rmonIfIn']['attributes']['errors'],
                        outcounter=x['l1PhysIf']['children'][2]['rmonIfOut']['attributes']['errors']))
            else:
                errorlist.append(perleaf_locall1PhysIf(leaf,x['l1PhysIf']['attributes'], interface=x['l1PhysIf']['attributes']['dn'],
                        incounter=x['l1PhysIf']['children'][1]['rmonIfIn']['attributes']['errors'],
                        outcounter=x['l1PhysIf']['children'][0]['rmonIfOut']['attributes']['errors']))
        upto40counter = 1

        for num,errorline in enumerate(sorted(errorlist, key=lambda x: float(x.incounter), reverse=True)):
            if interfaceorder.get(num):
                a = " node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf, errorline.name, int(errorline.incounter))
                interfaceorder[num].append(a)
            else:
                #import pdb; pdb.set_trace()
                a = list()
                a.append(" node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf, errorline.name, int(errorline.incounter)))
                interfaceorder[num] = a
            if upto40counter == 40:
                break
            else:
                upto40counter += 1
                counter += 1
        upto40counter = 1
        counter = 0
       # #import pdb; pdb.set_trace()
        for num,errorline in enumerate(sorted(errorlist, key=lambda x: float(x.outcounter), reverse=True)):
            if interfaceorder.get(num):
                a = " node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf, errorline.name, int(errorline.outcounter))
                interfaceorder[num].append(a)
            else:
                #import pdb; pdb.set_trace()
                a = list()
                a.append(" node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf, errorline.name, int(errorline.outcounter)))
                interfaceorder[num] = a
            if upto40counter == 40:
                break
            else:
                upto40counter += 1
                counter += 1

       # #import pdb; pdb.set_trace()
        ratelist = []
        for x in result:
            ##import pdb; pdb.set_trace()
            if 'epg' in x['l1PhysIf']['attributes']['usage'] or 'fex-fabric' in x['l1PhysIf']['attributes']['mode']:
                if x['l1PhysIf'].get('children') and len(x['l1PhysIf']['children']) > 2:
                    ratelist.append(perleaf_locall1PhysIf(leaf,x['l1PhysIf']['attributes'], interface=x['l1PhysIf']['attributes']['dn'],
                            incounter=x['l1PhysIf']['children'][0]['eqptIngrTotal5min']['attributes']['bytesRate'],
                            outcounter=x['l1PhysIf']['children'][1]['eqptEgrTotal5min']['attributes']['bytesRate']))
        upto40counter = 1
        counter = 0
        for num,errorline in enumerate(sorted(ratelist, key=lambda x: float(x.incounter), reverse=True)):
            if interfaceorder.get(num):
                a = "node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf,errorline.name, int(round(float(errorline.incounter))) * 8)
                interfaceorder[num].append(a)
            else:
                a = list()
                a.append("node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf,errorline.name, int(round(float(errorline.incounter))) * 8))
                interfaceorder[num] = a
            if upto40counter == 40:
                break
            else:
                upto40counter += 1
                counter += 1
        counter = 0
        upto40counter = 1
        for num,errorline in enumerate(sorted(ratelist, key=lambda x: float(x.outcounter), reverse=True)):
            if interfaceorder.get(num):
                a = "node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf,errorline.name, int(round(float(errorline.outcounter))) * 8)
                interfaceorder[num].append(a)
            else:
                a = list()
                a.append("node-{} {}: \x1b[1;33;40m{:,}\x1b[0m".format(errorline.leaf,errorline.name, int(round(float(errorline.outcounter))) * 8))
                interfaceorder[num] = a
            if upto40counter == 40:
                break
            else:
                upto40counter += 1
                counter += 1
        for num,x in enumerate(sorted(interfaceorder, key=lambda x: int(x))):
            if len(interfaceorder[x]) == 4:
                if num == 0:
                    print("\x1b[10;0H{:50} {:50} {:59} {:60}".format(interfaceorder[x][0],interfaceorder[x][1],interfaceorder[x][2],interfaceorder[x][3]))
                else:
                    print("{:50} {:50} {:59} {:60}".format(interfaceorder[x][0],interfaceorder[x][1],interfaceorder[x][2],interfaceorder[x][3]))
            elif len(interfaceorder[x]) == 2:
                if num == 0:
                    print("\x1b[10;0H{:50} {:50} {:45} {:60}".format(interfaceorder[x][0],interfaceorder[x][1],'No Stats Found','No Status Found'))
                else:
                    print("{:50} {:50} {:45} {:60}".format(interfaceorder[x][0],interfaceorder[x][1],'No Stats Found','No Status Found'))

        ratelist = []
        interfaceorder = []
