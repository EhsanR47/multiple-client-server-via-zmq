import zmq
import time
import sys
import json
import os
from subprocess import check_output
from datetime import datetime
import gevent
from  multiprocessing import Process
import platform
import gevent
from gevent import subprocess


class Server():
    def __init__(self, socket):
        #, getip, getport
        #self.getip = getip
        #self.getport = getport
        #self.context = zmq.Context()
        #self.socket = self.context.socket(zmq.REP)
        #self.socket.bind("tcp://{0}:{1}".format(self.getip, self.getport))
        self.socket = socket
        self.data = self.socket.recv(1024)
        self.json_object = self.data.decode()
        self.writeFile()
        self.sendMsg()
        #self.endConnection()

    def writeFile(self):
        now = datetime.now()
        current_time = now.strftime("%H-%M-%S")
        # Writing to Client.json
        extension =".json"
        filename =  current_time + extension
        with open(filename, "w") as outfile:
            outfile.write(self.json_object)
            #print("Received")
        return str(filename)

    
    #Create result
    def oscp_Result(self):
        # Data to be written
        temp={}
        f = open(self.writeFile(),)
        temp = json.load(f)
        dic={}
        str1=""
        print(type(temp))
        print("self.json_object\n",temp)
        if temp['command_type']=="os":
            for i in range(len(temp['parameters'])):
                str1 += temp['parameters'][i]+' '
            str2= str(temp['command_name']) +" "+ str1
            dic={
                "given_os_command" : str2,
                "result" : self.os_Result(str2)
            }

        elif temp['command_type']=="compute":
            dic = {
                "given_math_expression" : temp['expression'],
                "result" : self.os_Compute(temp['expression'])
            }
        
        print("oscp_Result dic :\n",dic)
        json_result = json.dumps(dic, indent = 10)
        return json_result


    def os_Result(self,in_os):
        self.in_os = in_os
        if platform.system() =="Windows":
            o1=subprocess.Popen(self.in_os, stdout=subprocess.PIPE, shell=True)
            self.result = str(o1.stdout.read().decode())
        else:
            result_lin = check_output(self.in_os, shell=True)
            #print(os.popen(self.in_os).read())
            #return(os.popen(self.in_os).read())
            self.result=result_lin.decode('utf-8')
        return self.result
        


    def os_Compute(self,in_compute):
        self.in_compute = in_compute
        if platform.system() =="Windows":
            str_win = "set /a "+ str(self.in_compute)
            p1=subprocess.Popen(str_win, stdout=subprocess.PIPE, shell=True)
            return str(p1.stdout.read().decode())

        else:
            str_linux = f'echo "$(({self.in_compute}))"'
            p2=subprocess.Popen(str_linux, stdout=subprocess.PIPE, shell=True)
            return str(p2.stdout.read().decode('utf-8'))

        #print((eval(self.in_compute)))
        #return(eval(self.in_compute))

    def sendMsg(self):
        rs = self.oscp_Result()
        print("rs: \n",rs)
        self.socket.send(rs.encode())
        #self.socket.send("Message Received!".encode())

    def endConnection(self):
        self.socket.close()




def run_s(port="14200"):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://127.0.0.1:%s" % port)
    print ("Running server on port: ", port)
    # serves only 5 request and dies
    try:
        for reqnum in range(5):
            # Wait for next request from client
            #message = socket.recv(1024)
            message = socket
            server= Server(message)

    except Exception as e:
        print(e)

def main():
    # Now we can run a few servers 
    server_ports = range(14200,14208,2)
    for server_port in server_ports:
        Process(target=run_s, args=(server_port,)).start()



if __name__ == "__main__":
    main()

