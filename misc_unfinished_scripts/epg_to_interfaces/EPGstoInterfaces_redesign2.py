#!/bin//python

import re
import readline
import urllib2
import json
import ssl
import os
import datetime
import itertools
import trace
import pdb
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
    return itertools.izip_longest(*args, fillvalue=fillvalue)



def menu():
    while True:
        os.system('clear')
        print("\nSelect interface for adding EPGs: \n" + \
          "\n\t1.) Physical Interfaces: \n" + \
          "\t2.) PC Interfaces: \n" + \
          "\t3.) VPC Interfaces: \n")
        selection = raw_input("Select number: ")
        print('\r')
        if selection.isdigit() and selection != '' and 1 <= int(selection) <= 3:
            break
        else:
            continue
    return selection 

def get_All_EGPs_names():
    get_Cookie()
    epgdict = {}
    url = """https://localhost/api/node/class/fvAEPg.json"""
    result, totalCount = GetResponseData(url)
    #print(json.dumps(result, indent=2))
    epglist = [epg['fvAEPg']['attributes']['dn'] for epg in result]
            #epgdict[epg['fvAEPg']['attributes']['name']] = epg['fvAEPg']['attributes']['dn']
    #    epglist.append(epg['fvAEPg']['attributes']['dn'])
    return epglist

def get_All_PCs():
    url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """eq(fabricPathEp.lagT,"link"))"""
    result, totalCount = GetResponseData(url)
    return result

def get_All_vPCs():
    url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))"""
    result, totalCount = GetResponseData(url)
    return result

def get_All_leafs():
    url = """https://localhost/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))"""
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

        #1,2,4,5,10]
        #[object1,object2,object3,object4,object5,object6]

    except ValueError as v:
        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
        return 'invalid'



def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)


def vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist):
   # uniquenumber = 0
    urllist = []
   # urldict = {}
    for epg in sorted(epgsinglelist):
        url = """https://localhost/api/node/mo/{}.json""".format(numepgdict[epg])
        print("\nProvide a vlan number for epg: {}".format(numepgdict[epg]))
        while True:
            try:
                vlan = raw_input('vlan number [1-3899]: ')
                print('\r')
                if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
                   break
                else:
                    print('Invalid vlan number')
            except:
                continue
        for interface in sorted(choseninterfaceobjectlist):
            #uniquenumber += 1
            #pdb.set_trace()
            fvRsPa = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","instrImedcy":"immediate",\
                         "tDn":"{}","status":"created"}},"children":[]}}}}'""".format(interface.dn,vlan=vlan)
            #print(fvRsPa)
            urllist.append((url, interface, fvRsPa))
           # urldict[uniquenumber] = (url, interface.dn, fvRsPa)
    return urllist

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

def port_channel_selection(allpclist,allepglist):
    pcdict = {}  
    pcobjectlist = []
    for pc in allpclist:
        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
    #for pc in allpclist:
    #    pcdict[pc['fabricPathEp']['attributes']['name']] = pc['fabricPathEp']['attributes']['dn']
    print("\n{:>4} |  {}".format("#","Port-Channel Name"))
    print("-"* 65)
   # numpcdict = {}
    for num,pc in enumerate(sorted(pcobjectlist),1):
        print("{:>4}.) {}".format(num,pc.name))
        pc.number = num
    #    numpcdict[num] = pc
    while True:
        try:
            askpcnum = raw_input("\nWhich number(s)?: ")
            print('\r')
            if askpcnum.strip().lstrip() == '':
                continue
            #askpcnum = '1,2,3,6,9,12,14'
            pcsinglelist = parseandreturnsingelist2(askpcnum,pcobjectlist)
            if pcsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in pcsinglelist, pcobjectlist)
           # for chosennumber in pcsinglelist:
           #     #if chosennumber in 
           #     pcdict[pcobjectlist[int(t)]]
            break
        except:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
            
    numepgdict = {}

    print("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG"))
    print("-"* 65)
    for num,epg in enumerate(sorted(allepglist),1):
        numepgdict[num] = epg
        egpslit = epg.split('/')[1:]
        print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    while True:
        try:
            askepgnum = raw_input("\nWhich number(s)?: ")
            print('\r')
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
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    urllist =  vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist)
        ##        urldict[uniquenumber] = (url, interface.dn, fvRsPa)
    for url in urllist:
        #print(url[0],data)
       # try:
        result, error = PostandGetResponseData(url[0],url[2])
        shorturl = url[0][30:-5]
        if error == None and result == []:
            print('Success for ' + shorturl + ' > ' + str(url[1]))

            #print('Success for ' + str(url[1]))
        elif result == 'invalid':
           # print('level1')
            interfacepath = re.search(r'\[.*\]', error)
            if 'already exists' in error:
                #print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + interfacepath.group() + ' -- EPG already on Interface ' )    
                print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + url[1] + ' -- EPG already on Interface ' )    
            elif 'AttrBased EPG' in error:
              #  print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + pcdict[numpcdict[interface]] +' -- Attribute EPGs need special static attirbutes')    
                print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + ' > ' + url[1] + ' -- Attribute EPGs need special static attirbutes')    
            else:
                print('\x1b[1;37;41mFailure\x1b[0m for ' + shorturl + '\t -- ' + error)  
                # "\x1b[1;37;41mIncorrect Date/Format, Please try again\x1b[0m\x1b[0m\n\n"
           #pass#print('Failed for ' + url[0])
        else:
            print(error)
         #   print('level2')


def physical_selection(all_leaflist, allepglist):
    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
    nodelist.sort()
    for num,node in enumerate(nodelist,1):
        print("{}.) {}".format(num,node))
    while True:
        try:
            asknode = raw_input('\nWhat leaf(s): ')
            print('\r')
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
        url = """https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf)
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
        try:
            selectedinterfaces = raw_input("\nSelect interface(s) by number: ")
            print('\r')
            if selectedinterfaces.strip().lstrip() == '':
                continue
            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
            if intsinglelist == 'invalid':
                continue
            choseninterfaceobjectlist = filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist)

           # for number in intsinglelist:
           #     if not (0 < int(number) <= len(finalsortedinterfacelist)):
           #         print('here')
           #         print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
           #         continue
            break
        except KeyboardInterrupt as k:
            print('\n\nEnding Script....\n')
            return
      #  except Exception as e:
      #      print(e)
      #      print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
      #      continue
    #print(intsinglelist)
    numepgdict = {}
    print("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG"))
    print("-"* 65)
    allepglist = sorted(allepglist)
    for num,epg in enumerate(allepglist,1):
        numepgdict[num] = epg
        egpslit = epg.split('/')[1:]
        print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    while True:
        try:
            askepgnum = raw_input("\nWhich number(s)?: ")
            print('\r')
            if askepgnum.strip().lstrip() == '':
                continue
            epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
            if epgsinglelist == 'invalid':
                continue
            chosenepgs = [allepglist[x] for x in epgsinglelist]
            #for x in epgsinglelist:
            #    print(numepgdict[x])
            break
        except KeyboardInterrupt as k:
            print('\n\nEnding Script....\n')
            return
        #except:
        #    print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    
    #print(sorted(epgsinglelist))
    compoundurllist = []
    urllist =  vlan_and_url_generating(epgsinglelist,numepgdict,choseninterfaceobjectlist)
    ##urldict = {}
    ##uniquenumber = 0
    ##for epg in sorted(epgsinglelist):
    ##    url = """https://localhost/api/node/mo/{}.json""".format(numepgdict[epg])
    ##    print("\nProvide a vlan number for epg: {}".format(numepgdict[epg]))
    ##    while True:
    ##        try:
    ##            vlan = raw_input('Vlan number [1-3899]: ')
    ##            print('\r')
    ##            if vlan.isdigit() and vlan.strip().lstrip() != '' and int(vlan) > 0 and int(vlan) < 4096:
    ##               break
    ##            else:
    ##                print('Invalid vlan number')
    ##        except KeyboardInterrupt as k:
    ##            print('\n\nEnding Script....\n')
    ##            return
    ##        except:
    ##            continue
    ##    #print(interfacedict)
    ##   # for interface in sorted(intsinglelist):
    ##   #     for name,inter in interfacedict.items():
    ##   #         #print(interface,inter[:-3])
    ##   #         if str(interface) == str(inter[:-3]):
    ##   #             print("""{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(name,vlan=vlan))
    ##    for interface in sorted(intsinglelist):
    ##        uniquenumber += 1
    ##      #  for name,inter in interfacedict.items():
    ##            #print(interface,inter[:-3])
    ##        #    if str(interface) == str(inter[:-3]):
    ##        fvRsPa = """'{{"fvRsPathAtt":{{"attributes":{{"encap":"vlan-{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}'""".format(finalsortedinterfacelist[interface-1],vlan=vlan)
    ##    #print(finalsortedinterfacelist[1])
    ##        #print(type(fvRsPa))
    ##        #compoundurllist.append(urldict[url] = fvRsPa)
    ##        urldict[uniquenumber] = (url, finalsortedinterfacelist[interface-1], fvRsPa)
        
    for url in urllist:
        #print(url[0],data)
       # try:
        #pdb.set_trace()
        result, error = PostandGetResponseData(url[0],url[2])
        if error == None and result == []:
           # print('physical')
            print('Success for ' + url[0][34:-5] + ' > ' + str(url[1]))
        elif result == 'invalid':
           # print('level1')
            interfacepath = re.search(r'\[.*\]', error)
            if 'already exists' in error:
            #    print('\x1b[1;37;41mFailure\x1b[0m ' + url[0][30:-5] + '\t -- EPG already on Interface ' + interfacepath.group())    
                print('\x1b[1;37;41mFailure\x1b[0m ' + url[0][30:-5] + ' > ' + url[1].dn + '\t -- EPG already on Interface ')# + interfacepath.group())    
            else:
                print('\x1b[1;37;41mFailure\x1b[0m ' + url[0][30:-5] + '\t -- ' + error)
           #pass#print('Failed for ' + url[0])
        else:
            print(error)
           # print('level2')

def main():
    while True:
        get_Cookie()
        allepglist = get_All_EGPs_names()
        allpclist = get_All_PCs()
        allvpclist = get_All_vPCs()
        all_leaflist = get_All_leafs()
    
        selection = menu()
    
        if selection == '1':
            physical_selection(all_leaflist, allepglist)
            print('\r')
            raw_input('#Press enter to continue...')
        elif selection == '2':
            port_channel_selection(allpclist,allepglist)
            print('\r')
            raw_input('#Press enter to continue...')
          #      for number in sorted(pcsinglelist):
          #          data = """{{"fvRsPathAtt":{{"attributes":{{"encap":"{vlan}","instrImedcy":"immediate","tDn":"{}","status":"created"}},"children":[]}}}}""".format(numepgdict[number],vlan=vlan)
          #          print(data)
            #result, totalcount = PostandGetResponseData(url, data)
        elif selection == '3':
            port_channel_selection(allvpclist,allepglist)
            print('\r')
            raw_input('#Press enter to continue...')
        
        #print(numepglist[int(askepgnum)])
     #   for num,a in enumerate(sorted(epgdict, reverse=False),1): 
     #       numepgdict[num] = epgdict[a]
     #       egpslit = epgdict[a].split('/')[1:]
     #       print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
     #   epgnum = raw_input("which number(s)?: ")

        #print(numepgdict[int(epgnum)])
            #print(pcdict)
            #print(epgdict)
#            Curr
#url: https://192.168.255.2/api/node/mo/uni/tn-SI/ap-APP-MGMT/epg-EPG-ESXI-MGMT.json
#payload{"fvRsPathAtt":{"attributes":{"encap":"vlan-235","instrImedcy":"immediate","tDn":"topology/pod-1/paths-102/extpaths-112/pathep-[Find-vpc]","status":"created"},"children":[]}}
#response: {"totalCount":"0","imdata":[]}
#            raw_input("#Press enter to return to main menu...")
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
                print('\n\nEnding Script....\n')
                exit()

#                        url = 'https://localhost/api/node/mo/uni/fabric/outofsvc.json'
#                        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a fex interface
#                        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
#                        PostandGetResponseData(url, data)
#                        print(leaf + ' ' + fexnumber + ' ' +  ints + ' shut')
#PC
#url: https://localhost/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),eq(fabricPathEp.lagT,"link"))