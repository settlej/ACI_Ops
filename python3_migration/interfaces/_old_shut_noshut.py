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
import readline
import urllib.request, urllib.error, urllib.parse
import json
import ssl
import os

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

def GetResponseData(url):
    # Fuction to take JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
    # Perform a GetRequest function to perform a GET REST call to server and provide response data
    response = GetRequest(url, cookie) # here for this
    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
    result = json.loads(response.read()) # here for this
    # return only infomation inside the dictionary under 'imdata'
    return result['imdata'] #here for this

def PostandGetResponseData(url, data):
    # Fuction to submit JSON and load it into Python Dictionary format and present all JSON inside the 'imdata' level
    # Perform a POSTRequest function to perform a POST REST call to server and provide response data
    response = POSTRequest(url, data, cookie)
    # the 'response' is an urllib2 object that needs to be read for JSON data, this loads the JSON to Python Dictionary format
    result = json.loads(response.read())
    # return only infomation inside the dictionary under 'imdata'
    return result['imdata']

def retrieve_leaf_list():
    # Display available leafs beginning of script
    url = """https://localhost/api/node/mo/topology/pod-1.json?query-target=children&target-subtree-class=fabricNode&query-target-filter=and(wcard(fabricNode.id,"^1[0-9][0-9]"))"""
    result = GetResponseData(url)
    leafs = [leaf['fabricNode']['attributes']['id'] for leaf in result]
    #print('Available leafs to bounce ports...')
    print(('\nAvailable Leafs\n' + '-'*12))
    for leaf in sorted(leafs):
        print(leaf)#Leaf' + ' Leaf'.join(leafs))

def whatleafs():
    # Fuction to ask user what leafs will be targeted for bouncing interfaces
    # Loop to ask repeativily until user input has data and not blank
    while True: # why is it true: what makes it false
        # Clear ssh session screen to make script look clean
        os.system('clear')
        retrieve_leaf_list()
        print('\n[Use format: 101,102 etc]')
        leafs = str(eval(input('\nWhat leaf(s): ')))
        if leafs == "":
            # 'continue' is built in fuction to restart the while loop
            continue 
        else:
            # If user input isn't blank then exit the while loop
            break
    # remove any spaces and return LIST if more than one leaf is declared via comma
    return leafs.replace(" ", "").split(',')

def whatinterfaces():
    # Fuction to ask user what interfaces will be targeted for bouncing interfaces
    # Loop to ask repeativily until user input has data and not blank
    while True:
        interfaces = str(eval(input('What interface(s): ')))
        #interfaces format needs to be 'eth1/2,6-10,33,45,47-48'
        if interfaces == "": #what makes this condition true
            continue 
        else:
            break
    # remove any spaces and return a STRING
    return interfaces.replace(" ", "") #what is this suppost to return

# Global variable 'cookie' to authenticate POST and GET REST requests to APICs
# .token file on server is a text file with APIC genearted 'APIC Cookie' info
with open('/.aci/.sessions/.token', 'r') as f:
    cookie = f.read()

while True:
    fex = False # what this for
    ending_interfaces = ""
    starting_interfaces = ""				
    leafs = whatleafs()
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
        slash_location = interfaces.rfind('/') #what are these doing
        ending_interfaces = interfaces[slash_location+1:]
        starting_interfaces = interfaces[:slash_location+1]
        fexnumber = re.search(r'[0-9]{3}', starting_interfaces).group()
    elif interfaces.count('/') == 1:
        slash_location = interfaces.find('/')
        ending_interfaces = interfaces[slash_location+1:]
        starting_interfaces = interfaces[:slash_location+1]
    else:
        print('incorrect format')
        continue

    #create list for interface numbers
    numlist = []	
    # If else to calculate interfaces for ranges and single interfaces
    if ',' in ending_interfaces:
        ending_interfaces = ending_interfaces.split(',')
        for num_int in ending_interfaces:
            #checking to see if range includes a '-' if so include in numlist
            if re.search(r'-', num_int):
                if not re.search(r'^([1-5]{0,2}|[0-9]{0,2})-[0-9]{1,3}', num_int):
                    print('fail incorrect numbers')
                else:
                    ending_interfaces = re.search(r'^([1-5]{0,2}|[0-9]{0,2})-[0-9]{1,3}', num_int).group()
                    num_int = num_int.replace('-', ',').split(',')
                    for x in range(int(num_int[0]),int(num_int[-1])+1):
                        numlist.append(str(x))
            else:
                numlist.append(num_int)
            #print(numlist)
    elif '-' in ending_interfaces:
        if not re.search(r'^([1-5]{0,1}|[0-9]{0,2})-[0-9]{1,2}', ending_interfaces):
            print('fail restart')	
        ending_interfaces = re.search(r'^([1-5]{0,1}|[0-9]{0,2})-[0-9]{1,2}', ending_interfaces).group()
        ending_interfaces = ending_interfaces.replace('-', ',').split(',')
        for x in range(int(ending_interfaces[0]),int(ending_interfaces[-1])+1):
            numlist.append(x)
    else:
        numlist.append(ending_interfaces)


    interfaces = [starting_interfaces + str(x) for x in numlist]	
    leafinterfacenotification = ""		
    for leaf in leafs:
        for inter in interfaces:
            leafinterfacenotification += str(leaf) + '\t' + str(inter) + '\n'
        leafinterfacenotification += '\n'	

    while True:
        ask = str(eval(input('\nBounce ports: \n\n' + '{:<5}\t{}\n'.format('leaf', 'interface') + '{:-<40}\n'.format('-') + leafinterfacenotification + '\nCorrect? [y/n]: ')))	

        if ask == "":
            continue
    
        if ask[0].lower() == "y":
            
            print(('\n' + 
                'leaf\tinterface\n' +
                '-'*40))
            # incase there are multiple leafs, declaired by user, interate through each leaf
            for leaf in leafs:
                # upon current leaf interation go through list of interfaces declaired by user
                for ints in interfaces:
                    if fex:
                        # Shutting fex interfaces
                        url = 'https://localhost/api/node/mo/uni/fabric/outofsvc.json'
                        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a fex interface
                        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
                        PostandGetResponseData(url, data)
                        print((leaf + ' ' + fexnumber + ' ' +  ints + ' shut'))
                        #verifysuccessfulsubmition(command, prompt, 'shut', (fexnumber + ints))
                        
                        # No Shutting fex interfaces
                        url = 'https://localhost/api/node/mo/uni/fabric/outofsvc.json'
                        # data is the 'POST' data sent in the REST call to delete 'blacklist' (shutdown) on a fex interface
                        data = """'{{"fabricRsOosPath":{{"attributes":{{"dn":"uni/fabric/outofsvc/rsoosPath-[topology/pod-1/paths-{leaf}/extpaths-{fexnumber}/pathep-[{ints}]]","status":"deleted"}},"children":[]}}}}'""".format(fexnumber=fexnumber,ints=('eth1' + ints[8:]),leaf=leaf)
                        PostandGetResponseData(url, data)
                        print((leaf + ' ' + fexnumber + ' ' + ints + ' no shut'))
                        #verifysuccessfulsubmition(command, prompt, 'no-shut', (fexnumber + ints))
                    else:
                        # Shutting normal interfaces
                        url = 'https://localhost/api/node/mo/uni/fabric/outofsvc.json' 
                        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a normal interface
                        data = """'{{"fabricRsOosPath":{{"attributes":{{"tDn":"topology/pod-1/paths-{leaf}/pathep-[{ints}]","lc":"blacklist"}},"children":[]}}}}'""".format(ints=ints,leaf=leaf)
                        PostandGetResponseData(url, data)
                        print((leaf + '\t' + ints + ' shut'))
    
                        # No Shutting normal interfaces
                        #verifysuccessfulsubmition(command, prompt, 'shut', (ints))
                        url = 'https://localhost/api/node/mo/uni/fabric/outofsvc.json'
                        # data is the 'POST' data sent in the REST call to 'blacklist' (shutdown) on a normal interface
                        data = """'{{"fabricRsOosPath":{{"attributes":{{"dn":"uni/fabric/outofsvc/rsoosPath-[topology/pod-1/paths-{leaf}/pathep-[{ints}]]","status":"deleted"}},"children":[]}}}}'""".format(ints=ints,leaf=leaf) 
                        PostandGetResponseData(url, data)
                        print((leaf + '\t' + ints + ' no shut'))
                        #verifysuccessfulsubmition(command, prompt, 'no-shut', (ints))
                print('\n')
    
            #leafs = []
            #interfaces = []	
            #print('\n')
            askmore = eval(input('Would you like to bounce more ports? [y/n]:  '))
            if askmore[0].lower() == 'y' and not askmore == '':
                break
            else:
                exit()
            
    
        elif ask[0].lower() == "n":
            leafs = []
            interfaces = []	
            print('Canceling....\n')
            continue
    
        else:
            leafs = []
            interfaces = []	
            print('Canceling.....\n')
            break