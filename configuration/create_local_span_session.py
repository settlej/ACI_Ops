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
import trace
import pdb
import getpass
import datetime
from localutils.custom_utils import *
import logging

# Create a custom logger
# Allows logging to state detailed info such as module where code is running and 
# specifiy logging levels for file vs console.  Set default level to DEBUG to allow more
# grainular logging levels
logger = logging.getLogger(__name__)

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


def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)

def grouper(iterable, n, fillvalue=''):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
    return itertools.izip_longest(*args, fillvalue=fillvalue)

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
   #     print(sorted(singlelist))
        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
            return 'invalid'
        return list(set(singlelist)) 
    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'

class fabricPathEp(object):
    def __init__(self, descr=None, dn=None,name=None, number=None):
        self.name = name
        self.descr = descr
        self.dn = dn
        self.number = number
        self.leaf =  dn.split('/')[2].replace('paths','leaf')
        self.shortname = name.replace('eth1/','')
        self.removedint = '/'.join(dn.split('/')[:-2])
        if 'extpaths' in self.dn:
            self.fex = self.dn.split('/')[3].replace('extpaths','fex')
        else:
            self.fex = ''
    def __repr__(self):
        return self.dn
    def __getitem__(self, number):
        if number in self.dn:
            return self.dn
        else:
            return None


def physical_selection(all_leaflist,direction, leaf=None):
    if leaf == None:
        nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
        nodelist.sort()
        for num,node in enumerate(nodelist,1):
            print("{}.) {}".format(num,node))
        while True:
            asknode = custom_raw_input('\nWhat leaf: ')
            print('\r')
            if asknode.strip().lstrip() == '' or '-' in asknode or ',' in asknode or not asknode.isdigit():
                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
                continue
            returnedlist = parseandreturnsingelist(asknode, nodelist)
            if returnedlist == 'invalid':
                continue
            chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
            break
    else:
        chosenleafs = [leaf]
    compoundedleafresult = []
    for leaf in chosenleafs:
        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
        result = GetResponseData(url,cookie)
        compoundedleafresult.append(result)
    result = compoundedleafresult
    interfacelist = []
    interfacelist2 = []
    for x in result:
        for pathep in x:
            dn = pathep['fabricPathEp']['attributes']['dn']
            name = pathep['fabricPathEp']['attributes']['name']
            descr = pathep['fabricPathEp']['attributes']['descr']
            if 'extpaths' in dn:
                interfacelist2.append(fabricPathEp(descr=descr, dn=dn ,name=name))
            else:
                interfacelist.append(fabricPathEp(descr=descr, dn=dn ,name=name))
            
    interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortname)))
    interfacelist = sorted(interfacelist, key=lambda x: int(x.shortname))
    interfacenewlist = interfacelist2 + interfacelist
    interfacelist = []
    interfacelist2 = []
    finalsortedinterfacelist = sorted(interfacenewlist, key=lambda x: x.removedint)
    interfacedict = {}
    for num,interf in enumerate(finalsortedinterfacelist,1):
        if interf != '':
           interfacedict[interf] = str(num) + '.) '
           interf.number = num
    listlen = len(finalsortedinterfacelist) / 3
    #firstgrouped = [x for x in grouper(finalsortedinterfacelist,40)]
    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
    finalgrouped = zip(*firstgrouped)
    #pdb.set_trace()
    for column in finalgrouped:
        a = column[0].number
        b = goodspacing(column[0]) + '  ' + column[0].descr
        c = column[1].number
        d = goodspacing(column[1]) + '  ' + column[1].descr
        if column[2] == '' or column[2] == None:
            e = ''
            f = ''
        else:
            #e = interfacedict[column[2]]
            e = column[2].number
            f = goodspacing(column[2]) + '  ' + column[2].descr
            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
        print('{:6}.) {:42}{}.) {:42}{}.) {}'.format(a,b,c,d,e,f))
    while True:
        #try:
            selectedinterfaces = custom_raw_input("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: ".format(direction))
            print('\r')
            if selectedinterfaces.strip().lstrip() == '' or '-' in selectedinterfaces or ',' in selectedinterfaces: # or not selectedinterfaces.isdigit():
                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            if intsinglelist == 'invalid':
                continue
            return filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist), leaf
            #pdb.set_trace()

           # for number in intsinglelist:
           #     if not (0 < int(number) <= len(finalsortedinterfacelist)):
           #         print('here')
           #         print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
           #         continue
           #break
        #except KeyboardInterrupt as k:
        #    print('\n\nEnding Script....\n')
        #    return

      #  except Exception as e:

def create_span_dest_url(source_int, name, leaf):
    destport = source_int.dn
    spandestgrpname = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
    spandestname = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
    desturl = """https://{apic}/api/node/mo/uni/infra/destgrp-{}.json""".format(spandestname,apic=apic)
    destdata = """{"spanDestGrp":{"attributes":{"name":"%s","status":"created"},"children":[{"spanDest":{"attributes":{"name":"%s","status":"created"},"children":[{"spanRsDestPathEp":{"attributes":{"tDn":"%s","status":"created"},"children":[]}}]}}]}}""" % (spandestgrpname, spandestname, destport)
    result = PostandGetResponseData(desturl, destdata, cookie)
    if result[0] == []:
        print("Successfully added Destination Port")

def create_source_session_and_port(source_int, dest_int, name, leaf):
    spansourcename = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
    spandestname = name + '_leaf'  + leaf + '_'+ dest_int.name.replace('/','_')
    spansessionname = name  + '_leaf' + leaf + '_' + 'SPAN_SESSION' #+ datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
    sourceport = source_int.dn
    sourceurl = """https://{apic}/api/node/mo/uni/infra/srcgrp-{}.json""".format(spansessionname,apic=apic)
    sourcedata = """{"spanSrcGrp":{"attributes":{"name":"%s","status":"created"},"children":[{"spanSpanLbl":{"attributes":{"name":"%s","status:"created"},"children":[]}},{"spanSrc":{"attributes":{"name":"%s","status":"created"},"children":[{"spanRsSrcToPathEp":{"attributes":{"tDn":"%s","status":"created"},"children":[]}}]}}]}}""" % (spansessionname, spandestname, spansourcename, sourceport)
    result = PostandGetResponseData(sourceurl, sourcedata, cookie)
    #print(result)
    if result[0] == []:
        print("Successfully added Source Session and Source Port")
    else:
        print(result)


def main(import_apic,import_cookie):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    #print(vars())
    #print(dir())
    #import pdb; pdb.set_trace()
    while True:
        clear_screen()
        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
        #userpath = os.path.expanduser("~")
        #userpathmarker = userpath.rfind('/')
        #user = os.path.expanduser("~")[userpathmarker+1:]
        time = get_APIC_clock(apic,cookie)
        #name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S') + '_' + getpass.getuser()
        name = time.replace(' ','T') + '_' + getpass.getuser()
        direction = 'Destination'
        chosendestinterfaceobject, leaf = physical_selection(all_leaflist,direction)
        create_span_dest_url(chosendestinterfaceobject[0], name, leaf)
        direction= 'Source'
        chosensourceinterfacobject, leaf = physical_selection(all_leaflist,direction, leaf=leaf)
        create_source_session_and_port(chosensourceinterfacobject[0],chosendestinterfaceobject[0], name, leaf)
        cookie = refreshToken(apic, cookie)
        custom_raw_input('\n#Press enter to continue...')
        break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print('\n\nEnding Script....\n')
        exit()


#name = custom_raw_input("What is the source interface? ")
#
#name = custom_raw_input(")
#
#{"spanDestGrp":{"attributes":{"dn":"uni/infra/destgrp-SPAN_Destination_eth1_30","name":"SPAN_Destination_eth1_30",
#"rn":"{rn}","status":"created"},"children":[{"spanDest":
#{"attributes":{"dn":"uni/infra/destgrp-SPAN_Destination_eth1_30/dest-SPAN_Destination_eth1_30",
#"name":"SPAN_Destination_eth1_30","rn":"dest-SPAN_Destination_eth1_30","status":"created"},
#"children":[{"spanRsDestPathEp":{"attributes":{"tDn":"topology/pod-1/paths-101/pathep-[eth1/30]",
#"status":"created"},"children":[]}}]}}]}}.format(dn=dn, name=name, rn=rn, spanDestdn=spanDestdn, spanDestrn=spanDestrn,
#destport=destport)
