import re
import readline
import urllib2
import json
import ssl
import os
import datetime

def displaycurrenttime():
    currenttime = datetime.datetime.now()
    return str(currenttime)[:-3]

def time_difference(event_time):
    currenttime = datetime.datetime.now()
    ref_event_time = datetime.datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S.%f')
    return str(currenttime - ref_event_time)[:-7]


def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-trig", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())
def GetResponseData(url):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

def getCookie():
    global cookie
    with open('/.aci/.sessions/.token', 'r') as f:
        cookie = f.read()


def askrefresh():
    while True:
        refresh = raw_input("Return to event list? [y=default|n]:  ") or 'y'
        if refresh[0].lower() == 'y':
            return True
        elif refresh[0].lower() == 'n':
            return False
        else:
            continue
    

def gatheranddisplayrecentevents():
    while True:
        getCookie()
        os.system('clear')
        print("Current time = " + displaycurrenttime())
        print("\nEvents loading...\n")
        url = """https://localhost/api/node/class/eventRecord.json?query-target-filter=not(wcard(eventRecord.dn,%22__ui_%22))&order-by=eventRecord.created|desc&page=0&page-size=50"""
        result, totalcount = GetResponseData(url)
        #print(result)
        os.system('clear')
        print("Current time = " + displaycurrenttime())

        print('\n{:>5}   {:26}{:20}{:24}{}'.format('#','Time','Time Difference', 'Port','Event Summary'))
        print('-'*175)
        
        eventdict = {}
        for num,event in enumerate(result,1):
            if event.get('eventRecord'):
                eventdescr = event['eventRecord']['attributes']['descr'].split()
                eventdescr = ' '.join(eventdescr)
                if len(eventdescr) > 120:
                     summaryeventdescr = eventdescr[:120] + '...'
                else:
                    summaryeventdescr = eventdescr
                eventcreated = ' '.join(event['eventRecord']['attributes']['created'].split('T'))
                eventtrig = event['eventRecord']['attributes']['trig']
                eventuser = event['eventRecord']['attributes']['user']
                eventdn = event['eventRecord']['attributes']['dn']
                #if 'Port' in summaryeventdescr and 'po' in eventdn:
                #print(eventdn)
                if 'eth' in eventdn and not 'extpaths' in eventdn:
                    #print(eventdn)
                #    print(1)
                    leaf = re.search(r'(node-[0-9]{1,3})|(paths-[0-9]{1,3})', eventdn).group()
                    #leaf = leaf.replace('node', 'leaf')
                    if leaf.startswith('paths'):
                        leaf = leaf.replace('paths', 'leaf')
                    elif leaf.startswith('node'):
                        leaf = leaf.replace('node', 'leaf')
                    interface = re.search(r'eth.*\/[0-9]{1,3}\]', eventdn).group()
                    portinterfaces = '{} {}'.format(leaf,interface[:-1])
                elif re.search(r'po[0-9]*\]', eventdn):
                    
                #    print(2)
                    leaf = re.search(r'node-[0-9]{1,3}', eventdn).group()
                    leaf = leaf.replace('node', 'leaf')
                    interface = re.search(r'po[0-9]*\]', eventdn).group()
                    portinterfaces = '{} {}'.format(leaf,interface[:-1])
                #elif 'rsoosPath' in eventdn and not 'extpaths' in eventdn:
                #    print(3)
                #    #print(eventdn)
                #    leaf = re.search(r'protpaths-[0-9]{3}-[0-9]{3}', eventdn).group()
                #    leaf = leaf.replace('protpaths', 'VPC node')
                #    interface = re.search(r'pathep-.*\]', eventdn).group()
                #    interface = interface.replace('pathep-', "")
                #    portinterfaces = '{} {}'.format(leaf,interface[:-1])
                #elif 'rsoosPath' in eventdn and 'extpaths' in eventdn:
                #    print(4)
                #    leaf = re.search(r'paths-[0-9]{3}', eventdn).group()
                #    leaf = leaf.replace('paths','node')
                #    fex = re.search(r'extpaths-.*\]', eventdn).group()
                #    interface = re.search(r'eth[0-9]{1,3}/[0-9]{1,3}', eventdn).group()
                #    portinterfaces = '{} {} {}'.format(leaf,fex,interface)
                else:
                    portinterfaces = ""
                diff_time = time_difference(eventcreated[:-6])
                eventdict[num] = [eventcreated[:-6],eventtrig,eventuser,eventdn,eventdescr]
                print('{:5}.) {:26}{:20}{:24}{}'.format(num,eventcreated[:-6],diff_time,portinterfaces,summaryeventdescr))
        
        while True:
            moredetails = raw_input("\nMore details, select number [refresh=Blank and Enter]:  ")
            if moredetails == '':
                break
            if moredetails.isdigit() and eventdict.get(int(moredetails)):
                break
            else:
                print('\x1b[41;1mInvalid, number does not exist...try again\x1b[0m\n') 
        if moredetails == '':
            continue
        diff_time = time_difference(eventdict[int(moredetails)][0])
        print('\n\n{:26}{:20}{:18}{:18}{}'.format('Time','Time Difference', 'Type','User','Object-Affected'))
        print('-'*120)
        #print('/'.join(str(eventdict[int(moredetails)][3]).split('/')[:-1]))
        print('{:26}{:20}{:18}{:18}{}\n'.format(eventdict[int(moredetails)][0],diff_time, eventdict[int(moredetails)][1],eventdict[int(moredetails)][2],'/'.join(str(eventdict[int(moredetails)][3]).split('/')[:-1])))
        print('Event Details')
        print('-'*15)
        print(eventdict[int(moredetails)][4])
        print('\n\n')

        refresh = askrefresh()
        if refresh == True:
            continue
        else:
            print('\nEnding Program...\n')
            break
        

def main():
    gatheranddisplayrecentevents()

    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print("\n\nExiting Program....")
        exit()
   # except Exception as e:
    #    print(e)