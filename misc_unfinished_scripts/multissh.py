from multiprocessing.dummy import Pool as ThreadPool
import paramiko
import logging
import time
logging.basicConfig(level=logging.INFO)

switchlist = [#("10.200.200.203","cisco","cisco"),
              ##("10.200.200.204","cisco","cislco"),
              #("10.200.200.205","cisco","cisco"),
              #("10.200.200.206","cisco","cisco"),
             ## ("10.200.200.208","cisco","cisco"),
              #("10.200.200.205","cisco","cisco"),
              #("10.200.200.206","cisco","cisco"),
              #("10.200.200.205","cisco","cisco"),
              #("10.200.200.206","cisco","cisco"),
              ("192.168.255.1","cisco","cisco"),
              #              ("10.200.200.205","cisco","cisco"),
              #("10.200.200.206","cisco","cisco"),
              #("10.200.200.208","cisco","cisco"),
              #("10.200.200.209","cisco","cisco"),
              #("10.200.200.210","cisco","cisco"),
              ]

class ssh:
 
    def __init__(self, address, username, password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
       # self.transport = paramiko.Transport((address, 22))
        #self.session = self.transport.open_channel(kind='session')
        #self.session.setblocking(0)
        #print('hit1')
        #self.transport.connect(username=username, password=password)
        #print('connected')
 
       # thread = threading.Thread(target=self.process)
       # thread.daemon = Truec
       # thread.start()
 
    def closeConnection(self):
        if(self.client != None):
            self.client.close()
            self.transport.close()
    def sendcommand(self):
        print('hit2')
        self.session.send('show run\r')
        result = self.session.recv(9000)
        print(result)

    def openShell(self):
        self.shell = self.client.invoke_shell()
 
    def sendShell(self, command):
        if(self.shell):
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")
 
def create_switchobj(switch):
    sshobj = ssh(switch[0],switch[1],switch[2])
    #import pdb; pdb.set_trace()
    print('CONNECTED' + switch[0])
    shell = sshobj.client.invoke_shell()
    while True:
        if shell.recv_ready():
            break
    output = shell.recv(5000)
    shell.send('show run\n')
    print(shell.recv_ready(),1)
    #time.sleep(1)
    print(shell.recv_ready(),2)
    #import pdb; pdb.set_trace()
    while True:
        if shell.recv_ready():
            output += shell.recv(5000)
            time.sleep(10)
        elif not shell.recv_ready():
            break
            #while True:
            #    current = None
            #    current = shell.recv(5000)
            #    import pdb; pdb.set_trace()
            #    if current != None:
            #        output += current
            #    else:
            #        break
            #    print(repr(current))
            #break
    
    #import pdb; pdb.set_trace()
    if 'ERROR' in output:
        print('\t\t\t\t\t\t' +switch[0])
    print(output)

#def sendcommand_func(switchobj):
#    switchobj.sendcommand()

def multithreading_kickoff(switchlist):
    pool = ThreadPool(10)
    results = pool.map(lambda x : create_switchobj(x), switchlist)
    pool.close()
    pool.join()


def main():
    a = time.time()
    #switchlistobj = []
    #for switch in switchlist:
    #    sshobj = create_switchobj(switch)
    #    switchlistobj.append(sshobj)
    #for switch in switchlist:
    #    create_switchobj(switch)

    multithreading_kickoff(switchlist)
    b = time.time()
    print(b-a)

main()


