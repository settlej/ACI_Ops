import re
try:
    import readline
except:
    pass
import os
from localutils.custom_utils import *
from collections import namedtuple

class local_l2bd():
    def __init__(self, kwargs):
        self.__dict__.update(**kwargs)
    def __repr__(self):
        return self.name

def remotesshcommand(cmd,user,device):
    sshsequence = 'ssh -t {user}@{device} {cmd}'.format(user=user,device=device,cmd=cmd)
    print('SSHing to leaf to perform iping: "{cmd}"'.format(user=user,device=device,cmd=cmd))
    os.system(sshsequence)

def gather_vrfs(apic,cookie):
    url = """https://{apic}/api/node/class/fvCtx.json?&order-by=fvCtx.modTs|desc""".format(apic=apic)
    results = GetResponseData(url,cookie=cookie)
    dnlist = (x['fvCtx']['attributes']['dn'] for x in results)
    tenant_vrf_list = []
    for vrf in dnlist:
        tv = vrf.split('/')[1:]
        tenant = tv[0].replace('tn-','')
        vrf = tv[1].replace('ctx-','')
        tenant_vrf_list.append((tenant, vrf))
    return tenant_vrf_list

def gather_l2BD(apic,cookie,leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/l2BD.json""".format(apic=apic,leaf=leaf)
    #url = """https://{apic}/api/node/class/fvCtx.json?&order-by=fvCtx.modTs|desc""".format(apic=apic)
    results = GetResponseData(url,cookie=cookie)
    l2bdobjlist = [local_l2bd(x['l2BD']['attributes']) for x in results]
    for l2bd in l2bdobjlist:
        l2bd.tenant, l2bd.bd = l2bd.name.split(':')
    l2bdict = {l2bd.id:l2bd.__dict__ for l2bd in l2bdobjlist}
    return l2bdict

def gather_svi(apic,cookie,leaf):
    url = """https://{apic}/api/node/class/topology/pod-1/node-{leaf}/sviIf.json""".format(apic=apic,leaf=leaf)
    results = GetResponseData(url,cookie=cookie)
    dnlist = (x['sviIf']['attributes']['dn'] for x in results)
    svi = (x['sviIf']['attributes']['dn'] for x in results)
    tenant_vrf_list = []
    for vrf in dnlist:
        tv = vrf.split(':')
        tenant = tv[0]
        vrf = tv[1]
        tenant_vrf_list.append((tenant, vrf))
    return tenant_vrf_list

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
        location_banner('Ping Endpoints')
        #selection = interface_menu()
        #try:
        #if selection == '1':
        print("\nSelect leaf(s): ")
        print("\r")
        while True:
            chosenleafs = physical_leaf_selection(all_leaflist, apic, cookie)
            if len(chosenleafs) > 1:
                print('\n\x1b[1;31;40mOnce leaf supported at this time, please try again...\x1b[0m')
                print('\r')
            else:
                break
        url = """https://{apic}/api/node/class/topSystem.json?query-target-filter=and(eq(topSystem.id,"{chosenleafs}"))&order-by=fabricNode.modTs|desc""".format(apic=apic,chosenleafs=chosenleafs[0])
        results = GetResponseData(url,cookie)
        deviceip = results[0]['topSystem']['attributes']['oobMgmtAddr']
        gather_l2BD(apic,cookie,leaf=chosenleafs[0])
        tenant_vrf_list = gather_vrfs(apic,cookie)
        headers = ['#','Tenant','VRF']
        numbers_tenant_vrf = [str(len(tenant_vrf_list))] + tenant_vrf_list
        sizes = get_column_sizes(numbers_tenant_vrf, minimum=5, baseminimum=headers)
        columnsizes = {'column2':sizes[0],'column3':sizes[1]}
        print('{0:{column1}} | {1:{column2}} | {2:{column3}}'.format(*headers,column1=len(str(len(tenant_vrf_list)))+2,**columnsizes))
        print('{empty:-<{column1}}-|-{empty:-<{column2}}-|-{empty:-<{column3}}'.format(empty='',column1=len(str(len(tenant_vrf_list)))+2,**columnsizes))
        for num,tenantVrf in enumerate(tenant_vrf_list,1):
            print('{num:{column1}} | {tenant:{column2}} | {vrf:{column3}}'.format(num=str(num) + '.)',column1=len(str(len(tenant_vrf_list)))+2,tenant=tenantVrf[0],vrf=tenantVrf[1],**columnsizes))
        while True:
            chosenvrf = custom_raw_input("\nSelect tenant|vrf #: ")
            if chosenvrf.isdigit() and int(chosenvrf) > 0 and int(chosenvrf) <= len(tenant_vrf_list) + 1:
                break
            else:
                continue
        tenantandvrf = tenant_vrf_list[int(chosenvrf)-1]
        while True:
            endpoint = custom_raw_input("What is the Endpoint IP address: ")
            if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', endpoint):
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
        cmd='iping {endpoint} -t 1 -i 0 -V {vrf}'.format(endpoint=endpoint,vrf=':'.join(tenantandvrf))
        if options:
            cmd = cmd + ' ' + additionaloptions
            remotesshcommand(cmd,user=user,device=deviceip)
        else:
            remotesshcommand(cmd,user=user,device=deviceip)
        custom_raw_input('\n[End of Results]')