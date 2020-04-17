#!/bin//python
#############################################################################################################################################
#                               What does this program do
#                               What are you trying to accomplish
#                               Who program the damn thing
#                               What version you are on
#                               Date Created
#                               Date Last time modify
#############################################################################################################################################

import re
try:
    import readline
except:
    pass
import urllib.request, urllib.error, urllib.parse
import json
import ssl
import os
import itertools
import threading
import queue
from localutils.custom_utils import *


#############################################################################################################################################
#                               What does this def do period
#                               Who program the damn thing
#                               What version you are on
#                               Date Created
#                               Date Last time modify
#############################################################################################################################################

def GetRequest(url, icookie):
    # Function to Perform HTTP Get REST calls and return server recieved data in an http object
    method = "GET"
    # icookie comes from the GetResponseData fuction that references 'cookie' which is a global variable from reading /.aci/.sessions/.token
    cookies = 'APIC-cookie=' + icookie
    # create urllib2 object to add headers and cookies
    request = urllib.request.Request(url)
    # Function needs APIC cookie for authentication and what content format you need in returned http object (example JSON)
    # need to add header one at a time in urllib2
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib.request.urlopen(request, context=ssl._create_unverified_context())

#############################################################################################################################################
#                               What does this def do period
#                               Who program the damn thing
#                               What version you are on
#                               Date Created
#                               Date Last time modify
#############################################################################################################################################

def POSTRequest(url, data, icookie):
    # Function to Perform HTTP POST call to update and create objects and return server data in an http object
    # POST in urllib2 is special because it doesn't exist as a built-in method for the urllib2 object you need to make a function (aka lambda) and refrence this method
    method = "POST"
    # icookie comes from the PostandGetResponseData fuction that references 'cookie' which is a global variable from reading /.aci/.sessions/.token
    cookies = 'APIC-cookie=' + icookie
    # notice 'data' is going to added to the urllib2 object, unlike GET requests
    request = urllib.request.Request(url, data)
    # Function needs APIC cookie for authentication and what content format you need in returned http object (example JSON)
    # need to add header one at a time in urllib2
    request.add_header("cookie", cookies)
    request.get_method = lambda: method
    return urllib.request.urlopen(request, context=ssl._create_unverified_context())

#############################################################################################################################################
#                               What does this def do period
#                               Who program the damn thing
#                               What version you are on
#                               Date Created
#                               Date Last time modify
#############################################################################################################################################

#def GetResponseData(url):
#    # Fuction to take JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
#    # Perform a GetRequest function to perform a GET REST call to server and provide response data
#    response = GetRequest(url, cookie) # here for this
#    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
#    result = json.loads(response.read()) # here for this
#    # return only infomation inside the dictionary under 'imdata'
#    return result['imdata'] #here for this
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def PostandGetResponseData(url, data):
    # Fuction to submit JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
    # Perform a POSTRequest function to perform a POST REST call to server and provide response data
    response = POSTRequest(url, data, cookie)
    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
    result = json.loads(response.read())
    # return only infomation inside the dictionary under 'imdata'
    return result['imdata']

def get_Cookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()


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

def grouper(iterable, n, fillvalue=''):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
    return itertools.zip_longest(*args, fillvalue=fillvalue)

#def clear_screen():
#    if os.name == 'posix':
#        clear_screen()
#    else:
#        os.system('cls')

def menu():
    while True:
        clear_screen()
        print(("\nSelect interface type for shut/noshut/bounce: \n" + \
          "\n\t1.) Physical Interfaces: \n" + \
          "\t2.) PC Interfaces: \n" + \
          "\t3.) VPC Interfaces: \n"))
        selection = custom_raw_input("Select number: ")
        print('\r')
        if selection.isdigit() and selection != '' and 1 <= int(selection) <= 3:
            break
        else:
            continue
    return selection 

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

def get_All_EGPs_names():
    ##get_Cookie()
    epgdict = {}
    url = """https://{apic}/api/node/class/fvAEPg.json""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    #print(json.dumps(result, indent=2))
    epglist = [epg['fvAEPg']['attributes']['dn'] for epg in result]
            #epgdict[epg['fvAEPg']['attributes']['name']] = epg['fvAEPg']['attributes']['dn']
    #    epglist.append(epg['fvAEPg']['attributes']['dn'])
    return epglist

def get_All_PCs():
    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """eq(fabricPathEp.lagT,"link"))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    return result

def get_All_vPCs():
    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    return result

def get_All_leafs():
    url = """https://{apic}/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))""".format(apic=apic)
    result, totalCount = GetResponseData(url)
    #print(result)
    return result


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
                for i in range(int(tempsplit[0]), int(tempsplit[1])+1):
                    singlelist.append(int(i))
   #     print(sorted(singlelist))
        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
            return 'invalid'
        return list(set(singlelist)) 
    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'


def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)

def physical_selection(all_leaflist, allepglist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    nodelist.sort()
    for num,node in enumerate(nodelist,1):
        print(("{}.) {}".format(num,node)))
    while True:
        #try:
            asknode = custom_raw_input('\nWhat leaf(s): ')
            print('\r')
            returnedlist = parseandreturnsingelist(asknode, nodelist)
            if returnedlist == 'invalid':
                continue
            chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
            break
        #except KeyboardInterrupt as k:
        #    print('\n\nEnding Script....\n')
        #    return
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
    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
    finalgrouped = list(zip(*firstgrouped))
    for column in finalgrouped:
        a = column[0].number
        b = goodspacing(column[0]) + '  ' + column[0].descr[:25]
        c = column[1].number
        d = goodspacing(column[1]) + '  ' + column[1].descr[:25]
        if column[2] == '' or column[2] == None:
            e = ''
            f = ''
        else:
            #e = interfacedict[column[2]]
            e = column[2].number
            f = goodspacing(column[2])
            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
        print(('{:6}.) {:45}{}.) {:45}{}.) {}'.format(a,b,c,d,e,f)))
    while True:
        #try:
            selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
            print('\r')
            if selectedinterfaces.strip().lstrip() == '':
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            if intsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = [x for x in finalsortedinterfacelist if x.number in intsinglelist]
           # for number in intsinglelist:
           #     if not (0 < int(number) <= len(finalsortedinterfacelist)):
           #         print('here')
           #         print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
           #         continue
            break
        #except KeyboardInterrupt as k:
        #    print('\n\nEnding Script....\n')
        #    exit()
    return choseninterfaceobjectlist

      #  except Exception as e:

def shutinterfaces(interfaces):
    queue = queue.Queue()
    interfacelist = []
    interfacelist2 =[]
    for interface in interfaces:
        t = threading.Thread(target=postshut, args=(interface,queue,))
        t.start()
        interfacelist.append(t)
    for t in interfacelist:
        t.join()
        interfacelist2.append(queue.get())
    for x in sorted(interfacelist2):
        print(x)

def postshut(interface,queue):
        url = 'https://{apic}/api/node/mo/uni/fabric/outofsvc.json'.format(apic=apic)
        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a normal interface
        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"{interface}","lc":"blacklist"}},"children":[]}}}}'""".format(interface=interface)
        result =  PostandGetResponseData(url, data)
        if result == []:
            queue.put('[Complete] shut ' + interface.name)

def noshutinterfaces(interfaces):
    queue = queue.Queue()
    interfacelist = []
    interfacelist2 =[]
    for interface in interfaces:
        t = threading.Thread(target=postnoshut, args=(interface,queue,))
        t.start()
        interfacelist.append(t)
    for t in interfacelist:
        t.join()
        interfacelist2.append(queue.get())
    for x in sorted(interfacelist2):
        print(x)

def postnoshut(interface,queue):
        url = 'https://{apic}/api/node/mo/uni/fabric/outofsvc.json'.format(apic=apic)
        # data is the 'POST' data sent in the REST call to delete object from 'blacklist' (no shut)
        data = """'{{"fabricRsOosPath":{{"attributes":{{"dn":"uni/fabric/outofsvc/rsoosPath-[{interface}]","status":"deleted"}},"children":[]}}}}'""".format(interface=interface)
        result =  PostandGetResponseData(url, data)
        if result == []:
            queue.put('[Complete] no shut ' + interface.name)

def port_channel_selection(allpclist,allepglist):
    pcobjectlist = []
    for pc in allpclist:
        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
    print(("\n{:>4} |  {}".format("#","Port-Channel Name")))
    print(("-"* 65))
    for num,pc in enumerate(sorted(pcobjectlist),1):
        print(("{:>4}.) {}".format(num,pc.name)))
        pc.number = num
    while True:
        try:
            askpcnum = custom_raw_input("\nWhich number(s)?: ")
            print('\r')
            if askpcnum.strip().lstrip() == '':
                continue
            pcsinglelist = parseandreturnsingelist(askpcnum,pcobjectlist)
            if pcsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = [x for x in pcobjectlist if x.number in pcsinglelist]
            break
        except ValueError:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    return choseninterfaceobjectlist


def main(import_apic, import_cookie):
    while True:
        #get_Cookie()
        global apic
        global cookie
        cookie = import_cookie
        apic = import_apic
        allepglist = get_All_EGPs_names()
        allpclist = get_All_PCs()
        allvpclist = get_All_vPCs()
        all_leaflist = get_All_leafs()
    
        selection = menu()
    
        if selection == '1':
            interfaces = physical_selection(all_leaflist, allepglist)
            #print(interfaces)
            print('\r')
            while True:
                option = custom_raw_input(("Would you like to do?\n\
                        \n1.) shut\
                        \n2.) no shut\
                        \n3.) bounce \n\
                        \nSelect a number: "))
                if option == '1':
                    print('\n')
                    shutinterfaces(interfaces)
                    break
                elif option == '2':
                    print('\n')
                    noshutinterfaces(interfaces)
                    break
                elif option == '3':
                    print('\n')
                    shutinterfaces(interfaces)
                    noshutinterfaces(interfaces)
                    break
                else:
                    print('\n\x1b[1;31;40mInvalid option, please try again...\x1b[0m\n')
                    continue
            custom_raw_input('\n#Press enter to continue...')
        elif selection == '2':
            interfaces = port_channel_selection(allpclist,allepglist)
            print('\r')
          #      for number in sorted(pcsinglelist):
          #          data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(numepgdict[number],vlan=vlan)
          #          print(data)
            #result, totalcount = PostandGetResponseData(url, data)
            option = custom_raw_input(("Would you like to do?\n\
                        \n1.) shut\
                        \n2.) no shut\
                        \n3.) bounce \n\
                        \nSelect a number: "))
            if option == '1':
                print('\n')
                shutinterfaces(interfaces)
            elif option == '2':
                print('\n')
                noshutinterfaces(interfaces)
            else:
                print('\n')
                shutinterfaces(interfaces)
                noshutinterfaces(interfaces)
            custom_raw_input('\n#Press enter to continue...')

        elif selection == '3':
            interfaces = port_channel_selection(allvpclist,allepglist)
            print('\r')
          #      for number in sorted(pcsinglelist):
          #          data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(numepgdict[number],vlan=vlan)
          #          print(data)
            #result, totalcount = PostandGetResponseData(url, data)
            option = custom_raw_input(("Would you like to do?\n\
                        \n1.) shut\
                        \n2.) no shut\
                        \n3.) bounce \n\
                        \nSelect a number: "))
            if option == '1':
                print('\n')
                shutinterfaces(interfaces)
            elif option == '2':
                print('\n')
                noshutinterfaces(interfaces)
            else:
                print('\n')
                shutinterfaces(interfaces)
                noshutinterfaces(interfaces)
            custom_raw_input('\n#Press enter to continue...')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as k:
                print('\n\nEnding Script....\n')
                exit()