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

def GetRequest(url, icookie):
    method = "GET"
    cookies = 'APIC-cookie=' + icookie
    request = urllib2.Request(url)
    request.add_header("cookie", cookies)
    request.add_header("Content-trig", "application/json")
    request.add_header('Accept', 'application/json')
    return urllib2.urlopen(request, context=ssl._create_unverified_context())

def GetResponseData(url, cookie):
    response = GetRequest(url, cookie)
    result = json.loads(response.read())
    return result['imdata'], result["totalCount"]

#def getCookie():
#    global cookie
#    with open('/.aci/.sessions/.token', 'r') as f:
#        cookie = f.read()

def displaycurrenttime():
    currenttime = datetime.datetime.now()
    return str(currenttime)[:-3]

def time_difference(admin_time):
    currenttime = datetime.datetime.now()
    ref_admin_time = datetime.datetime.strptime(admin_time, '%Y-%m-%d %H:%M:%S.%f')
    return str(currenttime - ref_admin_time)[:-7]
