#!/usr/bin/env python

import os
import getpass
import urllib2
import ssl
import json
import sys
import threading
import time
from localutils.custom_utils import *
import interfaces.change_interface_state as shut_noshut_interfaces
import interfaces.assign_epg_interfaces as assign_epg_interfaces
import interfaces.remove_epgs_interfaces as remove_egps
#import interfaces.show_interface_epgs as show_epgs
import interfaces.show_all_endpoints_on_interface as show_all_endpoints_on_interface
import interfaces.portsanddescriptions as portsanddescriptions
import interfaces.interfacecounters as showinterface
import faults_and_logs.new_important_faults as fault_summary
import faults_and_logs.most_recent_fault_changes as most_recent_fault_changes
import faults_and_logs.most_recent_admin_changes as most_recent_admin_changes
import faults_and_logs.most_recent_event_changes as most_recent_event_changes
import faults_and_logs.alleventsbetweendates as alleventsbetweendates
import faults_and_logs.alleventsbetweendates_fulldetail as alleventsbetweendates_fulldetail
import information.endpoint_search as ipendpoint
import information.routetranslation as epg_troubleshooting
import information.routetranslation as routetranslation
import information.routetrace as check_routing
import information.show_static_routes as show_static_routes
import configuration.create_local_span_session as create_local_span_session
import configuration.span_to_server as span_to_server




# getToken is used if application is run on local machine and not directly on APIC server
# apic key word will be a string ipaddress
def getToken(apic, user, pwd):
    # Set ssl certificate to automatically verify and proceed 
    ssl._create_default_https_context = ssl._create_unverified_context
    # url POST request to login to APIC and recieve cookie hash
    url = "https://{apic}/api/aaaLogin.json".format(apic=apic)
    # POST Login requires user creds provided in the data section of url request
    payload = '{"aaaUser":{"attributes":{"name":"%(user)s","pwd":"%(pwd)s"}}}' % {"pwd":pwd,"user":user}
    request = urllib2.Request(url, data=payload)
    # If APIC is unreachable within 4 sec cancel URL request to server, prevents long timeouts on wrong input
    response = urllib2.urlopen(request, timeout=4)
    # If successful response transfer informaton to a dictionary format using 'loads'
    token = json.loads(response.read())
    # Set global variable to access 'cookie' everywhere in current module
    global cookie
    cookie = token["imdata"][0]["aaaLogin"]["attributes"]["token"]
    return cookie

# Allows automatic APIC session cookie for URL requests if ssh to server 
# and program run directly on server, prevents two logins
def getCookie():
    # location of session token/cookie, open as read-only
    with open('/.aci/.sessions/.token', 'r') as f:
        # Set global variable to access 'cookie' everywhere in current module
        global cookie
        cookie = f.read()
        # Currently unnecessary but 'return' provided until decision for global to be removed or not 
        return cookie # str

# Test if script is run on APIC or on local computer
def localOrRemote():
    # If path exisits the program is running on APIC server and bypass login
    if os.path.isfile('/.aci/.sessions/.token'):
        # APIC requires IP in urlpath to use a loopback address with said token above
        apic = "localhost"
        # Set global variable to access 'cookie' everywhere in current module
        global cookie
        cookie = getCookie()
        # return apic hostname and discovered cookie
        return apic, cookie # str , str
    else:
        if os.environ.get('apic'):
            user = os.environ.get('user')
            pwd = os.environ.get('password')
            apic = os.environ.get('apic')
            cookie = getToken(apic,user,pwd)
            return apic, cookie
        else:    
            # if '.token' file doesn't exist than prompt APIC ip and username/password login.
            # Set defaults variables before login, allow variable to change if login attempts fail.
            # if both are False the first to 'if' conditions will not match, cause haven't attempted login.
            unauthenticated = False
            timedout = False
            # error value required to prevent Exception stating error variable not defined for use below
            error = ''
            # Loop for login Attempts, requires 'break' to exit loop
            while True:
                # Clear console ouput creating clean login screen for login attempt
                clear_screen()
                if unauthenticated:
                    # print error reason after cleared console screen
                    print(error)
                    # reset unauthenticated to prevent 'if' capture if failure is a different reason
                    unauthenticated = False
                # Server doesn't respond in time to login request (unreachable default 4 sec)
                elif timedout:
                    # print error reason after cleared console screen
                    print(error)
                    # reask IP in cause IP typed incorrectly
                    apic = raw_input("Enter IP address or FQDN of APIC: ")
                    # reset time
                    timedout = False
                else:
                    print(error)
                    apic = raw_input("\nEnter IP address or FQDN of APIC: ")
                try:
                    user = raw_input('\nUsername: ')
                    pwd = getpass.getpass('Password: ')
                    getToken(apic, user,pwd)
                except urllib2.HTTPError as auth:
                    unauthenticated = True
                    error = '\n\x1b[1;31;40mAuthentication failed\x1b[0m\n'
                    continue
                except urllib2.URLError as e:
                    timedout = True
                    error = "\n\x1b[1;31;40mThere was an '%s' error connecting to APIC '%s'\x1b[0m\n" % (e.reason,apic)
                    continue
                except KeyboardInterrupt as k:
                    print("\nEnding Program\n")
                    exit()
                except Exception as e:
                    print(e)
                    print("\n\x1b[1;31;40mError has occured, please try again\x1b[0m\n")
                    continue
                break
    return apic, cookie

def reauthenticate(apic, error):
    unauthenticated = True
    timedout = False
    while True:
        clear_screen()
        if unauthenticated:
            print(error)
            unauthenticated = False
        elif timedout:
            print(error)
            apic = raw_input("Enter IP address or FQDN of APIC: ")
            timedout = False
        try:
            user = raw_input('\nUsername: ')
            pwd = getpass.getpass('Password: ')
            getToken(apic, user,pwd)
        except urllib2.HTTPError:
            unauthenticated = True
            error = '\n\x1b[1;31;40mAuthentication failed\x1b[0m\n'
            continue
        except urllib2.URLError as e:
            timedout = True
            error = "\n\x1b[1;31;40mThere was an '%s' error connecting to APIC '%s'\x1b[0m\n" % (e.reason,apic)
            continue
        except Exception as e:
            print("\n\x1b[1;31;40mError has occured, please try again\x1b[0m\n")
            continue
        return cookie

class AuthenticationFailure(Exception):
    """Authentication Failure"""
    pass

def authentication_session(apic, cookie):
    while True:
        time.sleep(3)
        print('auth session deamon')
    #q = Queue.Queue()
    #refreshToken()

def main():
    unauthenticated = False
    apic, cookie = localOrRemote()
    #a = threading.Thread(target=authentication_session, args=(apic,cookie))
    #a.daemon = True
    #a.start()
    #print(a.isDaemon)
   # raw_input('test')
    keyinterrupt = False
    while True:
        try:
            clear_screen()
            if unauthenticated:
                error = '\n\x1b[1;31;40mAuthentication Failed or timed out...restarting program\x1b[0m'
                cookie = reauthenticate(apic, error)
            unauthenticated = False
            clear_screen()
            if keyinterrupt:
                pass
                #print('\x1b[1;31;40m-------------------------------------------------')
                #print('\nPrevious operation cancelled\n')
                #print('-------------------------------------------------\x1b[0m')
          #  import pdb; pdb.set_trace()

            print('\n What would you like to do?:\n\n' +
                            '\t\x1b[1;32;40m  [INTERFACES]\n'+
                            '\t ---------------------------------------------------\n' +
                            '\t| 1.)  Shut/NoShut interfaces\n' + 
                            '\t| 2.)  Show interface stats and EPGs\n' + 
                            '\t| 3.)  Add EPGs to interfaces\n' +
                            '\t| 4.)  Remove EPGs from interfaces\n' + 
                            '\t| 5.)  Show interfaces status\n' +
                            #'\t| 6.)  Show single interface\n' + 
                            '\t| 6.)  Show Endpoints on interface (Not Available)\n' +
                            '\t ---------------------------------------------------\n\n' +
                            '\t  [FAULTS and LOGS]\n'
                            '\t ---------------------------------------------------\n' +
                            '\t| 7.)  Faults Summary\n' + 
                            '\t| 8.)  Recent Faults\n' +
                            '\t| 9.)  Recent Admin Changes\n' + 
                            '\t| 10.) Recent Events\n' +
                            '\t| 11.) Faults/Admin/Events Between Dates\n' + 
                            '\t| 12.) Faults/Admin/Events Between Dates (Detail)\n' +
                            '\t ---------------------------------------------------\n\n' +
                            '\t  [INFORMATION]\n'
                            '\t ---------------------------------------------------\n' +
                            '\t| 13.) Endpoint Search\n' + 
                            '\t| 14.) Show Leaf/Spine/APIC info (Not Available)\n' +
                            '\t| 15.) EPG to EPG troubleshooting (alpha)\n' +
                            '\t| 16.) Route lookup to endpoint \n' +
                            '\t| 17.) Show all static routes\n' + 
                            '\t ---------------------------------------------------\n\n' +
                            '\t  [CONFIGURATION]\n'
                            '\t ---------------------------------------------------\n' +
                            '\t| 18.) Configure Local Span\n' + 
                            '\t| 19.) Capture server traffic ERSPAN to server\n' + 
                            '\t| 20.) Create EPGs (Not Available)\n' +
                            '\t| 21.) Configure interface Descriptions (Not Available)\n' + 
                            #'\t| 21.) Import/Export interface Descriptions (Not Available)\n' + 
                            '\t ---------------------------------------------------\x1b[0m')
            print('\x1b[7')
            print('\x1b[1;33;40m\x1b[5;70H -----------------------------\x1b[0m')
            print('\x1b[1;33;40m\x1b[6;70H|           Hint:             \x1b[0m|')
            print('\x1b[1;33;40m\x1b[7;70H|  Type "exit" on any input   \x1b[0m|')
            print('\x1b[1;33;40m\x1b[8;70H|    to return to main menu   \x1b[0m|')
            print('\x1b[1;33;40m\x1b[9;70H -----------------------------\x1b[0m')
            print('\x1b[8')
            choosen = custom_raw_input('\x1b[u\x1b[40;1H Select a number: ')
            if choosen == '1':
                try:
                    shut_noshut_interfaces.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '2':
                try:
                    showinterface.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '3':
                try:
                    assign_epg_interfaces.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue            
            elif choosen == '4':
                try:
                    remove_egps.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '5':
                try:
                    portsanddescriptions.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
           # elif choosen == '55':
           #     try:
           #         showinterface.main(apic,cookie)
           #         keyinterrupt = False
           #     except KeyboardInterrupt as k:
           #         print('\nExit to Main menu\n')
           #         keyinterrupt = True
           #         continue
            elif choosen == '6':
                try:
                    show_all_endpoints_on_interface.main(apic,cookie)
                    keyinterrupt = False
                    continue
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '7':
                try:
                    fault_summary.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '8':
                try:
                    most_recent_fault_changes.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '9':
                try:
                    most_recent_admin_changes.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '10':
                try:
                    most_recent_event_changes.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '11':
                try:
                    alleventsbetweendates.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '12':
                try:
                    alleventsbetweendates_fulldetail.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '13':
                try:
                    ipendpoint.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue		
            elif choosen == '14':
                try:
                    routetranslation.main(apic,cookie)
                    keyinterrupt = False
                    continue
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '15':
                try:
                    epg_troubleshooting.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            elif choosen == '16':
                try:
                    check_routing.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue      

            elif choosen == '17':
                try:
                    show_static_routes.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue

            elif choosen == '18':
                try:
                    create_local_span_session.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue
            #elif choosen == 'exit':
            #    raise KeyboardInterrupt
            elif choosen == '19':
                try:
                    span_to_server.main(apic,cookie)
                    keyinterrupt = False
                except KeyboardInterrupt as k:
                    print('\nExit to Main menu\n')
                    keyinterrupt = True
                    continue

            
        except urllib2.HTTPError as e:
            unauthenticated = True
            continue

        except KeyboardInterrupt as k:
            print('\nEnding Program\n')
            exit()
        #except Exception as e:
        #    print(e)
        #    break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as k:
        print('\nEnding Program\n')
        #exit()
