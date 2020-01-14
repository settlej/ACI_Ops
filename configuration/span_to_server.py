#!/bin//python

import re
try:
    import readline
except:
    pass
import urllib2
import getpass
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


#def physical_selection(all_leaflist,direction, leaf=None):
#    if leaf == None:
#        nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
#        nodelist.sort()
#        for num,node in enumerate(nodelist,1):
#            print("{}.) {}".format(num,node))
#        while True:
#            asknode = custom_raw_input('\nWhat leaf: ')
#            print('\r')
#            if asknode.strip().lstrip() == '' or '-' in asknode or ',' in asknode or not asknode.isdigit():
#                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
#                continue
#            returnedlist = parseandreturnsingelist(asknode, nodelist)
#            if returnedlist == 'invalid':
#                continue
#            chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
#            break
#    else:
#        chosenleafs = [leaf]
#    compoundedleafresult = []
#    for leaf in chosenleafs:
#        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
#              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
#              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
# logger.info(url)
#        result = GetResponseData(url,cookie)
# logger.debug(result)       
# compoundedleafresult.append(result)
#    result = compoundedleafresult
#    interfacelist = []
#    interfacelist2 = []
#    for x in result:
#        for pathep in x:
#            dn = pathep['fabricPathEp']['attributes']['dn']
#            name = pathep['fabricPathEp']['attributes']['name']
#            descr = pathep['fabricPathEp']['attributes']['descr']
#            if 'extpaths' in dn:
#                interfacelist2.append(fabricPathEp(descr=descr, dn=dn ,name=name))
#            else:
#                interfacelist.append(fabricPathEp(descr=descr, dn=dn ,name=name))
#            
#    interfacelist2 = sorted(interfacelist2, key=lambda x: (x.fex, int(x.shortname)))
#    interfacelist = sorted(interfacelist, key=lambda x: int(x.shortname))
#    interfacenewlist = interfacelist2 + interfacelist
#    interfacelist = []
#    interfacelist2 = []
#    finalsortedinterfacelist = sorted(interfacenewlist, key=lambda x: x.removedint)
#    interfacedict = {}
#    for num,interf in enumerate(finalsortedinterfacelist,1):
#        if interf != '':
#           interfacedict[interf] = str(num) + '.) '
#           interf.number = num
#    listlen = len(finalsortedinterfacelist) / 3
#    #firstgrouped = [x for x in grouper(finalsortedinterfacelist,40)]
#    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
#    finalgrouped = zip(*firstgrouped)
#    #pdb.set_trace()
#    for column in finalgrouped:
#        a = column[0].number
#        b = goodspacing(column[0]) + '  ' + column[0].descr
#        c = column[1].number
#        d = goodspacing(column[1]) + '  ' + column[1].descr
#        if column[2] == '' or column[2] == None:
#            e = ''
#            f = ''
#        else:
#            #e = interfacedict[column[2]]
#            e = column[2].number
#            f = goodspacing(column[2]) + '  ' + column[2].descr
#            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
#        print('{:6}.) {:42}{}.) {:42}{}.) {}'.format(a,b,c,d,e,f))
#    while True:
#        #try:
#            selectedinterfaces = custom_raw_input("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: ".format(direction))
#            print('\r')
#            if selectedinterfaces.strip().lstrip() == '' or '-' in selectedinterfaces or ',' in selectedinterfaces: # or not selectedinterfaces.isdigit():
#                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
#                continue
#            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
#            if intsinglelist == 'invalid':
#                continue
#            return filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist), leaf
#            #pdb.set_trace()
#
#           # for number in intsinglelist:
#           #     if not (0 < int(number) <= len(finalsortedinterfacelist)):
#           #         print('here')
#           #         print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
#           #         continue
#           #break
#        #except KeyboardInterrupt as k:
#        #    print('\n\nEnding Script....\n')
#        #    return
#
      #  except Exception as e:
def parseandreturnsingelist2(liststring, collectionlist):
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


#def create_span_dest_url(source_int, name, leaf):
#    destport = source_int.dn
#    spandestgrpname = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
#    spandestname = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
#    desturl = """https://{apic}/api/node/mo/uni/infra/destgrp-{}.json""".format(spandestname,apic=apic)
#    destdata = """{"spanDestGrp":{"attributes":{"name":"%s","status":"created"},"children":[{"spanDest":{"attributes":{"name":"%s","status":"created"},"children":[{"spanRsDestPathEp":{"attributes":{"tDn":"%s","status":"created"},"children":[]}}]}}]}}""" % (spandestgrpname, spandestname, destport)
#    logger.info(desturl)
#    logger.info(destdata)
#    result, error = PostandGetResponseData(desturl, destdata, cookie)
#    if error:
#        print('Failure -- ' + error)
#        print('\nPress enter to continue...')
#        
#    logger.info(result)
#    if result[0] == []:
#        print("Successfully added Destination Port")

#def create_source_session_and_port(source_int, dest_int, name, leaf):
#    spansourcename = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
#    spandestname = name + '_leaf'  + leaf + '_'+ dest_int.name.replace('/','_')
#    spansessionname = name  + '_leaf' + leaf + '_' + 'SPAN_SESSION' #+ datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
#    sourceport = source_int.dn
#    sourceurl = """https://{apic}/api/node/mo/uni/infra/srcgrp-{}.json""".format(spansessionname,apic=apic)
#    sourcedata = """{"spanSrcGrp":{"attributes":{"name":"%s","status":"created"},"children":[{"spanSpanLbl":{"attributes":{"name":"%s","status:"created"},"children":[]}},{"spanSrc":{"attributes":{"name":"%s","status":"created"},"children":[{"spanRsSrcToPathEp":{"attributes":{"tDn":"%s","status":"created"},"children":[]}}]}}]}}""" % (spansessionname, spandestname, spansourcename, sourceport)
#    logger.info(sourceurl)
#    logger.info(sourcedata)
#    result = PostandGetResponseData(sourceurl, sourcedata, cookie)
#    logger.info(result)
#    #print(result)
#    if result[0] == []:
#        print("Successfully added Source Session and Source Port")
#    else:
#        print(result)

def display_and_select_epgs(allepglist):
    numepgdict = {}
    allepglist = sorted(allepglist)
    #print(allepglist)
    for num,epg in enumerate(allepglist,1):
        numepgdict[num] = epg
        egpslit = epg.split('/')[1:]
        print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    while True:
        #try:
            askepgnum = custom_raw_input("\nWhich number(s)?: ")
            print('\r')
            if askepgnum.strip().lstrip() == '':
                continue
            epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
            if epgsinglelist == 'invalid':
                continue
            chosenepgs = [allepglist[x-1] for x in epgsinglelist]
            break
    return chosenepgs

class pcObject():
    def __init__(self, name=None, dn=None, number=None):
        self.name = name
        self.dn = dn
        self.number = number
    def __repr__(self):
        return self.dn
    def __get__(self, num):
        if num in self.number:
            return self.name
        else:
            return None


def physical_selection(all_leaflist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    nodelist.sort()
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
        asknode = custom_raw_input('\nWhat leaf(s): ')
        print('\r')
        returnedlist = parseandreturnsingelist(asknode, nodelist)
        if returnedlist == 'invalid':
            continue
        chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
        break
    compoundedleafresult = []
    for leaf in chosenleafs:
        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
        logger.info(url)
        result = GetResponseData(url, cookie)
        logger.debug(result)
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
    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
    finalgrouped = zip(*firstgrouped)
    for column in finalgrouped:
        a = column[0].number
        b = goodspacing(column[0])
        c = column[1].number
        d = goodspacing(column[1])
        if column[2] == '' or column[2] == None:
            e = ''
            f = ''
        else:
            #e = interfacedict[column[2]]
            e = column[2].number
            f = goodspacing(column[2])
            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
        print('{:6}.) {:33}{}.) {:33}{}.) {}'.format(a,b,c,d,e,f))
    while True:
        #try:
            selectedinterfaces = custom_raw_input("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: ".format('monitored'))
            print('\r')
            if selectedinterfaces.strip().lstrip() == '':
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            if intsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist)
            break
    return choseninterfaceobjectlist

def port_channel_selection(allpclist):
    pcobjectlist = []
    for pc in allpclist:
        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
    print("\n{:>4} |  {}".format("#","Port-Channel Name"))
    print("-"* 65)
    for num,pc in enumerate(sorted(pcobjectlist),1):
        print("{:>4}.) {}".format(num,pc.name))
        pc.number = num
    while True:
        try:
            askpcnum = custom_raw_input("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: ".format('monitored'))
            print('\r')
            if askpcnum.strip().lstrip() == '':
                continue
            pcsinglelist = parseandreturnsingelist2(askpcnum,pcobjectlist)
            if pcsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in pcsinglelist, pcobjectlist)
            break
        except ValueError as v:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    return choseninterfaceobjectlist



def create_filter(apic, cookie, current_time, current_user, protocol='unspecified'):
    print('ACL Filter for SPAN:')
    srcaddr = raw_input('    Source ip: ')
    dstaddr = raw_input('    Destination ip: ')
    #name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
    filtername = (current_time + '_' + current_user +  '_filter_' + srcaddr[-7:] + '-' + dstaddr[-7:]).replace('.', '_')
    #desrc = raw_input('Description: ')
    ##def select_protocol():
    ##    #print('Select protcol to capture:\n')
    ##    print('\nSelect protocol to capture:n\n' +
    ##            '    1.) ICMP \n' +
    ##            '    2.) TCP  \n' +
    ##            '    3.) UDP  \n' +
    ##            '    4.) Any  \n\n')
    ##    while True:
    ##        selectednum = custom_raw_input('Option: ')
    ##        if selectednum == '1':
    ##            protocol = 'icmp':
    ##        elif selectednum == '2':
    ##            print('[Example format: (single port) 443 or (range) 1018-1022]')
    ##            while True:
    ##                srcPort = custom_raw_input('Provide source ports [default='any']') or 'unspecified'
    ##                if 'unspecified':
    ##                    break
    ##                elif '-' in srcPort:
    ##                    srcPort = srcPort.split('-')
    ##                    for src in srcPort:
    ##                        if not src.strip().lstrip().isdigit():
    ##                            print('\nInvalid format\n')
    ##                            continue
    ##                    if len(srcPort) > 2:
    ##                        print('\nInvalid range\n')
    ##                        continue
    ##                    break
    ##                elif srcPort.strip().lstrip().isdigit():
    ##                    break
    ##                else:
    ##                    print('\nInvalid format\n')
    ##                    continue
    ##            if type(srcPort) == list:
    ##                srcPortFrom = srcPort[0]
    ##                srcPortTo = srcPort[1]
    ##            else:
    ##                srcPortFrom = srcPort
    ##                srcPortTo = srcPort
     #               
     #                   
     #               
     #               
     #               
     #               srcPort.isdigit() or not 
#                srcPort = custom_raw_input('\nWhat are the source port(s)?\n')

       # exit()
       # custom_raw_input('')
    filterpath = """uni/infra/filtergrp-%(filtername)s.json""" % {"apic":apic, "filtername":filtername}
    url = """https://{apic}/api/node/mo/{filterpath}""".format(apic=apic,filterpath=filterpath)
    data = ("""{"spanFilterGrp":{"attributes":{"descr":"", "name":"%(filtername)s"},""" % {"filtername":filtername}
            + """"children":["""
            + """{"spanFilterEntry":{"attributes":{"descr":"","dstAddr":"%(addr)s","dstPortFrom":"unspecified","dstPortTo":"unspecified",""" % {"addr":dstaddr}
            + """"ipProto":"%(protocol)s","srcAddr":"%(addr)s","srcPortFrom":"unspecified","srcPortTo":"unspecified"}}},""" % {"addr":srcaddr, "protocol":protocol}
            + """{"spanFilterEntry":{"attributes":{"descr":"","dstAddr":"%(addr)s","dstPortFrom":"unspecified","dstPortTo":"unspecified",""" % {"addr":srcaddr}
            + """""ipProto":"%(protocol)s","srcAddr":"%(addr)s","srcPortFrom":"unspecified","srcPortTo":"unspecified"}}}]}}""" % {"addr":dstaddr, "protocol":protocol})
    logger.info(url)
    logger.info(data)
    result = PostandGetResponseData(url, data, cookie)
    logger.debug(result)
    
    if result[0] == []:
        print("Successfully created filter")
    else:
        return result
    return filterpath


def create_span_server(apic, cookie, current_time,current_user, allepglist, protocol='unspecified'):
    serverip = raw_input('Capture server IP: ')
    print('Where does the server reside?: ')
    serverepg_path = display_and_select_epgs(allepglist)
    spandestname = current_time + '_' + current_user + '_captureserver_' + serverip
    url = """https://{apic}/api/node/mo/uni/infra/destgrp-{spandestname}.json""".format(apic=apic,spandestname=spandestname)
    data = ("""{"spanDestGrp":{"attributes":{"descr":"","name":"%(spandestname)s"},"children":""" % {"spandestname":spandestname}
            + """[{"spanDest":{"attributes":{"descr":"","name":"%(spandestname)s"},""" % {"spandestname":spandestname}
            + """"children":[{"spanRsDestEpg":{"attributes":{"dscp":"unspecified","finalIp":"0.0.0.0","flowId":"1","ip":"%(serverip)s","mtu":"1518",""" % {"serverip":serverip}
            + """"srcIpPrefix":"199.199.199.199","tDn":"%(serverepg_path)s","ttl":"64","ver":"ver2","verEnforced":"no"}}}]}}]}}""" % {"serverepg_path":serverepg_path[0]})
    logger.info(url)
    logger.info(data)
    result = PostandGetResponseData(url, data, cookie)
    logger.debug(result)
    if result[0] == []:
        print("Successfully created server as ERSPAN collector")
    else:
        return result, ('failure', 'logs')
    #return filterpath
    return spandestname, serverip

def create_span_source(apic, cookie, current_time, spandestname, sourceinterfacepath, filterpath):
    sessionname = "{}-{}".format(current_time, "SPAN_SESSION_SERVER")
    spansourcename = current_time + '_source_'+ sourceinterfacepath.name.replace('/','_')
    url = """https://{apic}/api/node/mo/uni/infra/srcgrp-{sessionname}.json""".format(apic=apic,sessionname=sessionname)
    if filterpath == None:
        data = ("""{"spanSrcGrp":{"attributes":{name":"%(sessionname)s","status":"created"},"children":""" % {"sessionname":sessionname}
                + """[{"spanSpanLbl":{"attributes":{"name":"%(spandestname)s","status":"created"},""" % {"spandestname":spandestname}
                + """"children":[]}},{"spanSrc":{"attributes":{"name":"%(spansourcename)s","status":"created"},"children":""" % {"spansourcename":spansourcename}
                + """[{"spanRsSrcToPathEp":{"attributes":{"tDn":"%(sourceinterfacepath)s","status":"created"}}}]}}]}}""") % {"sourceinterfacepath":str(sourceinterfacepath)}
    else:
        data = ("""{"spanSrcGrp":{"attributes":{name":"%(sessionname)s","status":"created"},"children":""" % {"sessionname":sessionname}
                + """[{"spanSpanLbl":{"attributes":{"name":"%(spandestname)s","status":"created"},""" % {"spandestname":spandestname}
                + """"children":[]}},{"spanSrc":{"attributes":{"name":"%(spansourcename)s","status":"created"},"children":""" % {"spansourcename":spansourcename}
                + """[{"spanRsSrcToFilterGrp":{"attributes":{"tDn":"%(filterpath)s","status":"created"}}},{"spanRsSrcToPathEp":{"attributes":{"tDn":"%(sourceinterfacepath)s","status":"created"}}}]}}]}}""") % {"filterpath":filterpath,"sourceinterfacepath":str(sourceinterfacepath)}
    logger.info(url)
    logger.info(data)
    result = PostandGetResponseData(url, data, cookie)
    logger.debug(result)
    if result[0] == []:
        print("Successfully added span session")
    else:
        return result
    #return filterpath

#url: https://192.168.255.2/api/node/mo/uni/infra/srcgrp-NEW_SESSION.json
#payload{"spanSrcGrp":{"attributes":{"dn":"uni/infra/srcgrp-NEW_SESSION","name":"NEW_SESSION",
#"rn":"srcgrp-NEW_SESSION","status":"created"},"children":[{"spanSpanLbl":{"attributes":{"dn":"un
#i/infra/srcgrp-NEW_SESSION/spanlbl-DEST-GROUP_NAME","name":"DEST-GROUP_NAME","rn":"spanlbl-DEST-GROUP_N
#AME","status":"created"},"children":[]}},{"spanSrc":{"attributes":{"dn":"uni/infra/srcgrp-NEW_SESSION/src-S
#PAN_SROUCE","name":"SPAN_SROUCE","rn":"src-SPAN_SROUCE","status":"created"},"children":[{"spanRsSrcToFilterGrp":
#"attributes":{"tDn":"uni/infra/filtergrp-test-filter","status":"created"},"children":[]}},{"spanRsSrcToPathEp":{"attr
#ibutes":{"tDn":"topology/pod-1/paths-101/pathep-[eth1/26]","status":"created"},"children":[]}}]}}]}}
def main(import_apic,import_cookie, current_user):
    try:
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        allepglist = get_All_EGPs(apic,cookie)
        allpclist = get_All_PCs(apic,cookie)
        allvpclist = get_All_vPCs(apic,cookie)
        all_leaflist = get_All_leafs(apic,cookie)
    
        selection = interface_menu()
        #direction = "Source"
        
        if selection == '1':
            choseninterfaceobjectlist = physical_selection(all_leaflist)
        elif selection == '2':
            choseninterfaceobjectlist = port_channel_selection(allpclist)
        elif selection == '3':
            choseninterfaceobjectlist = port_channel_selection(allvpclist)
    
        while True:
            current_time = get_APIC_clock(apic,cookie)
            current_time = current_time.replace(' ', 'T')
            all_leaflist = get_All_leafs(apic,cookie)
            if all_leaflist == []:
                print('\x1b[1;31;40mFailed to retrieve active leafs, make leafs are operational...\x1b[0m')
                custom_raw_input('\n#Press enter to continue...')
                return
            #filterpath = create_filter(apic, cookie, current_time, current_user)
            #if isinstance(filterpath, tuple): # verify filter creating didn't return error
            #    print('\n\x1b[1;37;41mFailure\x1b[0m -- ' + filterpath[1])
            #    custom_raw_input('\n#Press enter to continue...')
            #    break
            spandestname, serverip = create_span_server(apic, cookie, current_time, current_user, allepglist)
            if isinstance(spandestname, tuple): # verify filter creating didn't return error
                print('\n\x1b[1;37;41mFailure\x1b[0m -- ' + spandestname[1])
                custom_raw_input('\n#Press enter to continue...')
                break
            try: 
                create_span_source(apic, cookie, current_time, spandestname, sourceinterfacepath=choseninterfaceobjectlist[0], filterpath=None)
                #create_source_session_and_port(chosensourceinterfacobject[0],chosendestinterfaceobject[0], name, leaf)
                if isinstance(spandestname, tuple): # verify filter creating didn't return error
                    print('\n\x1b[1;37;41mFailure\x1b[0m -- ' + spandestname[1])
                    custom_raw_input('\n#Press enter to continue...')
                    cookie = refreshToken(apic, cookie)
                    break
                cookie = refreshToken(apic, cookie)
                custom_raw_input('\n#Press enter to continue...')
                break
            except:
                import pdb; pdb.set_trace()
    except Exception as e:
        logger.critical(str(e))
#