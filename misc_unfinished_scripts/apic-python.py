import readline
import urllib2
import urllib
import json
import base64
import ssl
import getpass
import os
import re

os.system('clear')

#username = raw_input('username: ')
#password = getpass.getpass('password: ')


def addingmultipleheaders(items,request):
        if type(items) == list:
                for x, y in items:
                        request.add_header(x,y)

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    #addingmultipleheaders([("Content-Type", "application/json"),('Accept', 'application/json')], request)
 #   base64string = base64.b64encode('%s:%s' % (str(username), str(password)))
 #   request.add_header("Authorization", "Basic %s" % base64string)
    return urllib2.urlopen(request, context=ssl._create_unverified_context())

def PutRequest(url, icookie, data):
    method = "PUT"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url, data)
    addingmultipleheaders([("Content-Type", "application/json"),('Accept', 'application/json')], request)
    base64string = base64.b64encode('%s:%s' % (str(username), str(password)))
    request.add_header("Authorization", "Basic %s" % base64string)
    request.get_method = lambda: method
    return urllib2.urlopen(request, context=ssl._create_unverified_context())

def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata']

def APIC_login(url):
    method = "POST"
    #data = json.dumps({"aaaUser":{"attributes":{"name":str(username),"pwd":str(password)}}})
    data = json.dumps({"aaaUser":{"attributes":{"name":"admin","pwd":"Cisco12345"}}})
    request = urllib2.Request(url, data)
    #request.add_data(data)
    request.add_header("Content-Type", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())

def whatleafs():
    while True:
        leafs = str(raw_input('What leaf(s): '))
        if leafs == "":
            continue 
        else:
            break
    return leafs.replace(" ", "").split(',')

def whatinterfaces():
    while True:
        interfaces = str(raw_input('What interface(s): '))
        if interfaces == "":
            continue 
        else:
            break
        #interfaces = 'eth1/2,6-10,33,45,47-48'
    return interfaces.replace(" ", "")

def verifysuccessfulsubmition(command, prompt, status, interface):
    result = CaptureOutputOfCommand(command,prompt)
    result = result.lstrip()
    result = re.search(r'\{(.*)\}',result)
    #print(str(result.group()))
    if not result.group() == '{"totalCount":"0","imdata":[]}':
        if status == "shut":
            print(str('ERROR: Shutting ' + interface))
        else:
            print(str('ERROR: NO Shutting' + interface))

def wait4keypress():
    presskey = str(raw_input('\n### Press Enter to continue.....'))
    if presskey == '':
        os.system('clear')
    else:
        os.system('clear')


def Main():

    
    while True:
        question = str(raw_input('Select:\n\n' +
                        '   1 --  shut and no shut   (Physical interfaces)\n' +
                        '   2 --  shut and no shut   (Port-channel(s))\n' +
                        '   4 --  Port-channel info \n ' +
                        '   2 --  Full MAC Search [local]\t    (Faster on APIC)\n' + 
                        '   3 --  IP Endpoint Search [local]\t    (Faster on APIC)\n' +
                        '   4 --  Last 4 MAC search [local]\n'+
                        '   19 -- Troubleshoot Endpoint path\t  (INCOMPLETE)\n:' ))
                        #'   19 -- Show pim neighbors\n'
        if question == '1':
            while True:
                #generateinterfaces()
                fex = False
                ending_interfaces = ""
                starting_interfaces = ""				
                leafs = whatleafs()
                #if not leafs:
                #    continue
                interfaces = whatinterfaces()
                if not interfaces:
                    continue	
                if not '/' in interfaces:
                    print('Incorrect format')
                    continue
                # Dividing the user interfaces 'string' and getting the port numbers from the beginning 
                slash_location = interfaces.find('/')			
                if interfaces.count('/') == 2:
                    fex = True
                    slash_location = interfaces.rfind('/')
                    ending_interfaces = interfaces[slash_location+1:]
                    starting_interfaces = interfaces[:slash_location+1]
                    fexnumber = re.search(r'[0-9]{3}', starting_interfaces).group()
                                        #cat = False#print(str(fexnumbe				
                elif interfaces.count('/') == 1:
                    slash_location = interfaces.find('/')
                    ending_interfaces = interfaces[slash_location+1:]
                    starting_interfaces = interfaces[:slash_location+1]
                else:
                    print('incorrect format')
                    continue
                #create list for numbers
                numlist = []	
                # If else to calculate interfaces for ranges and single interfaces
                if ',' in ending_interfaces:
                    ending_interfaces = ending_interfaces.split(',')
                    for num_int in ending_interfaces:
                        if re.search(r'-', num_int):
                            if not re.search(r'^([1-5]{0,2}|[0-9]{0,2})-[0-9]{1,3}', num_int):
                                print('fail incorrect numbers')
                            else:
                                ending_interfaces = re.search(r'^([1-5]{0,2}|[0-9]{0,2})-[0-9]{1,3}', num_int).group()
                                num_int = num_int.replace('-', ',').split(',')
                                for x in xrange(int(num_int[0]),int(num_int[-1])+1):
                                    numlist.append(str(x))
                                #print(numlist)
                        else:
                            numlist.append(num_int)
                        #print(numlist)
                elif '-' in ending_interfaces:
                    if not re.search(r'^([1-5]{0,1}|[0-9]{0,2})-[0-9]{1,2}', ending_interfaces):
                        print('fail restart')	
                    ending_interfaces = re.search(r'^([1-5]{0,1}|[0-9]{0,2})-[0-9]{1,2}', ending_interfaces).group()
                    ending_interfaces = ending_interfaces.replace('-', ',').split(',')
                    for x in xrange(int(ending_interfaces[0]),int(ending_interfaces[-1])+1):
                        numlist.append(x)
                else:
                    numlist.append(ending_interfaces)
                interfaces = [str(starting_interfaces) + str(x) for x in numlist]	
                leafinterfacenotification = ""		
                for leaf in leafs:
                    for inter in interfaces:
                        leafinterfacenotification += str(leaf) + '\t' + str(inter) + '\n'
                    leafinterfacenotification += '\n'			
                ask = str(raw_input('Bounce ports: \n\n' + '{:<5}\t{}\n'.format('leaf', 'interface') + '{:-<40}\n'.format('-') + leafinterfacenotification + '\n\nCorrect\n ("yes" or "no"?)'))	
                if ask == "":
                    continue
                if ask.lower() == "yes" or ask[0].lower() == "y":
                    for leaf in leafs:
                        for ints in interfaces:
                            if fex:
                                command = """icurl -k 'https://localhost/api/node/mo/uni/fabric/outofsvc.json' -d '{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
                                verifysuccessfulsubmition(command, prompt, 'shut', (fexnumber + ints))
                                command = """icurl -k 'https://localhost/api/node/mo/uni/fabric/outofsvc.json' -d '{{"fabricRsOosPath":{{"attributes":{{"dn":"uni/fabric/outofsvc/rsoosPath-[topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]]","status":"deleted"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
                                verifysuccessfulsubmition(command, prompt, 'no-shut', (fexnumber + ints))
                            else:
                                command = """icurl -k 'https://localhost/api/node/mo/uni/fabric/outofsvc.json' -d '{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(ints=ints,leaf=leaf)
                                verifysuccessfulsubmition(command, prompt, 'shut', (ints))
                                command = """icurl -k 'https://localhost/api/node/mo/uni/fabric/outofsvc.json' -d '{{"fabricRsOosPath":{{"attributes":{{"dn":"uni/fabric/outofsvc/rsoosPath-[topology/pod-1/paths-{leaf}/pathep-[{ints}]]","status":"deleted"}},"children":[]}}}}'""".format(ints=ints,leaf=leaf) 
                                verifysuccessfulsubmition(command, prompt, 'no-shut', (ints))
    
                        print('\n')
                    leafs = []
                    interfaces = []	
                    #crt.Screen.Clear()
                    print('\n')
                    break
                elif ask.lower() == "no" or ask[0].lower() == "n":
                    leafs = []
                    interfaces = []	
                    print('Canceling\n')
                    break
                else:
                    leafs = []
                    interfaces = []	
                    print('Canceling\n')
                    break
        elif question == "2":
            command = """moquery -c pcAggrIf | grep -e 'name\|dn'"""
            result = CaptureOutputOfCommand(command,prompt)
            result = result.split('\r\n')
            #cat = False#print(str(result))
            #num = 0
            itemlist = []
            #for item in result[:-1]:
            #	num += 1
            #	if num % 2 == 0:
            #cat = False#print(str(result[0]))
    #why is this not working?		#result = ','.join(result[i:i+2] for i in range(0, len(result), 2))
            for i in range(0, len(result[:-1]), 2):
                itemlist.append((result[i] + " " + result[i+1]))
            
            #cat = False#print(str(itemlist))
            #foundgroups = []
            finallist = []
            dicofgroups = {}
            leafset = set()
            foundgroups = [re.findall(r'node-[0-9]{3}|po\d+|\w+$', str(item)) for item in itemlist]
            #for leaf,po,pcname in foundgroups:
            for leaf,po,pcname in foundgroups:
                dicofgroups[leaf[5:] + pcname] = [po]
            
    #			finallist = [[leaf[5:],po,pcname] for leaf,po,pcname in foundgroups]
    #			#cat = False#print(str(repr(leaf)))
    #			leafset.add(leaf[5:])
    #		leafset = list(leafset)
    #		for leaf in leafset:
    #			if leafset[0] == leaf[0]:
    #				cat = False#print(str(leaf))
            #	leaflist = [x for x in foundgroups if leaf == leaf[0]]
            #for leafnum in range(len(leafset)):
            #	l
            #for leaf in leafset:
                #if leaf[5:] == '101':
                    #cat = False#print(str('leaf:' + leaf[5:] + " port-channel:" + po + " name:" + pcname))
                
            ####finallist = [[leaf[5:],po,pcname] for leaf,po,pcname in foundgroups]	
            
            cat = False#print(str(dicofgroups))
            #cat = False#print(str(result))
            #for dnitem in result[1:-1:2]:
            #	dnitem = False
            #result[0]
            #for nameitem in result[:-1:2]:
            #	nameitem = False
                #
        elif question == '3':
            url = """https://192.168.255.2/api/node/class/fabricNode.json"""
            nodelist = GetResponseData(url)
            leaflist = [leaf['fabricNode']['attributes']['id'] for leaf in nodelist]
            leaflist = re.findall(r'1[0-9]{2}', (','.join(leaflist)))
            print(leaflist)
            url = """https://192.168.255.2/api/node/class/pcAggrIf.json"""
            pclist = GetResponseData(url)
            for pc in pclist:
                print(pc['pcAggrIf']['attributes']['name'], pc['pcAggrIf']['attributes']['dn'])
            wait4keypress()
        elif question == '4':
            #url = """https://localhost/api/node/class/pcAggrIf.json?rsp-subtree=children&target-subtree-class=ethpmAggrIf&rsp-subtree-filter=and(eq(ethpmAggrIf.operSt,"down"))"""
            url = """https://localhost/api/node/class/pcAggrIf.json?rsp-subtree=children"""
            pclist = GetResponseData(url)
            url = """https://192.168.255.2/api/node/class/fabricNode.json"""
            nodelist = GetResponseData(url)
            leaflist = [leaf['fabricNode']['attributes']['id'] for leaf in nodelist]
            #print(pclist)
            pcstringlist = ""
            pcstringlist += '\n{:<15}'.format('Leaf') + '{:<20}'.format('Name') + '{:<15}'.format('Local Po#') + '{:<30}'.format('Status') + '\n'
            pcstringlist += '-' * 100 + '\n'
            
            orderedlist = []
            for node in nodelist:
                for pc in sorted(pclist):
                    id = re.search(r'node-1[0-9]{2}', pc['pcAggrIf']['attributes']['dn']).group().replace('node-', "")
        #			print(node['fabricNode']['attributes']['id'], id )
                    if node['fabricNode']['attributes']['id'] == id:
    #					orderedlist.append(pc)
    #	#	print(orderedlist)
    #		for pc in orderedlist:
    #		#	print(pc)
                        leaf = (re.search(r'node-1[0-9]{2}', (pc['pcAggrIf']['attributes']['dn'])).group()).replace('node-', 'leaf ' )
                            #print(str(pc))
                        pcstringlist += '{:<15}'.format(leaf) + '{:<20}'.format(pc['pcAggrIf']['attributes']['name']) + '{:<15}'.format(pc['pcAggrIf']['attributes']['id']) + '{}'.format(pc['pcAggrIf']['attributes']['adminSt']) + "\\" 
                        #if pc.get('pcAggrIf').get('children'):
                        if pc['pcAggrIf']['children'][0]['ethpmAggrIf']['operSt'] != 'up':
                            pcstringlist += 'down\n'
                        else:
                            pcstringlist += 'up\n'
            leaflist = ['101','102']
            for x in leaflist[1:]:
                location = pcstringlist.find(x)
            breakline = '\n'
            pcstringlist = pcstringlist[:location-5] + breakline + pcstringlist[location-5:]
            
                #

            #for pc in sorted(pclist):
            #    #if not pc.get('pcAggrIf'):
            #	leaf = (re.search(r'node-1[0-9]{2}', (pc['pcAggrIf']['attributes']['dn'])).group()).replace('node-', 'leaf ' )
            #		#print(str(pc))
            #	pcstringlist += '{:<30}'.format(leaf) + '{:<20}'.format(pc['pcAggrIf']['attributes']['name']) + '{:<25}'.format(pc['pcAggrIf']['attributes']['id']) + '{}'.format(pc['pcAggrIf']['attributes']['adminSt']) + "\\" 
            #	if pc.get('pcAggrIf').get('children'):
            #		pcstringlist += 'down\n'
            #	else:
            #		pcstringlist += 'up \n'
            print(str(pcstringlist))
            
            url = """https://localhost/api/node/class/pcAggrIf.json?rsp-subtree=children"""
            test = GetResponseData(url)
            print('done')
            wait4keypress()
        elif question == 's':
            objConfig = currentTAB.Session.Config
            scroll = objConfig.GetOption("Scrollbackbuffer")
            cat = False#print(str(scroll))
            os.system('clear')
        
        elif question == '':
            break
        
    #cat = False#crt.Quit()



url = """https://localhost/api/aaaLogin.json"""
response = APIC_login(url)
result = json.loads(response.read())
cookie = result['imdata'][0]['aaaLogin']['attributes']['token']
#cookies = 'APIC-cookie=' + icookie
#print('cookie', cookies)

Main()
