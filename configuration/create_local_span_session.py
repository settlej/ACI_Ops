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

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def POSTRequest(url, data, icookie):
    # Function to Perform HTTP POST call to update and create objects and return server data in an http object
    # POST in urllib2 is special because it doesn't exist as a built-in method for the urllib2 object you need to make a function (aka lambda) and refrence this method
    method = "POST"
    # icookie comes from the PostandGetResponseData fuction that references 'cookie' which is a global variable from reading /.aci/.sessions/.token
    cookies = 'APIC-cookie=' + icookie
    # notice 'data' is going to added to the urllib2 object, unlike GET requests
    request = urllib2.Request(url, data)
    # Function needs APIC cookie for authentication and what content format you need in returned http object (example JSON)
    # need to add header one at a time in urllib2
    request.add_header("cookie", cookies)
    request.add_header("Content-type", "application/json")
    request.add_header('Accept', 'application/json')
    request.get_method = lambda: method
    #opener = urllib2.build_opener()
    #opener.addheaders =[("Content-type", "application/json"),("cookie", cookies),('Accept', 'application/json')]
    #return opener.open(url,context=ssl._create_unverified_context())
    try:
        return urllib2.urlopen(request, context=ssl._create_unverified_context()), None
    except urllib2.HTTPError as httpe:
        #print('url')
        failure_reason = json.loads(httpe.read())
        failure_info = failure_reason['imdata'][0]['error']['attributes']['text'].strip()
        return 'invalid', failure_info
    except urllib2.URLError as urle:
        #print(urle.code)
        #print(urle.read())
        failure_reason = json.loads(urle.read())
        #print(url)
        #print('EPG ' + url[45:-4])
        #print((failure_reason['imdata'][0]['error']['attributes']['text']).strip())
        return 'invalid', failure_reason


def PostandGetResponseData(url, data):
    # Fuction to submit JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
    # Perform a POSTRequest function to perform a POST REST call to server and provide response data
    response, error = POSTRequest(url, data, cookie)
    #print(error)
    if response is 'invalid':
        return 'invalid', error
    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
    result = json.loads(response.read())
    # return only infomation inside the dictionary under 'imdata'
    return result['imdata'], None


def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()

def get_All_leafs():
    url = """https://{apic}/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    #print(result)
    return result

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


def physical_selection(all_leaflist,direction):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    nodelist.sort()
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
        try:
            asknode = raw_input('\nWhat leaf: ')
            print('\r')
            if asknode.strip().lstrip() == '' or '-' in asknode or ',' in asknode or not asknode.isdigit():
                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
                continue
            returnedlist = parseandreturnsingelist(asknode, nodelist)
            if returnedlist == 'invalid':
                continue
            chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
            break
        except KeyboardInterrupt as k:
            print('\n\nEnding Script....\n')
            return
    compoundedleafresult = []
    for leaf in chosenleafs:
        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
        result, totalcount = GetResponseData(url)
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
            selectedinterfaces = raw_input("\nSelect \x1b[1;33;40m{}\x1b[0m interface by number: ".format(direction))
            print('\r')
            if selectedinterfaces.strip().lstrip() == '' or '-' in selectedinterfaces or ',' in selectedinterfaces or not asknode.isdigit():
                print("\n\x1b[1;37;41mInvalid format or number...Try again\x1b[0m\n")
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            #print(intsinglelist)
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
    result = PostandGetResponseData(desturl, destdata)
    if result[0] == []:
        print("Successfully added Destination Port")

def create_source_session_and_port(source_int, dest_int, name, leaf):
    spansourcename = name + '_leaf' + leaf + '_' + source_int.name.replace('/','_')
    spandestname = name + '_leaf'  + leaf + '_'+ dest_int.name.replace('/','_')
    spansessionname = name  + '_leaf' + leaf + '_' + 'SPAN_SESSION' #+ datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S')
    sourceport = source_int.dn
    sourceurl = """https://{apic}/api/node/mo/uni/infra/srcgrp-{}.json""".format(spansessionname,apic=apic)
    sourcedata = """{"spanSrcGrp":{"attributes":{"name":"%s","status":"created"},"children":[{"spanSpanLbl":{"attributes":{"name":"%s","status:"created"},"children":[]}},{"spanSrc":{"attributes":{"name":"%s","status":"created"},"children":[{"spanRsSrcToPathEp":{"attributes":{"tDn":"%s","status":"created"},"children":[]}}]}}]}}""" % (spansessionname, spandestname, spansourcename, sourceport)
    result = PostandGetResponseData(sourceurl, sourcedata)
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
    all_leaflist = get_All_leafs()
    print("\nWhat is the desired \x1b[1;33;40m'Destination'\x1b[0m leaf for span session?\r")
    userpath = os.path.expanduser("~")
    userpathmarker = userpath.rfind('/')
    user = os.path.expanduser("~")[userpathmarker+1:]
    name = datetime.datetime.now().strftime('%Y:%m:%dT%H:%M:%S') + '_' + user
    direction = 'Destination'
    chosendestinterfacobject, leaf = physical_selection(all_leaflist,direction)
    create_span_dest_url(chosendestinterfacobject[0], name, leaf)

    print("\nWhat is the desired \x1b[1;33;40m'Source'\x1b[0m leaf for span session?\r")

    direction= 'Source'
    chosensourceinterfacobject, leaf = physical_selection(all_leaflist,direction)
    create_source_session_and_port(chosensourceinterfacobject[0],chosendestinterfacobject[0], name, leaf)
    raw_input('\n#Press enter to continue...')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print('\n\nEnding Script....\n')
        exit()


#name = raw_input("What is the source interface? ")
#
#name = raw_input(")
#
#{"spanDestGrp":{"attributes":{"dn":"uni/infra/destgrp-SPAN_Destination_eth1_30","name":"SPAN_Destination_eth1_30",
#"rn":"{rn}","status":"created"},"children":[{"spanDest":
#{"attributes":{"dn":"uni/infra/destgrp-SPAN_Destination_eth1_30/dest-SPAN_Destination_eth1_30",
#"name":"SPAN_Destination_eth1_30","rn":"dest-SPAN_Destination_eth1_30","status":"created"},
#"children":[{"spanRsDestPathEp":{"attributes":{"tDn":"topology/pod-1/paths-101/pathep-[eth1/30]",
#"status":"created"},"children":[]}}]}}]}}.format(dn=dn, name=name, rn=rn, spanDestdn=spanDestdn, spanDestrn=spanDestrn,
#destport=destport)
