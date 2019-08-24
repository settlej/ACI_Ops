import os
import datetime
import json
import urllib2
import ssl

def custom_raw_input(inputstr):
    r = raw_input(inputstr)
    if r == 'exit':
        raise KeyboardInterrupt
    else:
        return r
def clear_screen():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')

#def GetRequest(url, icookie):
#    method = "GET"
#    cookies = 'APIC-cookie=' + icookie
#    request = urllib2.Request(url)
#    request.add_header("cookie", cookies)
#    request.add_header("Content-trig", "application/json")
#    request.add_header('Accept', 'application/json')
#    return urllib2.urlopen(request, context=ssl._create_unverified_context())
#
#def GetResponseData(url, cookie):
#    response = GetRequest(url, cookie)
#    result = json.loads(response.read())
#    return result['imdata'], result["totalCount"]
#
##def getCookie():
##    global cookie
##    with open('/.aci/.sessions/.token', 'r') as f:
##        cookie = f.read()
#
#def displaycurrenttime():
#    currenttime = datetime.datetime.now()
#    return str(currenttime)[:-3]
#
#def time_difference(admin_time):
#    currenttime = datetime.datetime.now()
#    ref_admin_time = datetime.datetime.strptime(admin_time, '%Y-%m-%d %H:%M:%S.%f')
#    return str(currenttime - ref_admin_time)[:-7]
#
#def physical_selection(all_leaflist, allepglist):
#    nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
#    nodelist.sort()
#    for num,node in enumerate(nodelist,1):
#        print("{}.) {}".format(num,node))
#    while True:
#        #try:
#            asknode = custom_raw_input('\nWhat leaf(s): ')
#            print('\r')
#            returnedlist = parseandreturnsingelist(asknode, nodelist)
#            if returnedlist == 'invalid':
#                continue
#            chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
#            break
#        #except KeyboardInterrupt as k:
#        #    print('\n\nEnding Script....\n')
#        #    return
#    compoundedleafresult = []
#    for leaf in chosenleafs:
#        url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
#              """and(eq(fabricPathEp.lagT,"not-aggregated"),eq(fabricPathEp.pathT,"leaf"),wcard(fabricPathEp.dn,"topology/pod-1/paths-{leaf}/"),""" \
#              """not(or(wcard(fabricPathEp.name,"^tunnel"),wcard(fabricPathEp.name,"^vfc")))))&order-by=fabricPathEp.dn|desc""".format(leaf=leaf,apic=apic)
#        result, totalcount = GetResponseData(url)
#        compoundedleafresult.append(result)
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
#    firstgrouped = [x for x in grouper(finalsortedinterfacelist,listlen)]
#    finalgrouped = zip(*firstgrouped)
#    for column in finalgrouped:
#        a = column[0].number
#        b = goodspacing(column[0]) + '  ' + column[0].descr[:25]
#        c = column[1].number
#        d = goodspacing(column[1]) + '  ' + column[1].descr[:25]
#        if column[2] == '' or column[2] == None:
#            e = ''
#            f = ''
#        else:
#            #e = interfacedict[column[2]]
#            e = column[2].number
#            f = goodspacing(column[2])
#            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
#        print('{:6}.) {:45}{}.) {:45}{}.) {}'.format(a,b,c,d,e,f))
#    while True:
#        #try:
#            selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
#            print('\r')
#            if selectedinterfaces.strip().lstrip() == '':
#                continue
#            intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
#            if intsinglelist == 'invalid':
#                continue
#            choseninterfaceobjectlist = filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist)
#           # for number in intsinglelist:
#           #     if not (0 < int(number) <= len(finalsortedinterfacelist)):
#           #         print('here')
#           #         print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
#           #         continue
#            break
#        #except KeyboardInterrupt as k:
#        #    print('\n\nEnding Script....\n')
#        #    exit()
#    return choseninterfaceobjectlist
#
#
#def port_channel_selection(allpclist,allepglist):
#    pcobjectlist = []
#    for pc in allpclist:
#        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
#                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
#    print("\n{:>4} |  {}".format("#","Port-Channel Name"))
#    print("-"* 65)
#    for num,pc in enumerate(sorted(pcobjectlist),1):
#        print("{:>4}.) {}".format(num,pc.name))
#        pc.number = num
#    while True:
#        try:
#            askpcnum = custom_raw_input("\nWhich number(s)?: ")
#            print('\r')
#            if askpcnum.strip().lstrip() == '':
#                continue
#            pcsinglelist = parseandreturnsingelist(askpcnum,pcobjectlist)
#            if pcsinglelist == 'invalid':
#                continue
#            choseninterfaceobjectlist = filter(lambda x: x.number in pcsinglelist, pcobjectlist)
#            break
#        except ValueError:
#            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
#    return choseninterfaceobjectlist
#
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
#   #     print(sorted(singlelist))
#        if max(singlelist) > len(collectionlist) or min(singlelist) < 1:
#            print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
#            return 'invalid'
#        return list(set(singlelist)) 
#    except ValueError as v:
#        print('\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n')
#        return 'invalid'



#def get_All_EGPs(apic):
#    ##get_Cookie()
#    epgdict = {}
#    url = """https://{apic}/api/node/class/fvAEPg.json""".format(apic=apic)
#    result, totalCount = GetResponseData(url)
#    epglist = [epg['fvAEPg']['attributes']['dn'] for epg in result]
#
#    return epglist
#
#def get_All_PCs(apic):
#    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
#          """eq(fabricPathEp.lagT,"link"))""".format(apic=apic)
#    result, totalCount = GetResponseData(url)
#    return result
#
#def get_All_vPCs(apic):
#    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
#          """and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))""".format(apic=apic)
#    result, totalCount = GetResponseData(url)
#    return result
#
#def get_All_leafs(apic):
#    url = """https://{apic}/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
#          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))""".format(apic=apic)
#    result, totalCount = GetResponseData(url)
#    #print(result)
#    return result
#