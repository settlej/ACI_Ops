#!/bin//python

import re
import readline
import urllib.request, urllib.error, urllib.parse
import json
import ssl
import os
import datetime
import itertools

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib.request.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-trig", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib.request.urlopen(request, context=ssl._create_unverified_context())
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
    request = urllib.request.Request(url, data)
    # Function needs APIC cookie for authentication and what content format you need in returned http object (example JSON)
    # need to add header one at a time in urllib2
    request.add_header("cookie", cookies)
    request.get_method = lambda: method
    return urllib.request.urlopen(request, context=ssl._create_unverified_context())
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
    def __init__(self, descr=None, dn=None,name=None):
        self.name = name
        self.descr = descr
        self.dn = dn
        self.leaf =  dn.split('/')[2].replace('paths','leaf')
        self.shortname = name.replace('eth1/','')
        self.removedint = '/'.join(dn.split('/')[:-2])
        if 'extpaths' in self.dn:
            self.fex = self.dn.split('/')[3].replace('extpaths','fex')
        else:
            self.fex = ''
    def __repr__(self):
        return self.dn
    def __getitem__(self, name):
        if name in self.name:
            return self.name
        else:
            return None

def grouper(iterable, n, fillvalue=''):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
    return itertools.zip_longest(*args, fillvalue=fillvalue)



def menu():
    while True:
        #os.system('clear')
        print(("\nSelect interface for adding EPGs: \n" + \
          "\t1.) Physical Interfaces: \n" + \
          "\t2.) PC Interfaces: \n" + \
          "\t3.) VPC Interfaces: \n"))
        selection = eval(input("Select number: "))
        if selection.isdigit() and selection != '':
            break
        else:
            continue
    return selection 

def get_All_EGPs_names():
    get_Cookie()
    epgdict = {}
    epglist = []
    url = """https://localhost/api/node/class/fvAEPg.json"""
    result, totalCount = GetResponseData(url)
    #print(json.dumps(result, indent=2))
    for epg in result:
        #epgdict[epg['fvAEPg']['attributes']['name']] = epg['fvAEPg']['attributes']['dn']
        epglist.append(epg['fvAEPg']['attributes']['dn'])
    return epglist

def get_All_PCs():
    url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),eq(fabricPathEp.lagT,"link"))"""
    result, totalCount = GetResponseData(url)
    return result

def get_All_vPCs():
    url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))"""
    result, totalCount = GetResponseData(url)
    return result

def get_All_Physinterfaces():
    url = """https://localhost/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))"""
    result, totalCount = GetResponseData(url)
    #print(result)
    return result


def parseandreturnsingelist(liststring, currentdict):
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
            for z in range(int(tempsplit[0]), int(tempsplit[1])+1):
                singlelist.append(int(z))
    print(singlelist)
    if sorted(singlelist)[-1] > len(currentdict):
        print('\nInvalid format and/or range...Try again\n')
        return 'invalid'
    return list(set(singlelist)) 

def parseandreturnsingelist2(liststring, currentlist):
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
            for z in range(int(tempsplit[0]), int(tempsplit[1])+1):
                singlelist.append(int(z))
    if sorted(singlelist)[-1] > len(currentlist):
        print('\nInvalid format and/or range...Try again\n')
        return 'invalid'
    return list(set(singlelist)) 

def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)


def main():
    get_Cookie()
    allepglist = get_All_EGPs_names()
    allpclist = get_All_PCs()
    allvpclist = get_All_vPCs()
    allphyslist = get_All_Physinterfaces()

    selection = menu()

    if selection == '1':
        nodelist = [node['fabricNode']['attributes']['id'] for node in allphyslist]
        
        nodelist.sort()
        for num,node in enumerate(sorted(nodelist),1):
            print(("{}.) {}".format(num,node)))
        while True:
            try:
                asknode = eval(input('What leaf(s): '))
                returnedlist = parseandreturnsingelist2(asknode, nodelist)
                if returnedlist == 'invalid':
                    continue
                chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
                break
            except:
                print("\nInvalid format and/or range...Try again\n")
        if len(chosenleafs) == 1:
            leaf = chosenleafs[0]
            url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf)
            result, totalcount = GetResponseData(url)
            interfacelist = []
            interfacelist2 = []
            for pathep in result:
                dn = pathep['fabricPathEp']['attributes']['dn']
                name = pathep['fabricPathEp']['attributes']['name']
                descr = pathep['fabricPathEp']['attributes']['descr']
                if 'extpaths' in dn:
                    interfacelist2.append(fabricPathEp(descr=descr, dn=dn ,name=name))
                else:
                    interfacelist.append(fabricPathEp(descr=descr, dn=dn ,name=name))

        else:
            compoundedresult = []
            for leaf in chosenleafs:
                url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf)
                result, totalcount = GetResponseData(url)
                compoundedresult.append(result)
            result = compoundedresult
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
        for num,v in enumerate(finalsortedinterfacelist,1):
            if v != '':
               interfacedict[v] = str(num) + '.) '

        listlen = len(finalsortedinterfacelist) / 3
        #firstgrouped = [x for x in grouper(finalsortedinterfacelist,40)]
        firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]

        finalgrouped = list(zip(*firstgrouped))
        for column in finalgrouped:
            a = interfacedict[column[0]]
            b = goodspacing(column[0])
            c = interfacedict[column[1]]
            d = goodspacing(column[1])
            if column[2] == '' or column[2] == None:
                e = ''
                f = ''
            else:
                e = interfacedict[column[2]]
                f = goodspacing(column[2])
                #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
            print(('{:6}{:33}{}{:33}{}{}'.format(a,b,c,d,e,f)))
        while True:
            try:
                selectedinterfaces = eval(input("Select interface(s) by number: "))
                if selectedinterfaces.strip().lstrip() == '':
                    continue
                intsinglelist = parseandreturnsingelist(selectedinterfaces,interfacedict)
                if intsinglelist == 'invalid':
                    continue
                for x in intsinglelist:
                    print((str(x)))
                    print('debug') 
                    print((str(interfacedict[x])))
                    #str(x) == str(interfacedict[x]) 
                    print('yessssss')
                break
            except:
                print('fail')
                break
        #print(intsinglelist)
        numepgdict = {}
        print(("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG")))
        print(("-"* 65))
        for num,epg in enumerate(sorted(allepglist),1):
            numepgdict[num] = epg
            egpslit = epg.split('/')[1:]
            print(("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:])))
        while True:
            try:
                askepgnum = eval(input("which number?: "))
                if askepgnum.strip().lstrip() == '':
                    continue
                epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
                if epgsinglelist == 'invalid':
                    continue
                #for x in epgsinglelist:
                #    print(numepgdict[x])
                break
            except:
                print("\nInvalid format and/or range...Try again\n")

        data = ""
        print((sorted(epgsinglelist)))
        for epg in sorted(epgsinglelist):
            url = """https://localhost/api/node/mo/{}.json""".format(numepgdict[epg])
            print(("\nProvide a vlan number for epg: {}".format(numepgdict[epg])))
            while True:
                try:
                    vlan = eval(input('pick a vlan number: '))
                    if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
                       break
                    else:
                        print('Invalid vlan number')
                except:
                    continue
            #print(interfacedict)
            for interface in sorted(intsinglelist):
                for name,inter in list(interfacedict.items()):
                    #print(interface,inter[:-3])
                    if str(interface) == str(inter[:-3]):
                        print(("""{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(name,vlan=vlan)))




















    if selection == '2':
        pcdict = {}  
        #epgdict = {}   
                
        for pc in allpclist:
            pcdict[pc['fabricPathEp']['attributes']['name']] = pc['fabricPathEp']['attributes']['dn']
        print(("\n{:>4} |  {}".format("#","Port-Channel Name")))
        print(("-"* 65))
        numpcdict = {}
        for num,pc in enumerate(sorted(pcdict),1):
            print(("{:>4}.) {}".format(num,pc)))
            numpcdict[num] = pc
        while True:
            try:
                askpcnum = eval(input("\nWhich number(s)?: "))
                if askpcnum.strip().lstrip() == '':
                    continue
                #askpcnum = '1,2,3,6,9,12,14'
                pcsinglelist = parseandreturnsingelist(askpcnum,numpcdict)
                if pcsinglelist == 'invalid':
                    continue
                for t in pcsinglelist:
                    pcdict[numpcdict[int(t)]]
                break
            except:
                print('hit1')
                print("\nInvalid format and/or range...Try again\n")
                

        numepgdict = {}
        print(("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG")))
        print(("-"* 65))
        for num,epg in enumerate(sorted(allepglist),1):
            numepgdict[num] = epg
            egpslit = epg.split('/')[1:]
            print(("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:])))
        while True:
            try:
                askepgnum = eval(input("which number?: "))
                if askepgnum.strip().lstrip() == '':
                    continue
                epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
                if epgsinglelist == 'invalid':
                    continue
                #for x in epgsinglelist:
                #    print(numepgdict[x])
                break
            except:
                print('hit2')
                print("\nInvalid format and/or range...Try again\n")

        data = ""
        vlan_and_data_list = []

            #print(data)
            #vlan
        for epg in sorted(epgsinglelist):
            url = """https://localhost/api/node/mo/{}.json""".format(numepgdict[epg])
            print(("\nProvide a vlan number for epg: {}".format(numepgdict[epg])))
            while True:
                try:
                    vlan = eval(input('pick a vlan number: '))
                    if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
                       break
                    else:
                        print('Invalid vlan number')
                except:
                    continue
            for interface in sorted(pcsinglelist):
                print(("""{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(pcdict[numpcdict[interface]],vlan=vlan)))

      #      for number in sorted(pcsinglelist):
      #          data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(numepgdict[number],vlan=vlan)
      #          print(data)


        result, totalcount = PostandGetResponseData(url, data)
        #print(numepglist[int(askepgnum)])
     #   for num,a in enumerate(sorted(epgdict, reverse=False),1): 
     #       numepgdict[num] = epgdict[a]
     #       egpslit = epgdict[a].split('/')[1:]
     #       print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
     #   epgnum = raw_input("which number?: ")

        #print(numepgdict[int(epgnum)])
            #print(pcdict)
            #print(epgdict)
#            Curr
#url: https://192.168.255.2/api/node/mo/uni/tn-SI/ap-APP-MGMT/epg-EPG-ESXI-MGMT.json
#payload{"fvRsPathAtt":{"attributes":{"encap":"vlan-235","instrImedcy":"immediate","tDn":"topology/pod-1/paths-102/extpaths-112/pathep-[Find-vpc]","status":"created"},"children":[]}}
#response: {"totalCount":"0","imdata":[]}
#            raw_input("#Press enter to return to main menu...")
if __name__ == '__main__':
    main()
#                        url = 'https://localhost/api/node/mo/uni/fabric/outofsvc.json'
#                        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a fex interface
#                        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
#                        PostandGetResponseData(url, data)
#                        print(leaf + ' ' + fexnumber + ' ' +  ints + ' shut')
#PC
#url: https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),eq(fabricPathEp.lagT,"link"))