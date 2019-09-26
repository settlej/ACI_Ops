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
import datetime
from localutils.custom_utils import *
import logging

logger = create_logger()
logger.setLevel(logging.DEBUG)

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
    while True:
        current_time = get_APIC_clock(apic,cookie)
        all_leaflist = get_All_leafs(apic,cookie)
        if all_leaflist == []:
            print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
            custom_raw_input('\n#Press enter to continue...')
            return
        print("\nWhat is the desired \x1b[1;33;40m'Source'\x1b[0m leaf for span session?\r")
#        desiredleaf = custom_custom_raw_input("\nWhat is the desired \x1b[1;33;40m'Source and Destination'\x1b[0m leaf for span session?\r")
       
        #print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
        userpath = os.path.expanduser("~")
        userpathmarker = userpath.rfind('/')
        user = os.path.expanduser("~")[userpathmarker+1:]
        name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S') + '_' + user
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



def create_filter(apic, cookie, current_time, protocol='unspecified'):
    srcaddr = raw_input('Source ip: ')
    dstaddr = raw_input('Destination ip: ')
    name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
    filtername = name + '_filter_' + srcaddr + '_' + dstaddr
    #desrc = raw_input('Description: ')
    filtername = raw_input('filtername: ')
    filterpath = """uni/infra/filtergrp-%(filter)s.json""" % {"apic":apic, "filtername":filtername}
    url = """https://{apic}/api/node/mo/{}""".format(filterpath)
    data = ("""{"spanFilterGrp":{"attributes":{"descr":"", "name":"%(filtername)s"},""" % {"filtername":filtername}
            """"children":["""
            """{"spanFilterEntry":{"attributes":{"descr":"","dstAddr":"%(addr)s","dstPortFrom":"unspecified","dstPortTo":"unspecified",""" % {"addr":dstaddr}
            """"ipProto":"%(protocol)s","srcAddr":"%(addr)s","srcPortFrom":"unspecified","srcPortTo":"unspecified"}}},""" % {"addr":srcaddr, "protocol":protocol}
            """{"spanFilterEntry":{"attributes":{"descr":"","dstAddr":"%(addr)s","dstPortFrom":"unspecified","dstPortTo":"unspecified",""" % {"addr":srcaddr}
            """""ipProto":"%(protocol)s","srcAddr":"%(addr)s","srcPortFrom":"unspecified","srcPortTo":"unspecified"}}}]}}""" % {"addr":dstaddr, "protocol":protocol})
    return filterpath


def create_span_server(apic, cookie, current_time, protocol='unspecified'):
    serverip = raw_input('Capture server IP: ')
    name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
    spandestname = name + '_server_' + serverip
    url = """https://{apic}/api/node/mo/uni/infra/destgrp-{spandestname}.json""".format(apic=apic,spandestname=spandestname)
    data = ("""{"spanDestGrp":{"attributes":{"descr":"","name":"%(spandestname)s"},"children":""" % {"spandestname":spandestname}
            """[{"spanDest":{"attributes":{"descr":"","name":"%(spandestname)s"},""" % {"spandestname":spandestname}
            """"children":[{"spanRsDestEpg":{"attributes":{"dscp":"unspecified","finalIp":"0.0.0.0","flowId":"1","ip":"%(serverip)s","mtu":"1518",""" % {"serverip":serverip}
            """"srcIpPrefix":"199.199.199.199","tDn":"%(serverepg_path)","ttl":"64","ver":"ver2","verEnforced":"no"}}}]}}]}}""" % {serverepg_path})
    return spandestname

def create_span_source(apic, cookie, current_time, spandestname, filter):
    sessionname = "SPAN_SESSION_2_SERVER"
    url = """https://{apic}/api/node/mo/uni/infra/srcgrp-{sessionname}.json""".format(sessionname)
    data = ("""{"spanSrcGrp":{"attributes":{name":"%(sesssionname)s","status":"created"},"children":""" % {"sessionname":sessionname}
            """[{"spanSpanLbl":{"attributes":{"name":"%(spandestname)s","status":"created"},""" % {"spandestname":spandestname}
            """"children":[]}},{"spanSrc":{"attributes":{"name":"%(spansourcename)s","status":"created"},"children":""" % {"spansourcename":spansourcename}
            """[{"spanRsSrcToFilterGrp":{"attributes":{"tDn":"%(filterpath)s","status":"created"}}},{"spanRsSrcToPathEp":{"attributes":{"tDn":"%(destportpath)s","status":"created"}}}]}}]}}""") % {"filterpath":filterpath,"destport":destportpath}


url: https://192.168.255.2/api/node/mo/uni/infra/srcgrp-NEW_SESSION.json
payload{"spanSrcGrp":{"attributes":{"dn":"uni/infra/srcgrp-NEW_SESSION","name":"NEW_SESSION",
"rn":"srcgrp-NEW_SESSION","status":"created"},"children":[{"spanSpanLbl":{"attributes":{"dn":"un
i/infra/srcgrp-NEW_SESSION/spanlbl-DEST-GROUP_NAME","name":"DEST-GROUP_NAME","rn":"spanlbl-DEST-GROUP_N
AME","status":"created"},"children":[]}},{"spanSrc":{"attributes":{"dn":"uni/infra/srcgrp-NEW_SESSION/src-S
PAN_SROUCE","name":"SPAN_SROUCE","rn":"src-SPAN_SROUCE","status":"created"},"children":[{"spanRsSrcToFilterGrp":
"attributes":{"tDn":"uni/infra/filtergrp-test-filter","status":"created"},"children":[]}},{"spanRsSrcToPathEp":{"attr
ibutes":{"tDn":"topology/pod-1/paths-101/pathep-[eth1/26]","status":"created"},"children":[]}}]}}]}}
