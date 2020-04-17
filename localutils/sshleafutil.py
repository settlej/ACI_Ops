import re
try:
    import readline
except:
    pass
import os
from localutils.custom_utils import *
from collections import namedtuple
import subprocess

SSH_METHOD = 'oobMgmtAddr'

class local_l2bd():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return self.name

def remotesshcommand(cmd,user,device,leafnumber):
    sshsequence = 'ssh -t {user}@{device} -o ConnectTimeout=3 {cmd} '.format(user=user,device=device,cmd=cmd)
    print(("SSHing to leaf {leafnumber} to perform: '{cmd}'".format(user=user,device=device,cmd=cmd, leafnumber=leafnumber)).replace('\\',''))
    output = subprocess.Popen(sshsequence, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = output.communicate()
    if stderr:
        print(stderr)
        return True
    else:
        return False

class local_vrfobj():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return self.name

def get_epmMacEp(mac):
    #url = """https://{{apic}}/api/node/class/epmMacEp.json?rsp-subtree=full&query-target-filter=wcard(epmMacEp.flags,"local")""".format(apic=apic,mac=mac)
    url = """https://{apic}/api/node/class/epmMacEp.json?query-target-filter=and(eq(epmMacEp.addr,"{mac}"),wcard(epmMacEp.flags,"local"))&order-by=epmMacEp.modTs|desc""".format(apic=apic,mac=mac)
    results, totalcount = GetResponseData(url,cookie,return_count=True)
    if int(totalcount) == 1:
        dn = results[0]['epmMacEp']['attributes']['dn']
        l2bdpath = re.search(r'(^.*)/db-ep',dn).group(1)
        node = re.search(r'/node-(.+?)/',dn).group(1)
        return [[node, l2bdpath]]
    elif int(totalcount) > 1:
        multiple_locations = []
        for mac in results:
            dn = mac['epmMacEp']['attributes']['dn']
            l2bdpath = re.search(r'(^.*)/db-ep',dn).group(1)
            node = re.search(r'/node-(.+?)/',dn).group(1)
            multiple_locations.append((node,l2bdpath))
        return multiple_locations
    else:
        return 0



def gather_vrfs(apic,cookie,leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l3Ctx.json?&order-by=l3Ctx.modTs|desc""".format(apic=apic,leaf=leaf)
    results = GetResponseData(url,cookie=cookie)
    vrfobjlist = [local_vrfobj(x['l3Ctx']['attributes']) for x in results]
    #namelist = (x['l3Ctx']['attributes']['name'] for x in results)
    tenant_vrf_list = []
    for vrfobj in vrfobjlist:
        scope = vrfobj.scope
        if ':' in vrfobj.name:
            tenant, vrf = vrfobj.name.split(':')
            tenant_vrf_list.append((scope,[tenant, vrf]))
        else:
            tenant_vrf_list.append((scope,[vrf,""]))
    #import pdb; pdb.set_trace()
    return tenant_vrf_list
    #import pdb; pdb.set_trace()
    #tenant_vrf_list = []
    #for vrf in dnlist:
    #    tv = vrf.split('/')[1:]
    #    tenant = tv[0].replace('tn-','')
    #    vrf = tv[1].replace('ctx-','')
    #    tenant_vrf_list.append((tenant, vrf))
    #return namelist

def gather_l2BD(apic,cookie,leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l2BD.json""".format(apic=apic,leaf=leaf)
    #url = """https://{apic}/api/node/class/fvCtx.json?&order-by=fvCtx.modTs|desc""".format(apic=apic)
    results = GetResponseData(url,cookie=cookie)
    l2bdobjlist = [local_l2bd(x['l2BD']['attributes']) for x in results]
    for l2bd in l2bdobjlist:
        l2bd.tenant, l2bd.bd = l2bd.name.split(':')
    l2bdict = {l2bd.id:l2bd.__dict__ for l2bd in l2bdobjlist}
    return l2bdict

def gather_svi(apic,cookie,scope,leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/sviIf.json""".format(apic=apic,leaf=leaf)
    results = GetResponseData(url,cookie=cookie)
    svilist = []
    for svi in results:
        if scope in svi['sviIf']['attributes']['dn']:
            svilist.append(svi['sviIf']['attributes']['id'])
    #dnlist = (x['sviIf']['attributes']['dn'] for x in results)
    #svi = [x['sviIf']['attributes']['id'] for x in results]
    #svilist = []
    #for vrf in dnlist:

     #   tenant_vrf_list.append((tenant, vrf))
    return svilist

def tools_menu():
    location_banner('Tool Menu (SSH to leafs Requried)')
    print("\n" + 
            "Options:\n" +
            "--------\n\n" +
            "1.) iping endpoint from leaf\n" + 
            "2.) Clear endpoint on leaf\n" + 
            "3.) Check endpoint on leaf (placeholder)\n" + 
            "4.) Change ssh method (inband,oobm,infra) [default=oobm]\n")
    while True:
        result = custom_raw_input("What would you like to do?: ")
        result = result.strip().lstrip()
        if result != "" and result.isdigit() and int(result) <= 4 and int(result) > 0 and int(result) != 3:
            return result
        else:
            print('\n Invalid option...\n')

def ask_leaf_and_vrf(apic,cookie,user,all_leaflist):
    print("\nSelect leaf(s): ")
    print("\r")
    while True:
        chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
        if len(chosenleafs) > 1:
            print('\n\x1b[1;31;40mOne supported at this time, please try again...\x1b[0m')
            print('\r')
        else:
            break
    leafnumber = chosenleafs[0]
    url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=and(eq(topSystem.id,"{leafnumber}"))&order-by=fabricNode.modTs|desc""".format(apic=apic,leafnumber=leafnumber)
    results = GetResponseData(url,cookie)
    deviceip = results[0]['topSystem']['attributes'][SSH_METHOD]
    tenant_vrf_list = gather_vrfs(apic,cookie,leaf=chosenleafs[0])
    headers = ['#','Tenant','VRF']
    #import pdb; pdb.set_trace()
    numbers_tenant_vrf = [[str(len(tenant_vrf_list))] + x[1] for x in tenant_vrf_list] 
    sizes = get_column_sizes(numbers_tenant_vrf, minimum=5, baseminimum=headers)
    columnsizes = {'column1':sizes[0]+2,'column2':sizes[1],'column3':sizes[2]}
    print('{0:{column1}} | {1:{column2}} | {2:{column3}}'.format(*headers,**columnsizes))
    print('{empty:-<{column1}}-|-{empty:-<{column2}}-|-{empty:-<{column3}}'.format(empty='',**columnsizes))
    for num,tenantVrf in enumerate(numbers_tenant_vrf,1):
        print('{num:{column1}} | {tenant:{column2}} | {vrf:{column3}}'.format(num=str(num) + '.)',tenant=tenantVrf[1],vrf=tenantVrf[2],**columnsizes))
    while True:
        chosenvrf = custom_raw_input("\nSelect tenant|vrf #: ")
        if chosenvrf.isdigit() and int(chosenvrf) > 0 and int(chosenvrf) <= len(tenant_vrf_list) + 1:
            break
        else:
            continue
    tenantandvrf = numbers_tenant_vrf[int(chosenvrf)-1]
    selected_scope = tenant_vrf_list[int(chosenvrf)-1][0]
    tenantandvrf = ':'.join(tenantandvrf[1:])
    if tenantandvrf.endswith(':'):
        tenantandvrf = tenantandvrf[:-1]
    return tenantandvrf, deviceip, selected_scope, leafnumber


def iping_option(apic,cookie,user,all_leaflist):
    clear_screen
    location_banner('Ping Endpoints')

    #print("\nSelect leaf(s): ")
    #print("\r")
    #while True:
    #    chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
    #    if len(chosenleafs) > 1:
    #        print('\n\x1b[1;31;40mOne supported at this time, please try again...\x1b[0m')
    #        print('\r')
    #    else:
    #        break
    #url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=and(eq(topSystem.id,"{chosenleafs}"))&order-by=fabricNode.modTs|desc""".format(apic=apic,chosenleafs=chosenleafs[0])
    #results = GetResponseData(url,cookie)
    #deviceip = results[0]['topSystem']['attributes']['oobMgmtAddr']
    #tenant_vrf_list = gather_vrfs(apic,cookie,leaf=chosenleafs[0])
    #headers = ['#','Tenant','VRF']
    ##import pdb; pdb.set_trace()
    #numbers_tenant_vrf = [[str(len(tenant_vrf_list))] + x[1] for x in tenant_vrf_list] 
    #sizes = get_column_sizes(numbers_tenant_vrf, minimum=5, baseminimum=headers)
    #columnsizes = {'column1':sizes[0]+2,'column2':sizes[1],'column3':sizes[2]}
    #print('{0:{column1}} | {1:{column2}} | {2:{column3}}'.format(*headers,**columnsizes))
    #print('{empty:-<{column1}}-|-{empty:-<{column2}}-|-{empty:-<{column3}}'.format(empty='',**columnsizes))
    #for num,tenantVrf in enumerate(numbers_tenant_vrf,1):
    #    print('{num:{column1}} | {tenant:{column2}} | {vrf:{column3}}'.format(num=str(num) + '.)',tenant=tenantVrf[1],vrf=tenantVrf[2],**columnsizes))
    #while True:
    #    chosenvrf = custom_raw_input("\nSelect tenant|vrf #: ")
    #    if chosenvrf.isdigit() and int(chosenvrf) > 0 and int(chosenvrf) <= len(tenant_vrf_list) + 1:
    #        break
    #    else:
    #        continue
    #tenantandvrf = numbers_tenant_vrf[int(chosenvrf)-1]
    #selected_scope = tenant_vrf_list[int(chosenvrf)-1][0]
    #tenantandvrf = ':'.join(tenantandvrf[1:])
    #if tenantandvrf.endswith(':'):
    #    tenantandvrf = tenantandvrf[:-1]
    tenantandvrf, deviceip, vrf_scope, leafnumber = ask_leaf_and_vrf(apic,cookie,user,all_leaflist)
    while True:
        endpoint = custom_raw_input("What is the Endpoint IP address: ")
        if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', endpoint):
            break
        else:
            print('')
            print('Invalid IP address, try again...')
            print('')
    while True:
        options = custom_raw_input("Additional Options? [N]: ") or "N"
        options = options.strip().lstrip()
        if options != "" and options[0].upper() == 'N':
            options = False
            break
        elif options != "" and options[0].upper() == 'Y':
            options = True
            break
        else:
            print('\nInvalid entry, try again...\n')
            continue
    additionaloptions = None
    cmd='iping {endpoint} -V {vrf}'.format(endpoint=endpoint,vrf=tenantandvrf)
    if options:
        while True:
            count = custom_raw_input("Number of pings <count> [5]: ") or '5'
            count = count.strip().lstrip()
            if count != "" and count.isdigit():
                cmd = cmd + ' -c ' + str(count) 
                break
            else:
                print('\nInvalid entry, try again...\n')
                continue
        while True:
            packetsize = custom_raw_input("<packetsize> [1500]: ") or '1500'
            packetsize = packetsize.strip().lstrip()
            if packetsize != "" and packetsize.isdigit():
                cmd = cmd + ' -s ' + str(packetsize) 
                break
            else:
                print('\nInvalid entry, try again...\n')
                continue
        while True:
            dfbit = custom_raw_input("<df-bit> [N]: ") or 'N'
            dfbit = dfbit.strip().lstrip()
            if dfbit != "" and dfbit[0].upper() == 'Y':
                cmd = cmd + ' -F' 
                break
            elif dfbit != "" and dfbit[0].upper() == 'N':
                break
            else:
                print('\nInvalid entry, try again...\n')
                continue
        while True:
            timeout = custom_raw_input("<timeout> [2]: ") or '2'
            timeout = timeout.strip().lstrip()
            if timeout != "" and timeout.isdigit():
                cmd = cmd + ' -t ' + str(timeout) 
                break
            else:
                print('\nInvalid entry, try again...\n')
                continue
        while True:
            wait = custom_raw_input("<interval per packet sec> [0]: ") or '0'
            wait = wait.strip().lstrip()
            if wait != "" and wait.isdigit():
                cmd = cmd + ' -i ' + str(wait) 
                break
            else:
                print('\nInvalid entry, try again...\n')
                continue
        svilist = gather_svi(apic,cookie,scope=vrf_scope,leaf=leafnumber)
        l2bd_dict = gather_l2BD(apic,cookie,leaf=leafnumber)
        for num,x in enumerate(svilist,1):
            print('{}.) {:7} {}'.format(num,x, l2bd_dict[x.replace('vlan','')]['name']))
        while True:
            source = custom_raw_input("Source interface: ")
            source = source.strip().lstrip()
            if source == "":
                break
            if source != "" and source.isdigit() and int(source) > 0 and int(source) <= len(svilist) + 1:
                cmd = cmd + ' -S ' + str(svilist[int(source)-1]) 
                break
            else:
                print('\nInvalid entry, try again...\n')
                continue
        remotesshcommand(cmd,user=user,device=deviceip,leafnumber=leafnumber)
    else:
        cmd += ' -t 1 -i 0' 
        remotesshcommand(cmd,user=user,device=deviceip,leafnumber=leafnumber)
    custom_raw_input('\n[End of Results]')

def clear_endpoint_wizard(apic,cookie,user,all_leaflist):
    location_banner("Clear endpoint")
    while True:
        endpoint = custom_raw_input("\nFormat: [10.10.10.10 or aaaa.aaaa.aaaa]\n\n" + 
                    "What is the endpoint IP/MAC you would like to clear?: ")
        endpoint = endpoint.strip().lstrip()
        if re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', endpoint):
            while True:
                ask = custom_raw_input("\nMethod to find:\n" + \
                                    "1.) Manually select leaf\n" + \
                                    "2.) Search for me (beta)\n\n" + \
                                    "Selection [Default=2]: ") or "2"
                ask = ask.strip().lstrip()
                if ask != "" and ask.isdigit() and int(ask) > 0 and int(ask) <= 2:
                    break
                else:
                    print('\nInvalid option...\n')
            if ask == '1':
                tenantandvrf, deviceip, selected_scope, leafnumber = ask_leaf_and_vrf(apic,cookie,user,all_leaflist)
                endpoint = re.search(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', endpoint).group()
                clear_endpoint_ssh(endpoint,user,deviceip,leafnumber,tenantandvrf=tenantandvrf)
                break
            else:
                url = """https://{apic}/api/node/class/epmIpEp.json?query-target-filter=and(wcard(epmIpEp.flags,"local"),eq(epmIpEp.addr,"{ip}"))""".format(apic=apic,ip=endpoint)
                results, totalcount = GetResponseData(url,cookie,return_count=True)
                if totalcount == '0':
                    print('\nUnable to locate endpoint with IP address {ip}'.format(ip=endpoint))
                else:
                    ipMOlist = grab_lowest_MO_keyvalues(results, primaryKey='dn', keys=['addr','ifId'])
                    vlanresults = get_All_vlanCktEp(apic, cookie)
                    vlanMOlist = grab_lowest_MO_keyvalues(vlanresults, primaryKey='dn', keys=['name','id'])
                    print('\nFound:\n')
                    retopology = re.compile(r"(topology/pod-\d/(node-\d{1,4})/.*/vlan-\[(vlan-\d{1,4})\])")
                    for num,ipMO in enumerate(ipMOlist,1):
                        dn, node, vlan = retopology.findall(ipMO.dn)[0]
                        print("{num}.) leaf{leaf} | {ifId} | encap [{vlan}] | {ip}".format(num=num,leaf=node[4:],vlan=vlan,ip=endpoint,ifId=ipMO.ifId))
                    while True:
                        ask = custom_raw_input("\nDesired removal (only one supported): ")
                        if ask != "" and ask.isdigit() and int(ask) > 0 and int(ask) <= len(ipMOlist):
                            break
                    clear_endpoint_ssh(ipMO.ifId,user,deviceip,leafnumber,tenantandvrf=tenantandvrf)
                    
        elif re.search(r'([0-9a-fA-F]{2,4}[\:|\.]?){6}',endpoint):
            endpoint = re.search(r'([0-9a-fA-F]{2,4}[\:|\.]?){6}',endpoint).group()
            endpoint = endpoint.replace('.','').replace(':','').upper()
            endpoint = ':'.join((endpoint[x]+endpoint[x+1] for x in range(0,len(endpoint),2)))
            #results = get_All_l2BDs(apic,cookie)
           # vrf_bd_dict = grab_lowest_MO_keyvalues(results, primaryKey='dn', keys=['accEncap','id','name'])
            #import pdb; pdb.set_trace()
            locations_and_vlans = get_epmMacEp(endpoint)
            if locations_and_vlans == 0:
                custom_raw_input("\nUnable to locate MAC address on any leaf, please try another MAC\n")
                continue
            maclocation_list = []
            for maclocation in locations_and_vlans:
                node, l2path = maclocation
                url = "https://{apic}/api/mo/".format(apic=apic) + l2path + ".json"
                results = GetResponseData(url,cookie)
                l2bdmo = grab_lowest_MO_keyvalues(results, primaryKey='id', keys=['name'])
                maclocation_list.append((node,l2bdmo))
            if len(maclocation_list) == 1: 
                m = maclocation_list[0]
                while True:
                    ask = custom_raw_input("\nRemove MAC {0} on leaf {1} in {2}? [n]: ".format(endpoint,m[0],m[1][0].name)) or 'n'
                    ask = ask.strip().lstrip()
                    if ask != "" and ask.lower()[0] == 'n':
                        custom_raw_input('\nCancalled...')
                        break
                    elif ask != "" and ask.lower()[0] == 'y':
                        print('\nSubmitting for deletion...')
                        url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=and(eq(topSystem.id,"{leafnumber}"))&order-by=fabricNode.modTs|desc""".format(apic=apic,leafnumber=m[0])
                        results = GetResponseData(url,cookie)
                        deviceip = results[0]['topSystem']['attributes'][SSH_METHOD]
                        clear_endpoint_ssh(endpoint,user,deviceip,leafnumber=m[0],vlannum=m[1][0].id)
                        break
                    else:
                        print('\nInvalid option\n')
                        continue
            elif len(maclocation_list) > 1: 
                print('')
                for num,multiple in enumerate(maclocation_list,1):
                    print('{}.) leaf{} | localvlan-[{}] | {}'.format(num,multiple[0],multiple[1][0].id,multiple[1][0].name))
                while True:
                    ask = custom_raw_input("\nWhich MAC entry would you like removed? ")
                    ask = ask.strip().lstrip()
                    if ask != "" and ask.isdigit() and int(ask) > 0 and int(ask) <= (len(ask) + 1):
                        remove = maclocation_list[int(ask)-1]
                        confirm = custom_raw_input("Confirm removal {} [n]: ".format(endpoint)) or 'n'
                        if confirm.strip().lstrip()[0].lower() == 'y':
                            print('\nSubmitting for deletion...')
                            url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=and(eq(topSystem.id,"{leafnumber}"))&order-by=fabricNode.modTs|desc""".format(apic=apic,leafnumber=remove[0])
                            results = GetResponseData(url,cookie)
                            deviceip = results[0]['topSystem']['attributes'][SSH_METHOD]
                            clear_endpoint_ssh(endpoint,user,deviceip,leafnumber=remove[0],vlannum=remove[1][0].id)
                        custom_raw_input('\nCancalled...')
            else:
                print("Error: Unable to locate")
            break
            #import pdb; pdb.set_trace()
           # svilist = gather_svi(apic,cookie,scope=selected_scope,leaf=leafnumber)
           # l2bd_dict = gather_l2BD(apic,cookie,leaf=leafnumber)
        #    for num,x in enumerate(svilist,1):
        #        print('\t{}.) {:7} {}'.format(num,x, l2bd_dict[x.replace('vlan','')]['name']))
        #    while True:
        #        source = custom_raw_input("\nWhere does the MAC address reside?: ")
        #        source = source.strip().lstrip()
        #        if source != "" and source.isdigit() and int(source) > 0 and int(source) <= len(svilist) + 1:
        #            vlannum = svilist[int(source)-1][4:]
        #            #import pdb; pdb.set_trace()# cmd = cmd + ' -S ' + str(svilist[int(source)-1]) 
        #            break
        #        else:
        #            continue
        #    clear_endpoint_ssh(endpoint,user,deviceip,tenantandvrf,leafnumber,vlannum=vlannum)
        #    break
        #else:
        #    print('\nInvalid Endpoint...')

def clear_endpoint_ssh(endpoint,user,deviceip,leafnumber,tenantandvrf=None,vlannum=None):
    if ':' in endpoint:
        cmd = 'vsh -c \\"clear system internal epm endpoint key vlan {vlannum} mac {mac}\\"'.format(vlannum=vlannum,mac=endpoint)
    else:
        cmd = 'vsh -c \\"clear system internal epm endpoint key vrf {tenantandvrf} ip {ip}\\"'.format(tenantandvrf=tenantandvrf,ip=endpoint)
    error = remotesshcommand(cmd,user,deviceip,leafnumber=leafnumber)
    if not error:
        print("If no 'EP not found' it was a successful removal!")
    custom_raw_input('Continue...')

def change_ssh_method():
    print('\nSSH Options:\n' +
          '1.) OOBM IP (default)\n' +
          '2.) Inband IP\n' +  
          '3.) Infra vlan IP\n\n')
    while True:
        method = custom_raw_input("Select method: ")
        method = method.strip().lstrip()
        if method != "" and method.isdigit() and int(method) > 0 and int(method) <= 3:
            break
        else:
            print('\nInvalid Option...')
    global SSH_METHOD
    if method == '1':
        SSH_METHOD = 'oobMgmtAddr'
        print("\nSSH will use OOBM IP to ssh to leaf")
        custom_raw_input('Continue...')
    elif method == '2':
        SSH_METHOD = 'inbMgmtAddr'
        print("\nSSH will use INBAND IP to ssh to leaf")
        custom_raw_input('Continue...')
    else:
        SSH_METHOD = 'address'
        print("\nSSH will use INFRA IP to ssh to leaf")
        custom_raw_input('Continue...')


def main(import_apic,import_cookie,user):
    global apic
    global cookie
    cookie = import_cookie
    apic = import_apic
    all_leaflist = get_All_leafs(apic,cookie)
    if all_leaflist == []:
        print('\x1b[1;31;40mFailed to retrieve active leafs, make sure leafs are operational...\x1b[0m')
        custom_raw_input('\n#Press enter to continue...')
        return
    while True:
        clear_screen()
        option = tools_menu()
        if option == '1':
            iping_option(apic,cookie,user,all_leaflist)
        elif option == '2':
            clear_endpoint_wizard(apic,cookie,user,all_leaflist)
        elif option == '3':
            search_endpoint_on_leaf(apic,cookie,user,all_leaflist)
        elif option == '4':
            change_ssh_method()

