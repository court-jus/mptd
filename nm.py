import socket
import threading
import pygame

class nm(threading.Thread):
    def __init__(self,cm,hostname,port):        
        threading.Thread.__init__(self)
        self.cm = cm
        self.hostname = hostname
        self.port = port
        self._stopevent = threading.Event()
	self.cm.register(self)
        self.connected = False
        
    def run(self):
	#create an INET, STREAMing socket
	self.cs = socket.socket(
	    socket.AF_INET, socket.SOCK_STREAM)
	#now connect to the web server on port 80 
	# - the normal http port
        self.cs.setblocking(0)
        print "trying to connect to server"
        try:
           print "connecting to",self.hostname,"on",self.port
	   self.cs.connect((self.hostname, int(self.port)))
        except:
            pass
        self.connected = True
        while not self._stopevent.isSet():
            pygame.time.wait(1)
            try:
                r = self.cs.recv(4096)
                if r:
                    #print "received",r
                    event = ["network_recv",r]
                    #print "here NM, i post",event
                    self.cm.post(event)
            except:
                pass
        print "nm thread ended"
    
    def send(self,message):
        #print "sending",message
        self.cs.send(message)
    
    def stop(self):
        self.send("I Quit")
        self._stopevent.set()
        
    def notify(self,event):
        if event [0] == "network_send":
            self.cs.send(event[1])
