import os
import re
import socket
import datetime
import json
import urllib2
import ssl
import itertools
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

def location_banner(location):
    banner = ("######################################\n"
            + "#{:^36}#\n".format('')
            + "#{:^36}#\n".format(location)
            + "#{:^36}#\n".format('')
            + "######################################\n")
    print(banner)


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

def time_difference(current_time, event_time):
    currenttime = datetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S.%f')
    ref_event_time = datetime.datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S.%f')
    calculatedtime = str(currenttime - ref_event_time)
    if '.' in calculatedtime:
        return calculatedtime[:-7]
    else:
        return calculatedtime


def get_APIC_clock(apic,cookie):
    if apic == 'localhost':
        serverhostname = socket.gethostname()
        url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=or(eq(topSystem.name,"{serverhostname}"))""".format(apic=apic,serverhostname=serverhostname)
    elif not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",apic.strip().lstrip()):
        apicip = socket.gethostbyname(apic)
        url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=or(eq(topSystem.oobMgmtAddr,"{apicip}"),eq(topSystem.inbMgmtAddr,"{apicip}"))""".format(apic=apic,apicip=apicip)
    else:
        url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=or(eq(topSystem.oobMgmtAddr,"{apic}"),eq(topSystem.inbMgmtAddr,"{apic}"))""".format(apic=apic)
    logger.info(url)
    result = GetResponseData(url,cookie)
    if result == []:
        url = """https://{apic}/api/mo/info.json""".format(apic=apic)
        result = GetResponseData(url,cookie)
        return result[0]['topInfo']['attributes']['currentTime'][:-7].replace('T', ' ')
    return result[0]['topSystem']['attributes']['currentTime'][:-7].replace('T', ' ')

def refreshToken(apic,icookie):
    ssl._create_default_https_context = ssl._create_unverified_context
    url = "https://{apic}/api/aaaRefresh.json".format(apic=apic)
    logger.info(url)
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("Cookie", cookies)
    response = urllib2.urlopen(request, timeout=4)
    result = json.loads(response.read())
    return result["imdata"][0]["aaaLogin"]["attributes"]["token"]

#############################################################################################################################################
#                               What does this program do
#                               What are you trying to accomplish
#                               Who program the thing
#                               What version you are on
#                               Date Created
#                               Date Last time modify
#############################################################################################################################################

#############################################################################################################################################
#                               What does this def do period
#                               Who program the thing
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
    request = urllib2.Request(url)
    # Function needs APIC cookie for authentication and what content format you need in returned http object (example JSON)
    # need to add header one at a time in urllib2
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())

def GetResponseData(url, cookie, return_count=False):
    # Fuction to take JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
    # Perform a GetRequest function to perform a GET REST call to server and provide response data
    response = GetRequest(url, cookie) # here for this
    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
    result = json.loads(response.read()) # here for this
    # return only infomation inside the dictionary under 'imdata'
    #logger.debug(result)
    if return_count == True:
        return result['imdata'], result['totalCount']
    else:
        return result['imdata'] #here for this

def PostandGetResponseData(url, data, cookie):
    # Fuction to submit JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
    # Perform a POSTRequest function to perform a POST REST call to server and provide response data
    response, error = POSTRequest(url, data, cookie)
    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
        # return only infomation inside the dictionary under 'imdata'.  If response is a string rether than a urllib object return str with error
    if isinstance(response,str):
        return response, error
    else:
        result = json.loads(response.read())
        return result['imdata'], error

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
    # Mandate the urllib request is a POST instead of default GET request
    request.get_method = lambda: method
    try:
        return urllib2.urlopen(request, context=ssl._create_unverified_context()), None
    except urllib2.HTTPError as httpe:
        failure_reason = json.loads(httpe.read())
        failure_reason = failure_reason['imdata'][0]['error']['attributes']['text'].strip()
        return 'invalid', failure_reason
    except urllib2.URLError as urle:
        #print(urle.code)
        failure_reason = json.loads(urle.read())
        return 'invalid', failure_reason

def interface_menu():
    while True:
        print("\nSelect type of interface(s): \n\n" + \
          "\t1.) Physical Interfaces: \n" + \
          "\t2.) PC Interfaces: \n" + \
          "\t3.) VPC Interfaces: \n")
        selection = custom_raw_input("Select number: ")
        print('\r')
        if selection.isdigit() and selection != '' and 1 <= int(selection) <= 3:
            break
        else:
            continue
    return selection 

class epgformater():
    def __init__(self, epgdn):
        self.dnsplit = epgdn.split('/')
        self.tenant = self.dnsplit[1]
        self.app = self.dnsplit[2]
        self.epg = self.dnsplit[3]
        self.clean = '|'.join((self.tenant.replace('tn-',''),self.app.replace('ap-',''),self.epg.replace('epg-','')))
    def __repr__(self):
        return self.clean
    def __str__(self):
        return self.clean

class fabricPathEp(object):
    def __init__(self, descr=None, dn=None,name=None, number=None):
        self.name = name
        self.descr = descr
        self.dn = dn
        self.number = number
        self.epgfvRsPathAttlist = []
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

class l1PhysIf():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.fex = None
        self.typefex = None 
        self.uplink = None 
        self.pctype = None
       # self.
        self.pc_mbmr = []
        self.children = []
    def __repr__(self):
        return self.id
    def __setitem__(self, a,b):
        setattr(self, a, b)
    def add_child(self, obj):
        self.children.append(obj)
    def __getitem__(self, x):
        if x == self.id:
            return True
    def add_portchannel(self, p):
        self.pc_mbmr.append(p) 
    def port_adminstatus_color(self):
        if self.adminSt == 'up':
            return '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)
        else:
            return '\x1b[3;47;40m{:2}\x1b[0m'.format(self.shortnum)
    def port_epgusage_color(self):
        if 'epg' in self.usage:
            #return '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)
            return '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)
        else:
            #return '\x1b[2;30;47m{:2}\x1b[0m'.format(self.shortnum)
            return '\x1b[3;47;40m{:2}\x1b[0m'.format(self.shortnum)            
    def port_status_color(self):
        if self.portstatus == 'up/up' and self.switchingSt == 'enabled':
            return '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)
        elif self.portstatus == 'up/up' and self.switchingSt == 'disabled':
            return '\x1b[0;30;43m{:2}\x1b[0m'.format(self.shortnum)
        elif self.portstatus == 'admin-down':
            #2;30;47
            return '\x1b[2;30;47m{:2}\x1b[0m'.format(self.shortnum)
            #return '\x1b[0;37;45m{:2}\x1b[0m'.format(self.shortnum)
        else:
            return '\x1b[1;37;41m{:2}\x1b[0m'.format(self.shortnum)
    def port_type_color(self):
        if not 'not-a-span-dest' in self.spanMode:
            return '\x1b[1;31;40m{:2}\x1b[0m'.format(self.shortnum)
        elif 'controller' in self.usage:
            return '\x1b[1;37;45m{:2}\x1b[0m'.format(self.shortnum)
        elif self.layer == "Layer2" and self.pcmode == 'off' and self.epgs_status == 'yes':
            return '\x1b[2;30;42m{:2}\x1b[0m'.format(self.shortnum)
        elif self.layer == "Layer2" and not self.pcmode == 'off' and self.pctype == 'pc':
            return '\x1b[2;30;42m{:2}\x1b[0m'.format(self.shortnum)
        elif self.layer == "Layer2" and not self.pcmode == 'off' and self.pctype == 'vpc':
            return '\x1b[2;37;44m{:2}\x1b[0m'.format(self.shortnum)
        elif 'fabric' in self.usage:
            return '\x1b[3;30;47m{:2}\x1b[0m'.format(self.shortnum)
        elif self.layer == "Layer3":
            return '\x1b[2;30;43m{:2}\x1b[0m'.format(self.shortnum)
        elif self.fex == True:
            return '\x1b[2;30;41m{:2}\x1b[0m'.format(self.shortnum)
        else:
            return '\x1b[2;30;37m{:2}\x1b[0m'.format(self.shortnum)
    def port_error_color(self):
        if self.allerrors <= 100:
            return '\x1b[2;30;47m{:2}\x1b[0m'.format(self.shortnum)        
        elif 1000 <= self.allerrors >= 101:
            return '\x1b[2;30;43m{:2}\x1b[0m'.format(self.shortnum)
        elif self.allerrors >= 1001:
            return '\x1b[2;30;47m{:2}\x1b[0m'.format(self.shortnum)          
        else:
            return '\x1b[1;37;42m{:2}\x1b[0m'.format(self.shortnum)


def grouper(iterable, n, fillvalue=''):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n  # creates list * n so args is a list of iters for iterable
    return itertools.izip_longest(*args, fillvalue=fillvalue)

def goodspacing(column):
    if column.fex:
        return column.leaf + ' ' + column.fex + ' ' + str(column.name)
    elif column.fex == '':
        return column.leaf + ' ' + str(column.name)

def display_and_select_epgs(choseninterfaceobjectlist, allepglist):
    numepgdict = {}
    print("\n{:>4} | {:8}|  {:15}|  {}".format("#","Tenant","App-Profile","EPG"))
    print("-"* 65)
    allepglist = sorted(allepglist)
    for num,epg in enumerate(allepglist,1):
        numepgdict[num] = epg
        egpslit = epg.split('/')[1:]
        print("{:4}.) {:8}|  {:15}|  {}".format(num,egpslit[0][3:],egpslit[1][3:],egpslit[2][4:]))
    while True:
        askepgnum = custom_raw_input("\nWhich number(s)?: ")
        print('\r')
        if askepgnum.strip().lstrip() == '':
            continue
        epgsinglelist = parseandreturnsingelist(askepgnum,numepgdict)
        if epgsinglelist == 'invalid':
            continue
        chosenepgs = [allepglist[x-1] for x in epgsinglelist]
        break
    return chosenepgs, choseninterfaceobjectlist


def physical_leaf_selection(all_leaflist, apic, cookie, leafnum=None):
    if leafnum == None:
        nodelist = [node['fabricNode']['attributes']['id'] for node in all_leaflist]
        nodelist.sort()
        for num,node in enumerate(nodelist,1):
            print("{}.) {}".format(num,node))
        while True:
            asknode = custom_raw_input('\nWhich leaf(s): ')
            print('\r')
            returnedlist = parseandreturnsingelist(asknode, nodelist)
            if returnedlist == 'invalid':
                continue
            chosenleafs = [nodelist[int(node)-1] for node in returnedlist]
            break
    else:
        chosenleafs = [leafnum]
    return chosenleafs

def physical_interface_selection(apic, cookie, chosenleafs, provideleaf=False):
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
        if len(goodspacing(column[0]) + '  ') >= 22:
            b = goodspacing(column[0]) + '  ' + column[0].descr[:18]
        else:
            b = goodspacing(column[0]) + '  ' + column[0].descr[:25]
        c = column[1].number
        if len(goodspacing(column[1]) + '  ') >= 22:
            d = goodspacing(column[1]) + '  ' + column[1].descr[:18]
        else:
            d = goodspacing(column[1]) + '  ' + column[1].descr[:25]
        if column[2] == '' or column[2] == None:
            e = ''
            f = ''
        else:
            #e = interfacedict[column[2]]
            e = column[2].number
            if len(goodspacing(column[2]) + '  ') >= 22:
                f = goodspacing(column[2]) + '  ' + column[2].descr[:18]
            else:
                f = goodspacing(column[2]) + '  ' + column[2].descr[:25]
            #f = row[2].leaf + ' ' + row[2].fex + ' ' + str(row[2].name)
        print('{:6}.) {:45}{}.) {:45}{}.) {}'.format(a,b,c,d,e,f))
    while True:
        selectedinterfaces = custom_raw_input("\nSelect interface(s) by number: ")
        print('\r')
        if selectedinterfaces.strip().lstrip() == '':
            continue
        intsinglelist = parseandreturnsingelist(selectedinterfaces,finalsortedinterfacelist)
        if intsinglelist == 'invalid':
            continue
        if provideleaf == False:
            choseninterfaceobjectlist = filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist)
            return choseninterfaceobjectlist
        else:
            #chosenleafs
            choseninterfaceobjectlist = filter(lambda x: x.number in intsinglelist, finalsortedinterfacelist)
            return choseninterfaceobjectlist, chosenleafs

def port_channel_location(pcname, apic, cookie, pctype='vpc'):
    if pctype == 'vpc':
        url = """https://{apic}/api/class/pcAggrIf.json?query-target-filter=eq(pcAggrIf.name,"{pcname}")&rsp-subtree=full&rsp-subtree-class=pcRsMbrIfs""".format(apic=apic,pcname=pcname)
        result = GetResponseData(url, cookie)
    else:
        url = """https://{apic}/api/class/pcAggrIf.json?query-target-filter=eq(pcAggrIf.name,"{pcname}")&rsp-subtree=full&rsp-subtree-class=pcRsMbrIfs""".format(apic=apic,pcname=pcname)
        result = GetResponseData(url, cookie)
    all_locationlist = []
    for pcaggrif in result:
        pcdn = pcaggrif['pcAggrIf']['attributes']['dn']
        pcsplit = pcdn.split('/')
        pcdn_pod = pcsplit[1]
        pcdn_node = pcsplit[2]
        #pcdn_pcnum = pcsplit[4]
        nodelocation = '{}, {}'.format(pcdn_pod,pcdn_node)
        #print('pcnum {}'.format(pcdn_pcnum))
        if pcaggrif['pcAggrIf']['children']:
            interfacelist = []
            for child in pcaggrif['pcAggrIf']['children']:
                childtdn = child['pcRsMbrIfs']['attributes']['tDn']
                pcaggrif_begin = childtdn.find('[')
                pcaggrif_end = childtdn.find(']')
                pcinterface = childtdn[pcaggrif_begin+1:pcaggrif_end]
                interfacelist.append(pcinterface)
        interfacelist.sort()
        all_locationlist.append((nodelocation, interfacelist))
    #import pdb; pdb.set_trace()
    return all_locationlist

class pcObject():
    def __init__(self, name=None, dn=None, number=None):
        self.name = name
        self.dn = dn
        self.number = number
        self.epgfvRsPathAttlist = []
    def __repr__(self):
        return self.dn
    def __get__(self, num):
        if num in self.number:
            return self.name
        else:
            return None

def port_channel_selection(allpclist):
    pcobjectlist = []
    for pc in allpclist:
        pcobjectlist.append(pcObject(name = pc['fabricPathEp']['attributes']['name'],
                                     dn = pc['fabricPathEp']['attributes']['dn'] ))
    print("\n{:>4} |  {}".format("#","Port-Channel Name"))
    print("-"* 65)
    pcobjectlist = sorted(pcobjectlist, key=lambda x:x.name)
    #import pdb; pdb.set_trace()
    for num,pc in enumerate(pcobjectlist,1):
        print("{:>4}.) {}".format(num,pc.name))
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
            choseninterfaceobjectlist = filter(lambda x: x.number in pcsinglelist, pcobjectlist)
            break
        except ValueError:
            print("\n\x1b[1;37;41mInvalid format and/or range...Try again\x1b[0m\n")
    return choseninterfaceobjectlist

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



def get_All_EGPs(apic, cookie, return_count=False):
    url = """https://{apic}/api/node/class/fvAEPg.json""".format(apic=apic)
    logger.info(url)
    if return_count == True:
        result, totalcount = GetResponseData(url, cookie, return_count=True)
        return [epg['fvAEPg']['attributes']['dn'] for epg in result], totalcount
    else:
        result = GetResponseData(url, cookie)
        return [epg['fvAEPg']['attributes']['dn'] for epg in result]

def get_All_PCs(apic, cookie, return_count=False):
    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """eq(fabricPathEp.lagT,"link"))""".format(apic=apic)
    logger.info(url)
    if return_count == True:
        result, totalcount = GetResponseData(url, cookie, return_count=True)
        return result, totalcount
    else:
        result = GetResponseData(url, cookie)
        return result

def get_All_vPCs(apic, cookie, return_count=False):
    url = """https://{apic}/api/node/class/fabricPathEp.json?query-target-filter=and(not(wcard(fabricPathEp.dn,%22__ui_%22)),""" \
          """and(eq(fabricPathEp.lagT,"node"),wcard(fabricPathEp.dn,"^topology/pod-[\d]*/protpaths-")))""".format(apic=apic)
    logger.info(url)
    if return_count == True:
        result, totalcount = GetResponseData(url, cookie, return_count=True)
        return result, totalcount
    else:
        result = GetResponseData(url, cookie)
        return result


def get_All_leafs(apic, cookie, return_count=False):
    url = """https://{apic}/api/node/class/fabricNode.json?query-target-filter=and(not(wcard(fabricNode.dn,%22__ui_%22)),""" \
          """and(eq(fabricNode.role,"leaf"),eq(fabricNode.fabricSt,"active"),ne(fabricNode.nodeType,"virtual")))""".format(apic=apic)
    logger.info(url)
    if return_count == True:
        result, totalcount = GetResponseData(url, cookie, return_count=True)
        return result, totalcount
    else:
        result = GetResponseData(url, cookie)
        return result
