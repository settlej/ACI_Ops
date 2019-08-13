#!/bin//python
import readline
import urllib2
import json
import base64
import ssl
import getpass
import os

os.system('clear')

username = raw_input('username: ')
password = getpass.getpass('(Backspace not supported...blame APIC terminal)\npassword: ')
print(password)

def addingmultipleheaders(items,request):
        if type(items) == list:
                for x, y in items:
                        request.add_header(x,y)

def GetRequest(url):
        method = "GET"
        request = urllib2.Request(url)
        request.add_header("Content-Type", "application/json")
        request.add_header('Accept', 'application/json')
        #addingmultipleheaders([("Content-Type", "application/json"),('Accept', 'application/json')], request)
        base64string = base64.b64encode('%s:%s' % (str(username), str(password)))
        request.add_header("Authorization", "Basic %s" % base64string)  
        return urllib2.urlopen(request, context=ssl._create_unverified_context())


url = 'https://10.100.100.29:9060/ers/config/endpoint'  #.format(endpointmac)
response = GetRequest(url)

print('\r')
endpointmac = str(raw_input('Last 4 of MAC? : '))
print('\r')
#convert any mac combination (. or :) to API acceptiable MAC format
if '.' in endpointmac or ':' in endpointmac:
	endpointmac.replace('.', '').replace(':', '')
endpointmac = ':'.join(endpointmac[i:i+2] for i in range(0, len(endpointmac), 2))
endpointmac = endpointmac.upper()

#
#url = 'https://10.100.100.29:9060/ers/config/endpoint'  #.format(endpointmac)
#response = GetRequest(url)
if response:
	possiblematches = []
        matchdic = {}
        getendpointresult = json.loads(response.read())
	for idfound in getendpointresult['SearchResult']['resources']:
		if endpointmac in idfound['name']:
			possiblematches.append(idfound['name'])
        if possiblematches:
		#print('\n')
		print("Found Possible MACs:")
		#matchdic = {}
                #start = 0
		for num, mac in enumerate(possiblematches, 1):
			matchdic[num] = mac
			print('\t' + str(num) + '.) ' + mac)
	else:
		print('No matches found')
#        print('\n')
#        print('***********************')
#	print('Available Groups:')
	if len(possiblematches) == 1:
		endpointmac = possiblematches[0]
	elif len(possiblematches) > 1:
		print('\r')
		numberselected = int(raw_input('Select MAC address #: ')) 
	        endpointmac = matchdic[numberselected]
	else:
		print("No Matches found")
	print('\r')	
	print('Available Groups:') 
	print('***********************')

url = 'https://10.100.100.29:9060/ers/config/endpoint/name/{}'.format(endpointmac)
response = GetRequest(url)
if response:
        getendpointresult = json.loads(response.read())
        endpointid = getendpointresult['ERSEndPoint']['id']
        

url = 'https://10.100.100.29:9060/ers/config/endpointgroup'
response = GetRequest(url)
if response:
        #print(response.read())
        groupdic = {}
        allgroupresult = json.loads(response.read())
        listofgroups = allgroupresult['SearchResult']['resources']
        for num, group in enumerate(listofgroups, 1):
                print('\t' + str(num) + '.) ' + group['name'])
                groupdic[num] = group['name']


print('\r')
desiredgroup = int(raw_input('What is new Endpoint Group?: '))
#print(desiredgroup)
#desiredgroup = str(groupdic[desiredgroup])
#print(desiredgroup)
url = 'https://10.100.100.29:9060/ers/config/endpointgroup/name/{}'.format(groupdic[desiredgroup])

response = GetRequest(url)
if response:
    endgroupresult = json.loads(response.read())
    endpointgroupid = endgroupresult['EndPointGroup']['id']



url = "https://10.100.100.27:9060/ers/config/endpoint/{}".format(endpointid)
data = json.dumps({"ERSEndPoint": {"groupId": endpointgroupid, "staticGroupAssignment": True}})
method = "PUT"
request = urllib2.Request(url, data)
addingmultipleheaders([("Content-Type", "application/json"),('Accept', 'application/json')], request)
base64string = base64.b64encode('%s:%s' % (str(username), str(password)))
request.add_header("Authorization", "Basic %s" % base64string)  
request.get_method = lambda: method
#if data: request.add_data(data)
response = urllib2.urlopen(request, context=ssl._create_unverified_context())
if response:
        responseoutput = response.read() 
	if responseoutput == '{\n  "UpdatedFieldsList" : {\n    "updatedField" : [ ]\n  }\n}':
		print("""\n(INFO) MAC already using """ + groupdic[desiredgroup] + '\n')
	else:
                if response.getcode() == 200:
			print("\nSuccess: Endpoint updated to " + groupdic[desiredgroup] + "\n")
		#print(response.getcode())
		#print(responseoutput)
