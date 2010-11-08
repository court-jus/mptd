#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.internet import reactor, protocol
from twisted.protocols import basic
from lw_dm import MptdScreen
import time

game = None
connection = None
serverFound = False

class GameNetwork(MptdScreen):
    
    def __init__(self, *args, **kwargs):
        self._lastptime = time.time()
        super(GameNetwork, self).__init__(*args, **kwargs)

    def serversend(self, msg):
        global connection
        print "connection : ", connection,"msg",msg
        if connection:
            connection.transport.write("%s\n" % (msg,))

    def superloop (self, fps = 10): 
        global connection, serverFound
        #self._exit = 0 
    
        def _loop():
            if time.time() - self._lastptime > 1:
                self._lastptime = time.time()
            if self._exit:
                reactor.stop()
                return
            self.mainloop(fps)
            reactor.callLater(1./fps, _loop)
        _loop()    
   
class MptdLineReceiver(basic.LineReceiver):

    def connectionMade(self):
        global connection
        connection = self
        connection.transport.write("hi there\n")
        print 'Connection Made'
            
    def lineReceived(self, data):
        print "Data received", data
        
    def connectionLost(self, reason):
        print 'Connection Lost:', reason
        try:
            reactor.stop()
        except:
            pass

class MptdClientFactory(protocol.ClientFactory):
    protocol = MptdLineReceiver

class ServerFinder(protocol.DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        global serverFound
        if not serverFound:
            factory = MptdClientFactory()
            reactor.connectTCP(host, int(data), factory)
            serverFound = True
        
def main():
    global game
    t = reactor.listenUDP(0, ServerFinder())
    t.write('find', ('224.0.0.1', 9300))
    game = GameNetwork()

    # Initialize game looping
    game.superloop(fps = 60)

    # Launch twisted main loop
    reactor.run()

if __name__ == '__main__':
    main()
